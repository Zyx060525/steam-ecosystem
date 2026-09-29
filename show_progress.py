# -*- coding: utf-8 -*-
"""进度可视化：一键查看 Steam 数据采集的当前进度。

包含两部分：
1. Kaggle 评论数据集下载进度（当前分卷 1.archive 已下/总量）
2. Steam 在线人数采集进度（CSV 行数 + 各游戏在线人数时间曲线）

用法：
    python show_progress.py            # 终端打印摘要 + 生成 show_progress.png
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")  # 无界面后端，直接存图
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))

# Kaggle 当前分卷（kagglehub 命名 1.archive，总 4.21 GB）
ARCHIVE = os.path.join(BASE, "steam_reviews", "1.archive")
ARCHIVE_TOTAL = 4.21 * 1024 ** 3  # 4.21 GB

# 爬虫 CSV
CRAWLER_CSV = os.path.join(BASE, "steam_online", "steam_online.csv")


def kaggle_progress():
    if os.path.exists(ARCHIVE):
        size = os.path.getsize(ARCHIVE)
        pct = size / ARCHIVE_TOTAL * 100
        return size, pct
    return 0, 0.0


def crawler_data():
    if not os.path.exists(CRAWLER_CSV):
        return None
    df = pd.read_csv(CRAWLER_CSV)
    df["ts"] = pd.to_datetime(df["timestamp_local"])
    return df


def draw(kaggle_size, kaggle_pct, df):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：Kaggle 下载进度条
    ax1.set_title("Kaggle Download Progress (1.archive)")
    ax1.barh([0], [kaggle_pct], color="#4c9aff", height=0.4)
    ax1.barh([0], [100], color="#e0e0e0", height=0.4, zorder=0)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(-0.5, 0.5)
    ax1.set_yticks([])
    ax1.set_xlabel("percent (%)")
    ax1.text(
        kaggle_pct, 0,
        f"  {kaggle_size/1024**3:.2f} GB / {ARCHIVE_TOTAL/1024**3:.2f} GB  ({kaggle_pct:.1f}%)",
        va="center", fontsize=11,
    )

    # 右图：各游戏在线人数时间曲线
    ax2.set_title("Steam Online Players Over Time")
    if df is not None and len(df) > 0:
        for game, grp in df.groupby("game"):
            grp = grp.sort_values("ts")
            ax2.plot(grp["ts"], grp["player_count"], label=game, linewidth=1.2)
        ax2.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.0, 0.5))
        ax2.set_xlabel("time")
        ax2.set_ylabel("players online")
        ax2.ticklabel_format(axis="y", style="plain")
        ax2.grid(alpha=0.3)
    else:
        ax2.text(0.5, 0.5, "no data yet", ha="center", va="center", transform=ax2.transAxes)

    fig.tight_layout()
    out = os.path.join(BASE, "show_progress.png")
    fig.savefig(out, dpi=110)
    plt.close(fig)
    return out


def main():
    ksize, kpct = kaggle_progress()
    df = crawler_data()

    # 终端摘要
    print("=" * 50)
    print("Kaggle 评论数据集下载：")
    bar = "█" * int(kpct // 5) + "░" * (20 - int(kpct // 5))
    print(f"  [{bar}] {kpct:.1f}%   ({ksize/1024**3:.2f} GB / {ARCHIVE_TOTAL/1024**3:.2f} GB)")
    print("Steam 在线人数采集：")
    if df is not None:
        print(f"  已采集 {len(df)} 行 | 时间跨度 {df['ts'].min()} ~ {df['ts'].max()}")
        latest = df.sort_values("ts").groupby("game").tail(1).sort_values("player_count", ascending=False)
        for _, r in latest.iterrows():
            print(f"    {r['game']:<22} {int(r['player_count']):>10,}")
    else:
        print("  尚无数据")
    print("=" * 50)

    png = draw(ksize, kpct, df)
    print(f"图表已保存: {png}")


if __name__ == "__main__":
    main()
