# -*- coding: utf-8 -*-
"""下载 Kaggle 数据集 steam-games-reviews-2024 到项目文件夹。

数据量约 14.2 GB，按游戏拆分为 SteamReviews2024/{appid}.csv。
下载时间取决于网速（本机实测约 2 MB/s，预计 2 小时左右）。
"""
import os
import time

import kagglehub

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "steam_reviews")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"[start] {time.strftime('%Y-%m-%d %H:%M:%S')} output_dir={OUTPUT_DIR}", flush=True)

path = kagglehub.dataset_download(
    "artermiloff/steam-games-reviews-2024",
    output_dir=OUTPUT_DIR,
)

print(f"[done] {time.strftime('%Y-%m-%d %H:%M:%S')} path={path}", flush=True)
print("DOWNLOAD_COMPLETE", flush=True)
