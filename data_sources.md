# 数据源清单（Data Sources）

> 项目主题：Steam 游戏生态的多维画像
> 数据源数量：5 个独立数据源，覆盖「官方统计 + 行为数据 + 事件文本 + 实体映射」4 类形态

## 总览

| # | 数据源 | 类型 | 获取方式 | 规模 | 时间范围 | 采集时间 | 关联字段 | 许可 |
|---|--------|------|---------|------|---------|---------|---------|------|
| 1 | Steam 硬件调查 | 官方统计（月度） | 下载现成数据集 | 31 MB | 2008-11 ~ 2026-08 | 2026-09 | `date`（时间） | MIT |
| 2 | Steam 在线人数 | 公开 API（分钟级行为数据） | 自写爬虫轮询 | 1.3 MB（持续扩采 Top100） | 2026-09-17 ~ 09-19 | 2026-09-17~19 | `appid` + `timestamp` | 公开 API |
| 3 | Steam 评论 | 现成开放数据（文本） | 下载数据集 | 8 游戏 1.83GB / 全量 13.25GB | 至 2024 | 2026-09 | `appid`（文件名）+ `timestamp_created` | MIT |
| 4 | 游戏元数据 | 官方 API（实体映射） | 自写脚本 | 辅助源（KB 级） | 2026-09 | 2026-09 | `appid` | 公开 API |
| 5 | 新闻/更新事件 | 官方 API（事件文本） | 自写脚本 | 辅助源（KB 级） | 2024-07 ~ 2026-09 | 2026-09 | `appid` + `date` | 公开 API |

## 各数据源详情

### 1. Steam 硬件调查
- **来源**：GitHub `jdegene/steamHWsurvey`（底层为 Steam 官方 `hwsurvey` 页面 + web.archive 历史存档）
- **获取方式**：下载 GitHub 仓库（ZIP）
- **文件**：`shs.csv`（67,569 行）、`shs_platform.csv`（306,621 行）
- **主要字段**：`date, category, name, change, percentage`（分平台表多 `platform`）
- **含义**：Steam 玩家硬件分布（显卡/CPU/内存/分辨率/系统等 32 类，月度占比）
- **关联方式**：时间关联（月度日期）

### 2. Steam 在线人数
- **来源**：Steamworks API `ISteamUserStats/GetNumberOfCurrentPlayers/v1`（无需 key）
- **获取方式**：自写 Python 爬虫（`steam_online/steam_online_crawler.py`），每 60 秒轮询，重试 + 限速
- **文件**：`steam_online.csv`（20,377 行清洗后）、`steam_online_raw.csv`（原始含异常）、`steam_online_top100.csv`（Top100 扩采中）
- **主要字段**：`timestamp_utc, timestamp_local, appid, game, player_count`
- **含义**：各游戏分钟级同时在线人数
- **关联方式**：实体关联（appid）+ 时间关联（分钟级时间戳）
- **数据质量**：已剔除 123 行 API 异常返回的 `player_count=0`（集中在 09-19 凌晨 00:27~03:06）

### 3. Steam 评论
- **来源**：Kaggle `artermiloff/steam-games-reviews-2024`（底层为 Steam API `Get List`）
- **获取方式**：kagglehub / curl 下载（4.21GB 压缩包，解压 13.25GB）
- **文件**：`SteamReviews2024/{appid}.csv`（79,994 个游戏，本项目取 8 个核心游戏共 1.83GB）
- **主要字段**：`recommendationid, language, timestamp_created, voted_up, votes_up, weighted_vote_score, comment_count, steam_purchase, received_for_free, author_playtime_forever, author_playtime_at_review` 等 21 字段
- **含义**：128M 条游戏评论（好评率、点赞、游玩时长、语言）
- **关联方式**：实体关联（appid，文件名即 appid）+ 时间关联（`timestamp_created` Unix 时间戳）

### 4. 游戏元数据
- **来源**：Steam Store API `appdetails`（无需 key）
- **获取方式**：自写脚本（`crawler/collect_metadata_news.py`）
- **文件**：`steam_metadata/games_metadata.json`
- **主要字段**：`appid, name, type, genres, categories, release_date, developers, publishers, is_free, price`
- **含义**：游戏实体属性（作为实体映射表，把 appid 映射到游戏名称/类型/发行日期）
- **关联方式**：实体关联（appid）

### 5. 新闻/更新事件
- **来源**：Steamworks API `ISteamNews/GetNewsForApp/v2`（无需 key）
- **获取方式**：自写脚本（`crawler/collect_metadata_news.py`）
- **文件**：`steam_news/{appid}.json`（每游戏 100 条）
- **主要字段**：`gid, appid, title, date(Unix), tags, feedlabel, contents`
- **含义**：游戏更新公告/赛事/活动事件（如 `patchnotes` 标签 = 补丁更新）
- **关联方式**：实体关联（appid）+ 时间关联（`date`）+ 事件关联（更新事件 vs 在线波动）

## 跨源关联方式总结

| 关联维度 | 关联的数据源 | 说明 |
|---------|------------|------|
| **实体关联（appid）** | 在线 + 评论 + 元数据 + 新闻 | 通过 Steam appid 统一映射（评论文件名、在线 appid、元数据/新闻 appid） |
| **时间关联** | 硬件（月度）+ 在线（分钟）+ 新闻（时间戳） | 统一时间格式，按需聚合到日/月 |
| **事件关联** | 新闻事件 + 在线人数 | 更新/赛事事件的时间点 → 在线人数波动分析 |
