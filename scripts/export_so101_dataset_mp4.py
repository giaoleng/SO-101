#!/usr/bin/env python3
"""Export real success/failure SO-101 episodes as MP4 from rovolabs dataset.

Run from the Git working tree root (or set --output-dir to an absolute path).
Requires: pip install huggingface_hub pandas pyarrow; ffmpeg & ffprobe.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

REPO = "rovolabs/so-arm101-pick-place"
CONTROLLERS = {"gpudad": 0, "ik": 1, "smolvla": 2}


def scalar(value):
    """LeRobot stores these episode-constant labels as scalars or 1-item arrays."""
    for _ in range(8):
        if isinstance(value, (list, tuple)):
            if len(value) != 1:
                raise ValueError(f"Expected one label value: {value!r}")
            value = value[0]
        elif hasattr(value, "tolist"):
            value = value.tolist()
        elif hasattr(value, "item"):
            value = value.item()
        else:
            break
    return value


def fetch(filename, revision, cache_dir):
    return Path(hf_hub_download(
        repo_id=REPO, repo_type="dataset", filename=filename,
        revision=revision, cache_dir=cache_dir,
    ))


def repo_paths(revision):
    names = HfApi().list_repo_files(repo_id=REPO, repo_type="dataset", revision=revision)
    data = sorted(name for name in names if name.startswith("data/") and name.endswith(".parquet"))
    episodes = sorted(name for name in names if name.startswith("meta/episodes/") and name.endswith(".parquet"))
    if not data or not episodes:
        raise RuntimeError("Dataset is missing LeRobot v3 parquet data/episode metadata")
    return data, episodes


def find_labeled_examples(data_paths, source, revision, cache_dir):
    """Scan *every needed* data shard; file-000 alone may not contain SmolVLA."""
    matches = {True: None, False: None}
    for remote in data_paths:
        print(f"Reading labels: {remote}", flush=True)
        local = fetch(remote, revision, cache_dir)
        frame_labels = pd.read_parquet(
            local, columns=["episode_index", "episode_success", "annotation.action_source"]
        )
        # Both fields are constant within each episode (as documented by dataset).
        episode_labels = frame_labels.drop_duplicates(subset=["episode_index"])
        for row in episode_labels.itertuples(index=False, name=None):
            episode_index, success, controller = row
            if int(scalar(controller)) != source:
                continue
            success = bool(scalar(success))
            idx = int(episode_index)
            current = matches[success]
            if current is None or idx < current:
                matches[success] = idx
        if all(idx is not None for idx in matches.values()):
            break
    if any(idx is None for idx in matches.values()):
        raise RuntimeError(f"Unable to find both outcomes for controller={source}: {matches}")
    return matches


def all_episode_metadata(paths, revision, cache_dir):
    frames = [pd.read_parquet(fetch(name, revision, cache_dir)) for name in paths]
    metadata = pd.concat(frames, ignore_index=True)
    if metadata.episode_index.duplicated().any():
        raise RuntimeError("Duplicate episode_index entries in metadata")
    return metadata.set_index("episode_index", drop=False)


def locate_video(ep, video_key, metadata, video_template):
    if ep not in metadata.index:
        raise RuntimeError(f"Episode {ep} not present in metadata")
    row = metadata.loc[ep]
    prefix = f"videos/{video_key}/"
    required = [prefix + field for field in ("chunk_index", "file_index", "from_timestamp", "to_timestamp")]
    missing = [key for key in required if key not in row.index]
    if missing:
        raise RuntimeError(f"Metadata video fields not found: {missing}")
    remote_path = video_template.format(
        video_key=video_key,
        chunk_index=int(row[prefix + "chunk_index"]),
        file_index=int(row[prefix + "file_index"]),
    )
    start = float(row[prefix + "from_timestamp"])
    end = float(row[prefix + "to_timestamp"])
    if start < 0 or end <= start:
        raise RuntimeError(f"Invalid clip times for Episode {ep}: {start}, {end}")
    return remote_path, start, end


def export_mp4(source, target, start, end):
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.6f}", "-i", str(source),
        "-t", f"{end - start:.6f}", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "24",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
    ]
    subprocess.run(command, check=True)
    if not target.is_file() or target.stat().st_size <= 0:
        raise RuntimeError(f"Failed to export valid MP4: {target}")
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(target)],
        capture_output=True, text=True, check=True,
    )
    if float(probe.stdout.strip()) <= 0:
        raise RuntimeError(f"MP4 has no playable duration: {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", choices=CONTROLLERS, default="smolvla")
    parser.add_argument("--camera", choices=("front", "overhead", "wrist"), default="front")
    parser.add_argument("--output-dir", type=Path, default=Path("media/dataset_examples"))
    parser.add_argument("--revision", default="main", help="Optional commit SHA for reproducibility")
    parser.add_argument("--cache-dir", type=Path, default=None,
                        help="Override Hugging Face cache, useful if disk space is low")
    parser.add_argument("--dry-run", action="store_true", help="Show episodes and timestamps without video download")
    args = parser.parse_args()

    if not args.dry_run and (not shutil.which("ffmpeg") or not shutil.which("ffprobe")):
        parser.error("Install ffmpeg first: sudo apt install ffmpeg")

    print(f"Dataset: {REPO} | controller: {args.controller} | camera: {args.camera}", flush=True)
    video_key = "observation.images." + args.camera
    # Resolve a fixed commit SHA so metadata and video files can never come from
    # different revisions if the dataset's main branch is updated mid-download.
    resolved = HfApi().repo_info(repo_id=REPO, repo_type="dataset", revision=args.revision).sha
    print(f"Resolved dataset revision: {resolved}", flush=True)
    info = json.loads(fetch("meta/info.json", resolved, args.cache_dir).read_text())
    data_paths, episode_paths = repo_paths(resolved)
    examples = find_labeled_examples(data_paths, CONTROLLERS[args.controller], resolved, args.cache_dir)
    meta = all_episode_metadata(episode_paths, resolved, args.cache_dir)

    clips = []
    for outcome, success in (("success", True), ("failure", False)):
        ep = examples[success]
        remote, start, end = locate_video(ep, video_key, meta, info["video_path"])
        dest = args.output_dir / f"{args.controller}_{outcome}.mp4"
        clips.append({
            "dataset": REPO,
            "revision": resolved,
            "episode_index": ep,
            "episode_success": success,
            "controller": args.controller,
            "camera": args.camera,
            "source_video": remote,
            "start_seconds": start,
            "end_seconds": end,
            "local_video": str(dest),
        })
        print(f"{outcome.upper()}: Episode {ep}; {remote}; {start:.3f} - {end:.3f}s", flush=True)

    if args.dry_run:
        print("Dry run finished. MP4 files not downloaded. Remove --dry-run to export.")
        return

    for clip in clips:
        print(f"Downloading shared video file: {clip['source_video']}", flush=True)
        source = fetch(clip["source_video"], resolved, args.cache_dir)
        export_mp4(source, Path(clip["local_video"]), clip["start_seconds"], clip["end_seconds"])
        print(f"Written: {clip['local_video']}", flush=True)

    # Preserve the source_manifest.json schema used by the existing Codex change.
    # Never mark examples "generated" unless both outputs are checked first.
    entries = []
    for clip in clips:
        result = Path(clip["local_video"])
        if not result.exists() or result.stat().st_size == 0:
            raise RuntimeError(f"Missing exported MP4: {result}")
        entries.append({
            "output": result.name,
            "episode_index": clip["episode_index"],
            "episode_success": clip["episode_success"],
            "annotation.action_source": CONTROLLERS[args.controller],
            "controller": "ACTION_" + args.controller.upper(),
            "source_revision": resolved,
            "source_video": clip["source_video"],
            "source_time_range_s": [clip["start_seconds"], clip["end_seconds"]],
            "status": "generated",
        })
    manifest_data = {
        "source_dataset": REPO,
        "source_url": "https://huggingface.co/datasets/" + REPO,
        "license": "CC-BY-4.0",
        "task": "Pick up the red cube and place it in the blue box.",
        "status": "generated",
        "examples": entries,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = args.output_dir / "source_manifest.json"
    manifest.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nDone. Videos come from an external CC BY 4.0 dataset, not your own evaluation.")
    print("Provenance: " + str(manifest))


if __name__ == "__main__":
    main()
