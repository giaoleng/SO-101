# 外部参考素材与来源

此目录仅用于独立开源项目的参考图表，不属于 SO-101 项目的实验产物；图表与本项目成功率表格无对应关系。

- `act_mujoco_loss_reference.png`：原图来自 [rocPAI-Forge/so101-simstudio](https://github.com/rocPAI-Forge/so101-simstudio/blob/main/labs/lab01_pnp/loss_curve_act_mi300x_50k.png)。该仓库的原始作品采用 Apache License 2.0，原图为 ACT 50K steps 训练 Loss（MI300X），未修改图片内容。源项目包含 NOTICE 与 THIRD_PARTY_NOTICES，复用时应保留其版权与许可说明。
- README 中直接引用的 `act_single_cube_success.gif` 与 `smolvla_20k_pink_then_cyan.gif` 来自 [IptiharPolat/so101-robot-learning](https://github.com/IptiharPolat/so101-robot-learning/blob/main/media/README.md)，Apache License 2.0。GIF 分别为 ACT 单方块与 SmolVLA 双方块真机示例，均经过演示加速，SmolVLA 示例还裁去了开头停顿。它们**不是本项目的仿真或真机 Rollout**，故不进入本项目的结果统计。

开源项目的参考图像、视频及其报道的模型性能不可直接写作本项目的实测结果；如需按 Apache-2.0 再分发修改版素材，应保留版权、许可证与修改声明。

## README 首页真机失败模式演示（2026-11-17）

原首页 ACT / SmolVLA 成功 GIF 的展示已撤下（仍保留本文件上述历史来源记录）；现首页仅使用以下来自 [Andresg324/so101-vla-data-study](https://github.com/Andresg324/so101-vla-data-study) 的第三方失败参考 GIF，图片通过原项目 raw 地址展示，未复制二进制文件到本仓库。

| 素材 | 原项目的具体场景 | 阅读时的边界 |
|---|---|---|
| [clip2_offset_2in.gif](https://github.com/Andresg324/so101-vla-data-study/blob/main/media/clip2_offset_2in.gif) | Clean 策略，方块移动约 2 英寸，机械臂未能到达并抓取 | 位置变化下的 Reach Failure（第三方） |
| [clip3_no_motion.gif](https://github.com/Andresg324/so101-vla-data-study/blob/main/media/clip3_no_motion.gif) | Randomized seed 2000，机械臂在初始位姿附近抖动 | 无有效动作的 Motion Failure（第三方） |
| [clip4_drop_no_recovery.gif](https://github.com/Andresg324/so101-vla-data-study/blob/main/media/clip4_drop_no_recovery.gif) | Recovery seed 2000，两次中途释放且未恢复 | Drop / Recovery Failure（第三方） |

**许可：** 原项目 [MIT License](https://github.com/Andresg324/so101-vla-data-study/blob/main/LICENSE)，Copyright (c) 2026 Andres Garcia；使用原始 GIF 网络地址展示，来源、作者与许可证均保留。第三方录像与本项目实测成功率、Checkpoint、机器人场景和训练数据没有验证过对应关系。
