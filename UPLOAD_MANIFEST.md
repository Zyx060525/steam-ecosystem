# 仓库文件清单（GitHub 上传清单）

## 上传（代码 + 文档 + 样本 + 校验）
- README.md                项目说明与复现步骤
- data_sources.md          数据源清单与 provenance
- AI_USAGE.md              AI 使用记录与反思
- checksums.txt            数据文件 SHA256 校验值
- data/sample/             代表性样本（评论 1600 行 + 在线 500 行）
- crawler/                 数据采集代码
- processing/              清洗与融合代码
- analysis/                分析代码
- visualization/           可视化代码
- steam_metadata/          游戏元数据（小，可上传）
- steam_news/              新闻事件（小，可上传）

## 不上传（完整数据，可由脚本重建）
- steam_reviews/SteamReviews2024/   评论全量（13.25GB，Kaggle 可重新下载）
- steamHWsurvey/shs*.csv            硬件调查（GitHub jdegene/steamHWsurvey 可重新下载）
- steam_online/*.csv                在线人数（可由 crawler 重新采集）

## 数据重建方式
1. 评论：kagglehub.dataset_download("artermiloff/steam-games-reviews-2024") 或 curl 下载
2. 硬件：git clone https://github.com/jdegene/steamHWsurvey.git
3. 在线：python steam_online/steam_online_crawler.py --interval 60
4. 元数据/新闻：python crawler/collect_metadata_news.py
