# Calibration workspace

This directory contains instructions and placeholders for device-specific SO-101 calibration.

- <code>robots/</code>: local LeRobot motor calibration JSON files. For the current project config, the Follower file is <code>robots/so101_follower.json</code>.
- <code>camera/reference/</code>: reference photos for camera framing, checkerboard or AprilTag capture. These are not calibration matrices.

Actual robot calibration JSON and camera intrinsic/extrinsic outputs are device-specific and are intentionally ignored by Git. Do not copy another robot's values into this directory.

Start with [the hardware deployment guide](../docs/REAL_HARDWARE_SETUP.md), then follow the three modules:
- [Robot calibration](../docs/real-hardware/ROBOT_CALIBRATION.md)
- [Camera calibration](../docs/real-hardware/CAMERA_CALIBRATION.md)
- [Hardware check](../docs/real-hardware/HARDWARE_CHECK.md)
