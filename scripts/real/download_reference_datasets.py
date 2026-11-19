#!/usr/bin/env python3
"""Download the four SO-101 demonstration datasets used in the real-robot study.

The binary LeRobot data is kept under data/ (git-ignored), not committed to Git.
Each download is pinned to the Hugging Face dataset commit resolved at download time
and recorded in download_manifest.json for reproducibility.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DATASETS = {
    "clean": "Andresg324/cube-pickup-clean_20260809_105745",
    "randomized": "Andresg324/cube-pickup-randomized_20260809_115825",
    "recovery": "Andresg324/cube-pickup-recovery_20260809_141725",
    "color": "Andresg324/cube-pickup-color_20260809_183224",
}
EXPECTED_EPISODES = 50
EXPECTED_FPS = 30
REQUIRED_FEATURES = (
    "action",
    "observation.state",
    "observation.images.overhead",
    "observation.images.wrist",
)
ALLOW_PATTERNS = ("meta/**", "data/**", "videos/**", "README.md", "LICENSE")


def validate_dataset_metadata(metadata: dict[str, Any]) -> None:
    if metadata.get("total_episodes") != EXPECTED_EPISODES:
        raise ValueError(
            f"Expected {EXPECTED_EPISODES} episodes, got {metadata.get('total_episodes')}"
        )
    if metadata.get("fps") != EXPECTED_FPS:
        raise ValueError(f"Expected {EXPECTED_FPS} FPS, got {metadata.get('fps')}")
    features = metadata.get("features", {})
    missing = [key for key in REQUIRED_FEATURES if key not in features]
    if missing:
        raise ValueError(f"Missing required LeRobot features: {missing}")
    for key in ("action", "observation.state"):
        if features[key].get("shape") != [6]:
            raise ValueError(f"{key} must have shape [6]")


def _card_license(info: Any) -> str | None:
    card = getattr(info, "card_data", None)
    if card is None:
        return None
    if isinstance(card, dict):
        return card.get("license")
    return getattr(card, "license", None)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--condition",
        nargs="+",
        choices=tuple(DATASETS),
        default=list(DATASETS),
        help="Conditions to download; defaults to all four registered conditions.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/real_demonstrations"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the four-condition download plan without downloading files.",
    )
    args = parser.parse_args(argv)

    plan = [
        {
            "condition": condition,
            "repo_id": DATASETS[condition],
            "target": str(args.output_root / condition),
        }
        for condition in args.condition
    ]
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise SystemExit(
            "huggingface_hub is required. Install it with: "
            "python -m pip install -U huggingface_hub"
        ) from exc

    api = HfApi()
    completed = {}
    args.output_root.mkdir(parents=True, exist_ok=True)

    for item in plan:
        condition = item["condition"]
        repo_id = item["repo_id"]
        target = Path(item["target"])
        print(f"[{condition}] Resolving {repo_id} ...")
        repo_info = api.dataset_info(
            repo_id=repo_id,
            revision="main",
            files_metadata=True,
        )
        revision = repo_info.sha
        if not revision:
            raise RuntimeError(f"Could not resolve an immutable revision for {repo_id}")

        print(f"[{condition}] Downloading revision {revision} to {target} ...")
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            revision=revision,
            local_dir=str(target),
            allow_patterns=list(ALLOW_PATTERNS),
        )

        info_path = target / "meta" / "info.json"
        if not info_path.is_file():
            raise FileNotFoundError(f"Downloaded dataset is missing {info_path}")
        metadata = json.loads(info_path.read_text(encoding="utf-8"))
        validate_dataset_metadata(metadata)

        siblings = getattr(repo_info, "siblings", None) or []
        total_bytes = sum(
            getattr(sibling, "size", 0) or 0
            for sibling in siblings
            if any(
                getattr(sibling, "rfilename", "").startswith(prefix.rstrip("*"))
                for prefix in ("meta/", "data/", "videos/")
            )
        )
        completed[condition] = {
            "repo_id": repo_id,
            "revision": revision,
            "local_path": str(target),
            "license": _card_license(repo_info),
            "total_episodes": metadata["total_episodes"],
            "total_frames": metadata.get("total_frames"),
            "fps": metadata["fps"],
            "features": list(metadata["features"]),
            "reported_file_bytes": total_bytes or None,
        }
        print(
            f"[{condition}] Verified {metadata['total_episodes']} episodes, "
            f"{metadata.get('total_frames')} frames, {metadata['fps']} FPS."
        )

    manifest_path = args.output_root / "download_manifest.json"
    temporary_path = manifest_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(
            {
                "source_repository": "https://github.com/Andresg324/so101-vla-data-study",
                "conditions": completed,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(manifest_path)
    print(f"Download manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
