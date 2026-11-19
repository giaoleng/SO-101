#!/usr/bin/env python3
"""Plan and optionally start a 50-demo teleoperation session for one condition.

Operator must follow the printed numbered plan and change the physical scene
between episodes. All commands are dry-run unless --execute is supplied.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.real.study_protocol import TASK, TRAIN_CONDITIONS, collection_plan


def record_command(*, repo_id: str, dataset_root: Path, follower_port: str,
                   leader_port: str, follower_id: str, leader_id: str,
                   front_idx: int, wrist_idx: int) -> list[str]:
    if front_idx == wrist_idx or min(front_idx, wrist_idx) < 0:
        raise ValueError('Camera indices must be distinct nonnegative integers')
    cameras = {'front': {'type': 'opencv', 'index_or_path': front_idx, 'width': 640, 'height': 480, 'fps': 30},
               'wrist': {'type': 'opencv', 'index_or_path': wrist_idx, 'width': 640, 'height': 480, 'fps': 30}}
    return ['lerobot-record', '--robot.type=so101_follower', f'--robot.port={follower_port}',
            f'--robot.id={follower_id}', '--robot.cameras=' + json.dumps(cameras, separators=(',', ':')),
            '--teleop.type=so101_leader', f'--teleop.port={leader_port}', f'--teleop.id={leader_id}',
            f'--dataset.repo_id={repo_id}', f'--dataset.root={dataset_root}',
            '--dataset.single_task=' + TASK, '--dataset.num_episodes=50',
            '--dataset.fps=30', '--dataset.episode_time_s=45', '--dataset.reset_time_s=15',
            '--dataset.push_to_hub=false']


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--condition', required=True, choices=TRAIN_CONDITIONS)
    p.add_argument('--repo-id', required=True)
    p.add_argument('--dataset-root', required=True, type=Path)
    p.add_argument('--follower-port', required=True)
    p.add_argument('--leader-port', required=True)
    p.add_argument('--follower-id', default='so101_follower')
    p.add_argument('--leader-id', default='so101_leader')
    p.add_argument('--front-idx', type=int, required=True)
    p.add_argument('--wrist-idx', type=int, required=True)
    p.add_argument('--plan-output', type=Path, help='Optional new JSON run sheet (no overwrite)')
    p.add_argument('--execute', action='store_true')
    args = p.parse_args(argv)
    try:
        cmd = record_command(repo_id=args.repo_id, dataset_root=args.dataset_root,
                             follower_port=args.follower_port, leader_port=args.leader_port,
                             follower_id=args.follower_id, leader_id=args.leader_id,
                             front_idx=args.front_idx, wrist_idx=args.wrist_idx)
    except ValueError as exc:
        p.error(str(exc))
    plan = collection_plan(args.condition)
    print(json.dumps({'condition': args.condition, 'will_execute': args.execute,
                      'record_command': cmd, 'demos': plan}, ensure_ascii=False, indent=2))
    if args.plan_output:
        args.plan_output.parent.mkdir(parents=True, exist_ok=True)
        with args.plan_output.open('x', encoding='utf-8') as fh:
            json.dump({'condition': args.condition, 'demos': plan}, fh, ensure_ascii=False, indent=2)
    if not args.execute:
        return
    if args.dataset_root.exists():
        p.error('Dataset root already exists; refuse to overwrite or append')
    input('确认已验证 SO-101 标定、急停、相机与工作空间。按 Enter 开始人工遥操作采集 50 条示教：')
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
