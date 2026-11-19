#!/usr/bin/env python3
"""Score a fixed 16-rollout SO-101 cell using the existing guarded real runner.

Each trial requires manual scene setup and operator scoring. Without --execute the
command only prints the plan and never opens cameras or the robot serial port.
"""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.real.deploy_policy import metadata
from scripts.real.evaluate_policy import read_outcome
from scripts.real.runtime import RealPolicyRunner, local_path
from scripts.real.study_protocol import (EVAL_CELLS, TRAIN_CONDITIONS, TRAINING_SEEDS,
                                         evaluation_plan)
from scripts.eval.act_rollout import JsonlRecorder


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/real/so101.yaml')
    p.add_argument('--condition', choices=TRAIN_CONDITIONS, required=True,
                   help='Training data condition, not the evaluation scene')
    p.add_argument('--cell', choices=EVAL_CELLS, required=True)
    p.add_argument('--seed', type=int, choices=TRAINING_SEEDS, required=True,
                   help='Seed of the trained checkpoint (not an inference RNG seed)')
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--training-manifest', type=Path, required=True, help='Matching study_manifest.json from training run')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    return p


def _prepare_runner_config(args):
    from scripts.real.runtime import load_config
    cfg = load_config(args.config)
    if cfg['policy']['type'] != 'smolvla' or cfg['conditioning']['mode'] != 'language':
        raise ValueError('Study evaluation requires SmolVLA with language conditioning')
    cfg['policy']['checkpoint'] = str(local_path(args.checkpoint))
    return cfg


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    cfg = _prepare_runner_config(args)
    cells = evaluation_plan(args.cell)
    summary = {'condition': args.condition, 'eval_cell': args.cell,
               'seed': args.seed, 'checkpoint': cfg['policy']['checkpoint'],
               'training_manifest': str(local_path(args.training_manifest)),
               'scored_episodes': 15, 'warmup_episodes': 1,
               'output': str(local_path(args.output)), 'will_execute': args.execute}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.execute:
        return
    manifest = json.loads(local_path(args.training_manifest).read_text(encoding='utf-8'))
    if (manifest.get('condition') != args.condition or manifest.get('seed') != args.seed or
            manifest.get('steps') != 10000 or manifest.get('batch_size') != 32):
        p.error('Training manifest condition/seed/budget does not match this evaluation')
    # Align camera feature names with the rename map saved by the training run.
    rename = manifest.get('rename_map', {})
    if not isinstance(rename, dict):
        p.error('Malformed training rename_map')
    cameras = {}
    for old_name, settings in cfg['robot']['cameras'].items():
        raw_feature = 'observation.images.' + old_name
        new_feature = rename.get(raw_feature, raw_feature)
        if not isinstance(new_feature, str) or not new_feature.startswith('observation.images.'):
            p.error(f'Invalid renamed feature: {new_feature}')
        new_name = new_feature.removeprefix('observation.images.')
        if not new_name or new_name in cameras:
            p.error('Camera rename_map would duplicate a camera key')
        cameras[new_name] = settings
    cfg['robot']['cameras'] = cameras
    cfg['policy']['dataset_root'] = str(Path(manifest['dataset_root']))
    weights = Path(cfg['policy']['checkpoint']) / 'model.safetensors'
    with weights.open('rb') as fh:
        digest = hashlib.file_digest(fh, 'sha256').hexdigest()
    if digest != manifest.get('model_sha256'):
        p.error('Checkpoint weights do not match the training manifest')
    if Path(local_path(args.output)).exists():
        p.error('Output JSONL already exists; refuse to overwrite')
    recorder = JsonlRecorder(local_path(args.output), {**metadata(cfg), 'training_manifest': str(local_path(args.training_manifest))})
    try:
        runner = RealPolicyRunner(cfg)
        for item in cells:
            label = ('warmup (not scored)' if item['warmup'] else f"scored {item['scored_episode']}/15")
            input(f"[{args.condition}/seed{args.seed} {args.cell}] episode {item['episode']} {label}\n"
                  f"Position={item['position_id']}, color={item['cube_color']}, lighting={item['lighting']}, "
                  f"distractors={item['distractors']}. Confirm physical scene + safe home; Enter to run: ")
            common = {'train_condition': args.condition, 'eval_cell': args.cell,
                      'seed': args.seed, 'episode': item['episode'],
                      'position_id': item['position_id'], 'cube_color': item['cube_color'],
                      'lighting': item['lighting'], 'distractors': item['distractors'],
                      'is_warmup': item['warmup']}
            try:
                motion = runner.run_episode('cube')
                if motion['reason'] == 'stop_file':
                    recorder({**common, **motion, 'completed': False})
                    break
                if item['warmup']:
                    recorder({**common, **motion, 'completed': False})
                    print('Warmup recorded without success label; excluded from scored results.')
                    continue
                outcome = read_outcome()
                recorder({**common, **motion, **outcome, 'completed': True})
            except BaseException as exc:
                recorder({**common, 'completed': False, 'reason': 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'error',
                          'error_type': type(exc).__name__})
                raise
    finally:
        recorder.close()


if __name__ == '__main__':
    main()
