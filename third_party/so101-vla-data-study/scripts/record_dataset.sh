#!/usr/bin/env bash
# Adapted from Andresg324/so101-vla-data-study/scripts/record_dataset.sh.
# Formal conditions only: clean | randomized | recovery | color.
# Linux usage: export FOLLOWER_PORT, LEADER_PORT, OVERHEAD_IDX, WRIST_IDX first.
set -euo pipefail
CONDITION=${1:-clean} # Conditions are 'clean' | 'randomized' | 'recovery' | 'color'
NUM_EPISODES=${2:?usage: record_dataset.sh <condition> <num_episodes>}
DATASET_ROOT=${DATASET_ROOT:-$HOME/lerobot_data/cube-pickup-${CONDITION}}

case "$CONDITION" in
    clean|randomized|recovery|color) ;;
    *) echo "unknown condition '$CONDITION' (clean|randomized|recovery|color)"; exit 1;;
esac

# ---- Hardware information ----
: "${FOLLOWER_PORT:?Set FOLLOWER_PORT to the SO-101 follower serial port}"
: "${LEADER_PORT:?Set LEADER_PORT to the SO-101 leader serial port}"
: "${OVERHEAD_IDX:?Set OVERHEAD_IDX to the overhead camera index}"
: "${WRIST_IDX:?Set WRIST_IDX to the wrist camera index}"
HF_USER=${HF_USER:-Andresg324}

# Confirm indices with tools/check_cameras.py before every session
# Camera indices are supplied by the operator for this Linux host.

# Two cameras -> dataset keys 'wrist' (Seeed idx0) and 'overhead' (C270 idx1)
# dataset name encodes the condition; instruction is the same across all conditions

lerobot-record \
    --robot.type=so101_follower \
    --robot.port=${FOLLOWER_PORT} \
    --robot.id=my_follower_arm \
    --robot.cameras="{ overhead: {type: opencv, index_or_path: ${OVERHEAD_IDX}, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: ${WRIST_IDX}, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port=${LEADER_PORT} \
    --teleop.id=my_leader_arm \
    --dataset.repo_id=${HF_USER}/cube-pickup-${CONDITION} \
    --dataset.single_task="Pick up the cube and place it in the cup" \
    --dataset.num_episodes=${NUM_EPISODES} \
    --dataset.root=${DATASET_ROOT} \
    --dataset.fps=30 \
    --dataset.episode_time_s=45 \
    --dataset.reset_time_s=15 \
    --dataset.push_to_hub=${PUSH:-false} \
    --resume=${RESUME:-false}
