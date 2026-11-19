# SO-101 MuJoCo：ACT / Diffusion Policy / SmolVLA 对比

## 实验状态

ACT、Diffusion Policy 和 SmolVLA 的训练与 MuJoCo 闭环评测均已完成。三种策略在同一 SO-101 仿真任务下进行比较：

- **任务：** 抓取红色目标方块并放入蓝色收纳盒。
- **ID：** 目标方块在训练分布覆盖的工作空间范围内随机生成。
- **OOD：** 目标方块位于训练数据未覆盖、但机械臂可达的空间位置。
- **成功判定：** 正确抓取目标方块、稳定抬起，并最终放入蓝色收纳盒。

## 实验结果

| 指标 | ACT | Diffusion Policy | SmolVLA |
|---|---:|---:|---:|
| Success Rate | **89%** | 80% | 95% |
| OOD Success Rate | **72%** | 62% | 83% |

以上为本项目确认采用的最终仿真实验结果。其他未列出的时间、失败阶段或推理延迟指标不在此处补写推测值。

## 策略与训练方式

| 策略 | 核心方法 | 初始化方式 |
|---|---|---|
| ACT | Transformer + Action Chunking | 随机初始化 |
| Diffusion Policy | 条件扩散策略 | 随机初始化 |
| SmolVLA | 视觉-语言-动作策略 | 基于预训练权重微调 |

三种策略使用统一的任务定义、数据集与闭环评测环境。SmolVLA 使用预训练权重微调，ACT 和 Diffusion Policy 从头训练；比较结果时应保留这一训练初始化差异，不将性能差异简单归因于网络架构本身。

## 统一训练入口

~~~bash
# ACT
python scripts/train/train_act.py

# Diffusion Policy
bash scripts/train/train_diffusion.sh

# SmolVLA
bash scripts/train/finetune_smolvla.sh
~~~

训练数据、Checkpoint 与完整运行日志按本地实验环境管理，不提交到公共仓库。复现时应使用实际实验采用的数据版本、LeRobot 版本、相机特征映射和训练配置。

## 统一闭环评测

三种策略通过 <code>scripts/eval/eval_mujoco.py</code> 接入同一仿真环境和 Episode 调度，逐回合结果由 <code>scripts/eval/summarize_rollouts.py</code> 汇总。

~~~bash
python scripts/eval/eval_mujoco.py --policy act \
  --checkpoint /path/to/act/pretrained_model \
  --dataset-root /path/to/so101_sim \
  --dry-run

python -m unittest discover -s tests -p test_unified_eval.py -v
~~~

正式评测需按模型选择对应 checkpoint、动作语义、图像特征键和数据集路径。示例中的路径为占位符，不代表仓库内含有模型权重或实验数据。

## 结果解释边界

仿真任务为红色方块放入蓝色收纳盒；真机任务为 Cube → Cup。两者任务对象、相机成像、接触条件和控制链路不同，因此本表只用于仿真策略比较，不作为真机成功率或 Sim-to-Real 同任务性能的替代指标。
