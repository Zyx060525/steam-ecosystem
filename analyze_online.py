# -*- coding: utf-8 -*-
"""Steam 在线人数数据分析（2 天分钟级数据）"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

BASE = r"d:\zyx百度备份dell宿舍\zyx百度网盘bak\08轩轩  参加的杂七杂八的活动\神秘大数据"

df = pd.read_csv(os.path.join(BASE, "steam_online", "steam_online.csv"))
df["ts"] = pd.to_datetime(df["timestamp_local"])
df["date"] = df["ts"].dt.date
df["hour"] = df["ts"].dt.hour

print("=" * 62)
print("一、基础概览")
print("=" * 62)
print(f"总行数: {len(df):,}")
print(f"时间范围: {df['ts'].min()} ~ {df['ts'].max()}")
print(f"采集天数: {df['date'].nunique()} 天 -> {[str(d) for d in sorted(df['date'].unique())]}")
print(f"游戏数: {df['game'].nunique()}")

print()
print("=" * 62)
print("二、各游戏在线人数统计（按峰值降序）")
print("=" * 62)
rows = []
for game, grp in df.groupby("game"):
    rows.append(
        {
            "游戏": game,
            "采样点": len(grp),
            "峰值": int(grp["player_count"].max()),
            "谷值": int(grp["player_count"].min()),
            "均值": int(grp["player_count"].mean()),
            "标准差": int(grp["player_count"].std()),
            "波动率": grp["player_count"].std() / grp["player_count"].mean(),
        }
    )
stats = pd.DataFrame(rows).sort_values("峰值", ascending=False)
for _, r in stats.iterrows():
    print(
        f"{r['游戏']:<22} 峰值 {r['峰值']:>9,}  谷值 {r['谷值']:>9,}  "
        f"均值 {r['均值']:>9,}  波动率 {r['波动率']:.3f}"
    )

print()
print("=" * 62)
print("三、峰值 / 谷值发生时刻")
print("=" * 62)
for game, grp in df.groupby("game"):
    p = grp.loc[grp["player_count"].idxmax()]
    l = grp.loc[grp["player_count"].idxmin()]
    print(f"{game:<22} 峰值 {int(p['player_count']):>9,} @ {str(p['ts'])}")
    print(f"{'':<22} 谷值 {int(l['player_count']):>9,} @ {str(l['ts'])}")

print()
print("=" * 62)
print("四、日内规律（各游戏在线高峰时段，按小时均值）")
print("=" * 62)
for game, grp in df.groupby("game"):
    hourly = grp.groupby("hour")["player_count"].mean()
    peak_h = hourly.idxmax()
    print(f"{game:<22} 高峰 {peak_h:02d}:00 时  (该时段均值 {int(hourly.max()):,})")

print()
print("=" * 62)
print("五、三天在线总量趋势（日均在线人数）")
print("=" * 62)
daily = df.groupby(["date", "game"])["player_count"].mean().unstack()
for d in sorted(df["date"].unique()):
    s = daily.loc[d].sum()
    print(f"{d}  8 游戏日均在线总和 {int(s):,}")

# ---------- 绘图 ----------
games = stats["游戏"].tolist()

# 图1：8 游戏完整时间序列
fig, axes = plt.subplots(4, 2, figsize=(16, 13))
for ax, game in zip(axes.flat, games):
    g = df[df["game"] == game].sort_values("ts")
    ax.plot(g["ts"], g["player_count"], linewidth=0.7, color="#4c9aff")
    ax.set_title(game, fontsize=11)
    ax.ticklabel_format(axis="y", style="plain")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    ax.grid(alpha=0.3)
fig.suptitle("Steam Online Players - 2 Day Trend (09-17 ~ 09-19)", fontsize=14)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "analysis_online_timeseries.png"), dpi=110)
plt.close(fig)

# 图2：日内规律（归一化）
fig, ax = plt.subplots(figsize=(12, 6))
for game in games:
    h = df[df["game"] == game].groupby("hour")["player_count"].mean()
    h_norm = (h - h.min()) / (h.max() - h.min())
    ax.plot(h_norm.index, h_norm.values, marker="o", linewidth=1.5, label=game)
ax.set_xlabel("Hour of day")
ax.set_ylabel("Normalized players online")
ax.set_title("Daily Attention Rhythm (0-1 normalized by game)")
ax.set_xticks(range(0, 24))
ax.legend(fontsize=9, loc="center left", bbox_to_anchor=(1.0, 0.5))
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "analysis_online_hourly.png"), dpi=110)
plt.close(fig)

print()
print("图表已保存: analysis_online_timeseries.png / analysis_online_hourly.png")
