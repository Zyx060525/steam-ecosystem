# -*- coding: utf-8 -*-
"""核心可视化：生成 5 张「问题式标题」的图，覆盖总体特征 / 跨源关系 / 时间分析 3 种视角。

每张图底部标注数据范围与来源。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# 中文字体支持
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "visualization")
os.makedirs(OUT, exist_ok=True)

SRC_NOTE = "Data: Steam Hardware Survey / Steamworks API / Kaggle Steam Reviews 2024"

online = pd.read_csv(os.path.join(BASE, "steam_online", "steam_online.csv"))
online["ts"] = pd.to_datetime(online["timestamp_local"])
online["hour"] = online["ts"].dt.hour

overview = pd.read_csv(os.path.join(BASE, "integrated", "games_overview.csv"))

shs = pd.read_csv(os.path.join(BASE, "steamHWsurvey", "shs.csv"))
shs["date"] = pd.to_datetime(shs["date"])

NEWS_DIR = os.path.join(BASE, "steam_news")
CORE = [730, 570, 1172470, 578080, 440, 271590, 252490, 1085660]

games_order = overview.sort_values("online_mean", ascending=False)["appid"].tolist()


def save(fig, name):
    fig.text(0.01, 0.01, SRC_NOTE, fontsize=8, color="gray", ha="left")
    fig.savefig(os.path.join(OUT, name), dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {name}")


# 图1 总体特征：在线时间序列
fig, axes = plt.subplots(4, 2, figsize=(16, 12))
for ax, appid in zip(axes.flat, games_order):
    g = online[online["appid"] == appid].sort_values("ts")
    ax.plot(g["ts"], g["player_count"], linewidth=0.7, color="#4c9aff")
    ax.set_title(g["game"].iloc[0], fontsize=10)
    ax.ticklabel_format(axis="y", style="plain")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H"))
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    ax.grid(alpha=0.3)
fig.suptitle("不同游戏的在线人数如何随时间波动？(09-17~09-19, 分钟级)", fontsize=14)
save(fig, "v1_online_timeseries.png")

# 图2 跨源关系：口碑 vs 在线
fig, ax = plt.subplots(figsize=(9, 6))
for _, r in overview.iterrows():
    ax.scatter(r["positive_rate"] * 100, r["online_mean"], s=300, alpha=0.7)
    ax.annotate(r["game_name"], (r["positive_rate"] * 100, r["online_mean"]),
                fontsize=8, xytext=(5, 5), textcoords="offset points")
ax.set_xlabel("好评率 (%)")
ax.set_ylabel("平均在线人数")
ax.set_title("游戏好评率能解释其在线人气吗？(Pearson r = -0.068, 基本无关)")
ax.grid(alpha=0.3)
save(fig, "v2_reputation_vs_online.png")

# 图3 跨源关系：事件冲击
fig, ax = plt.subplots(figsize=(10, 6))
impacts = []
for appid in CORE:
    f = os.path.join(NEWS_DIR, f"{appid}.json")
    if not os.path.exists(f):
        continue
    with open(f, encoding="utf-8") as fp:
        items = json.load(fp)
    g = online[online["appid"] == appid]
    for it in items:
        d = pd.to_datetime(it["date"], unit="s")
        if pd.Timestamp("2026-09-17") <= d <= pd.Timestamp("2026-09-20"):
            before = g[(g["ts"] >= d - pd.Timedelta(hours=3)) & (g["ts"] < d)]["player_count"].mean()
            after = g[(g["ts"] > d) & (g["ts"] <= d + pd.Timedelta(hours=3))]["player_count"].mean()
            if pd.notna(before) and pd.notna(after) and before > 0:
                impacts.append({"title": it["title"][:40], "pct": (after - before) / before * 100})
imp = pd.DataFrame(impacts).sort_values("pct")
colors = ["#4c9aff" if x >= 0 else "#ff6b6b" for x in imp["pct"]]
ax.barh(imp["title"], imp["pct"], color=colors)
ax.set_xlabel("事件前后 3 小时在线人数变化 (%)")
ax.set_title("更新/赛事事件后，游戏在线人数是否显著上升？")
ax.axvline(0, color="black", linewidth=0.8)
ax.grid(alpha=0.3, axis="x")
save(fig, "v3_event_impact.png")

# 图4 时间分析：硬件演变
fig, ax = plt.subplots(figsize=(11, 6))
ram = shs[shs["category"] == "System RAM"]
for name in ["4 GB", "8 GB", "16 GB", "32 GB or higher"]:
    s = ram[ram["name"] == name]
    if len(s):
        s = s.sort_values("date")
        ax.plot(s["date"], s["percentage"] * 100, label=name, linewidth=1.8)
ax.set_ylabel("玩家占比 (%)")
ax.set_title("玩家内存配置如何随新一代游戏发行而演进？(2008~2026 月度)")
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
save(fig, "v4_hardware_evolution.png")

# 图5 时间分析：日内规律
fig, ax = plt.subplots(figsize=(11, 6))
for appid in games_order:
    g = online[online["appid"] == appid]
    h = g.groupby("hour")["player_count"].mean()
    h_norm = (h - h.min()) / (h.max() - h.min())
    ax.plot(h_norm.index, h_norm.values, marker="o", linewidth=1.3, label=g["game"].iloc[0])
ax.set_xlabel("一天中的小时")
ax.set_ylabel("归一化在线人数")
ax.set_title("全球玩家上线高峰出现在哪些时段？(0-1 归一化)")
ax.set_xticks(range(0, 24))
ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1, 0.5))
ax.grid(alpha=0.3)
save(fig, "v5_hourly_rhythm.png")

print("\n全部 5 张核心可视化已生成到 visualization/ 目录")
