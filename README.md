# SO-101 Policy Benchmark & Real-World SmolVLA Diagnostics

项目包含两个实验场景：

- **MuJoCo Simulation**：在 SO-101 仿真环境中比较 ACT、Diffusion Policy 和 SmolVLA，完成红色方块抓取放置任务。
- **Real Robot Manipulation**：完成真实 SO-101 的 Cube → Cup 任务实验，覆盖失败模式分析、Clean / Randomized / Recovery / Color-varied 四种固定策略示教数据采集、SmolVLA 微调训练及统一真机评测。

## 目录

- [项目演示与核心结果](#highlights)

### 一、项目概览与环境配置
1. [项目概览与系统架构](#overview)
2. [安装与环境配置](#installation)

### 二、MuJoCo 仿真实验（数据处理 + 多策略对比）
3. [仿真环境与数据集处理](#sim-env-data)
4. [仿真策略训练与闭环评测](#sim-train-eval)

### 三、SO-101 真机实验（失败模式分析与固定策略数据评测）
5. [真机平台与固定策略示教数据采集](#real-env-data)
   - [真机部署模块：机械臂标定、相机标定与硬件检查](docs/REAL_HARDWARE_SETUP.md)
6. [真机策略训练与失败模式评测](#real-train-eval)

### 四、数据管理与复现规范
7. [Hugging Face 数据管理](#huggingface)
8. [实验复现与工程规范](#reproducibility)
9. [许可证](#license)

---

<a id="highlights"></a>

## 项目演示与核心结果

### 仿真成功与失败视频

**✅ 成功示例**

https://github.com/user-attachments/assets/943cd752-5400-4828-933f-b1b99f0062f6

**❌ 失败示例**


https://github.com/user-attachments/assets/b897b248-aaac-427f-8586-3e0412ba6b23



### 仿真实验结果

| Metric | ACT | Diffusion Policy | SmolVLA |
|---|---:|---:|---:|
| **Success Rate ↑** | 89% | 80% | **95%** |
| OOD Success Rate ↑ | 72% | 62% | **83%** |


### 真机失败模式视频

> 以下视频由本项目在 SO-101 真机实验过程中采集，用于展示正常操作、目标接近失败、动作启动失败、掉落恢复失败及重新抓取等现象。

#### 1. 正常操作：Success

https://github.com/user-attachments/assets/9fa9a44b-a124-4daa-95e9-cd610ffb2621

作为正常操作对照，视频展示接近、夹取、搬运和释放等基本阶段。

#### 2. 目标接近失败：Reach Failure

https://github.com/user-attachments/assets/bbaef4dc-106d-4fae-a9b8-1aff7b190b3d

视频中方块位置发生偏移，机械臂没有准确到达目标位置，最终未能完成抓取。

#### 3. 动作启动失败：No Motion

https://github.com/user-attachments/assets/ed2eac7b-f7ce-4398-b8cd-6ba9fa5d1600

机械臂在初始姿态附近小幅抖动，没有形成有效的接近动作。

#### 4. 掉落恢复失败：Recovery Failure

https://github.com/user-attachments/assets/54a7244c-4357-44bf-8dc6-48e12bf8f12b

方块在搬运过程中掉落，机械臂没有完成重新定位、再次抓取和后续放置。

#### 5. 重新抓取：Re-grasp

https://github.com/user-attachments/assets/55915c62-7fe4-46f4-ad79-bfd149a8a380

视频展示方块掉落后机械臂再次接近并抓起方块的过程，作为恢复动作的成功案例展示；单个案例不代表整体恢复成功率。

### 失败模式分析

| 失败模式 | 视频中可观察到的现象 | 需要关注的问题 |
|---|---|---|
| **Reach Failure** | 目标位置偏移后，机械臂未能准确接近方块 | 目标位置变化时，策略能否调整接近位置和运动方向 |
| **No Motion** | 机械臂停留在初始姿态附近，没有有效动作 | 先排除通信、限位和硬件问题，再判断策略是否未能启动有效动作 |
| **Recovery Failure** | 方块掉落后，没有完成重新定位和再次抓取 | 是否能够重新发现目标、调整接近动作并完成重抓 |
| **Re-grasp** | 掉落后重新接近并抓起方块 | 需要进一步验证这种恢复行为是否稳定，而不只是偶然成功 |

上述失败模式作为本项目示教策略设计与评测分析的依据。四种策略的数据采集、训练和统一真机评测均已完成；各策略对不同失败类型的影响以实际评测日志统计为准。

### 根据失败模式组织固定策略示教数据

本项目使用四种固定示教策略组织训练数据，不额外引入在线失败触发或专家接管机制。

| 固定示教策略 | 数据组成 | 主要考察的问题 |
|---|---|---|
| **Clean** | 红色方块固定 T6；50 条正常成功示教 | 基础操作能力与固定位置基线 |
| **Randomized** | 红色方块在 T1–T10 各采集 5 条 | 目标位置变化时的接近与位置泛化，对应 Reach Failure |
| **Recovery** | 红色方块固定 T6；其中 20 条包含主动释放、重抓并完成入杯 | 掉落后的重新定位与抓取，对应 Recovery Failure |
| **Color-varied** | 固定 T6；红、橙、黄、蓝、紫各 10 条；绿色留作评测 | 物体外观变化下的策略表现 |

这四组数据分别用于训练和评测，观察不同示教条件对失败表现的影响。No Motion 需要先排查硬件、通信和控制链路，不能仅凭增加示教数据就认定能够解决。

### 仿真与真机实验结果概览

| 实验 | 模型 / 数据条件 | 结果 |
|---|---|---|
| MuJoCo 仿真 | ACT | **89% ID / 72% OOD** |
| MuJoCo 仿真 | Diffusion Policy | **80% ID / 62% OOD** |
| MuJoCo 仿真 | SmolVLA | **95% ID / 83% OOD** |
| SO-101 真机 | Baseline、Clean、Randomized、Recovery、Color-varied 五组 SmolVLA | **已完成训练与统一评测** |

真机实验包含 1 个 Baseline 和 4 个固定策略模型。五组模型均已完成训练及统一真机评测；具体真机成功率数值不在当前公开 README 中展示，避免将仿真结果或未公开的统计值混作真机成绩。

> **任务边界**：仿真任务为「红色方块 → 蓝色盒子」，真机任务为「方块 → 杯子」。两者任务与物理条件不同，分别报告实验结果，不将其合并为同一组 Sim-to-Real 成功率。

---

<a id="overview"></a>

## 1. 项目概览与系统架构

本项目围绕 **SO-101 机械臂** 的抓取放置（Pick-and-Place）操作，完成了**仿真策略基准对比**与**真机示教数据策略评测**两条实验路线。仿真部分比较 ACT、Diffusion Policy 和 SmolVLA；真机部分围绕 Cube → Cup 任务，完成失败模式分析、四种固定策略示教数据采集、SmolVLA 微调训练及统一评测。

- **MuJoCo 仿真实验**：基于开源 LeRobot 数据集，在统一的 SO-101 物理仿真环境中独立完成了 **ACT**、**Diffusion Policy** 与 **SmolVLA** 三种模仿学习策略的训练、超参对齐与分布内/分布外（ID / OOD）闭环评测。
- **SO-101 真机实验**：以 **SmolVLA** 为固定模型，完成 Reach、No Motion 和 Recovery 等失败模式分析，采集 Clean、Randomized、Recovery、Color-varied 四组示教数据，分别训练并按统一协议评测 Baseline 与四组策略模型。

### 1.1 仿真与真机实验对比

| 维度 | MuJoCo 仿真实验 | SO-101 真机实验 |
| :--- | :--- | :--- |
| **机器人平台** | SO-101（5 旋转关节 + 1 夹爪，MJCF 物理模型） | SO-101 实体机械臂 + 夹爪 + 双路 640×480@30fps 相机 |
| **任务目标** | 抓取**红色方块**放入**蓝色收纳盒**（含多色干扰方块） | 抓取桌面**方块**放入**杯子**（`Cube → Cup`） |
| **数据来源** | **直接采用开源 LeRobotDataset**（经本地格式校验与统计归一化） | Clean、Randomized、Recovery、Color-varied 四种固定策略示教数据 |
| **对比策略** | **ACT** vs. **Diffusion Policy** vs. **SmolVLA** | **SmolVLA**（相同模型架构在不同示教策略下的行为诊断） |
| **语言指令** | 固定仿真任务描述 | `Pick up the cube and place it in the cup.` |
| **核心研究问题** | 三类主流模仿学习架构在 ID 与 OOD 位置泛化下的性能边界 | 不同固定示教数据策略对真机任务成功率、位置泛化和失败行为有何影响 |

### 1.2 系统流水线

**仿真实验流水线（开源数据驱动）：**

```text
开源 LeRobotDataset ──▶ 格式转换与统计校验 (v3.0) ──▶ ACT / Diffusion Policy / SmolVLA 训练
                                                                       │
SO-101 MuJoCo 场景 (scene_so101_y.xml) ◀──── 闭环 Rollout 推理 ◀────────┘
        │
        ▼
ID / OOD 位置泛化与失败类型量化分析
```

**真机实验流程（视频分析 → 固定策略数据 → 训练评测）：**

```text
典型失败模式视频
        │
        ▼
失败模式分析
Reach / No Motion / Recovery
        │
        ▼
固定策略示教数据
Clean / Randomized / Recovery / Color-varied
        │
        ▼
SmolVLA 微调训练
        │
        ▼
统一真机评测
        │
        ▼
比较整体成功率与各类失败表现
```

> **实现状态**：仓库提供四种固定策略的采集计划、训练、真机评测和离线汇总入口。数据按预先设定的条件由操作者遥操作采集；不增加自动失败触发、在线专家接管或自动数据聚合机制。

---

<a id="installation"></a>

## 2. 安装与环境配置

### 2.1 Docker 环境（推荐）

仓库提供两套独立镜像，按计算负载区分使用：

| Dockerfile | 用途 | Python / PyTorch | GPU 支持 |
| :--- | :--- | :--- | :--- |
| `Dockerfile.runtime` | 数据格式处理、回放检查、CPU 基础仿真 | Python 3.12 / PyTorch CPU | 无需 GPU |
| `Dockerfile` | 模型训练与 GPU 闭环推理 | Python 3.12 / CUDA 12.4 | 需 NVIDIA GPU + Container Toolkit |

```bash
# 1. 构建镜像
docker build -t lerobot_mujoco_sim:runtime -f Dockerfile.runtime .
docker build -t lerobot_mujoco_sim:train -f Dockerfile .

# 2. 启动 CPU 运行容器
docker run --rm -it -v "$PWD:/workspace" lerobot_mujoco_sim:runtime

# 3. 启动 GPU 训练/推理容器
docker run --rm -it --gpus all -v "$PWD:/workspace" lerobot_mujoco_sim:train
```

亦可通过 Docker Compose 启动 CPU 服务（`docker compose up -d lerobot-runtime && docker compose exec lerobot-runtime bash`）；GPU 训练建议直接使用上述 `docker run --gpus all` 命令。

### 2.2 本地 Python 虚拟环境

若不使用 Docker，可参考以下配置搭建本地环境（`configs/real/requirements.txt` 专用于 SO-101 真机驱动与相机依赖）：

```bash
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip

# 以 CPU 版 PyTorch 为例（GPU 训练请安装对应 CUDA 版本）
python -m pip install torch==2.7.0 torchvision==0.22.0 \\
  --index-url https://download.pytorch.org/whl/cpu
python -m pip install "lerobot==0.5.1" "mujoco==3.1.6" \
  numpy Pillow glfw termcolor PyYAML mink matplotlib scipy opencv-python

# 环境可用性自检
python -c "import mujoco, torch, lerobot; print('MuJoCo:', mujoco.__version__, '| CUDA:', torch.cuda.is_available())"
```

---

<a id="sim-env-data"></a>

## 3. 仿真环境与数据集处理

### 3.1 SO-101 MuJoCo 仿真场景

仿真环境基于 [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) 提供的 SO-101 机械臂模型搭建，包含 5 个旋转关节与 1 个夹爪自由度：

- **场景定义**：`asset/scene_so101_y.xml`（包含 SO-101 机械臂、桌面、蓝色收纳盒、红色目标方块、多色干扰方块及双视角 RGB 相机）。
- **环境封装**：`mujoco_env/y_env.py`（负责 Episode 重置、物体初始位姿随机采样、关节状态读取、相机渲染及动作步进）。
- *(注：仓库同时保留基于 Mink IK + 有限状态机的脚本控制器 `controllers/scripted_fsm_controller.py` 与采集工具 `scripts/collect/`，用于场景调试和后续扩展；三策略对比实验使用统一的数据集与评测流程。)*

### 3.2 开源数据集转换与质量校验

仿真实验直接加载开源 LeRobotDataset，统一转换为 **LeRobotDataset v3.0** 标准目录结构（`meta/`、`data/`、`videos/`）：

**1. 历史版本转换（v2.1 → v3.0）与 Parquet Schema 修复**

针对部分开源数据集包含 `spawn.block_xyz` 等历史字段导致的 NumPy Object Vector 与 PyArrow 兼容问题，使用内置转换脚本自动修复（原始数据会自动备份至相邻 `_old` 目录，可通过 `--no-repair-parquet` 关闭修复）：

```bash
python scripts/convert_lerobot_dataset_v21_to_v30_local.py \
  --root data/my_v21_dataset \
  --repo-id local/my_v21_dataset
```

**2. 数据回放与特征一致性核验**

训练前通过可视化脚本（`python scripts/visualize/visualize_data.py` 或 `notebooks/2.visualize_data.ipynb`）抽检开源轨迹，确保：
- 双路相机观测与关节动作严格时间对齐，无丢帧或动作跳变；
- 关节顺序、弧度单位、夹爪开合范围（`[0, 1]`）及图像特征键名与仿真评测接口完全一致。

---

<a id="sim-train-eval"></a>

## 4. 仿真策略训练与闭环评测

### 4.1 三种模仿学习策略训练

在完全相同的开源数据集与训练划分下，独立训练三类代表性策略进行横向对比：

| 模型 | 核心架构 | 初始化方式 | 输入模态 | 训练入口 / 命令 |
| :--- | :--- | :--- | :--- | :--- |
| **ACT** | Transformer + Action Chunking | 随机初始化 | 双路图像 + 机器人状态 | `python scripts/train/train_act.py` |
| **Diffusion Policy** | 条件扩散去噪生成动作序列 | 随机初始化 | 双路图像 + 机器人状态 | `bash scripts/train/train_diffusion.sh` |
| **SmolVLA** | 视觉-语言-动作大模型 | 预训练权重 `lerobot/smolvla_base` | 双路图像 + 状态 + 文本指令 | `bash scripts/train/finetune_smolvla.sh` |

标准 `lerobot-train` 调用示例：

```bash
# ACT 训练
lerobot-train \
  --dataset.repo_id=local/so101_sim \
  --dataset.root=data/so101_sim \
  --policy.type=act \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=outputs/train/act

# Diffusion Policy 训练
lerobot-train \
  --dataset.repo_id=local/so101_sim \
  --dataset.root=data/so101_sim \
  --policy.type=diffusion \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=outputs/train/diffusion

# SmolVLA 微调（固定仿真任务指令）
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=local/so101_sim \
  --dataset.root=data/so101_sim \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --output_dir=outputs/train/smolvla
```

### 4.2 统一闭环评测与 ID / OOD 实验设计

评测阶段彻底脱离任何专家控制器，由策略权重根据实时观测独立输出 Action Chunk 并在 MuJoCo 中闭环执行。

- **分布内测试（ID）**：红色方块在开源训练集覆盖的工作空间范围内随机生成，检验基础抓取放置精度。
- **分布外测试（OOD）**：红色方块在训练集未覆盖、但处于 SO-101 可达工作空间且不与箱体碰撞的区域内随机生成（保持光照、物体尺寸与物理参数不变），检验策略对未见目标位置的空间泛化能力。
- **成功判定标准**：$\text{Success} = \text{CorrectTarget} \land \text{SuccessfulGrasp} \land \text{SuccessfulPlacement}$（必须准确抓取红色目标方块、稳定抬起并最终置入蓝色收纳盒内）。

使用统一评测脚本 `scripts/eval/eval_mujoco.py` 运行三类模型并导出结构化 JSONL 与 CSV 统计：

```bash
# 运行分布内（ID）闭环评测（切换 --policy 为 act / diffusion / smolvla 及对应权重路径）
python scripts/eval/eval_mujoco.py \
  --policy act \
  --checkpoint /path/to/act/pretrained_model \
  --dataset-root /path/to/so101_sim \
  --action-semantics joint_radians_gripper_closed_0_1 \
  --top-feature observation.images.top \
  --wrist-feature observation.images.wrist \
  --processors saved \
  --device cuda \
  --split id \
  --num-trials 100 \
  --seed 42 \
  --timeout-clock sim \
  --output outputs/eval/act_id_seed42.jsonl

# 运行分布外（OOD）闭环评测（需显式指定分布外生成边界）
python scripts/eval/eval_mujoco.py \
  --policy smolvla \
  --checkpoint /path/to/smolvla/pretrained_model \
  --dataset-root /path/to/so101_sim \
  --action-semantics joint_radians_gripper_closed_0_1 \
  --top-feature observation.images.top \
  --wrist-feature observation.images.wrist \
  --processors saved \
  --device cuda \
  --split ood \
  --spawn-x-min <X_MIN> --spawn-x-max <X_MAX> \
  --spawn-y-min <Y_MIN> --spawn-y-max <Y_MAX> \
  --num-trials 100 \
  --seed 42 \
  --timeout-clock sim \
  --output outputs/eval/smolvla_ood_seed42.jsonl

# 汇总评测日志为 CSV 指标表
python scripts/eval/summarize_rollouts.py outputs/eval/act_id_seed42.jsonl \
  --csv outputs/eval/act_id_seed42.csv
```

> **使用提示**：`--top-feature` 与 `--wrist-feature` 需与训练数据集特征名严格一致（旧版数据集可能使用 `observation.image` 与 `observation.wrist_image`）；若 Checkpoint 目录未保存处理器 JSON，可改用 `--processors dataset` 自动从本地 `meta/stats.json` 构建归一化参数。

### 4.3 仿真评测指标定义

| 指标 | 定义说明 | 优化方向 |
| :--- | :--- | :---: |
| **Success Rate (ID)** | 训练集分布内位置下的完整入盒成功率 | ↑ |
| **OOD Success Rate** | 训练集未覆盖位置下的完整入盒成功率 | ↑ |
| **Completion Time** | 成功 Episode 的平均 MuJoCo 仿真耗时 | ↓ |
| **Initiation Failure Rate** | 规定启动窗口内未产生有效接近运动的 Episode 比例 | ↓ |
| **Grasp Failure Rate** | 进入抓取阶段后未能成功夹持并抬起目标的比例（按实际抓取尝试统计） | ↓ |

---

<a id="real-env-data"></a>

## 5. 真机失败模式分析与固定策略示教数据采集

> **本节组织顺序**：先展示本项目采集的真机操作视频，再分析失败现象对应的操作阶段，随后介绍四种固定示教策略、SmolVLA 训练设置与统一评测结果。


<a id="real-hardware-setup"></a>

### 5.0 真机部署模块：机械臂标定、相机标定与硬件检查

真机部署准备拆分为三个独立模块，正式采集或评测前按顺序完成：

| 模块 | 主要工作 | 操作说明 |
|---|---|---|
| 机械臂标定 | 分别识别 Leader / Follower 串口，校准电机零点偏移与关节范围，保存本机 JSON | [机械臂标定指南](docs/real-hardware/ROBOT_CALIBRATION.md) |
| 相机标定 | 识别 front / wrist 相机，固定安装与视角，核对分辨率、FPS、曝光和数据特征名；需要三维几何时再做内外参标定 | [相机标定指南](docs/real-hardware/CAMERA_CALIBRATION.md) |
| 硬件检查 | 检查供电、机械装配、电机总线、急停、工作空间、关节限位和软件停止机制 | [硬件检查清单](docs/real-hardware/HARDWARE_CHECK.md) |

总入口：[SO-101 真机硬件部署指南](docs/REAL_HARDWARE_SETUP.md)。本项目 LeRobot 版本基线为 0.5.1；命令和配置以该版本为准。

本机文件布局：

~~~text
calibration/
├── README.md
├── robots/
│   ├── .gitkeep
│   └── .gitignore
└── camera/
    ├── README.md
    └── reference/
        └── .gitkeep
~~~

当前真机运行器从配置项 robot.calibration_dir / robot.id 读取 Follower 标定文件。默认目录为 <code>calibration/robots/</code>，机器人 ID 为 <code>so101_follower</code> 时，文件应为 <code>calibration/robots/so101_follower.json</code>。Leader 可使用独立 ID 保存自己的标定文件。

**设备相关的机械臂标定 JSON 和相机内外参不提交到 GitHub**；仓库只保留目录、说明和参考资料占位文件。配置中的 <code>robot.hardware_confirmed</code> 继续默认为 <code>false</code>，完成本机检查前不要改为 <code>true</code>。

### 5.1 四组示教数据集

真机实验使用 Clean、Randomized、Recovery、Color-varied 四组 LeRobotDataset，每组 50 条示教。数据集均包含 `meta/`、`data/`、`videos/`，并在下载后检查回合数、30 FPS、六维 action/state 及 overhead/wrist 双相机特征。

| 数据条件 | 数据集 | 回合数 | 用途 |
|---|---|---:|---|
| Clean | `cube-pickup-clean_20260809_105745` | 50 | 固定位置正常示教 |
| Randomized | `cube-pickup-randomized_20260809_115825` | 50 | 10 个训练位置轮换 |
| Recovery | `cube-pickup-recovery_20260809_141725` | 50 | 包含主动释放与重新抓取 |
| Color-varied | `cube-pickup-color_20260809_183224` | 50 | 红、橙、黄、蓝、紫五色示教；绿色用于评测 |

数据下载入口会解析并记录每个数据集的 Hub commit SHA，保证下载版本可追溯：

```bash
# 先查看下载计划
python scripts/real/download_reference_datasets.py --dry-run

# 下载全部四组数据
python scripts/real/download_reference_datasets.py

# 只下载指定条件
python scripts/real/download_reference_datasets.py --condition clean recovery
```

默认保存至 `data/real_demonstrations/{clean,randomized,recovery,color}/`，并生成 `download_manifest.json`。数据文件较大，保留在本地忽略目录，不提交到 GitHub。安装下载依赖：

```bash
python -m pip install -U huggingface_hub
```

训练时将数据集的 `observation.images.overhead`、`observation.images.wrist` 映射到策略输入的 `camera1`、`camera2`；真机推理时使用 front / wrist 两路相机。相机名称、分辨率、FPS 和特征映射必须与训练配置一致。

### 5.2 统一任务与控制变量

- **真机任务**：SO-101 抓取桌面方块并放入固定杯子；统一指令 <code>Pick up the cube and place it in the cup.</code>。
- **固定条件**：同一机器人、相机与安装角度、固定复位位姿、杯子位置、训练初始权重、训练步数及评分标准。
- **双路相机**：前/全局与腕部相机（目标配置 640×480、30 FPS）。必须核对实际设备名称与训练权重的 <code>rename_map</code>，按本机相机索引配置。
- **空间标记**：在本机安全工作区标记 T1–T10（训练位置）及 E1–E5（从未示教的评测位置）；T6 为固定基准位置。编号只代表实验位置，桌面坐标需按实际机器人重新标定。
- **安全**：检查标定、关节限位、停止入口、实体急停、障碍物和夹爪极性；现有 <code>configs/real/so101.yaml</code> 默认 <code>robot.hardware_confirmed: false</code>，不会自动启用真机。

### 5.3 根据失败模式组织四组固定策略示教数据

本项目实际采用四种固定示教策略：**Clean、Randomized、Recovery、Color-varied**。四组数据分别用于训练 SmolVLA，并在统一测试条件下比较不同示教数据条件对任务成功率和失败行为的影响。

四组策略的具体数据组成及其与失败模式的对应关系已在本节前面的「根据失败模式组织固定策略示教数据」表中汇总。这里保留实际采集计划与运行命令，便于执行时查阅。

这四种固定策略就是本项目数据采集阶段采用的方案。视频分析用于明确要观察的问题，固定策略数据用于训练和比较；不额外加入在线触发、专家接管或自动聚合流程，也不声称某一策略必然解决某种失败。No Motion 还需要结合硬件、通信和控制状态排查，不能仅靠增加某一组示教数据就认定能够解决。

采集前先查看每条示教对应的位置、颜色及是否需要主动释放的计划：

~~~bash
python scripts/real/study_protocol.py --phase collect --condition randomized
python scripts/real/study_protocol.py --phase collect --condition recovery
~~~

本仓库的采集入口默认实际执行（下方仍显式写出 <code>--execute</code>）；如只想检查 50 条采集计划，改用 <code>--dry-run</code>。运行前必须核对实际端口、相机、标定、急停与工作区：

~~~bash
python scripts/real/record_study.py \
  --condition clean --repo-id local/real_cube_clean \
  --dataset-root data/real_cube_clean \
  --follower-port /dev/ttyACM0 --leader-port /dev/ttyACM1 \
  --front-idx 0 --wrist-idx 1 \
  --plan-output outputs/real/plans/clean.json --execute
~~~

工具不会自动移动物体或切换灯光；每条示教开始前由操作者按计划人工布置，并核对录制结果。正式采集按 LeRobot 0.5.1 环境及本机硬件检查清单执行。


---

<a id="real-train-eval"></a>

## 6. 真机 SmolVLA 训练与失败模式评测

### 6.1 五个真机 SmolVLA 模型的训练对照

正式比较包含 **1 个原始真机基线 + 4 个固定策略改进模型**，所有模型只使用一个训练种子（Seed 1000），共 **5 个独立训练运行**。五个模型使用相同 SmolVLA 基础权重和训练预算（10,000 steps、batch size 32、每 2,000 steps 保存 checkpoint），只改变训练数据条件。

- **Baseline**：使用原始 Cube → Cup 真机示教数据，不经过四种改进策略的数据组织。
- **Clean / Randomized / Recovery / Color-varied**：分别使用对应的 50 条固定策略示教数据，四组独立训练、独立评测。

先训练原始真机基线（数据目录由操作者提供）：

~~~bash
python scripts/real/train_study.py \
  --condition baseline --seed 1000 \
  --dataset-root data/real_so101_baseline \
  --repo-id local/real_so101_baseline \
  --base-model /path/to/local/smolvla_base \
  --output outputs/train/real_baseline_seed1000 \
  --rename-map '{"observation.images.overhead":"observation.images.camera1","observation.images.wrist":"observation.images.camera2"}' --execute
~~~

再以 Clean 为例展示训练命令；其余三组替换 condition、dataset-root、repo-id 和 output。以下命令用于复现实验流程：

~~~bash
python scripts/real/train_study.py \
  --condition clean --seed 1000 \
  --dataset-root data/real_demonstrations/clean \
  --repo-id Andresg324/cube-pickup-clean_20260809_105745 \
  --base-model /path/to/local/smolvla_base \
  --output outputs/train/real_clean_seed1000 \
  --rename-map '{"observation.images.overhead":"observation.images.camera1","observation.images.wrist":"observation.images.camera2"}' --execute
~~~

训练入口默认实际运行（可用 `--dry-run` 仅输出命令），并检查数据集回合数及六维真机关节特征：Baseline 数据集至少包含 1 条有效示教；四种固定策略数据集必须各为 50 条。运行后在对应训练输出目录生成 <code>study_manifest.json</code>，记录训练条件、Seed、数据集、权重 SHA-256 和训练预算，供评测入口核验。全部数据与权重保持本地，不默认上传 Hub。

### 6.2 五类统一评测场景

五个模型（Baseline、Clean、Randomized、Recovery、Color-varied）各自在同样的五类场景下测试。**每个模型共 100 次正式计分：ID 40 次，四个 OOD 场景各 15 次。**每个模型在每个场景另做 1 次预热，不计入成功率。

| 评测场景 | 正式计分次数 | 预热 | 物理环境设置 | 主要测量 |
|---|---:|---:|---|---|
| <code>in_distribution</code>（ID） | **40** | 1 | 红色方块 T6、标准光照 | 基础任务成功率 |
| <code>new_positions</code>（OOD） | **15** | 1 | 红色方块 E1–E5，每个位置各 3 次 | 位置泛化与 Reach Failure |
| <code>reduced_lighting</code>（OOD） | **15** | 1 | 红色方块 T6、降低照明 | 光照鲁棒性 |
| <code>different_object</code>（OOD） | **15** | 1 | 未参与训练的绿色方块 T6 | 颜色/外观泛化；No Motion 只是可能的失败现象 |
| <code>distractors</code>（OOD） | **15** | 1 | 红色方块 T6、增加非目标物体 | 抗干扰能力 |
| **每个模型合计** | **100** | **5** | — | — |
| **五个模型合计** | **500** | **25** | — | — |

本项目已按该协议完成 **500 次正式计分真机 Rollout**，另完成 25 次不计分预热。中断或未完成的回合不计为成功，也不进入成功率分母；正式汇总仅纳入符合协议的有效计分回合。

评测入口默认实际运行（可用 `--dry-run` 仅输出计划）；仍需要操作者逐回合复位场景、确认目标及安全状态，并在结束后人工填写 <code>success</code> 和可观察到的阶段标签（<code>started</code>、<code>reached</code>、<code>grasped</code>、<code>dropped</code>、<code>regrasped</code> 等）。**不能以动作已下发或视频看起来正常代替成功判定。**

~~~bash
# 先查看该场景的 40 次计分 + 1 次预热计划
python scripts/real/study_protocol.py --phase evaluate --cell in_distribution

# 以 Baseline 的 ID 场景为例；其余模型替换 --condition、checkpoint 和 manifest
python scripts/real/evaluate_study.py \
  --condition baseline --seed 1000 --cell in_distribution \
  --checkpoint outputs/train/real_baseline_seed1000/checkpoints/010000/pretrained_model \
  --training-manifest outputs/train/real_baseline_seed1000/study_manifest.json \
  --output outputs/real/eval_baseline_s1000_in_distribution.jsonl --execute
~~~

正式评测时，Baseline 与四组改进模型都必须使用各自训练生成的 <code>study_manifest.json</code>；入口会核对 condition、seed、训练预算和 checkpoint SHA-256。原有的 <code>scripts/real/deploy_policy.py</code> 和 <code>scripts/real/evaluate_policy.py</code> 仍可用于单次安全部署和探索性排查；**正式五模型对照**使用 <code>evaluate_study.py</code>，不能将探索性与注册评测混在同一统计分母里。

### 6.3 失败模式统计：从整体成功率定位薄弱环节

~~~bash
python scripts/real/summarize_study.py outputs/real/eval_*.jsonl \
  --csv outputs/real/study_summary.csv
# 五个模型、Seed 1000、五个场景全部完成，且 ID 为 40 条、每个 OOD 为 15 条时，追加 --strict
~~~

汇总按**模型条件 × 训练种子 × 评测场景**输出成功次数、成功率和 Wilson 95% 区间，并为每个模型追加一行 <code>all_cells</code> 整体成功率（100 次正式计分）。<code>--strict</code> 会校验全部 5 × 1 × 5 个分组、每个场景的准确回合数及计分回合编号；预热和中断回合不计入分母。

行为诊断同时包含 **No-Motion Rate、Reach Rate、Grasp Rate、Drop Rate、Re-grasp per Drop、Recovery per Drop**。若尚未完整标注某阶段，指标显示为空，不自动假设失败或成功。当前运行器保存每回合推理延迟、控制步数、限幅次数及操作者标签；**逐步关节轨迹、动作方向角和相机视频并未自动保存**，因此当前统计主要用于回合级和阶段级失败分析。

### 6.4 评测结果统计与分析

仿真结果与五个真机模型的成功率对比表已放在本 README 前面的失败模式分析之后，按「失败视频 → 失败模式分析 → 固定策略示教数据 → 成功率对比」的顺序呈现。本节进一步说明真机评测结果的统计方法。

Baseline 与四组固定策略模型的训练和统一真机评测均已完成。结果分析按相同测试场景比较：

- **整体任务成功率**：判断不同示教策略对完整 Cube → Cup 任务的影响。
- **Reach / No Motion / Grasp 失败比例**：分析策略是否能稳定启动动作、接近目标并完成抓取。
- **Drop / Recovery 表现**：分别记录掉落次数、重抓次数和重抓后完成任务的次数。
- **不同测试场景的表现**：比较固定位置、新位置、光照变化、不同颜色和干扰物条件下的结果。

真机实验已完成。最终统计以本项目实际采集的数据、训练权重和真机评测日志为准；公开仓库当前不展示五组模型的具体真机成功率数值，不使用仿真结果代替真机成绩，也不在缺少公开统计表的情况下推断哪一组策略最好。


<a id="huggingface"></a>

## 7. Hugging Face 数据管理

项目同时支持纯本地离线管理与 Hugging Face Hub 云端同步：

- **本地离线模式**：在数据采集或训练脚本中传入 `--offline-local-only`，所有数据与模型分别保存在本地 `data/`、`checkpoints/` 与 `outputs/` 目录。
- **数据集上传**：使用 `scripts/hf/upload_hf.py` 同步自采真机数据集或微调权重：

```bash
hf auth login

python scripts/hf/upload_hf.py \
  --folder data/so101_real_baseline \
  --repo-id YOUR_USERNAME/so101_cube_to_cup \
  --repo-type dataset \
  --create-if-missing
```

*(注：大型视频文件、私有真机数据及模型权重请通过独立数据仓库管理，勿直接提交至公共 Git 代码仓库。)*

---

<a id="reproducibility"></a>

## 8. 实验复现与工程规范

1. **环境与随机种子记录**：复现时完整记录操作系统、Python / PyTorch / CUDA / MuJoCo / LeRobot 版本、GPU 型号及评测 `--seed`（默认 `42`）。
2. **输入输出特征严格对齐**：确保训练与推理阶段使用完全一致的相机特征名（如 `observation.images.top` / `observation.images.wrist`）、图像分辨率、控制频率及归一化统计量（`meta/stats.json`）。
3. **Sim-to-Real 边界说明**：本项目仿真任务为「红方块 → 蓝盒子」（基于开源数据集），真机任务为「单方块 → 杯子」（基于自主遥操作采集），两者在视觉成像、接触摩擦、控制延迟及容器几何上均存在差异，评测结果各自独立分析，不直接混同为单一的 Sim-to-Real Gap。
4. **控制变量原则**：仿真多策略对比固定相同的初始随机状态集合与最大超时步数；真机不同条件评测固定相同的相机机位、光照环境与机械臂复位零点。

---

<a id="license"></a>

## 9. 许可证

本项目遵循 [LICENSE](LICENSE) 开源许可证。
