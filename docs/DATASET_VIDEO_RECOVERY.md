# 真实 MP4 与闭环验证：网络恢复后的最短步骤

2026-11-17 再次尝试，尚未安装 mink、尚未下载/提取视频、尚未完成完整闭环。不要把下面的命令当作已执行成功的结果。

## 当前诊断

- Python 3.12，现有 lerobot 环境含 MuJoCo 3.8.1、huggingface_hub 1.33.0、pyarrow 25.0.1；缺少 mink、qpsolvers。
- Dockerfile.runtime / INSTALL_RUNTIME_NO_DOCKER.md 使用 pip 安装 mink；控制器指定 QP solver 为 daqp，所以还需要该求解器可用。
- 尝试安装到工作区/临时 target，避免写入原 conda 环境；包括显式 PyPI 地址的重试均未获得包。pip 的 “No matching distribution” 在这里不能作为版本不兼容证据。
- HTTP_PROXY / HTTPS_PROXY / ALL_PROXY 及小写变量均指向 127.0.0.1:12450；curl 通过代理连接失败，绕过代理后 huggingface.co 域名解析失败。Python 直接创建 socket 报 PermissionError: Operation not permitted，说明本会话的网络执行权限也限制了下载，不能只修改代理解决。
- 默认 Hugging Face 缓存约 144 KB，未找到此数据集；磁盘约 1.2 TB 可用，容量不是阻塞原因。
- 完整闭环脚本再次在导入控制器时因缺 mink 退出，零个完整 Episode，不能报告成功率。

## 安装依赖（有网络的普通终端）

在工作区创建隔离环境，复用已有大依赖，不升级原 conda 环境。先确认终端网络可用；仅在本地代理确实未运行时，为当前终端取消错误代理：

```bash
cd /home/giao/.local/share/chatgpt-cli/new/workspace/so101-review-main
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
/home/giao/anaconda3/envs/lerobot/bin/python -m venv --system-site-packages /tmp/so101-video-runtime
/tmp/so101-video-runtime/bin/python -c 'import mujoco; print("mujoco==" + mujoco.__version__)' > /tmp/so101-mujoco-constraint.txt
/tmp/so101-video-runtime/bin/python -m pip install -c /tmp/so101-mujoco-constraint.txt mink daqp
/tmp/so101-video-runtime/bin/python -c 'import mink, qpsolvers; assert "daqp" in qpsolvers.available_solvers; print("IK dependencies OK")'
```

这里锁定当前 MuJoCo 版本，若依赖求解报版本冲突应停止并查看约束，不自动改已验证运行环境。官方安装说明：https://kevinzakka.github.io/mink/installation.html 。

原有录制入口 `scripts/demo/record_scripted_demo.py` 拒绝覆盖历史视频；不要直接删除历史录像来绕过保护。完整无界面闭环可重跑本会话准备的 `/tmp/so101_closed_loop.py`（脚本依赖源工作区并仅禁用 viewer 初始化）：

```bash
PYTHONPATH="$PWD" /tmp/so101-video-runtime/bin/python /tmp/so101_closed_loop.py
```

该脚本计划运行种子 42、7、123，每个最多 25000 个外层物理步，沿用原演示入口的 40 Hz 控制与连续 6 次成功门控；实际模拟总时长还包含 env.step 的推进。临时 JSON 与日志输出 `/tmp/so101-closed-loop.json`、`/tmp/so101-closed-loop.log`。需要检查阶段序列、抬起历史、最终位置与成功门控；它是脚本专家验证，不能当作 ACT/DP/SmolVLA 成功率。

## 最简单的手动下载方法

1. 用可联网浏览器打开 https://huggingface.co/datasets/rovolabs/so-arm101-pick-place/tree/main ，记录当前仓库完整 revision。所有下载固定到同一 revision；不借用其他仓库视频。
2. 只先下载 `meta/info.json` 与 `meta/episodes/chunk-000/file-000.parquet`（若该 revision 的目录不同，以 Files 页为准）。保留目录结构，放到工作区外的缓存目录，例如 `/tmp/so101-source/`。
3. 查看 Episode 元数据。根据其 `data/chunk_index`、`data/file_index` 下载少量对应帧数据 parquet；从帧数据检查 `annotation.action_source` 与 `episode_success`。选择 source=2 且 success=true/false 的 Episode 各一个。不要凭视频观感或编号范围推断标签。
4. 按已选 Episode 的 `videos/observation.images.front/*` 元数据，下载对应 front MP4（可选 overhead/wrist，但 manifest 必须注明）。v3 视频文件可能包含多个 Episode，不能直接把整段文件当作单个 Episode。
5. 用相应 `from_timestamp` / `to_timestamp` 裁切，只导出选定时间段。示例（变量必须先填入实际元数据，不是示例 Episode 编号）：

```bash
ffmpeg -ss "$START" -i "$SOURCE_MP4" -t "$DURATION" \
  -an -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$OUTPUT_MP4"
```

这保持 MP4 容器，重新编码用于准确边界裁切，避免 `-c copy` 在关键帧处混入相邻 Episode；不转 GIF。若源文件只包含完整单个 Episode，可直接复制原始 MP4。

输出名称：

- `media/dataset_examples/smolvla_success.mp4`
- `media/dataset_examples/smolvla_failure.mp4`

6. 更新 `source_manifest.json`：填写真实 episode_index、episode_success、action_source=2、控制器 ACTION_SMOLVLA、固定 revision、源视频路径、摄像头、起止时间、源数据集与署名（Rovo Labs，CC BY 4.0）。只在实际导出并验证后改状态为 generated。
7. 检查两个文件：

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of json media/dataset_examples/smolvla_success.mp4
ffmpeg -v error -i media/dataset_examples/smolvla_success.mp4 -f null -
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of json media/dataset_examples/smolvla_failure.mp4
ffmpeg -v error -i media/dataset_examples/smolvla_failure.mp4 -f null -
```

还需用浏览器/播放器观看，确认首尾画面属于同一 Episode。外部数据集为筛选后的正负集合，不能从两段视频或样本比例报告本项目模型成功率。

## README 播放

本次没有真实视频，所以不添加可点击的虚假文件链接。生成后可使用仓库相对 MP4 链接供下载。GitHub README 的相对 MP4 链接不保证内嵌播放；要播放请把两个真实 MP4 分别拖到 GitHub issue/PR 的编辑框，上传完成后复制真实 `https://github.com/user-attachments/assets/...` 链接到演示章节，附来源、Episode、状态与许可。不要编造附件 URL，也不要把草稿发布当作本会话已授权发送行为。
