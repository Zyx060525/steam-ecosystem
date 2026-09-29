# Steam 游戏生态的多维画像

> 大数据原理与应用 · 课程中期大作业
> 多源多维度数据采集、融合分析与可视化

围绕「Steam 游戏生态」这一真实问题，从 5 个相互独立的数据源观察与验证，通过实体（appid）、时间、事件三种关联维度将多源数据融合，完成跨源分析。

## 核心研究问题

| # | 研究问题 | 依赖数据源 | 关联方式 |
|---|---------|-----------|---------|
| Q1 | 游戏好评率能否解释其在线人气？ | 评论 + 在线 | 实体关联（appid） |
| Q2 | 玩家硬件配置是否随新一代游戏发行而协同演进？ | 硬件 + 元数据 | 时间关联 |
| Q3 | 一次更新/赛事对游戏在线人数能产生多大冲击？ | 新闻事件 + 在线 | 事件关联 + 时间 |

## 数据源（5 个独立源，详见 data_sources.md）

1. Steam 硬件调查（官方统计，月度，2008~2026）
2. Steam 在线人数（公开 API 自采，分钟级）
3. Steam 评论（Kaggle 数据集，1.28 亿条）
4. 游戏元数据（Steam API，实体映射）
5. 新闻/更新事件（Steam API，事件文本）

## 目录结构

```
├── steamHWsurvey/          # 源1 硬件调查（原始）
├── steam_online/           # 源2 在线人数（爬虫 + 数据）
├── steam_reviews/          # 源3 评论（原始，抽样到 8 核心游戏）
├── steam_metadata/         # 源4 游戏元数据
├── steam_news/             # 源5 新闻事件
├── integrated/             # 跨源融合后的核心数据（games_overview.csv）
├── crawler/                # 数据采集代码
├── processing/             # 清洗、融合、对齐
├── analysis/               # 分析与数据挖掘
├── visualization/          # 可视化代码与结果（5 张核心图）
├── data_sources.md         # 数据源清单
├── AI_USAGE.md             # AI 使用记录
└── README.md
```

## 复现步骤

### 1. 采集数据

```bash
# 在线人数（8 个核心游戏，每 60 秒）
python steam_online/steam_online_crawler.py --interval 60

# 在线人数（Top100 游戏，每 300 秒）
python steam_online/steam_online_crawler.py --games-file top100_games.json --interval 300 --out steam_online_top100.csv

# 游戏元数据 + 新闻事件
python crawler/collect_metadata_news.py
```

### 2. 清洗

```bash
python clean_online.py        # 剔除在线人数 0 值异常
```

### 3. 融合（跨源关联）

```bash
python processing/integrate.py   # 生成 integrated/games_overview.csv
```

### 4. 分析

```bash
python analysis/event_correlation.py     # Q3 事件关联
python analysis/time_correlation.py      # Q2 时间关联
python analysis/core_questions.py        # Q1 口碑 vs 人气 + 聚类
```

### 5. 可视化

```bash
python visualization/core_visualizations.py   # 生成 5 张核心图
```

## 主要结论

1. **口碑与在线人气几乎无关**（Pearson r = -0.068）：PUBG 好评率最低（58.2%）但在线人数第三高，说明免费制、电竞生态、社交网络等因素比口碑更能决定人气。
2. **硬件配置与游戏发行协同演进**：内存主流从 8GB（2013-2018）切换到 16GB（2019-2020），与新一批大型游戏发行时间吻合。
3. **更新/赛事显著拉动在线**：PUBG 电竞赛事带来 +60% 以上的在线增长；但需剔除「日周期」混淆，不能把凌晨的自然下降误读为事件负效应。

## 数据规模与局限

- 评论为「大规模」主体（8 核心游戏 1.83GB / 全量 13.25GB）
- 在线人数为「行为数据」，规模受采集周期限制，已扩展至 Top100 持续采集
- 硬件/元数据/新闻为「辅助源」（官方统计/映射/事件，天然规模小）
- 核心研究对象为 8 个游戏，样本量较小，统计结论（如相关性）仅供参考
