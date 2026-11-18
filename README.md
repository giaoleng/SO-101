# SO-101

**SO-101 Robotic Imitation Learning: ACT, Diffusion Policy & SmolVLA**

基于 [LeRobot](https://github.com/huggingface/lerobot) 与 [MuJoCo](https://mujoco.org/) 构建的 **SO-101 机器人模仿学习实验平台**，覆盖专家示范采集、数据集处理、策略训练、仿真闭环评测及真实机器人操作。

项目包含两个实验场景：

- **MuJoCo Simulation**：在 SO-101 仿真环境中比较 ACT、Diffusion Policy 和 SmolVLA，完成红色方块抓取放置任务。
- **Real Robot Manipulation**：在真实 SO-101 机械臂上使用 SmolVLA，完成单个方块抓取并放入杯子的任务，分析位置偏移、策略不启动与掉落后恢复。

通过统一的实验设置与评测协议，比较不同模仿学习策略的任务成功率、位置泛化能力、目标选择能力及失败类型。

<a id="highlights"></a>

## 项目演示与核心结果

### 仿真成功与失败视频

**任务：**抓取红色方块，放入蓝色盒子（Red Cube → Blue Box）。

**✅ 成功示例**


https://github.com/user-attachments/assets/943cd752-5400-4828-933f-b1b99f0062f6

**❌ 失败示例**





https://github.com/user-attachments/assets/912d4b07-6fdc-4b79-84c3-de75a64860ce



> **视频来源：** [Rovo Labs / SO-ARM101 Pick-and-Place](https://huggingface.co/datasets/rovolabs/so-arm101-pick-place)，CC BY 4.0。这里展示的是外部数据集中的 SmolVLA 抓取放置示例，不是下方本项目仿真策略评测表的逐 Episode 录像，也不能用来计算本项目模型的成功率。

### 仿真实验结果

#### Simulation Policy Benchmark

**Environment:** SO-101 MuJoCo  
**Task:** Red Cube Pick-and-Place / Blue Box Placement

| Metric | ACT | Diffusion Policy | SmolVLA |
|---|---:|---:|---:|
| **Success Rate ↑** | **82%** | 69% | 77% |
| Completion Time ↓ | **1.42 × Expert** | 1.58 × Expert | 1.67 × Expert |
| OOD Success Rate ↑ | 62% | 49% | **63%** |
| Initiation Failure Rate ↓ | **4%** | 13% | 14% |
| Grasp Failure Rate ↓ | **17%** | 22% | 21% |

Completion Time 使用相对于脚本专家平均完成时间的比例表示。

上述为项目维护者确认的已完成仿真实验汇总。原始训练日志、模型权重、逐 Episode 评测记录和数据集保留在私有存储中，未提交至 GitHub；本仓库仅展示指标汇总。具体测试 Episode 数量与完整训练配置尚未在本 README 披露。

> **结果说明：**项目维护者确认上述数值对应当前**红方块 → 蓝盒子**仿真任务；本次更新不修改、不重新计算任何统计值。原始逐 Episode 日志与模型权重尚未在本仓库公开。

### SmolVLA 失败模式与视频（第三方参考）

**真机参考任务：** `Pick up the cube and place it in the cup.`（方块 → 杯子）。这一任务与仿真的「红色方块 → 蓝色盒子」属于同一类 Pick-and-Place，但具体容器、环境与数据来源不同。

以下 GIF 来自独立开源项目 [Andresg324/so101-vla-data-study](https://github.com/Andresg324/so101-vla-data-study) 的 SmolVLA 数据研究。它们用于说明常见失败机制，不是本项目的仿真或真机评测录像。

#### Reach Failure：目标偏移导致抓取失败

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip2_offset_2in.gif" width="460" alt="第三方 SO-101 偏移目标抓取失败轨迹">

原项目将方块相对训练位置移动约 2 英寸，机械臂仍沿接近固定的运动轨迹伸出，停在目标前方，夹爪最终闭合但没有抓住方块。这反映出对物体位置变化的视觉条件适应不足。

*来源：[原项目失败模式视频与分析](https://github.com/Andresg324/so101-vla-data-study#failure-modes-on-video)，MIT License；第三方 SmolVLA 实验，不是本项目 OOD 评测录像。*

#### Motion Failure：策略未产生有效动作

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip3_no_motion.gif" width="460" alt="第三方 SO-101 无有效动作失败轨迹">

原项目使用位置随机化示教训练的策略，在绿色方块的某次评测中，机械臂在初始位姿附近小幅抖动，没有形成有效的接近与抓取动作。训练损失下降并不保证闭环动作能够正常启动。

*来源：[原项目失败模式视频与分析](https://github.com/Andresg324/so101-vla-data-study#failure-modes-on-video)，MIT License；第三方实验，不代表本项目模型发生了同样的故障。*

#### Recovery Failure：物体掉落后未能恢复

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip4_drop_no_recovery.gif" width="460" alt="第三方 SO-101 掉落后未恢复失败轨迹">

原项目使用恢复示教训练的策略，在某次评测中搬运途中出现两次释放，但未能重新成功抓取，最终超时，物体留在桌面。该案例说明模仿掉落动作不等于学会掉落后的恢复策略。

*来源：[原项目失败模式视频与分析](https://github.com/Andresg324/so101-vla-data-study#failure-modes-on-video)，MIT License；第三方实验，不是本项目真机失败轨迹。*

> **说明：**以上 GIF 来自其他 SO-101 / SmolVLA 研究项目，不能当作本项目真机实测失败录像。本项目真机实验设计与结果见 [第 13 节](#real-evaluation)。

---

## 目录

- [项目演示与核心结果](#highlights)

### 项目概览

1. [项目介绍](#overview)
2. [系统架构](#architecture)
3. [项目演示](#demo)
4. [安装与环境配置](#installation)
5. [项目结构](#project-structure)

### MuJoCo 仿真实验

6. [SO-101 MuJoCo 仿真环境](#simulation-environment)
7. [仿真专家示范与数据采集](#simulation-data)
8. [LeRobotDataset 数据处理](#dataset)
9. [仿真策略训练](#simulation-training)
10. [MuJoCo 闭环评测与实验结果](#simulation-evaluation)

### SO-101 真机实验

11. [SO-101 真机实验环境](#real-environment)
12. [真机策略训练与部署](#real-deployment)
13. [真机实验设计与结果](#real-evaluation)

### 数据管理与实验复现

14. [Hugging Face 数据管理](#huggingface)
15. [实验复现与注意事项](#reproducibility)
16. [致谢](#acknowledgements)
17. [许可证](#license)

---

<a id="overview"></a>

## 1. 项目介绍

本项目面向低成本机器人操作任务，构建基于视觉观测、机器人状态及任务条件的模仿学习系统。

通过 SO-101 机械臂，在 MuJoCo 仿真环境与真实机器人环境中分别研究固定目标操作、多物体干扰、目标条件操作以及策略泛化能力。

### 1.1 实验任务

项目设计两个相互关联但具有不同任务设置的实验场景。

#### MuJoCo Simulation

仿真环境包含 SO-101 机械臂、蓝色盒子以及红色、蓝色、黄色和绿色方块。

基础任务要求机器人抓取指定的**红色方块**，并将其放入**蓝色盒子**。

其他颜色方块作为干扰物，不属于当前操作目标。

使用以下三种模仿学习策略完成训练与闭环评测：

- ACT
- Diffusion Policy
- SmolVLA

主要研究：

- 不同策略在相同仿真任务中的成功率。
- 多物体干扰下的抓取与放置能力。
- 目标方块初始位置变化下的泛化能力。
- 策略启动、抓取和放置阶段的失败情况。

#### Real Robot Manipulation

真实 SO-101 采用 **SmolVLA**，执行方块放入杯子（Cube → Cup）任务，指令为：

```text
Pick up the cube and place it in the cup.
```

实验重点是方块位置偏移后抓取能力、策略是否启动，以及搬运途中掉落后的重新抓取与恢复。不同颜色方块仅用于独立的外观泛化测试，不再开展多玩具目标类别切换实验。

首页三段失败 GIF 是 [Andresg324/so101-vla-data-study](https://github.com/Andresg324/so101-vla-data-study) 的第三方真实机器人实验，不能当作本项目已完成实机评测的证据。具体实验设计见第 11–13 节。

### 1.2 对比模型

| 模型 | 核心方法 | 训练方式 | 实验环境 |
|---|---|---|---|
| ACT | Transformer + Action Chunking | 监督模仿学习 | 仿真 |
| Diffusion Policy | Diffusion-based Action Generation | 扩散式模仿学习 | 仿真 |
| SmolVLA | Vision-Language-Action | 预训练模型微调 | 仿真 + 真机 |

ACT 与 Diffusion Policy 主要学习从机器人观测到动作序列的映射。

SmolVLA 在视觉和机器人状态基础上引入语言条件，利用预训练视觉语言表示与动作生成模块学习机器人操作策略。


### 1.3 研究问题

本项目主要关注以下问题。

**Simulation Policy Benchmark**

在相同的 SO-101 MuJoCo 操作任务下，ACT、Diffusion Policy 和 SmolVLA 的任务成功率与失败类型有何差异？

**Position Generalization**

当目标方块出现在训练数据未覆盖的位置时，策略能否继续完成抓取放置？

**Real-world Position Generalization**

真机目标方块相对训练起点偏移时，SmolVLA 能否调整接近轨迹并成功抓取？

**Policy Initiation**

在示教位置多样化的条件下，SmolVLA 是否会停留在初始位姿而无法启动有效动作？

**Drop Recovery**

方块在搬运途中掉落后，SmolVLA 能否再次抓取并完成入杯？

---

<a id="architecture"></a>

## 2. 系统架构

项目包含仿真模仿学习系统和真实机器人操作系统。

两部分使用相同的 SO-101 机器人类型，但采用不同的任务设置与数据采集流程。

### 2.1 MuJoCo 仿真系统

```text
                  SO-101 MuJoCo
                        │
                        ▼
              Multi-Object Scene
                        │
                        ▼
              Red Cube → Blue Box
                        │
                        ▼
                Expert Controller
                  Mink IK + FSM
                        │
                        ▼
              Expert Demonstrations
                        │
                        ▼
                 LeRobotDataset
                        │
              ┌─────────┼─────────┐
              │         │         │
              ▼         ▼         ▼
             ACT       DP       SmolVLA
              │         │         │
              └─────────┼─────────┘
                        │
                        ▼
               Closed-loop Rollout
                        │
                        ▼
              Simulation Benchmark
```

系统使用 Mink IK 与有限状态机生成专家轨迹，将视觉、机器人状态和动作保存为 LeRobotDataset。

训练后的策略在 MuJoCo 环境中独立执行闭环 Rollout。

### 2.2 真实机器人系统

```text
                  SO-101 Real Robot
                         │
                         ▼
                 Single Cube + Cup
                         │
                         ▼
                 Camera + Joint State
                         │
                         ▼
                Language Instruction
                         │
                         ▼
                       SmolVLA
                         │
                         ▼
                 Action Prediction
                         │
                         ▼
                 SO-101 Controller
                         │
                         ▼
                 Closed-loop Rollout
                         │
              Reach / No Motion / Recovery
```

真机通过统一的方块入杯自然语言指令驱动 SmolVLA；训练和测试分别检查接近目标、启动行为及掉落恢复，机器人动作必须经过安全检查后下发。

### 2.3 核心功能模块

| 模块 | 功能 |
|---|---|
| MuJoCo Environment | SO-101 机器人与物理场景仿真 |
| Expert Controller | 基于 Mink IK 与 FSM 生成专家示范 |
| Data Collection | 采集图像、机器人状态、动作及任务信息 |
| LeRobotDataset | 统一存储机器人操作数据 |
| Policy Training | ACT、Diffusion Policy 和 SmolVLA 训练 |
| Simulation Evaluation | MuJoCo 闭环评测 |
| Real Robot Interface | SO-101 状态读取与动作执行 |
| Task Conditioning | 仿真任务描述、真机方块入杯语言指令 |
| Performance Analysis | 成功率、泛化能力与失败类型分析 |

---

<a id="demo"></a>

## 3. 项目演示

### 3.1 SO-101 MuJoCo 仿真演示

[▶ 查看 SO-101 MuJoCo 仿真演示](media/simulation_demo.mp4)

仿真场景包含：

- SO-101 机械臂。
- 桌面与蓝色目标盒子。
- 红色目标方块。
- 蓝色、黄色和绿色干扰方块。
- 用于策略观测的 RGB 相机。

基础任务为抓取红色方块，并将其放入蓝色盒子。

演示由基于 **Mink Inverse Kinematics + Finite State Machine** 的脚本专家生成，不代表 ACT、Diffusion Policy 或 SmolVLA 的训练结果。

### 3.2 SmolVLA 失败模式参考

Reach Failure、Motion Failure 和 Recovery Failure 的 GIF 与分析已移至开头的 [项目演示与核心结果](#highlights)。

---

<a id="installation"></a>

## 4. 安装与环境配置

### 4.1 环境依赖

| 组件 | 用途 |
|---|---|
| Python | 项目运行环境 |
| MuJoCo | 物理仿真 |
| LeRobot | 数据集、策略训练及机器人接口 |
| PyTorch | 深度学习 |
| Mink | 逆运动学 |
| OpenCV | 图像处理 |
| FFmpeg | 视频编码 |
| Transformers | SmolVLA 模型组件 |

数据处理采用 LeRobotDataset v3.0 格式。

不同模型 Checkpoint 可能依赖不同版本的 LeRobot、PyTorch 和 Transformers，应以对应的运行环境配置为准。

### 4.2 Docker：区分 CPU 运行与 GPU 训练

仓库有两套不同用途的镜像，请按任务选择，**不要把 CPU 运行镜像当成 GPU 推理镜像**。

| Dockerfile | 用途 | Python / PyTorch | GPU |
|---|---|---|---|
| `Dockerfile.runtime` | 数据处理、CPU 推理与基础仿真 | Python 3.12 / PyTorch CPU | 不需要，也不提供 CUDA PyTorch |
| `Dockerfile` | 远程 GPU 训练与 GPU 推理环境 | Python 3.12 / CUDA 12.4 对应 PyTorch | 需要 NVIDIA GPU 与容器运行时 |

从仓库根目录构建：

```bash
# CPU 运行镜像
docker build -t lerobot_mujoco_sim:runtime -f Dockerfile.runtime .

# GPU 训练/推理镜像
docker build -t lerobot_mujoco_sim:train -f Dockerfile .
```

运行 **CPU 镜像**（不加 `--gpus all`）：

```bash
docker run --rm -it \
  -v "$PWD:/workspace" \
  lerobot_mujoco_sim:runtime
```

在已配置 NVIDIA Container Toolkit 的远程 GPU 主机上运行 **GPU 镜像**：

```bash
docker run --rm -it \
  --gpus all \
  -v "$PWD:/workspace" \
  lerobot_mujoco_sim:train
```

进入容器后项目位于 `/workspace`。以上命令仅为镜像与运行方式说明；MuJoCo 的 viewer、EGL 或 OSMesa 能否使用，还取决于主机图形环境和容器挂载配置。**这些示例不代表本次重新构建或执行了实验。**

### 4.3 Docker Compose

`docker-compose.yml` 中 `lerobot-runtime` 对应 **CPU 运行镜像**，`lerobot` 对应 **GPU 训练镜像的构建配置**；Compose 文件本身没有启用 GPU 设备预留。启动 CPU 服务：

```bash
docker compose up -d lerobot-runtime
docker compose exec lerobot-runtime bash
cd /workspace
```

如需 **GPU 训练或评测**，建议使用上一节的 `docker run --gpus all ... lerobot_mujoco_sim:train`，并在有 GPU 的远程平台运行；不能仅凭 Compose 中设置 NVIDIA 环境变量就认为容器获得了 GPU。

### 4.4 Python 环境（不使用 Docker）

根目录**没有** `requirements.txt`；依赖由两个 Dockerfile 分别安装，`configs/real/requirements.txt` 专用于 SO-101 真机环境，**不是**仿真通用依赖文件。

本地只需验证基础 MuJoCo、数据处理或 CPU 推理时，可以参考 `Dockerfile.runtime` 创建 Python 3.12 虚拟环境：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# CPU 版 PyTorch，与 Dockerfile.runtime 的基础版本对应
python -m pip install torch==2.7.0 torchvision==0.22.0 \
  --index-url https://download.pytorch.org/whl/cpu

python -m pip install "lerobot==0.5.1" "mujoco==3.1.6" \
  numpy Pillow glfw termcolor PyYAML mink matplotlib scipy opencv-python
```

上述为无 Docker 的**参考安装命令**，不保证自动覆盖每个模型 Checkpoint 的额外依赖。SmolVLA/真机推理需核对对应模型与相机/驱动依赖；正式 GPU 训练优先使用项目的 GPU Docker 环境或已验证的远程环境。

验证 MuJoCo：

```bash
python -c "import mujoco; print(mujoco.__version__)"
```

验证 PyTorch：

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

验证 LeRobot：

```bash
python -c "import lerobot; print(lerobot.__file__)"
```

模型训练应使用与实际依赖版本及硬件兼容的环境。

---

<a id="project-structure"></a>

## 5. 项目结构

项目按仿真环境、机器人控制、数据采集、策略训练、评测和真机部署划分模块。

以下为项目采用的模块组织结构；具体脚本与配置入口以仓库实际文件为准。

```text
LeRobot-MuJoCo-SO101/
│
├── README.md
├── LICENSE
├── Dockerfile                  # GPU 训练/推理镜像
├── Dockerfile.runtime          # CPU 运行镜像
├── docker-compose.yml          # Compose 服务配置
│
├── asset/
│   ├── scene_so101_y.xml
│   ├── so_arm100/
│   │   └── SO101/
│   └── tabletop/
│
├── mujoco_env/
│   └── y_env.py
│
├── controllers/
│   └── scripted_fsm_controller.py
│
├── so101/
│
├── configs/
│   ├── collect_data.yaml
│   ├── collect_manual.yaml
│   ├── collect_batch.yaml
│   ├── deploy_act.yaml
│   └── real/
│       ├── so101.yaml
│       └── requirements.txt  # 真机环境专用依赖
│
├── scripts/
│   ├── collect/
│   │   ├── manual_collect_data.py
│   │   └── batch_collect_data.py
│   │
│   ├── train/
│   │   ├── train_act.py
│   │   ├── train_diffusion.sh
│   │   └── finetune_smolvla.sh
│   │
│   ├── deploy/
│   │   └── deploy_act.py
│   │
│   ├── eval/
│   │   ├── eval_mujoco.py
│   │   └── summarize_rollouts.py
│   │
│   ├── real/
│   │   ├── deploy_policy.py
│   │   ├── evaluate_policy.py
│   │   └── task_conditioning.py
│   │
│   ├── demo/
│   │   └── record_scripted_demo.py
│   │
│   ├── visualize/
│   │   └── visualize_data.py
│   │
│   ├── hf/
│   │   └── upload_hf.py
│   │
│   └── convert_lerobot_dataset_v21_to_v30_local.py
│
├── notebooks/
│
├── docs/
│   ├── PROJECT_STATE.md
│   ├── POLICY_COMPARISON.md
│   ├── ENGINEERING_NEXT_STEPS.md
│   └── REAL_DEPLOYMENT.md
│
├── media/
│   └── simulation_demo.mp4
│
└── third_party/
    └── SO-ARM100/
```

**说明：** `data/`、`checkpoints/`、`outputs/` 是私有数据、权重和实验输出的建议存放目录，不是 GitHub 当前跟踪的目录；项目结构图只列出已提交的文件与主要目录。

### 5.1 主要目录说明

| 目录 | 说明 |
|---|---|
| `asset/` | SO-101 机器人模型与 MuJoCo 场景 |
| `mujoco_env/` | MuJoCo 仿真环境 |
| `controllers/` | 脚本专家控制器 |
| `so101/` | SO-101 机器人相关工具 |
| `configs/` | 数据采集、训练、评测及硬件配置 |
| `scripts/collect/` | 专家示范与数据采集 |
| `scripts/train/` | 策略训练 |
| `scripts/deploy/` | MuJoCo 策略执行 |
| `scripts/eval/` | 仿真闭环评测 |
| `scripts/real/` | 真机部署与评测 |
| `scripts/visualize/` | 数据可视化 |
| `scripts/hf/` | Hugging Face 数据管理 |
| `docs/` | 技术文档 |
| `media/` | 演示视频 |
| `data/` | 数据集 |
| `checkpoints/` | 模型权重 |
| `outputs/` | 实验输出 |

---

# Part I. MuJoCo Simulation

<a id="simulation-environment"></a>

## 6. SO-101 MuJoCo 仿真环境

### 6.1 SO-101 机器人模型

本项目的仿真与真实机器人操作均使用 **SO-101 机械臂**。

机器人资源基于 [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) 项目提供的 SO-101 模型。

主要文件：

```text
third_party/SO-ARM100/
asset/so_arm100/SO101/
asset/scene_so101_y.xml
```

其中 `SO-ARM100` 和 `so_arm100` 为上游资源及原始目录命名；本项目使用的机器人模型为 SO-101。

SO-101 具有五个机械臂旋转关节和一个夹爪自由度。

MuJoCo 使用 MJCF/XML 描述机器人关节、执行器、几何模型及物理参数。

### 6.2 MuJoCo 场景

仿真场景定义：

```text
asset/scene_so101_y.xml
```

场景包含：

- SO-101 机械臂。
- 桌面。
- 目标收纳盒。
- 多个不同颜色的方块。
- RGB 相机。

机器人环境接口：

```text
mujoco_env/y_env.py
```

环境负责：

- 初始化机器人与场景。
- 重置 Episode。
- 设置物体初始状态。
- 读取机器人关节状态。
- 渲染相机观测。
- 执行机器人动作。
- 更新 MuJoCo 物理状态。

### 6.3 红色方块抓取与蓝色盒子放置任务

基础任务：

```text
Pick up the red cube and place it into the blue box.
```

场景中同时存在：

```text
Red Cube     → Target
Blue Cube    → Distractor
Yellow Cube  → Distractor
Green Cube   → Distractor

Blue Box     → Placement Target
```

机器人需要抓取红色方块，并将其放入蓝色盒子。

抓取其他颜色的方块，或未能完成放置，都不算任务成功。

该任务用于比较 ACT、Diffusion Policy 和 SmolVLA 在相同多物体干扰场景中的操作能力。

### 6.4 Mink IK + FSM 专家控制器

仿真专家控制器采用：

- **Mink Inverse Kinematics**：根据末端执行器目标计算关节运动。
- **Finite State Machine（FSM）**：组织抓取放置任务的执行阶段。

专家控制器入口：

```text
controllers/scripted_fsm_controller.py
```

执行流程：

```text
Initialize
    │
    ▼
Approach
    │
    ▼
Grasp
    │
    ▼
Lift
    │
    ▼
Transport
    │
    ▼
Place
    │
    ▼
Release
    │
    ▼
Success
```

FSM 负责决定当前任务阶段。

Mink IK 将各阶段的末端运动目标转换为机器人关节运动。

该组合属于基于模型的脚本专家控制方法，用于生成模仿学习示范，并不作为与 ACT、Diffusion Policy 和 SmolVLA 并列的学习策略。

---

<a id="simulation-data"></a>

## 7. 仿真专家示范与数据采集

### 7.1 数据采集方式

MuJoCo 环境支持人工遥操作与脚本专家两种数据采集方式。

采集内容包括：

- 相机图像。
- 机器人关节状态。
- 机器人动作。
- 任务描述。
- Episode 元数据。

数据使用 LeRobotDataset 格式存储。

### 7.2 人工遥操作采集

执行：

```bash
python scripts/collect/manual_collect_data.py \
  --env-robot-profile so101 \
  --num-demo 20 \
  --repo-name local/so101_manual \
  --root data/demo_data_so101 \
  --offline-local-only
```

该方式用于人工控制 SO-101 完成抓取放置任务，并记录对应示范数据。

### 7.3 脚本专家批量采集

执行：

```bash
python scripts/collect/batch_collect_data.py \
  --env-robot-profile so101 \
  --num-demo 200 \
  --repo-name local/so101_scripted \
  --root data/demo_data_so101 \
  --offline-local-only
```

也可以使用配置文件：

```bash
python scripts/collect/batch_collect_data.py \
  --config configs/collect_batch.yaml \
  --num-demo 100
```

其中：

- `--num-demo`：采集的示范数量。
- `--repo-name`：数据集标识。
- `--root`：数据集保存路径。
- `--offline-local-only`：仅保存本地数据。

### 7.4 数据质量检查

训练前应检查专家示范是否满足以下条件：

1. 机器人正确抓取红色方块。
2. 夹爪能够稳定夹持并抬起目标。
3. 目标方块被正确放入收纳盒。
4. 机器人动作与视频观测同步。
5. Episode 数据没有明显缺失或异常。
6. 训练数据包含足够的初始位置变化。

对于脚本专家，应单独统计其任务成功率，避免将专家控制失败混入模仿学习策略的性能评价。

---

<a id="dataset"></a>

## 8. LeRobotDataset 数据处理

项目使用 **LeRobotDataset v3.0** 存储机器人操作数据。

### 8.1 数据集结构

示例：

```text
data/demo_data_so101/
├── meta/
│   ├── info.json
│   ├── stats.json
│   └── ...
│
├── data/
│   └── ...
│
└── videos/
    └── ...
```

主要内容：

| 数据 | 作用 |
|---|---|
| RGB Images | 视觉观测 |
| Robot State | 机器人关节状态 |
| Actions | 监督学习目标 |
| Task | 任务描述 |
| Episode Metadata | Episode 相关信息 |
| Dataset Statistics | 归一化统计信息 |

具体字段名称由数据集的 Feature Schema 决定。

### 8.2 数据格式转换

对于旧版 LeRobotDataset，可以使用项目中的转换工具：

```bash
python scripts/convert_lerobot_dataset_v21_to_v30_local.py \
  --root data/my_v21_dataset \
  --repo-id local/my_v21_dataset
```

转换工具基于 LeRobot 官方 v2.1 → v3.0 转换流程，并包含历史数据兼容处理。

转换时原始 v2.1 数据会移动至相邻的 `_old` 目录。

正式转换前应检查目标路径及可用磁盘空间。

### 8.3 Parquet 兼容处理

针对部分包含 `spawn.block_xyz` 字段的历史数据，转换工具支持处理 NumPy Object Vector 与 PyArrow Schema 的兼容问题。

如果不需要执行该修复：

```bash
python scripts/convert_lerobot_dataset_v21_to_v30_local.py \
  --root data/my_v21_dataset \
  --repo-id local/my_v21_dataset \
  --no-repair-parquet
```

### 8.4 数据集回放

通过可视化脚本检查采集结果：

```bash
python scripts/visualize/visualize_data.py
```

也可以使用：

```text
notebooks/2.visualize_data.ipynb
```

回放时重点检查：

- 相机视频是否正确。
- 机器人状态与动作是否同步。
- 夹爪开合是否符合实际操作。
- Episode 是否包含完整抓取放置过程。
- 动作序列是否存在异常跳变。

### 8.5 数据一致性检查

训练与推理阶段应保持一致的：

- 关节名称与顺序。
- 动作维度。
- 动作单位和范围。
- 夹爪动作映射。
- 相机数量与特征名称。
- 图像分辨率。
- 数据归一化方式。
- 机器人控制频率。

数据格式和动作定义不一致可能导致模型训练 Loss 正常下降，但闭环执行失败。

---

<a id="simulation-training"></a>

## 9. 仿真策略训练

MuJoCo 仿真实验使用相同任务与对应的专家示范数据，比较三种策略：

- ACT
- Diffusion Policy
- SmolVLA

模型训练使用 LeRobot 提供的策略实现，并根据 SO-101 的观测和动作空间进行配置。

以下命令保留项目原有的训练入口示例；具体参数需与实际安装的 LeRobot 版本及数据集配置一致。

### 9.1 ACT

ACT（Action Chunking with Transformers）使用 Transformer 预测未来一段机器人动作。

主要输入：

```text
Camera Images
      +
Robot State
      │
      ▼
     ACT
      │
      ▼
 Action Chunk
```

训练入口：

```bash
python scripts/train/train_act.py
```

也可以使用 LeRobot 训练接口：

```bash
lerobot-train \
  --dataset.repo_id=local/so101_scripted \
  --dataset.root=data/demo_data_so101 \
  --policy.type=act \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=outputs/train/act \
  --job_name=act_so101
```

ACT 使用监督模仿学习，从专家轨迹中学习视觉观测、机器人状态与动作之间的映射。

### 9.2 Diffusion Policy

Diffusion Policy 使用条件扩散模型，通过迭代去噪生成机器人动作序列。

主要流程：

```text
Camera Images + Robot State
              │
              ▼
       Observation Encoder
              │
              ▼
       Diffusion Policy
              │
              ▼
       Iterative Denoising
              │
              ▼
          Action Chunk
```

训练入口：

```bash
bash scripts/train/train_diffusion.sh
```

LeRobot 训练接口示例：

```bash
lerobot-train \
  --dataset.repo_id=local/so101_scripted \
  --dataset.root=data/demo_data_so101 \
  --policy.type=diffusion \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=outputs/train/diffusion \
  --job_name=diffusion_so101
```

对于包含明显初始静止片段的专家示范，应分析数据预处理是否影响策略启动和动作生成。

### 9.3 SmolVLA

SmolVLA 是视觉语言动作模型，使用视觉语言表示与动作生成模块学习机器人操作策略。

预训练模型：

```text
lerobot/smolvla_base
```

主要输入：

```text
Camera Images
      +
Robot State
      +
Task Instruction
      │
      ▼
    SmolVLA
      │
      ▼
  Action Expert
      │
      ▼
  Action Chunk
```

在当前仿真任务中，任务描述固定为：

```text
Pick up the blue cube and place it into the bin.
```

微调入口：

```bash
bash scripts/train/finetune_smolvla.sh
```

LeRobot 训练接口示例：

```bash
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=local/so101_scripted \
  --dataset.root=data/demo_data_so101 \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=outputs/train/smolvla \
  --job_name=smolvla_so101
```

### 9.4 模型训练配置

| 模型 | 初始化方式 | 主要输入 | 训练目标 |
|---|---|---|---|
| ACT | 随机初始化 | 图像、状态 | 专家动作 |
| Diffusion Policy | 随机初始化 | 图像、状态 | 专家动作序列 |
| SmolVLA | 预训练权重 | 图像、状态、任务指令 | 专家动作序列 |

为保证实验具有可比性，应记录：

- 训练示范数量。
- 数据集划分。
- 图像分辨率与相机配置。
- 动作表示。
- Batch Size。
- 训练 Steps。
- Learning Rate。
- Action Chunk 配置。
- 训练使用的 GPU。
- 模型初始化方式。

不同模型的预训练条件与架构不同，不能仅根据最终成功率将性能差异完全归因于网络结构。

---

<a id="simulation-evaluation"></a>

## 10. MuJoCo 闭环评测与实验结果

本章统一评测 ACT、Diffusion Policy 和 SmolVLA 在 SO-101 MuJoCo 环境中的操作性能。

### 10.1 实验环境与设置

| 项目 | 实验设置 |
|---|---|
| Robot | SO-101 |
| Simulator | MuJoCo |
| Task | Blue Cube Pick-and-Place |
| Target | Red Cube |
| Distractors | Blue / Yellow / Green Cubes |
| Expert Controller | Mink IK + FSM |
| Models | ACT / DP / SmolVLA |
| Evaluation | Closed-loop Rollout |

所有模型使用相同的任务目标、物理环境及成功判定标准。

训练阶段使用专家示范数据。

评测阶段由策略模型独立生成动作，不再使用脚本专家决定抓取轨迹。

### 10.2 统一闭环评测流程

```text
Environment Reset
        │
        ▼
    Observation
        │
        ▼
  Policy Inference
        │
        ▼
    Action Chunk
        │
        ▼
  MuJoCo Execution
        │
        ▼
 Updated Observation
        │
        ├─────────────┐
        │             │
        ▼             │
 Success Check        │
        │             │
        ▼             │
 Success / Failure    │
        │             │
        └─────────────┘
```

如果任务尚未结束，环境继续提供新的观测，策略根据当前状态生成后续动作。

评测接口：

```text
scripts/eval/
├── eval_mujoco.py
└── summarize_rollouts.py
```

模型评测需要统一：

- Episode 初始化方式。
- 机器人初始状态。
- 方块位置采样规则。
- 控制频率。
- 任务最大执行时间。
- 成功与失败判定条件。

### 10.3 评测指标

| 指标 | 含义 | 优化方向 |
|---|---|---|
| **Success Rate** | 完整完成抓取放置任务的比例 | ↑ |
| **OOD Success Rate** | 未见目标位置下的任务成功率 | ↑ |
| Completion Time | 成功 Episode 的平均完成时间 | ↓ |
| Initiation Failure Rate | 策略未能正常启动操作的比例 | ↓ |
| Grasp Failure Rate | 已尝试抓取但未能成功抓起目标的比例 | ↓ |

其中：

**Success Rate**

任务成功次数占全部测试 Episode 的比例。

**OOD Success Rate**

在训练数据未覆盖的目标位置上，机器人成功完成任务的比例。

**Completion Time**

从 Episode 开始到成功完成任务所用的时间。

仿真实验优先使用 MuJoCo 的仿真时间。

**Initiation Failure Rate**

策略在规定启动时间内没有产生有效机器人运动的 Episode 比例。

启动阈值需根据专家轨迹与控制频率确定。

**Grasp Failure Rate**

进入抓取阶段后，未能成功抓住并抬起目标方块的比例。

该指标按实际发生的抓取尝试统计，以便与未能接近目标等失败情况区分。

### 10.4 ID / OOD 测试设置

为研究策略的位置泛化能力，分别进行 ID 和 OOD 测试。

#### In-Distribution Evaluation

红色方块在训练数据覆盖的位置范围内随机初始化。

测试目标：

- 策略是否学会基本抓取放置行为。
- 是否能够处理训练分布内的位置变化。

#### Out-of-Distribution Evaluation

红色方块在训练数据未覆盖、但机器人能够到达的位置范围内初始化。

测试目标：

- 策略是否能够适应新的目标位置。
- 是否过度依赖训练时的固定抓取轨迹。

OOD 位置应满足：

- 与训练位置范围明确分离。
- 位于 SO-101 可达工作空间。
- 不与其他方块或场景物体重叠。
- 不超出桌面边界。
- 脚本专家能够在该区域完成任务。

两组测试应尽可能只改变目标位置，避免同时改变光照、颜色、物体尺寸或物理参数。

建议使用相同的测试初始状态集合比较三个模型。

例如，可分别配置100个 ID Episode 和100个 OOD Episode。该数量属于建议评测协议，并非已经完成的测试记录。

### 10.5 仿真任务成功判定

完整任务成功条件：

**Success = CorrectTarget ∧ SuccessfulGrasp ∧ SuccessfulPlacement**

其中：

- **CorrectTarget**：抓取正确的红色方块。
- **SuccessfulGrasp**：成功夹住并抬起目标。
- **SuccessfulPlacement**：成功将目标放入收纳盒。

三个条件全部满足，才判定当前 Episode 成功。

如果抓取其他颜色方块、目标中途掉落或未能完成放置，则判定为失败。

### 10.5.1 ACT / Diffusion Policy / SmolVLA 统一仿真评测入口

仓库提供 `scripts/eval/eval_mujoco.py`，通过相同的 SO-101 MuJoCo 环境、任务定义和 Episode 调度选择三种策略，并记录带策略名称、Checkpoint、seed、ID/OOD 分组和推理延迟的 JSONL。该入口仅使用**本地** LeRobot Checkpoint 与数据元信息，不连接真机，也不自动下载权重。

```bash
# 在项目根目录；先查看参数与目录规划，无需模型/数据/显卡
python scripts/eval/eval_mujoco.py --policy act \
  --checkpoint /private/weights/act/pretrained_model \
  --dataset-root /private/datasets/so101_sim \
  --dry-run

# 使用实际本地路径运行，三种策略分别运行（不能共用不匹配的权重）
python scripts/eval/eval_mujoco.py --policy act \
  --checkpoint /private/weights/act/pretrained_model \
  --dataset-root /private/datasets/so101_sim \
  --action-semantics joint_radians_gripper_closed_0_1 \
  --top-feature observation.images.top \
  --wrist-feature observation.images.wrist \
  --processors saved --device cuda --split id \
  --num-trials 20 --seed 42 --timeout-clock sim \
  --output outputs/eval/act_id_seed42.jsonl

# 将 --policy act 与 --checkpoint 改为 diffusion 或 smolvla 的实际配置，
# 其他测试参数保持一致，分别保存不同路径的 JSONL。
# OOD：必须同时传入实际的 --spawn-x/y/z-min/max 分布外边界。
# 仅修改 --split ood 不构成 OOD 评测，脚本会拒绝沿用默认 ID 位置范围。
python scripts/eval/summarize_rollouts.py outputs/eval/act_id_seed42.jsonl \
  --csv outputs/eval/act_id_seed42.csv
```

**使用前必须核对：** `--top-feature`/`--wrist-feature` 是实际训练数据中的图像键；旧数据可能使用 `observation.image` 和 `observation.wrist_image`（可省略两个相机参数），新数据可使用 `observation.images.*`。策略输入目前支持**6 维末端 xyz+rpy + 两路 RGB**；如果模型还要求类别条件、额外相机或其他状态，需要先补专用适配器，不能忽略该输入。环境输出必须是 **5 个绝对关节弧度 + 1 个夹爪闭合比例 [0,1]**，不接受真机 degrees/百分比动作。预处理器需与训练时一致，`--processors saved` 需要 Checkpoint 内的处理器 JSON；未保存时可使用 `--processors dataset` 从本地 `meta/stats.json` 构建。

该入口沿用 **LeRobot 0.5.1** 的策略工厂及处理器 API。默认使用现有可视化环境，需 MuJoCo viewer 可用。源码静态检查与轻量单元测试不等价于真实权重集成测试；三种模型需要在实际 GPU/仿真环境分别做一次加载和 Episode 冒烟验收，确认 checkpoint 特征与处理器匹配。

**结果来源：** 第 10.6 节的百分比沿用此前完成的私有实验汇总，**不是**这次新增评测脚本重新跑出来的结果。已有实验不需要重训，原始数据/权重也无需上传 GitHub。

### 10.6 仿真实验结果

原有完整实验结果表已移至开头的 [项目演示与核心结果](#highlights)，保留原始统计数值；本节前文仍为完整评测设置与指标定义。


### 10.7 失败类型分析

为了进一步解释任务成功率差异，将失败情况划分为以下类型。

| Failure Type | Description |
|---|---|
| Initiation Failure | 机器人未正常开始执行操作 |
| Approach Failure | 末端未能正确接近目标 |
| Grasp Failure | 夹爪未能成功抓起目标 |
| Transport Failure | 搬运过程中目标掉落 |
| Placement Failure | 目标未能正确放入收纳盒 |
| Wrong-object Grasp | 错误抓取其他颜色方块 |
| Timeout | 在最大执行时间内未完成任务 |

评测时记录各 Episode 的执行结果与主要失败原因。

失败类型用于辅助判断：

- 数据覆盖是否不足。
- 视觉定位是否准确。
- 模型动作是否连续。
- 夹爪控制是否稳定。
- 模型是否能够处理执行过程中的状态变化。

---

# Part II. Real-world SO-101 Manipulation

<a id="real-environment"></a>

## 11. SO-101 真机实验环境

**任务：使用 SmolVLA 控制 SO-101 机械臂抓起桌面方块并放入杯子（Cube → Cup）。** 与仿真红方块→蓝盒子任务同属抓取放置，但真机实验的放置容器是杯子。以下条件以首页 [第三方失败模式视频](#highlights) 为参照设计，并不代表本仓库已经完成这些新条件的真机实测。

### 11.1 实验装置

- SO-101 真机及夹爪、桌面方块、固定位置的杯子。
- 俯视/前视相机和腕部相机及关节观测；训练、推理必须使用相同相机特征名和动作语义。
- 稳定光照、可标记的方块起点、可复位的机器人初始位姿与物理急停。
- 原研究使用两路 640×480 @ 30 FPS 摄像头，这只是第三方设备配置参考，不能代替本项目的实际标定记录。

### 11.2 基线任务与示教

统一自然语言任务指令：

```text
Pick up the cube and place it in the cup.
```

每段示教包含接近、抓取、抬起、搬运、放入杯子及释放动作。基线固定方块起点与杯子位置；物体颜色或起点改变时必须在数据集中明确标记，不能与基线数据混报。

### 11.3 与三段失败视频对应的实验条件

| 条件 | 核心变化 | 观察现象 |
|---|---|---|
| Clean / ID | 方块位于示教位置，正常放入杯子 | 标准任务完成情况 |
| Reach / Position Shift | 方块相对基线**向机器人方向偏移 2 英寸（5.08 cm）**，相机与杯子位置固定 | 是否仍在旧位置闭合夹爪、发生抓空 |
| No Motion | 位置随机化示教策略，在新回合从相同机器人初态执行 | 是否停留初态、小幅抖动而不接近方块 |
| Recovery | 示教中包含搬运中释放、重新抓取、继续入杯的完整恢复序列 | 掉落后是否再次抓取并最终入杯 |
| Color Variation（可选） | 改变方块颜色，保持任务文本及杯子不变 | 未见颜色下是否完成抓取 |

源项目 No Motion GIF 对应位置随机化策略在绿色方块条件下的一次回合，不等于“绿色方块必然造成不运动”。三段 GIF 分别来自不同示教条件，**不是本项目自己的真机录像**。

### 11.4 数据采集与任务条件

仅采集 Cube → Cup 任务的相机图像、关节状态、动作和任务指令。对于 Clean、Position-randomized、Recovery（可选 Color-varied）分别保存数据与 Checkpoint，并记录方块位置、数据采集条件和回合标签。

```json
{
  "task": "Pick up the cube and place it in the cup."
}
```

参考研究每种条件有 50 段示教，Recovery 中 20/50 段含故意释放及后续恢复；这些是**第三方研究的设定**，不应称为本项目已采集的数据。

### 11.5 数据集划分

| Split | 评测目的 |
|---|---|
| `baseline` | 固定示教位置下的入杯成功率 |
| `position_shift` | 目标偏移后是否仍能到达并抓起方块 |
| `no_motion` | 统计初态附近停滞或仅小幅抖动 |
| `recovery` | 掉落后是否尝试并成功重新抓取 |
| `color_variation` | 颜色泛化，独立于前三组诊断 |

训练/测试应独立，并固定复位条件、摄像头与超时上限。

---

<a id="real-deployment"></a>

## 12. 真机策略训练与部署

真机实验**只使用 SmolVLA**，不同条件对比的是相同架构在不同示教策略下的行为。

### 12.1 SmolVLA 方块入杯

```text
Overhead/Front Camera + Wrist Camera + Robot State
                        +
     "Pick up the cube and place it in the cup."
                        │
                        ▼
                      SmolVLA
                        │
                        ▼
                Action Chunk → SO-101
```

需使用真实 SO-101 标定、与训练特征一致的预处理器/动作处理器及对应的本地 SmolVLA Checkpoint。**本次只更新仓库代码与参考配置，不训练模型，也不声称已完成新的真机评测。**

### 12.2 已提供的真机接口

```text
configs/real/so101.yaml
scripts/real/deploy_policy.py
scripts/real/evaluate_policy.py
scripts/real/task_conditioning.py
```

默认配置改为 SmolVLA、`language` 模式、单个 `cube` 目标和杯子任务文本。参考配置仍保留 `hardware_confirmed: false`，Checkpoint 路径是占位符，不能把这些改动理解为已连接真机或通过实测。

现有入口仅在显式指定 `--execute` 并通过实际硬件/权重/安全检查后才会运行；若现在没有时间或硬件，**不需要运行**。原有 ACT 类别条件工具保留为历史代码，不作为当前真机实验入口。

### 12.3 回合记录与失败标签

评测时使用 `--condition` 选择 `baseline`、`position_shift`、`no_motion` 或 `recovery`，默认配置为 `baseline`。实际结果仍需要操作者确认，不会把机械臂移动或运行结束自动判定为成功。

可选结果字段包括 `started`、`reached`、`grasped`、`placed`、`released`、`dropped`、`regrasp_attempted`、`regrasped`、`failure_mode`；这使得 No Motion、抓空与恢复失败可以分别记录，而非仅保存一个总成功标签。

### 12.4 安全与兼容性

真机动作使用实际校准的五个关节角度及夹爪百分比，不可直接混用 MuJoCo 的关节弧度或末端位姿。必须核对相机键、模型动作维度、夹爪开合方向、工作空间和急停。参考研究使用 45 秒评测窗口；本仓库配置中也作为**待核验参考设置**，没有运行验证。

---

<a id="real-evaluation"></a>

## 13. 真机实验设计与结果

### 13.1 当前评测任务

| 项目 | 实验设置 |
|---|---|
| Robot | SO-101 real robot |
| Model | SmolVLA |
| Task | Cube Pick-and-Place into Cup |
| Instruction | `Pick up the cube and place it in the cup.` |
| Target | 单个方块（颜色变化单独评测） |
| Destination | Cup（杯子） |
| Inputs | 双路 RGB、机器人状态、语言指令 |
| Conditions | Baseline / Position Shift / No Motion / Recovery |
| Current Status | 新条件的本项目真机逐 Episode 数据尚未在此仓库公开 |

### 13.2 Baseline：标准抓取放置

在训练覆盖的固定起点抓起方块，移至杯子上方并释放。检查有效启动、抓取、入杯成功和完成时间。

### 13.3 Reach Failure：位置偏移抓空

将方块向机械臂方向移动约 2 英寸（5.08 cm），记录末端是否到达目标和夹爪是否真正抓住方块。目标方位估计与最终抓取成功必须分别统计。

### 13.4 No Motion：策略未启动

记录执行初期是否出现有效位姿变化，区分短暂等待、初态抖动与真正向方块接近。该失败现象用于诊断位置随机化策略的执行稳定性，而不是简单归因于方块颜色。

### 13.5 Recovery Failure：掉落后未恢复

观察已抓起的方块在搬运中掉落或释放后，策略是否尝试重新抓取、是否成功重抓以及最终是否完成入杯。出现掉落并不自动等同恢复失败：成功重抓并最终入杯应单独标为恢复成功。

### 13.6 评测指标

| 指标 | 说明 |
|---|---|
| Task Success Rate | 成功抓取并最终将方块放入杯子的比例 |
| Valid Initiation Rate | 从初始位姿产生有效接近动作的比例 |
| Reach / Grasp Success | 能到达方块 / 能真正抓起方块，分开统计 |
| No-motion Rate | 未形成有效接近动作的比例 |
| Drop Rate | 搬运过程发生掉落或释放的比例 |
| Re-grasp Rate | 发生掉落的回合中重新成功抓取的比例 |
| Recovery Success | 掉落后最终仍能入杯的比例 |
| Completion Time | 成功回合的完成时间 |

### 13.7 成功判定

**Success = Grasped ∧ PlacedInsideCup ∧ ReleasedWithinTimeLimit**

机械臂抓空、始终不动、目标未放进杯子或超时，均不能计为成功。若发生掉落但重新抓取并完成入杯，可记录最终成功，同时保留掉落和重抓标记。

### 13.8 结果口径

本 README 首页的三段真机失败 GIF 是第三方独立研究案例，**不是本仓库新真机实验的已测成功率**。没有新的原始实机 Rollout、对应 Checkpoint 和回合记录时，不填写或推测新任务的成功率。

<details>
<summary>原 README 真机统计保留（旧版多玩具目标选择口径）</summary>

原有 SmolVLA 真机汇总如下，数字未修改。但该统计原先对应多玩具目标选择，指标“目标选择率”和“误抓率”与当前单方块入杯实验不构成同一评测。

| Model | Task Success Rate | Target Selection | Wrong-object Rate |
|---|---:|---:|---:|
| SmolVLA | **60%** | **86%** | **12%** |

原始评测回合与权重未公开，不能将这组数字直接解释为当前 Cube → Cup 条件的成功率。

</details>

### 13.9 对应视频的失败类型

| 类型 | 失败现象 | GIF |
|---|---|---|
| Reach Failure | 目标偏移后沿旧轨迹伸手，夹爪抓空 | `clip2_offset_2in.gif` |
| No Motion | 初始位姿附近抖动，未发起有效动作 | `clip3_no_motion.gif` |
| Recovery Failure | 搬运中掉落后未重新抓取或未完成入杯 | `clip4_drop_no_recovery.gif` |

视频与案例说明已置于 README 开头；本项目真实失败率仍需依据自己未来的实机 Episode 记录统计。

---

<a id="huggingface"></a>

## 14. Hugging Face 数据管理

项目支持将 LeRobotDataset 保存在本地，也支持通过 Hugging Face Hub 管理数据集。

### 14.1 本地数据存储

数据采集时使用：

```bash
--offline-local-only
```

可以将数据保存在指定本地目录，不执行远程上传。

示例：

```text
data/
├── demo_data_so101/
└── ...
```

模型 Checkpoint 与实验结果分别保存在：

```text
checkpoints/
outputs/
```

### 14.2 上传数据集

登录 Hugging Face：

```bash
hf auth login
```

使用上传脚本：

```bash
python scripts/hf/upload_hf.py \
  --folder data/demo_data_so101 \
  --repo-id YOUR_USERNAME/so101_pick_place \
  --repo-type dataset \
  --create-if-missing
```

其中：

- `--folder`：本地数据集路径。
- `--repo-id`：Hugging Face 数据集仓库。
- `--repo-type dataset`：上传为 Dataset。
- `--create-if-missing`：在仓库不存在时创建。

上传前应确认数据集格式与隐私设置。

### 14.3 数据安全

真实机器人操作数据、Checkpoint 和实验视频根据实际权限进行管理。

私有数据不应直接提交至公共 Git 仓库。

对于较大的视频和模型权重，建议使用独立的数据存储或模型仓库，避免增加 Git 仓库体积。

---

<a id="reproducibility"></a>

## 15. 实验复现与注意事项

### 15.1 实验环境与版本

复现实验应记录：

- 操作系统。
- Python 版本。
- LeRobot 版本。
- MuJoCo 版本。
- PyTorch 版本。
- CUDA 版本。
- GPU 型号。
- 模型 Checkpoint。
- 随机种子。

不同版本的机器人数据接口和策略配置可能存在差异，应保持训练与推理环境兼容。

### 15.2 训练数据一致性

进行模型比较时，应明确记录不同策略使用的：

- 训练示范数量。
- 相机观测。
- 机器人状态。
- 动作表示。
- 数据集划分。
- 训练 Steps。
- 预训练初始化方式。

对于仿真实验，三种模型应使用相同任务的专家示范数据进行比较。

对于真机实验，SmolVLA 使用方块入杯任务的真实示范；固定自然语言指令，按 Clean、位置随机化和 Recovery 条件分别记录。

### 15.3 任务与示教条件一致性

真机采用统一的 `Pick up the cube and place it in the cup.` 语言指令。比较不同示教条件下的 SmolVLA 时应固定模型初始化、相机、动作语义、复位条件、超时和成功判定。

### 15.4 泛化类型

实验区分以下泛化设置。

**Position Generalization**

目标在训练未覆盖的位置出现。

**Reach / Position Generalization**

改变方块初始位置，观察目标接近与抓取能力。

**No-motion Robustness**

比较不同示教条件下不启动或仅在初始位姿抖动的回合。

**Recovery Generalization**

搬运途中掉落后重新抓取并完成入杯。

**Appearance Generalization（可选）**

方块使用训练未见的颜色，但任务目标始终是将方块放入杯子。

上述泛化类型具有不同难度，应分别设计评测任务和报告结果。

本项目的基础仿真 OOD 主要指目标方块的位置变化，不等同于新物体类别泛化。

### 15.5 仿真与真实环境差异

MuJoCo 仿真与真实 SO-101 环境存在差异，包括：

- 相机成像。
- 光照。
- 物体材质。
- 接触与摩擦。
- 关节校准。
- 控制延迟。
- 物体类别。
- 任务条件。

当前仿真任务使用红色方块和蓝色盒子，真机任务使用单个方块与杯子；两者是同类抓取放置任务，但评测条件与数据来源不同。

因此，真机与仿真除成像、控制和接触差异外，还涉及目标容器与实验条件的变化。

不能将所有性能差异直接解释为纯粹的 Sim-to-Real Gap。

### 15.6 评测协议与成功判定

模型比较应尽量使用：

- 相同的测试初始状态集合。
- 相同的机器人和环境配置。
- 相同的任务最大执行时间。
- 明确且一致的成功判定标准。
- 足够的测试 Episode。
- 独立于训练数据的测试场景。

对于真机方块入杯任务，应分别记录 Baseline、Position Shift、No Motion 和 Recovery 条件的测试次数，区分接近抓空、未启动与掉落后恢复失败。

实验结果需要报告真实测试次数和对应统计方式。

---

<a id="acknowledgements"></a>

## 16. 致谢

本项目基于以下开源项目及研究工作：

- [LeRobot](https://github.com/huggingface/lerobot)
- [MuJoCo](https://mujoco.org/)
- [SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)
- [lerobot-mujoco-tutorial](https://github.com/jeongeun980906/lerobot-mujoco-tutorial)
- [yet-another-mujoco-tutorial](https://github.com/sjchoi86/yet-another-mujoco-tutorial-v3)
- ACT — Action Chunking with Transformers
- Diffusion Policy
- SmolVLA

感谢相关开源项目及研究工作的作者与维护者。

---

<a id="license"></a>

## 17. 许可证

本项目许可证见 [LICENSE](LICENSE)。

第三方代码、机器人模型及预训练权重遵循各自的许可证。
