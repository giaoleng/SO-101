SO-101 Policy Benchmark & Real-World SmolVLA Diagnostics

This repository contains two completed experiment tracks:

1. MuJoCo simulation benchmark: ACT, Diffusion Policy, and SmolVLA on the red-cube-to-blue-box task.
   - Success Rate: ACT 89%, Diffusion Policy 80%, SmolVLA 95%.
   - OOD Success Rate: ACT 72%, Diffusion Policy 62%, SmolVLA 83%.

2. SO-101 real-robot study: Cube-to-Cup task using SmolVLA.
   - Five training conditions: Baseline, Clean, Randomized, Recovery, and Color-varied.
   - Training and the unified real-robot evaluation protocol have been completed.

See README.md for the full experiment setup, hardware preparation, training commands, and evaluation procedure. See docs/PROJECT_STATE.md for the current project status, docs/POLICY_COMPARISON.md for the simulation benchmark, and docs/REAL_DEPLOYMENT.md for the real-robot study.

Real-robot datasets, calibration files, checkpoints, and raw run logs are maintained outside this public source repository.
