






# SO-101 Policy Benchmark & Real-World SmolVLA Diagnostics

项目包含两个实验场景：

- **MuJoCo Simulation**：在 SO-101 仿真环境中比较 ACT、Diffusion Policy 和 SmolVLA，完成红色方块抓取放置任务。
- **Real Robot Manipulation**：围绕真实 SO-101 的 Cube → Cup 任务，研究不同示教数据采集策略对 SmolVLA 泛化和失败行为的影响（实验代码已配置，当前新任务结果待实测）。

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

https://github.com/user-attachments/assets/9fa9a44b-a124-4daa-95e9-cd610ffb2621

**行为表现**：Clean 策略在训练分布内完成接近、夹取、搬运与释放。该视频作为对照基准，便于比较下方失败案例发生在哪个操作阶段。

#### ❌ Reach Failure：目标偏移后接近不足



https://github.com/user-attachments/assets/bbaef4dc-106d-4fae-a9b8-1aff7b190b3d



**失败现象**：方块相对训练位置向机械臂方向偏移约 2 英寸（5.08 cm），机械臂仍沿近似固定的方向伸出，最终在方块前方闭合夹爪，未完成抓取。

**诊断分析**：参考项目的轨迹统计显示，目标需要的接近角度约为 29.4°，而机械臂实际达到的角度不足。这更接近**策略未充分调整接近动作**的问题，不能仅从抓空现象推断为夹爪闭合故障。可通过目标位置与实际关节轨迹进一步区分目标定位、运动规划及夹爪执行失效。

#### ❌ No Motion：策略未有效离开初始位姿



https://github.com/user-attachments/assets/ed2eac7b-f7ce-4398-b8cd-6ba9fa5d1600



**失败现象**：位置随机化示教训练的策略面对绿色方块时，机械臂在初始姿态附近小幅抖动，始终没有形成有效接近动作。

**诊断分析**：这是 **Initiation Failure（动作启动失败）**，与“已接近目标但抓取失败”不同。应结合关节位移幅度、动作启动延迟与控制指令判断是否真正产生有效运动；仅凭该视频不能确定停滞源于模型预测、动作后处理还是硬件控制。

#### ❌ Recovery Failure：掉落后未完成恢复


https://github.com/user-attachments/assets/54a7244c-4357-44bf-8dc6-48e12bf8f12b



**失败现象**：使用恢复示教训练的策略在搬运过程中释放方块，但没有完成重新定位、再次抓取和最终入杯，任务超时。

**诊断分析**：模型可能学到了示教中的**释放动作**，却没有稳定学到释放之后的**闭环恢复序列**。因此需要分别记录掉落事件、是否尝试重抓、重抓是否成功以及最终任务是否完成，不能只统计完整任务成功率。

#### ✅ Re-grasp：少量成功重抓案例
https://github.com/user-attachments/assets/55915c62-7fe4-46f4-ad79-bfd149a8a380

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

本项目围绕 **SO-101 机械臂** 的抓取放置（Pick-and-Place）操作，包含**仿真基准对比**与**真机 SmolVLA 数据采集策略对照研究**两条实验路线；当前新真机研究协议已经补充，尚未上传其独立实测结果。

- **MuJoCo 仿真实验**：基于开源 LeRobot 数据集，在统一的 SO-101 物理仿真环境中独立完成了 **ACT**、**Diffusion Policy** 与 **SmolVLA** 三种模仿学习策略的训练、超参对齐与分布内/分布外（ID / OOD）闭环评测。
- **SO-101 真机实验**：以 **SmolVLA** 为固定模型，规划 Clean、Randomized、Recovery、Color-varied 四种示教策略的对照实验，提供遥操作采集、微调、人工监督安全评测和离线汇总入口；真实训练/评测成绩待验证。

### 1.1 仿真与真机实验对比

