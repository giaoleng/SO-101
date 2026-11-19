

https://github.com/user-attachments/assets/55915c62-7fe4-46f4-ad79-bfd149a8a380



https://github.com/user-attachments/assets/9fa9a44b-a124-4daa-95e9-cd610ffb2621

# SO-101 Policy Benchmark & Real-World SmolVLA Diagnostics

项目包含两个实验场景：

- **MuJoCo Simulation**：在 SO-101 仿真环境中比较 ACT、Diffusion Policy 和 SmolVLA，完成红色方块抓取放置任务。
- **Real Robot Manipulation**：在真实 SO-101 机械臂上使用 SmolVLA，完成单个方块抓取并放入杯子的任务，分析位置偏移、策略不启动与掉落后恢复。

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


### SmolVLA 真机操作视频与失败模式分析

> **视频来源说明**：本节五段真机视频均引用自 [Andresg324/so101-vla-data-study](https://github.com/Andresg324/so101-vla-data-study) 的 SO-101 / SmolVLA 实验，**不是本仓库独立采集或评测的真机结果**。以下分析解释参考案例中可观察到的行为，不代表本项目已复现实验。为保证当前 README 可直接预览，暂时使用原项目的 GIF；转换后的 MP4 有可访问的托管地址后再替换。

#### ✅ Success：正常抓取与放置

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip1_clean_success.gif" width="460" alt="参考项目：SO-101 SmolVLA 正常完成方块抓取、搬运与入杯">

**行为表现**：Clean 策略在训练分布内完成接近、夹取、搬运与释放。该视频作为对照基准，便于比较下方失败案例发生在哪个操作阶段。

#### ❌ Reach Failure：目标偏移后接近不足

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip2_offset_2in.gif" width="460" alt="参考项目：方块偏移两英寸后机械臂未到达目标">

**失败现象**：方块相对训练位置向机械臂方向偏移约 2 英寸（5.08 cm），机械臂仍沿近似固定的方向伸出，最终在方块前方闭合夹爪，未完成抓取。

**诊断分析**：参考项目的轨迹统计显示，目标需要的接近角度约为 29.4°，而机械臂实际达到的角度不足。这更接近**策略未充分调整接近动作**的问题，不能仅从抓空现象推断为夹爪闭合故障。可通过目标位置与实际关节轨迹进一步区分目标定位、运动规划及夹爪执行失效。

#### ❌ No Motion：策略未有效离开初始位姿

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip3_no_motion.gif" width="460" alt="参考项目：机械臂在初始位姿附近轻微抖动，没有形成有效抓取动作">

**失败现象**：位置随机化示教训练的策略面对绿色方块时，机械臂在初始姿态附近小幅抖动，始终没有形成有效接近动作。

**诊断分析**：这是 **Initiation Failure（动作启动失败）**，与“已接近目标但抓取失败”不同。应结合关节位移幅度、动作启动延迟与控制指令判断是否真正产生有效运动；仅凭该视频不能确定停滞源于模型预测、动作后处理还是硬件控制。

#### ❌ Recovery Failure：掉落后未完成恢复

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip4_drop_no_recovery.gif" width="460" alt="参考项目：方块搬运中释放后未完成重新抓取">

**失败现象**：使用恢复示教训练的策略在搬运过程中释放方块，但没有完成重新定位、再次抓取和最终入杯，任务超时。

**诊断分析**：模型可能学到了示教中的**释放动作**，却没有稳定学到释放之后的**闭环恢复序列**。因此需要分别记录掉落事件、是否尝试重抓、重抓是否成功以及最终任务是否完成，不能只统计完整任务成功率。

#### ✅ Re-grasp：少量成功重抓案例

<img src="https://raw.githubusercontent.com/Andresg324/so101-vla-data-study/main/media/clip5_rare_regrasp.gif" width="460" alt="参考项目：方块掉落后成功重新抓取">

**行为表现**：方块掉落后，策略重新接近并抓起目标。参考项目报告在 53 次掉落回合中有 6 次成功重抓，说明恢复行为并非完全不存在，但**偶尔成功不代表恢复能力可靠**。

**分析重点**：对比 Recovery Failure 与 Re-grasp，可将“有没有主动重抓”和“重抓之后是否完成任务”分开评估，避免使用单一成功率掩盖恢复阶段的差异。
## 目录

### 一、项目概览与环境配置
1. [项目概览与系统架构](#overview)
2. [安装与环境配置](#installation)

### 二、MuJoCo 仿真实验（开源数据集 + 多策略对比）
3. [仿真环境与开源数据集处理](#sim-env-data)
4. [仿真策略训练与闭环评测](#sim-train-eval)

### 三、SO-101 真机实验（自主遥操作采集 + SmolVLA 部署）
5. [真机平台与遥操作数据采集](#real-env-data)
6. [真机策略训练、部署与诊断评测](#real-train-eval)

### 四、数据管理与复现规范
7. [Hugging Face 数据管理](#huggingface)
8. [实验复现与工程规范](#reproducibility)
9. [许可证](#license)

---

<a id="overview"></a>

## 1. 项目概览与系统架构

本项目围绕 **SO-101 机械臂** 的抓取放置（Pick-and-Place）操作，独立搭建并完成了**仿真基准对比**与**真机闭环部署**两套完整实验流程。

- **MuJoCo 仿真实验**：基于开源 LeRobot 数据集，在统一的 SO-101 物理仿真环境中独立完成了 **ACT**、**Diffusion Policy** 与 **SmolVLA** 三种模仿学习策略的训练、超参对齐与分布内/分布外（ID / OOD）闭环评测。
- **SO-101 真机实验**：从硬件标定与双目相机配置出发，通过**人工遥操作（Teleoperation）**亲自采集多条件专家示范数据，独立完成 **SmolVLA** 的微调训练、安全实机部署及针对典型失效模式（位置偏移抓空、策略未启动、搬运掉落恢复）的定量诊断评测。

### 1.1 仿真与真机实验对比

| 维度 | MuJoCo 仿真实验 | SO-101 真机实验 |
| :--- | :--- | :--- |
| **机器人平台** | SO-101（5 旋转关节 + 1 夹爪，MJCF 物理模型） | SO-101 实体机械臂 + 夹爪 + 双路 640×480@30fps 相机 |
| **任务目标** | 抓取**红色方块**放入**蓝色收纳盒**（含多色干扰方块） | 抓取桌面**方块**放入**杯子**（`Cube → Cup`） |
| **数据来源** | **直接采用开源 LeRobotDataset**（经本地格式校验与统计归一化） | **作者通过人工遥操作亲自采集**多条件专家示范数据 |
| **对比策略** | **ACT** vs. **Diffusion Policy** vs. **SmolVLA** | **SmolVLA**（相同模型架构在不同示教策略下的行为诊断） |
| **语言指令** | 固定仿真任务描述 | `Pick up the cube and place it in the cup.` |
| **核心研究问题** | 三类主流模仿学习架构在 ID 与 OOD 位置泛化下的性能边界 | 位置偏移接近能力（Reach）、策略启动稳定性（No Motion）与掉落重抓恢复（Recovery） |

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

**真机实验流水线（自主遥操作驱动）：**

```text
人工遥操作采集 (Clean / Position-Randomized / Recovery) ──▶ 自主构建真机 LeRobotDataset
                                                                       │
SO-101 真机控制器 (安全限位校验) ◀── SmolVLA 闭环微调与部署 ◀───────────┘
        │
        ▼
四类专项诊断评测 (Baseline / Reach Shift / No Motion / Drop Recovery)
```

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
python -m pip install torch==2.7.0 torchvision==0.22.0 --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu)
python -m pip install "lerobot==0.5.1" "mujoco==3.1.6" \
  numpy Pillow glfw termcolor PyYAML mink matplotlib scipy opencv-python

# 环境可用性自检
python -c "import mujoco, torch, lerobot; print('MuJoCo:', mujoco.__version__, '| CUDA:', torch.cuda.is_available())"
```

---

<a id="sim-env-data"></a>

## 3. 仿真环境与开源数据集处理

### 3.1 SO-101 MuJoCo 仿真场景

仿真环境基于 [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) 提供的 SO-101 机械臂模型搭建，包含 5 个旋转关节与 1 个夹爪自由度：

- **场景定义**：`asset/scene_so101_y.xml`（包含 SO-101 机械臂、桌面、蓝色收纳盒、红色目标方块、多色干扰方块及双视角 RGB 相机）。
- **环境封装**：`mujoco_env/y_env.py`（负责 Episode 重置、物体初始位姿随机采样、关节状态读取、相机渲染及动作步进）。
- *(注：仓库同时保留了基于 Mink IK + 有限状态机的脚本控制器 `controllers/scripted_fsm_controller.py` 与采集工具 `scripts/collect/` 供扩展使用，但本项目的仿真基准实验完全基于开源数据集开展。)*

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

## 5. 真机平台与遥操作数据采集

### 5.1 硬件平台与任务设定

真机实验在真实 **SO-101 机械臂** 上独立完成，任务为抓取桌面方块并放入固定位置的杯子（`Cube → Cup`）：

- **传感与执行配置**：SO-101 机械臂及夹爪 + 双路 RGB 相机（俯视/前视全局相机 + 腕部局部相机，分辨率 `640×480 @ 30 FPS`）。
- **统一自然语言指令**：所有真机示教与推理均使用固定指令：
  ```text
  Pick up the cube and place it in the cup.
  ```
- **物理安全保障**：配置固定机械臂复位初始位姿、工作空间软限位保护及物理急停开关。

### 5.2 自主遥操作数据采集

区别于仿真使用的开源数据，真机实验的全部专家示范均由作者通过**主从遥操作（Teleoperation）**亲自采集，并按实验条件严格隔离存储为独立 LeRobotDataset（绝不混用不同条件的训练数据）：

| 数据集 Split | 遥操作采集策略与场景设计 | 对应研究目的 |
| :--- | :--- | :--- |
| `baseline` | 方块置于固定标准起点，完整演示接近、抓取、抬起、入杯与释放 | 建立标准抓取放置性能基准 |
| `position_shift` | 评测时将方块向机械臂方向**偏移 2 英寸（5.08 cm）**（训练数据仅含固定起点） | 检验未见位置偏移下是否仍能调整接近轨迹，还是在原位抓空 |
| `no_motion` | 在较大范围内随机化方块起点进行遥操作示教，测试时从相同初始位姿启动 | 诊断示教位置多样性增加后，策略是否出现初态停滞或原地抖动 |
| `recovery` | 遥操作刻意演示「搬运中途主动释放/掉落 → 重新定位接近 → 再次抓取 → 最终入杯」的完整纠错序列 | 检验策略在意外掉落后的闭环重抓与任务恢复能力 |
| `color_variation` *(可选)* | 更换未见颜色的方块，保持文本指令与杯子位置不变 | 独立检验外观颜色泛化能力 |

---

<a id="real-train-eval"></a>

## 6. 真机策略训练、部署与诊断评测

### 6.1 SmolVLA 微调与真机安全部署

真机阶段固定使用 **SmolVLA** 架构，通过对比不同示教条件下微调得到的 Checkpoint，分析数据分布对实机操作鲁棒性的影响。

相关真机代码模块位于：
- `configs/real/so101.yaml`：真机相机设备号、关节零点标定、控制频率与安全工作空间配置。
- `scripts/real/task_conditioning.py`：统一封装语言指令与多模态观测输入预处理。
- `scripts/real/deploy_policy.py`：加载本地 SmolVLA Checkpoint 与真机处理器执行闭环推理。
- `scripts/real/evaluate_policy.py`：支持按条件（`--condition`）开展真机评测并结构化记录精细化过程标签。

> **动作空间安全隔离**：真机底层下发的是校准后的 **5 个关节角度（Degrees）+ 夹爪开合百分比**，与 MuJoCo 仿真的关节弧度制（Radians）严格隔离；部署前必须核对夹爪开合极性及双目相机键名映射。

### 6.2 细粒度行为诊断与评测指标

为避免单一“总成功率”掩盖具体的失效机理，真机评测在每回合结束后记录细粒度过程状态字段（`started`、`reached`、`grasped`、`placed`、`released`、`dropped`、`regrasp_attempted`、`regrasped`、`failure_mode`），并据此统计以下核心指标：

| 指标 | 计算口径与物理含义 |
| :--- | :--- |
| **Task Success Rate** | 满足 $\text{Grasped} \land \text{PlacedInsideCup} \land \text{ReleasedWithinTimeLimit}$ 的最终成功比例（含掉落后重抓成功） |
| **Valid Initiation Rate** | 从初始位姿产生有效接近轨迹的比例（用于量化 `No Motion` 失效） |
| **Reach / Grasp Success** | 末端准确到达方块位置的比例 vs. 夹爪真正抓起方块的比例（区分定位偏差与抓取闭合失误） |
| **Drop Rate** | 搬运过程中发生方块滑落或提前释放的比例 |
| **Re-grasp Rate** | 发生掉落的回合中，策略主动尝试并成功重新抓起方块的比例 |
| **Recovery Success** | 发生掉落后最终仍成功将方块放入杯子的比例 |
| **Completion Time** | 成功回合从启动到释放完成的平均耗时 |

---

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
