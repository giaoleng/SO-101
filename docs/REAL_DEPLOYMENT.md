# SO-101 真机 SmolVLA 训练与评测

## 实验状态与任务定义

本项目已完成 SO-101 真机 Cube → Cup 实验。任务为根据固定语言指令抓取桌面方块并放入杯子：

<code>Pick up the cube and place it in the cup.</code>

本轮真机实验比较一个原始示教 Baseline 和四种固定策略示教数据训练得到的 SmolVLA 模型：

- Baseline
- Clean
- Randomized
- Recovery
- Color-varied

五组模型均已完成独立训练与统一真机评测。公开仓库不展示五组模型的具体真机成功率数值；统计应以实际数据集、训练权重、manifest 和评测日志为准。

## 硬件与安全前置条件

正式采集、部署或评测前，先完成 [SO-101 真机硬件部署指南](REAL_HARDWARE_SETUP.md) 中的机械臂标定、相机检查和硬件安全检查。

- Follower / Leader 使用各自对应的串口和标定文件。
- 核对 front / wrist 相机索引、图像尺寸、FPS 和训练时的 feature rename map。
- 核对关节限位、夹爪方向、工作空间、软件停止入口和实体急停。
- 设备标定 JSON、相机参数和真实设备标识保存在本机，不提交到公共仓库。
- <code>configs/real/so101.yaml</code> 默认 <code>robot.hardware_confirmed: false</code>。只有完成本机硬件检查后，才按实际设备配置启用真机。

软件 STOP 文件不能替代实体急停。首次运行和配置变更后，应先执行低风险检查并确认机械臂处于可控状态。

## 示教数据

四种固定策略各包含 50 条示教：

| 条件 | 数据组成 | 主要考察能力 |
|---|---|---|
| Clean | 固定位置的正常成功示教 | 基础抓取放置 |
| Randomized | T1–T10 位置变化示教 | 位置泛化 |
| Recovery | 包含主动释放、重新抓取的示教 | 掉落后的恢复能力 |
| Color-varied | 红、橙、黄、蓝、紫五种颜色示教 | 外观变化下的任务表现 |

数据包含双相机图像、六维 action/state 和任务指令。下载入口为 <code>scripts/real/download_reference_datasets.py</code>，默认将数据保存在本地 <code>data/</code> 忽略目录，并记录数据版本及校验信息。训练时须将数据集相机特征映射到模型使用的 camera1 / camera2 输入。

## 训练设置

正式对照包含 5 次独立训练运行，训练种子为 Seed 1000：

- 基础模型：同一 SmolVLA 预训练权重；
- 训练预算：10,000 steps；
- Batch size：32；
- Checkpoint 保存间隔：2,000 steps；
- 唯一变化因素：训练数据条件。

训练入口：<code>scripts/real/train_study.py</code>。每次训练生成 <code>study_manifest.json</code>，记录数据条件、Seed、训练预算、数据集信息及权重摘要，供评测入口核验。

示例（路径按本机环境替换）：

~~~bash
python scripts/real/train_study.py \
  --condition clean --seed 1000 \
  --dataset-root data/real_demonstrations/clean \
  --repo-id YOUR_DATASET_REPO_ID \
  --base-model /path/to/local/smolvla_base \
  --output outputs/train/real_clean_seed1000 \
  --execute
~~~

## 统一真机评测

五个模型均按相同的五类场景评测。每个模型包含 100 次正式计分和 5 次预热：

| 场景 | 正式计分 | 环境条件 |
|---|---:|---|
| ID | 40 | 红色方块 T6、标准光照 |
| New positions | 15 | E1–E5 未示教位置，每处 3 次 |
| Reduced lighting | 15 | T6、降低照明 |
| Different object | 15 | 未参与训练的绿色方块 |
| Distractors | 15 | T6、增加非目标物体 |
| **每个模型** | **100** | 另有 5 次预热 |
| **五个模型** | **500** | 另有 25 次预热 |

该评测协议已执行完成，共完成 500 次正式计分 Rollout 和 25 次不计分预热。

评测入口为 <code>scripts/real/evaluate_study.py</code>。每个场景由操作者按协议复位物体、检查安全状态并记录结果；动作下发或视频观感不能代替成功判定。评测入口使用训练时生成的 manifest 核对模型条件、Seed、训练预算和 checkpoint。

## 失败模式汇总

使用 <code>scripts/real/summarize_study.py</code> 汇总逐回合日志，按模型条件、Seed 和评测场景统计成功次数、成功率及 Wilson 95% 区间，并计算：

- No-Motion Rate
- Reach Rate
- Grasp Rate
- Drop Rate
- Re-grasp per Drop
- Recovery per Drop

未被实际标注的阶段指标保持为空，不自动推断成功或失败。当前运行器记录回合级推理延迟、控制步数、限幅次数及操作者标签；逐步关节轨迹、动作方向角和相机视频不属于自动评测日志字段。

## 复现实验命令

先检查评测计划：

~~~bash
python scripts/real/study_protocol.py --phase evaluate --cell in_distribution
~~~

执行某个模型的 ID 评测（示例路径需替换为对应模型的实际产物）：

~~~bash
python scripts/real/evaluate_study.py \
  --condition baseline --seed 1000 --cell in_distribution \
  --checkpoint outputs/train/real_baseline_seed1000/checkpoints/010000/pretrained_model \
  --training-manifest outputs/train/real_baseline_seed1000/study_manifest.json \
  --output outputs/real/eval_baseline_s1000_in_distribution.jsonl --execute
~~~

汇总所有评测日志：

~~~bash
python scripts/real/summarize_study.py outputs/real/eval_*.jsonl \
  --csv outputs/real/study_summary.csv --strict
~~~

以上命令用于说明已实现的训练和评测入口。实际执行需要准备本地数据、模型权重、设备标定和运行环境；不要将示例路径当作仓库内已提供的实验产物。
