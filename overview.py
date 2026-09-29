# -*- coding: utf-8 -*-
"""三个 Steam 数据集的数据概览。"""
import glob
import os

import pandas as pd

BASE = r"d:\zyx百度备份dell宿舍\zyx百度网盘bak\08轩轩  参加的杂七杂八的活动\神秘大数据"


def hw_survey():
    print("=" * 62)
    print("① Steam 硬件调查 (steamHWsurvey)")
    print("=" * 62)
    shs = pd.read_csv(os.path.join(BASE, "steamHWsurvey", "shs.csv"))
    print(f"[shs.csv]  {shs.shape[0]:,} 行 × {shs.shape[1]} 列")
    print(f"字段: {list(shs.columns)}")
    print(f"时间范围: {shs['date'].min()} ~ {shs['date'].max()}")
    print(f"分类({shs['category'].nunique()}个): {shs['category'].unique().tolist()}")
    print(f"数据项(name)共 {shs['name'].nunique():,} 个")
    print("样例 3 行:")
    print(shs.head(3).to_string(index=False))

    shp = pd.read_csv(os.path.join(BASE, "steamHWsurvey", "shs_platform.csv"))
    print(f"\n[shs_platform.csv]  {shp.shape[0]:,} 行 × {shp.shape[1]} 列")
    print(f"字段: {list(shp.columns)}")
    print(f"时间范围: {shp['date'].min()} ~ {shp['date'].max()}")
    print(f"平台: {shp['platform'].unique().tolist()}")
    print(f"分类({shp['category'].nunique()}个): {shp['category'].unique().tolist()}")


def steam_online():
    print()
    print("=" * 62)
    print("② Steam 在线人数 (steam_online)")
    print("=" * 62)
    onl = pd.read_csv(os.path.join(BASE, "steam_online", "steam_online.csv"))
    onl["ts"] = pd.to_datetime(onl["timestamp_local"])
    print(f"[steam_online.csv]  {onl.shape[0]:,} 行 × {onl.shape[1]} 列")
    print(f"字段: {list(onl.columns)}")
    print(f"时间范围: {onl['ts'].min()} ~ {onl['ts'].max()}")
    print(f"游戏数: {onl['game'].nunique()} 个")
    latest = onl.sort_values("ts").groupby("game").tail(1).sort_values("player_count", ascending=False)
    print("各游戏最新在线人数:")
    for _, r in latest.iterrows():
        print(f"  {r['game']:<22} {int(r['player_count']):>10,}  ({r['ts']})")


def steam_reviews():
    print()
    print("=" * 62)
    print("③ Steam 评论数据集 (steam_reviews)")
    print("=" * 62)
    files = glob.glob(os.path.join(BASE, "steam_reviews", "SteamReviews2024", "*.csv"))
    total = sum(os.path.getsize(f) for f in files)
    sizes = sorted((os.path.getsize(f) for f in files), reverse=True)
    print(f"文件数: {len(files):,} 个游戏 CSV")
    print(f"总大小: {total/1e9:.2f} GB")
    print(f"最大文件: {sizes[0]/1e6:.0f} MB | 最小文件: {sizes[-1]/1e3:.2f} KB")
    # 按大小分桶
    import collections
    buckets = collections.Counter()
    for s in sizes:
        if s < 1e3:
            buckets["<1KB"] += 1
        elif s < 1e6:
            buckets["1KB~1MB"] += 1
        elif s < 100e6:
            buckets["1MB~100MB"] += 1
        else:
            buckets[">100MB"] += 1
    print("大小分布:", dict(buckets))
    sample = pd.read_csv(os.path.join(BASE, "steam_reviews", "SteamReviews2024", "10.csv"))
    print(f"\n样例 10.csv: {sample.shape[0]:,} 行 × {sample.shape[1]} 列")
    print(f"字段({len(sample.columns)}个): {list(sample.columns)}")
    print("样例 2 行:")
    print(sample.head(2).to_string(index=False))


if __name__ == "__main__":
    hw_survey()
    steam_online()
    steam_reviews()
