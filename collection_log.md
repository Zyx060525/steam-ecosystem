# 采集日志（Collection Log）

> 记录 5 个数据源的采集时间、方式、规模与异常处理，保证数据可追溯。

## 1. Steam 硬件调查

- **采集时间**：2026-09-17
- **方式**：下载 GitHub 仓库 `jdegene/steamHWsurvey`（ZIP 压缩包，因 git clone 多次中断改走 ZIP）
- **规模**：`shs.csv`（4.1MB）+ `shs_platform.csv`（27MB）
- **结果**：成功，数据完整
- **异常**：git clone 过程中终端多次中断，导致工作区文件未检出；改用 ZIP 下载一次性成功

## 2. Steam 在线人数

### 2.1 核心 8 游戏版（已完成）
- **采集时间**：2026-09-17 18:12 首次手动采集；18:39 启动循环爬虫（每 60 秒一轮）；09-19 21:28 停止
- **方式**：自写 Python 爬虫轮询 Steamworks API `GetNumberOfCurrentPlayers`（无需 key）
- **规模**：20,501 行（8 游戏 × 约 2560 轮），清洗后 20,377 行
- **异常处理**：
  - 发现 123 行 `player_count=0` 异常（集中在 09-19 凌晨 00:27~03:06，Steam API 异常返回），已剔除并备份原始数据
  - 采集期间 `api.steampowered.com` 偶发 SSL 握手超时，爬虫带 3 次重试机制

### 2.2 Top 100 游戏版（进行中）
- **采集时间**：2026-09-29 19:50 启动，持续采集中
- **方式**：同一爬虫，`--games-file top100_games.json --interval 300`（每 5 分钟一轮，100 游戏）
- **规模**：持续增长（启动 1 小时约 2,435 行）
- **说明**：因 100 游戏一轮需约 1 分钟，间隔调为 5 分钟

## 3. Steam 评论

- **采集时间**：2026-09-17
- **方式**：Kaggle 数据集 `artermiloff/steam-games-reviews-2024`
- **规模**：压缩包 4.21GB，解压 13.25GB（79,994 个游戏 CSV）；本项目取 8 个核心游戏共约 1.9GB
- **异常处理（重要）**：
  - 首次用 `kagglehub.dataset_download` 下载，因系统内存不足（7.7GB 内存被 VS Code 等占满）反复 `MemoryError` 崩溃
  - 改用 `curl -C -` 断点续传，内存占用 1MB、速度提升 10 倍，成功下载 4.21GB
  - 用 `tar` 解压（79,994 文件），无错误

## 4. 游戏元数据

- **采集时间**：2026-09-29
- **方式**：自写脚本调用 Steam Store API `appdetails`
- **规模**：8 个核心游戏 + Top 100 游戏名称
- **异常**：批量采集时 `store.steampowered.com` 响应较慢，个别游戏名称获取失败（用 `appid_xxx` 占位，已知核心游戏已手动补名）

## 5. 新闻/更新事件

- **采集时间**：2026-09-29
- **方式**：自写脚本调用 Steamworks API `ISteamNews/GetNewsForApp/v2`
- **规模**：8 游戏 × 100 条 = 799 条
- **异常**：`api.steampowered.com` 偶发连接失败，通过 curl `--retry` 与脚本重试解决
