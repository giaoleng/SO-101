# Upstream SO-101 VLA Data Study — selected code

Source repository: https://github.com/Andresg324/so101-vla-data-study  
Source commit: 175d3d057aa91ff785168400a24cc1410c140dbc

The selected source-derived files in this directory are included under the upstream MIT license
(copy at LICENSE).

## Included

- scripts/record_dataset.sh — teleoperated expert-data recording workflow.
- scripts/run_inference.sh — episodic real-robot rollout workflow.
- configs/train_config_{clean,randomized,recovery,color}.json — seed 1000 configs.
- configs/train_config_{clean,randomized,recovery,color}-seed2000.json — seed 2000 configs.

The eight training configs are copied verbatim from the upstream repository. The two shell
scripts are adapted for this Ubuntu project: the Density and exploratory-only conditions are
removed, serial ports and camera indices must be provided by the operator, inference defaults
to CUDA, and Hub upload defaults to false.

## Deliberately excluded

- Density and all Density datasets/configs.
- analysis/, probing/, tools/motion_stats.py, result-generation scripts, figure-generation
  scripts, plots, and derived chart assets.
- Historical run outputs and unrelated exploratory artifacts.

## Important

The copied configs are upstream experiment snapshots, not guaranteed drop-in configs for the
current local LeRobot installation. Review the camera feature names, LeRobot version, paths,
and W&B settings before using them. The active project entry points under scripts/real/
remain the preferred machine-specific interface.

Dataset binaries are downloaded separately by python scripts/real/download_reference_datasets.py
into the git-ignored data/reference/so101-vla-data-study/ directory.