| 维度 | MuJoCo 仿真实验 | SO-101 真机实验 |
| :--- | :--- | :--- |
| **机器人平台** | SO-101（5 旋转关节 + 1 夹爪，MJCF 物理模型） | SO-101 实体机械臂 + 夹爪 + 双路 640×480@30fps 相机 |
| **任务目标** | 抓取**红色方块**放入**蓝色收纳盒**（含多色干扰方块） | 抓取桌面**方块**放入**杯子**（`Cube → Cup`） |
| **数据来源** | **直接采用开源 LeRobotDataset**（经本地格式校验与统计归一化） | 计划通过人工遥操作采集、按条件隔离的专家示范 |
| **对比策略** | **ACT** vs. **Diffusion Policy** vs. **SmolVLA** | **SmolVLA**（相同模型架构在不同示教策略下的行为诊断） |
| **语言指令** | 固定仿真任务描述 | `Pick up the cube and place it in the cup.` |
| **核心研究问题** | 三类主流模仿学习架构在 ID 与 OOD 位置泛化下的性能边界 | 不同示教数据策略对成功率、位置泛化、动作启动和掉落恢复的影响 |

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
4 组专家示教 (Clean / Randomized / Recovery / Color) × 每组 50 条
        │
        ▼
相同 SmolVLA 基础模型 × 相同训练预算 × 2 个训练种子
        │
        ▼
5 类真机测试场景 × 每格 15 条计分回合（另有 1 条预热）
        │
        ▼
Task Success + Reach / No Motion / Grasp / Drop / Recovery 诊断统计
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

## 5. 真机平台与示教数据策略研究

