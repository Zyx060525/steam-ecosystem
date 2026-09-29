# -*- coding: utf-8 -*-
"""事件关联分析：Steam 更新事件（新闻） vs 在线人数波动。

关联维度: 事件关联（appid + 时间）
做法: 找出在线采集时段(09-17~09-19)内的更新公告，对比事件前后在线人数变化。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_DIR = os.path.join(BASE, "steam_news")
ONLINE = os.path.join(BASE, "steam_online", "steam_online.csv")

CORE = [730, 570, 1172470, 578080, 440, 271590, 252490, 1085660]

# 在线数据时间范围
START = pd.Timestamp("2026-09-17 00:00:00")
END = pd.Timestamp("2026-09-19 23:59:59")

df = pd.read_csv(ONLINE)
df["ts"] = pd.to_datetime(df["timestamp_local"])

print("=" * 66)
print("落在在线采集时段(09-17~09-19)内的更新事件")
print("=" * 66)

events = []
for appid in CORE:
    f = os.path.join(NEWS_DIR, f"{appid}.json")
    if not os.path.exists(f):
        continue
    with open(f, encoding="utf-8") as fp:
        items = json.load(fp)
    for it in items:
        d = pd.to_datetime(it["date"], unit="s")
        if START <= d <= END:
            events.append(
                {
                    "appid": appid,
                    "game": df[df["appid"] == appid]["game"].iloc[0],
                    "title": it["title"],
                    "date": d,
                    "tags": ",".join(it.get("tags") or []),
                }
            )

if not events:
    print("  在线采集时段内无新闻事件")
else:
    ev = pd.DataFrame(events).sort_values("date")
    for _, r in ev.iterrows():
        print(f"  {r['game']:<22} {r['date']}  {r['title']}  [{r['tags']}]")

    print()
    print("=" * 66)
    print("事件前后在线人数对比（事件时刻 ±3 小时均值）")
    print("=" * 66)
    for _, e in ev.iterrows():
        g = df[df["appid"] == e["appid"]].sort_values("ts")
        before = g[(g["ts"] >= e["date"] - pd.Timedelta(hours=3)) & (g["ts"] < e["date"])]
        after = g[(g["ts"] > e["date"]) & (g["ts"] <= e["date"] + pd.Timedelta(hours=3))]
        if len(before) > 0 and len(after) > 0:
            b = before["player_count"].mean()
            a = after["player_count"].mean()
            delta = (a - b) / b * 100
            print(
                f"  {e['game']:<22} {e['date'].strftime('%m-%d %H:%M')}  "
                f"前3h均值 {int(b):>9,} -> 后3h均值 {int(a):>9,}  ({delta:+.1f}%)  | {e['title']}"
            )

# 可视化：每个游戏在线曲线 + 事件标记
fig, axes = plt.subplots(4, 2, figsize=(16, 13))
for ax, appid in zip(axes.flat, CORE):
    g = df[df["appid"] == appid].sort_values("ts")
    ax.plot(g["ts"], g["player_count"], linewidth=0.7, color="#4c9aff")
    name = g["game"].iloc[0] if len(g) else appid
    ax.set_title(name, fontsize=11)
    ax.ticklabel_format(axis="y", style="plain")
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    # 标记事件
    for _, e in ev[ev["appid"] == appid].iterrows():
        ax.axvline(e["date"], color="red", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.grid(alpha=0.3)
fig.suptitle("Online players with update events marked (red dashed lines)", fontsize=14)
fig.tight_layout()
out = os.path.join(BASE, "analysis_event_correlation.png")
fig.savefig(out, dpi=110)
plt.close(fig)
print(f"\n图表已保存: {out}")
