# 模块 1：SO-101 机械臂标定

## 目的与适用范围

Follower 和 Leader 是两台不同的实体设备，必须分别识别串口并分别标定。标定文件包含电机 ID、零点偏移和关节范围等设备相关数据；不能从其他 SO-101 复制，也不能用仿真模型中的关节限位代替。

本项目部署运行器读取 Follower 文件：

- 目录：<code>calibration/robots/</code>
- ID：<code>so101_follower</code>
- 预期文件：<code>calibration/robots/so101_follower.json</code>

如果使用遥操作 Leader，也为它设置独立 ID，例如 <code>so101_leader</code>，并将它的标定文件保存在同一目录。

## 1. 准备环境与识别串口

在安装了本项目真机依赖的独立环境中执行：

~~~bash
python -m pip install -r configs/real/requirements.txt
lerobot-find-port
~~~

按照命令提示逐个断开/连接 USB，确认哪个端口属于 Follower、哪个属于 Leader。Ubuntu 也可查看稳定设备名：

~~~bash
ls -l /dev/serial/by-id/
ls -l /dev/ttyACM*
~~~

优先记录 /dev/serial/by-id/ 下的稳定路径；如果实际系统只显示 /dev/ttyACM0 等设备名，则记录当前对应关系。若当前用户没有串口权限，按 Ubuntu 的设备权限策略加入 dialout 组并重新登录，不要长期用宽泛的 chmod 666 作为解决方案。

在标定之前确认电源、USB、总线连接和电机安装正确。只有在电机 ID 或波特率尚未正确设置、且已按 LeRobot 官方 SO-101 步骤逐个隔离电机时，才执行电机 setup；已配置正常的设备不要重复写入电机 ID。

## 2. 标定 Follower

确认 Follower 端口后运行：

~~~bash
lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=so101_follower \
  --robot.calibration_dir=./calibration/robots
~~~

将端口替换为本机识别到的 Follower 端口。按交互提示操作：

1. 将机械臂放到各关节行程的中间位置，确保周围没有物体、线缆或人员阻挡。
2. 确认机械臂能够安全活动后按 Enter。
3. 按程序提示逐个移动关节，记录安全的活动范围；不要撞击机械限位或强行扭转关节。
4. 完成后确认程序显示标定文件保存路径。

LeRobot 0.5.1 的 SO-Follower 标定会记录电机 homing offset 和 range。标定时不要把机械臂压在桌面、夹住物体或让线缆缠绕。

## 3. 标定 Leader（用于遥操作时）

如果本项目使用 Leader 遥操作，也单独标定：

~~~bash
lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=so101_leader \
  --teleop.calibration_dir=./calibration/robots
~~~

将端口替换为 Leader 的实际端口。Follower 和 Leader 不能共用同一个 ID；不要把 Leader 的 JSON 当成 Follower 标定文件。

## 4. 核对文件与配置

检查本机文件是否存在：

~~~bash
ls -l calibration/robots/
python - <<'PY'
import json
from pathlib import Path
p = Path("calibration/robots/so101_follower.json")
data = json.loads(p.read_text())
print("Follower calibration:", p)
print("Motor entries:", sorted(data))
PY
~~~

确认 <code>configs/real/so101.yaml</code> 中以下字段与实际设备一致：

- <code>robot.port</code>：Follower 端口。
- <code>robot.id</code>：必须与标定文件名一致；例如 <code>so101_follower</code> 对应 <code>so101_follower.json</code>。
- <code>robot.calibration_dir</code>：本项目默认 <code>./calibration/robots</code>。

本项目运行器会检查该目录下的 <code>{robot.id}.json</code> 是否存在；缺失时会停止，不会替你自动标定。

## 5. 何时需要重新标定

发生以下情况时，先停止部署并重新核对标定：

- 更换电机、舵盘、关节安装位置或电机 ID。
- 拆装机械臂后零点关系发生变化。
- 机械臂在同一物理姿态下反馈位置明显异常。
- LeRobot 提示电机 EEPROM 标定与本地 JSON 不一致。
- 更换了另一台实体机械臂。

标定 JSON 属于具体设备的数据，目录中的 <code>.gitignore</code> 会阻止它们被提交到 GitHub。建议在自己的安全位置另做备份。
