# -*- coding: utf-8 -*-
"""生成 GitHub 上传准备材料：样本数据 + checksum + 文件清单。"""
import hashlib
import os

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE, "data", "sample")
os.makedirs(SAMPLE_DIR, exist_ok=True)

CORE = [730, 570, 1172470, 578080, 440, 271590, 252490, 1085660]
REVIEWS_DIR = os.path.join(BASE, "steam_reviews", "SteamReviews2024")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# 1. 评论样本（8 游戏各取前 200 行）
print("生成评论样本...")
frames = []
for appid in CORE:
    f = os.path.join(REVIEWS_DIR, f"{appid}.csv")
    if os.path.exists(f):
        chunk = pd.read_csv(f, nrows=200)
        chunk.insert(0, "appid", appid)
        frames.append(chunk)
sample = pd.concat(frames, ignore_index=True)
sample_out = os.path.join(SAMPLE_DIR, "reviews_sample.csv")
sample.to_csv(sample_out, index=False, encoding="utf-8-sig")
print(f"  样本: {sample_out}（{len(sample)} 行）")

# 在线样本（前 500 行）
online = pd.read_csv(os.path.join(BASE, "steam_online", "steam_online.csv"), nrows=500)
online_out = os.path.join(SAMPLE_DIR, "online_sample.csv")
online.to_csv(online_out, index=False, encoding="utf-8-sig")
print(f"  样本: {online_out}（{len(online)} 行）")

# 2. checksum（对关键数据文件）
print("\n计算 checksum...")
checks = [
    os.path.join(BASE, "steamHWsurvey", "shs.csv"),
    os.path.join(BASE, "steamHWsurvey", "shs_platform.csv"),
    os.path.join(BASE, "steam_online", "steam_online.csv"),
]
checks += [os.path.join(REVIEWS_DIR, f"{a}.csv") for a in CORE]

lines = ["# 数据文件 SHA256 校验值（完整数据不上传，此清单用于验证可重建数据）"]
for f in checks:
    if os.path.exists(f):
        rel = os.path.relpath(f, BASE)
        h = sha256(f)
        size = os.path.getsize(f)
        lines.append(f"{h}  {size:>14,}  {rel}")
        print(f"  {rel}  {size/1e6:.1f}MB  {h[:16]}...")

checksum_out = os.path.join(BASE, "checksums.txt")
with open(checksum_out, "w", encoding="utf-8") as fp:
    fp.write("\n".join(lines) + "\n")
print(f"checksum 已保存: {checksum_out}")

# 3. 文件清单
manifest = """# 仓库文件清单（GitHub 上传清单）

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
"""
manifest_out = os.path.join(BASE, "UPLOAD_MANIFEST.md")
with open(manifest_out, "w", encoding="utf-8") as fp:
    fp.write(manifest)
print(f"文件清单已保存: {manifest_out}")
print("\n全部 GitHub 准备材料生成完毕。")
