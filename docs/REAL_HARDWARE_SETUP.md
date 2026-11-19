# SO-101 真机硬件部署指南

本指南把真机部署前的准备拆成三个独立模块。请先完成机械臂标定，再固定并检查相机，最后执行硬件安全检查；完成后才进入数据采集、训练模型部署和评测。

## 模块

1. [机械臂标定](real-hardware/ROBOT_CALIBRATION.md)：Follower / Leader 串口识别、电机标定、标定文件保存与核对。
2. [相机标定](real-hardware/CAMERA_CALIBRATION.md)：相机识别、安装视角、图像流参数，以及何时需要内参/外参。
3. [硬件检查](real-hardware/HARDWARE_CHECK.md)：机械、电气、通信、安全、动作语义和首次低风险测试。

## 本项目的本机文件位置

- Follower 标定文件：<code>calibration/robots/so101_follower.json</code>
- Leader 标定文件：<code>calibration/robots/so101_leader.json</code>（如果使用该 ID）
- 相机参考图：<code>calibration/camera/reference/</code>
- 真机配置：<code>configs/real/so101.yaml</code>

<code>configs/real/so101.yaml</code> 的 <code>robot.calibration_dir</code> 已指向 <code>./calibration/robots</code>。运行器按 <code>{robot.id}.json</code> 查找标定文件。

## 安全默认值

- <code>robot.hardware_confirmed</code> 保持 <code>false</code>。
- 不使用其他机械臂的标定 JSON，不把模型/MJCF 关节范围当作真实硬件限位。
- 不把软件 STOP 文件当作实体急停的替代品。
- 标定和首次运动时，工作区必须清空，操作者保持在实体急停可触及的位置。
- 本指南只说明流程，不会自动连接设备、写入电机 EEPROM 或启动机械臂。

LeRobot 接口基线：<code>lerobot==0.5.1</code>。若更换版本，先核对对应版本的 SO-101 配置字段和命令行接口。
