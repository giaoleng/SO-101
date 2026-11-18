# 红方块 → 蓝盒子：审查记录

## 首轮历史记录：基于 f6346d4（保留原始阻塞情况）

- 原项目：`/home/giao/图片/桌面/Projects/LeRobot-MuJoCo-SO101-own`，初始工作区干净。
- 原项目 HEAD 和本地缓存 origin/main 均为 `f6346d415e82fb42152643fae3a6c88293505329`；缓存比较无差异。
- 原目录在本会话为只读。原目录 fetch 因不能写 FETCH_HEAD 失败。
- 可写副本：`/home/giao/.local/share/chatgpt-cli/new/workspace/so101-task`。
- 副本 fetch 被失效本地代理阻断；禁用代理后 DNS 解析失败；网页通道也无法取得 GitHub commits。
- 因而没有核验用户提到的远端 `c53800d...`，不能宣称远端已整合。没有 merge、commit、push、强推或修改原目录。
- 本次代码基于 f6346d4，应用前必须在可联网环境 fetch、比较 HEAD...origin/main，并人工审查远端重叠修改。不要直接覆盖最新远端文件。

## 实现

- 实际运行的 scene_so101_y.xml 包含 obj_blocks.xml / obj_bin.xml。
- 选择现有红方块 body_obj_block_1；蓝方块仍为干扰物；未改辅助标记、坐标轴或夹爪颜色。
- 给盒底和四壁命名并改为蓝色，碰撞、尺寸、质量保持原物理设置。
- 采集、部署、演示、数据可视化默认目标统一；默认英文指令为 `Pick up the red cube and place it in the blue box.`。
- SimpleEnv 默认按机器人类型选择正确目标，保留 OMY 旧默认。
- 成功判定从编译后的碰撞几何读取内边界、盒底和盒沿；方块旋转后的完整轮廓须在盒内。
- 保留抬起历史、盒接触、夹爪打开/撤离且不再接触方块等条件。2 mm 接触容差另加模型 margin，用于求解器接触误差。
- 原代码盒沿 76 mm 与实际 30.5 mm 不符，现已消除这组硬编码。
- 默认生成中心间距由 10 mm 改为 40 mm，狭窄生成区 X 上界从 0.22 扩为 0.27 m；保持盒外、可达区域。
- ACT / Diffusion / SmolVLA 训练入口保留；未训练、未声称旧权重兼容，README 说明相机键与动作顺序差异。

## 验证

使用 `/home/giao/anaconda3/envs/lerobot/bin/python`，MuJoCo 3.8.1。

- `python -m unittest discover -s tests -v`：8 项通过。
- 包含真实场景加载、目标/盒颜色、旋转方块角越界、盒外/悬空/穿底排除、释放/接触/抬起历史/撤离门控。
- 500 步 MuJoCo 物理模拟确认方块落在盒底并发生盒接触。
- 禁用 viewer 初始化的 SimpleEnv 无界面 smoke test：seed 0–9 reset 均通过，目标为红方块、生成间距 >= 40 mm、初始不成功。
- 三种训练 shell 入口 dry-run 均通过；未访问 GPU、模型或数据。
- `git diff --check` 通过。
- 未进行完整抓取闭环、渲染、模型训练或模型成功率评测；这些仍需新任务实际验证。

## 视频未完成

- 默认 Hugging Face 缓存仅约 144 KB，未发现目标数据集；可用磁盘约 1.2 TB。
- 网络受阻，未下载数据集或视频，没有生成两个 MP4，也未伪造链接、Episode 编号或成功/失败标签。
- `media/dataset_examples/source_manifest.json` 明确为 pending，空值不是已验证记录。
- 来源数据集卡确认 action_source=2 是 ACTION_SMOLVLA，episode_success 为评测标签；须选择真实正负样本、补齐编号/revision/视频时间范围后输出 MP4。
- 外部数据集示例不得作为本项目模型评测视频，也不得从平衡的筛选样本计算自然成功率。
- 来源：https://huggingface.co/datasets/rovolabs/so-arm101-pick-place （Rovo Labs，CC BY 4.0）。

## 审查

在副本目录运行 `git diff`，新增文件同时直接阅读。完整补丁位于副本外的 `so101-red-cube-blue-box.patch`。
用户审查 diff 后再决定提交；本次不自动提交或推送。


## 2026-11-17 审核修订：基于最新本地远端引用

- 本次已独立读取本地 `origin/main`，确认其为 c53800d；用户此前已成功 fetch。上面的代理/DNS 失败是首轮历史记录，不代表本次远端引用仍停留在 f6346d4。本次未通过网络刷新远端引用。
- 从 c53800d 创建 `review/red-cube-blue-box`，工作区为 `/home/giao/.local/share/chatgpt-cli/new/workspace/so101-review-main`。
- 对 `/home/giao/so101-full-review.patch` 执行 `git apply --3way`；README 两处冲突已逐处协调。保留远端新增的第三方参考来源、单组真机实验、评测/部署内容，没有恢复旧版 README。5 个新增文件全部合入。
- 修复仿真实验表：红方块是目标，Blue / Yellow / Green 是干扰物。真机章节保留远端“收纳盒”描述。
- 新任务采集 YAML、Python 默认、部署 YAML、Python ACT 训练入口统一使用 `data/red_cube_blue_box` 与 `local/so101_red_cube_blue_box`；Python ACT 权重默认 `checkpoints/act_red_cube_blue_box`。旧目录、标识、权重不迁移、不重标、不删除；README 保留历史来源说明。shell 训练实际输出权重由部署参数显式指定。
- 远端新加的 `scripts/eval/eval_mujoco.py` 也同步红方块指令/目标及采样区间，保留原有动作契约和模型预处理检查。
- task_geometry 仅支持当前命名盒底/四壁与单 Box 目标的 SO100/SO101 场景，非通用检测器；OMY 继续走原分支。其他场景缺失命名几何或目标结构不符会明确报错，不降级为接触即成功。
- 当前测试：`/home/giao/anaconda3/envs/lerobot/bin/python -m unittest discover -s tests`，41 项全部通过，含远端原有评测/真机接口测试以及新增任务默认配置一致性测试。
- 尝试完整脚本专家闭环（计划 seed 42/7/123，50 秒模拟时长，连续 6 次成功门控）；导入控制器即报 `ModuleNotFoundError: mink`，未执行任何完整闭环 Episode，因此没有闭环成功率，也没有学习策略成功率。未安装新依赖或改写控制器来绕过阻塞。
- 视频访问重试：本地代理 127.0.0.1:12450 不可用，绕过代理后 huggingface.co DNS 解析失败；两个 MP4 仍未生成，manifest 空编号/版本/源视频/时间段保持 pending，不添加虚假链接。
- 不新增或转换 GIF；README 的第三方历史 GIF 是 c53800d 的既有内容，与待提取的外部 rovolabs MP4 分节保留。
- 未提交、未推送。补丁应用会暂存部分改动，最终统一暂存仅方便审查；请分别检查 `git diff HEAD` 和新增文件后再决定后续操作。


## 本轮继续执行记录

再次检查项目 pip 依赖声明并尝试隔离安装 mink/daqp，未获得包；再次启动完整闭环仍在 mink 导入处失败。明确诊断到网络 socket PermissionError、失效代理与 DNS 失败，视频仍未下载。详见 DATASET_VIDEO_RECOVERY.md 的诊断与手动操作。既有功能代码未修改，未提交或推送。
