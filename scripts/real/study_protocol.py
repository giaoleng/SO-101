#!/usr/bin/env python3
"""Fixed-budget SO-101 SmolVLA study protocol; offline planning only.

The named positions are labels, not borrowed physical coordinates. The operator must
measure and mark their own safe workspace before any collection or rollout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TRAIN_CONDITIONS = ('clean', 'randomized', 'recovery', 'color')
EVAL_CELLS = ('in_distribution', 'new_positions', 'reduced_lighting', 'different_object', 'distractors')
TRAINING_SEEDS = (1000, 2000)
POSITIONS = tuple(f'T{i}' for i in range(1, 11))
HELD_OUT = tuple(f'E{i}' for i in range(1, 6))
COLORS = ('red', 'orange', 'yellow', 'blue', 'purple')
DEMOS_PER_CONDITION = 50
SCORED_EPISODES = 15
WARMUP_EPISODES = 1
TASK = 'Pick up the cube and place it in the cup.'


def collection_plan(condition: str) -> list[dict]:
    """One operator-facing instruction per expert demonstration (1-based)."""
    if condition not in TRAIN_CONDITIONS:
        raise ValueError(f'Unknown training condition: {condition}')
    rows = []
    for index in range(DEMOS_PER_CONDITION):
        drop = condition == 'recovery' and index % 5 in (1, 3)
        position = POSITIONS[index % 10] if condition == 'randomized' else 'T6'
        rows.append({
            'demo': index + 1, 'condition': condition,
            'position_id': position,
            'cube_color': COLORS[index % 5] if condition == 'color' else 'red',
            'demonstrate_drop_and_regrasp': drop,
            'instruction': ('Deliberately release once during carrying, re-grasp, and finish.'
                            if drop else 'Complete a first-try pick-and-place.'),
        })
    return rows


def evaluation_plan(cell: str) -> list[dict]:
    """Sixteen trials per cell: one discarded warmup, then fifteen scored rollouts."""
    if cell not in EVAL_CELLS:
        raise ValueError(f'Unknown evaluation cell: {cell}')
    result = []
    for index in range(WARMUP_EPISODES + SCORED_EPISODES):
        scored_index = max(index - WARMUP_EPISODES, 0)
        position = HELD_OUT[scored_index // 3] if cell == 'new_positions' else 'T6'
        scene = {
            'eval_cell': cell,
            'episode': index,
            'warmup': index < WARMUP_EPISODES,
            'scored_episode': None if index < WARMUP_EPISODES else scored_index + 1,
            'position_id': position,
            'cube_color': 'green' if cell == 'different_object' else 'red',
            'lighting': 'reduced' if cell == 'reduced_lighting' else 'baseline',
            'distractors': cell == 'distractors',
        }
        result.append(scene)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=('collect', 'evaluate'))
    parser.add_argument('--condition', choices=TRAIN_CONDITIONS)
    parser.add_argument('--cell', choices=EVAL_CELLS)
    parser.add_argument('--output', type=Path, help='Write JSON plan; refuses overwrite')
    args = parser.parse_args(argv)
    if args.phase == 'collect':
        if not args.condition or args.cell:
            parser.error('collect requires --condition and does not accept --cell')
        plan = collection_plan(args.condition)
    else:
        if not args.cell or args.condition:
            parser.error('evaluate requires --cell and does not accept --condition')
        plan = evaluation_plan(args.cell)
    payload = json.dumps(plan, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as handle:
            handle.write(payload + '\n')
    else:
        print(payload)


if __name__ == '__main__':
    main()