> **状态与参考**：本节将 Cube → Cup 真机实验重新组织为**待运行的、可复现的研究方案与离线/真机运行代码**。仓库当前未提供这套新任务的实机训练数据、Checkpoint 或评测日志，**本项目自己的真机成功率尚未实测**；上方真机视频来自 [Andresg324/so101-vla-data-study](https://github.com/Andresg324/so101-vla-data-study)，不是本项目实测。实验设计借鉴原项目的 [PROTOCOL.md](https://github.com/Andresg324/so101-vla-data-study/blob/main/PROTOCOL.md) 和 [SETUP.md](https://github.com/Andresg324/so101-vla-data-study/blob/main/SETUP.md)；第 6.3 节**单独引用其真实成功率**供对照，不能将引用结果当成本项目的实测结果。此方案属于**不同示教数据分布下的离线模仿学习对照实验**，不是 DAgger。


### 5.0 参考项目数据集与代码集成

参考来源：[Andresg324/so101-vla-data-study](https://github.com/Andresg324/so101-vla-data-study)，固定到上游提交 `175d3d057aa91ff785168400a24cc1410c140dbc`。**本项目只采用四组正式示教条件；Density（探索性实验）不纳入本项目，也不下载其数据或配置。**

#### 四组参考数据集

| 数据条件 | Hugging Face 数据集 | 回合数 | 用途 |
|---|---|---:|---|
| Clean | [cube-pickup-clean_20260809_105745](https://huggingface.co/datasets/Andresg324/cube-pickup-clean_20260809_105745) | 50 | 固定位置成功示教 |
| Randomized | [cube-pickup-randomized_20260809_115825](https://huggingface.co/datasets/Andresg324/cube-pickup-randomized_20260809_115825) | 50 | 10 个训练位置轮换 |
| Recovery | [cube-pickup-recovery_20260809_141725](https://huggingface.co/datasets/Andresg324/cube-pickup-recovery_20260809_141725) | 50 | 包含主动掉落与重抓示教 |
| Color-varied | [cube-pickup-color_20260809_183224](https://huggingface.co/datasets/Andresg324/cube-pickup-color_20260809_183224) | 50 | 五色示教；绿色留作测试 |

Color-varied 只使用上述正式保留版本；不使用后来被替换的 `cube-pickup-color_20260809_130649`。数据集名称及保留状态以原项目 [RUN_SHEET.md](https://github.com/Andresg324/so101-vla-data-study/blob/main/RUN_SHEET.md) 为准。

#### 下载数据集

新增下载入口会从 Hugging Face 下载四个 LeRobot 数据集的 `meta/`、`data/` 和 `videos/` 文件，校验每组 50 条示教、30 FPS、六维 action/state 和 overhead/wrist 双相机特征，并记录下载时解析到的 Hub commit SHA。

```bash
# 先查看下载计划（不下载）
python scripts/real/download_reference_datasets.py --dry-run

# 下载全部四组正式数据
python scripts/real/download_reference_datasets.py

# 也可以只下载指定条件
python scripts/real/download_reference_datasets.py --condition clean recovery
```

默认下载到 `data/reference/so101-vla-data-study/{clean,randomized,recovery,color}/`，并生成 `download_manifest.json`。数据文件包含视频，体积较大；**二进制数据保留在本地，不提交到 GitHub**（仓库的 `.gitignore` 已忽略 `data/`）。在运行环境安装依赖：`python -m pip install -U huggingface_hub`。公开数据集可直接下载，无需将数据文件复制进 Git 仓库。

#### 已复制的参考代码

已将选定代码放入 `third_party/so101-vla-data-study/`，并保留上游 MIT License：

| 文件 | 处理方式 |
|---|---|
| `scripts/record_dataset.sh` | 从原项目移植；仅保留 Clean、Randomized、Recovery、Color 四组，改为要求显式提供本机串口/相机编号 |
| `scripts/run_inference.sh` | 从原项目移植；仅保留四组策略和五类正式测试场景，默认 CUDA、本地保存，不自动上传 Hub |
| `configs/train_config_{clean,randomized,recovery,color}.json` | 原项目 Seed 1000 配置，原样复制 |
| `configs/train_config_{clean,randomized,recovery,color}-seed2000.json` | 原项目 Seed 2000 配置，原样复制 |
| `LICENSE` | 原项目 MIT 许可证 |

其中两份 Shell 脚本已针对 Ubuntu 和本项目实验范围做适配，不是未经修改的原文件。原始代码仍可在[上游仓库](https://github.com/Andresg324/so101-vla-data-study)查阅。复制的配置属于原项目训练快照，使用前需核对 LeRobot 版本、相机特征、路径和 W&B 设置；本项目日常运行仍优先使用 `scripts/real/` 下的适配入口。

**按你的要求，没有复制图表/结果生成代码**：不包含 `analysis/analyze_results.py`、`analysis/make_figures.py`、`tools/motion_stats.py`、`analysis/`、`probing/`、图表文件或历史结果输出；Density 数据集与 Density 配置也全部排除。

**相机特征兼容性**：参考数据集使用 `observation.images.overhead` 和 `observation.images.wrist`，训练时映射到策略的 `camera1`、`camera2`。本项目训练入口需要显式传入对应 `--rename-map`；真机推理时，当前配置中的 `front` 相机将作为 overhead 视角映射到 `camera1`，`wrist` 映射到 `camera2`。

### 5.1 统一任务与控制变量

- **真机任务**：SO-101 抓取桌面方块并放入固定杯子；统一指令 <code>Pick up the cube and place it in the cup.</code>。
- **固定条件**：同一机器人、相机与安装角度、固定复位位姿、杯子位置、训练初始权重、训练步数及评分标准。
- **双路相机**：前/全局与腕部相机（目标配置 640×480、30 FPS）。必须核对实际设备名称与训练权重的 <code>rename_map</code>，不能直接套用参考仓库的 macOS 相机索引。
- **空间标记**：在本机安全工作区标记 T1–T10（训练位置）及 E1–E5（从未示教的评测位置）；T6 为固定基准位置。编号只代表实验位置，**参考项目的桌面坐标不可直接用于另一台机器人**。
- **安全**：检查标定、关节限位、停止入口、实体急停、障碍物和夹爪极性；现有 <code>configs/real/so101.yaml</code> 默认 <code>robot.hardware_confirmed: false</code>，不会自动启用真机。

### 5.2 四组数据采集条件（训练集）

采用**相同 SmolVLA 基础模型、每组 50 条专家示教**，只改变专家示教数据的采集方式：

| 训练组 | 50 条示教的组成 | 研究的问题 |
|---|---|---|
| **Clean** | 红色方块固定 T6；50 条正常成功示教 | 基础性能与固定位置泛化边界 |
| **Randomized** | 红色方块在 T1–T10 各采集 5 条 | 位置覆盖范围与每个位置示教密度的权衡 |
| **Recovery** | 红色方块固定 T6；其中 20 条包含主动释放、重抓并完成入杯 | 仅增加恢复示教，能否获得可靠恢复能力 |
| **Color-varied** | 固定 T6；红、橙、黄、蓝、紫各 10 条；绿色留作评测 | 示教颜色多样性是否改善未见颜色表现 |

**重要区分**：<code>clean / randomized / recovery / color</code> 是**训练数据条件**；<code>no_motion / reach / recovery</code> 是评测时观察到的**失败行为**，不是独立的数据集 Split。所有训练数据都应隔离存储。Recovery 的主动释放也不等于真实意外掉落，必须单独解释。

采集前先查看每条示教对应的位置、颜色及是否需要主动释放的计划：

~~~bash
python scripts/real/study_protocol.py --phase collect --condition randomized
python scripts/real/study_protocol.py --phase collect --condition recovery
~~~

参考项目使用 LeRobot 主从遥操作接口。本仓库的采集入口**默认实际执行**（下方仍显式写出 `--execute`，便于直接使用）；如只想检查 50 条采集计划，改用 `--dry-run`。运行前必须核对实际端口、相机、标定、急停与工作区：

~~~bash
python scripts/real/record_study.py \
  --condition clean --repo-id local/real_cube_clean \
  --dataset-root data/real_cube_clean \
  --follower-port /dev/ttyACM0 --leader-port /dev/ttyACM1 \
  --front-idx 0 --wrist-idx 1 \
  --plan-output outputs/real/plans/clean.json --execute
~~~

工具不会自动移动物体或切换灯光；每条示教开始前操作者必须按计划人工布置，并核对录制结果。<code>lerobot-record</code> 的具体 CLI 及 LeRobot 版本须在真机环境验证。

---

<a id="real-train-eval"></a>

## 6. 真机 SmolVLA 训练、评测与数据质量诊断

### 6.1 固定训练预算与模型对照

每组数据训练两个种子（1000、2000），共 4 × 2 = **8 个独立训练运行**。使用相同基础模型和统一预算（10,000 steps、batch size 32、每 2,000 steps 保存 checkpoint），仅改变示教数据集与种子；请评估最终步数的 checkpoint，不按验证集结果为某一组挑选最优版本。

~~~bash
python scripts/real/train_study.py \
  --condition clean --seed 1000 \
  --dataset-root data/reference/so101-vla-data-study/clean \
  --repo-id Andresg324/cube-pickup-clean_20260809_105745 \
  --base-model /path/to/local/smolvla_base \
  --output outputs/train/real_clean_seed1000 \
  --rename-map '{"observation.images.overhead":"observation.images.camera1","observation.images.wrist":"observation.images.camera2"}' --execute
~~~

训练入口默认实际运行（可用 `--dry-run` 仅输出命令），并检查 LeRobotDataset 中的回合数及六维真机关节特征；运行后在对应训练输出目录生成 <code>study_manifest.json</code>，用于关联训练条件、种子及评测日志。全部数据与权重保持本地，不默认上传 Hub。现有 <code>scripts/train/finetune_smolvla.sh</code> 仍用于仿真/通用 SmolVLA 训练；研究协议以新的 <code>train_study.py</code> 为准。

### 6.2 五类统一评测场景

四组模型各自在同样的五类场景下测试，**每个场景 16 个回合：第 0 回合预热不计分，后续 15 回合正式计分**。

| 评测场景 | 物理环境设置 | 主要测量 |
|---|---|---|
| <code>in_distribution</code> | 红色方块 T6、标准光照 | 基础任务成功率 |
| <code>new_positions</code> | 红色方块 E1–E5，每个位置各 3 次 | 位置泛化与 Reach Failure |
| <code>reduced_lighting</code> | 红色方块 T6、降低照明 | 光照鲁棒性 |
| <code>different_object</code> | 未参与训练的绿色方块 T6 | 颜色/外观泛化；No Motion 只是可能的失败现象 |
| <code>distractors</code> | 红色方块 T6、增加非目标物体 | 抗干扰能力 |

评测入口默认实际运行（可用 `--dry-run` 仅输出计划）；仍需要操作者逐回合复位场景、确认目标及安全状态，并在结束后人工填写 <code>success</code> 和可观察到的阶段标签（<code>started</code>、<code>reached</code>、<code>grasped</code>、<code>dropped</code>、<code>regrasped</code> 等）。**不能以动作已下发或视频看起来正常代替成功判定。**

~~~bash
python scripts/real/study_protocol.py --phase evaluate --cell new_positions
python scripts/real/evaluate_study.py \
  --condition clean --seed 1000 --cell new_positions \
  --checkpoint outputs/train/real_clean_seed1000/checkpoints/010000/pretrained_model \
  --training-manifest outputs/train/real_clean_seed1000/study_manifest.json \
  --output outputs/real/eval_clean_s1000_new_positions.jsonl --execute
~~~

原有的 <code>scripts/real/deploy_policy.py</code> 和 <code>scripts/real/evaluate_policy.py</code> 仍可用于单次安全部署和探索性排查；**正式四条件对照**使用 <code>evaluate_study.py</code>，不能将探索性与注册评测混在同一统计分母里。

### 6.3 结果统计：不仅比较 Loss，还要比较执行行为

~~~bash
python scripts/real/summarize_study.py outputs/real/eval_*.jsonl \
  --csv outputs/real/study_summary.csv
# 所有 4×2×5 条件/种子/场景均完整且每格有 15 条正式回合时，追加 --strict
~~~

汇总按**训练组 × 训练种子 × 评测场景**输出成功次数、成功率和 Wilson 95% 区间，并为每个训练种子追加一行 <code>all_cells</code> 整体成功率；不把两个训练种子的结果直接混成单个结论。预热和中断回合不计入分母。

行为诊断同时包含 **No-Motion Rate、Reach Rate、Grasp Rate、Drop Rate、Re-grasp per Drop、Recovery per Drop**。若尚未完整标注某阶段，指标显示为空，不自动假设失败或成功。当前运行器保存每回合推理延迟、控制步数、限幅次数及操作者标签；**逐步关节轨迹、动作方向角和相机视频并未自动保存**，不能据此声称已经复现参考项目的运动轨迹图。

#### 参考项目实测结果（引用，不是本项目的评测结果）

下面数据**原样按成功回合数**整理自 [Andresg324/so101-vla-data-study — Table 1](https://github.com/Andresg324/so101-vla-data-study/blob/main/figures/table1.md)。每个训练条件在每个种子的五类场景中各计分 15 回合（共 75 回合/种子）；第 0 回合预热不计分。表中的成功率为 **Task Success Rate**，并非单独的 Reach、No Motion 或 Recovery 指标。

| 训练数据策略 | Seed | 标准场景 | 新位置 | 低光照 | 绿色方块 | 干扰物 | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Clean** | 1000 | 15/15 | 0/15 | 12/15 | 15/15 | 13/15 | **55/75 (73.3%)** |
| **Clean** | 2000 | 15/15 | 0/15 | 9/15 | 12/15 | 10/15 | **46/75 (61.3%)** |
| **Randomized** | 1000 | 6/15 | 0/15 | 5/15 | 0/15 | 1/15 | **12/75 (16.0%)** |
| **Randomized** | 2000 | 6/15 | 0/15 | 5/15 | 2/15 | 0/15 | **13/75 (17.3%)** |
| **Recovery** | 1000 | 8/15 | 0/15 | 7/15 | 11/15 | 13/15 | **39/75 (52.0%)** |
| **Recovery** | 2000 | 9/15 | 0/15 | 5/15 | 5/15 | 12/15 | **31/75 (41.3%)** |
| **Color-varied** | 1000 | 13/15 | 0/15 | 12/15 | 15/15 | 13/15 | **53/75 (70.7%)** |
| **Color-varied** | 2000 | 12/15 | 0/15 | 14/15 | 15/15 | 15/15 | **56/75 (74.7%)** |

只做描述性汇总（两种子共 150 回合/条件）时：Clean **101/150（67.3%）**、Randomized **25/150（16.7%）**、Recovery **70/150（46.7%）**、Color-varied **109/150（72.7%）**。**这不是“改进前 → 改进后”的实验，也不能证明所有数据增强都会提升性能。** 原项目的两种子分析与统计检验应以其原文为准。

**本仓库实测结果**：目前仍缺少在本项目设备上完成的 Cube → Cup 训练、Rollout 及标签数据，因此无法生成属于本项目的成功率。上面这张表只用于展示与对照参考项目的结果；后续可用 `scripts/real/summarize_study.py` 从本项目真实 JSONL 日志生成独立结果。

**仿真与真机的比较边界**：仿真 SmolVLA 完成“红方块→蓝盒子”，真机是“方块→杯子”，任务、接触动力学及评分环境不同；可以在项目内并列展示，但不可直接把两者的百分比差异解释为严格的 Sim-to-Real Gap。参考项目的重要结论是“示教多样性不一定提高整体成功率”，本项目会以独立数据验证，而不是预设 Randomized 或 Recovery 优于 Clean。

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
