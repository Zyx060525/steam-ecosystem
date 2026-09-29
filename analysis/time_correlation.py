# -*- coding: utf-8 -*-
"""时间关联分析：硬件配置月度演变 vs 游戏发行时间线。

关联维度: 时间关联（硬件月度数据 + 游戏发行时间点）
做法: 展示关键硬件(内存/分辨率)的历史占比演变，标记 8 个核心游戏的发行时间。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHS = os.path.join(BASE, "steamHWsurvey", "shs.csv")
META = os.path.join(BASE, "steam_metadata", "games_metadata.json")

df = pd.read_csv(SHS)
df["date"] = pd.to_datetime(df["date"])

with open(META, encoding="utf-8") as f:
    meta = json.load(f)

# 8 个核心游戏发行时间
releases = []
for appid, m in meta.items():
    rd = (m.get("release_date") or "").strip()
    releases.append((m.get("name"), rd))
print("游戏发行日期:")
for name, rd in releases:
    print(f"  {name:<22} {rd}")

# 选两个关键硬件维度
def top_share(category, top_n=5):
    """某类别下占比最高的 top_n 项（取最新月份）。"""
    sub = df[df["category"] == category]
    latest = sub[sub["date"] == sub["date"].max()]
    top = latest.nlargest(top_n, "percentage")["name"].tolist()
    return top


fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 图1: System RAM 演变
ax = axes[0]
ram = df[df["category"] == "System RAM"]
for name in top_share("System RAM", 4):
    s = ram[ram["name"] == name].sort_values("date")
    ax.plot(s["date"], s["percentage"] * 100, label=name, linewidth=1.5)
ax.set_title("System RAM share over time (monthly)")
ax.set_ylabel("share (%)")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# 图2: 分辨率演变
ax = axes[1]
res = df[df["category"] == "Primary Display Resolution"]
for name in top_share("Primary Display Resolution", 4):
    s = res[res["name"] == name].sort_values("date")
    ax.plot(s["date"], s["percentage"] * 100, label=name, linewidth=1.5)
ax.set_title("Primary display resolution share over time")
ax.set_ylabel("share (%)")
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

fig.suptitle("Hardware evolution (Steam Hardware Survey) vs game releases", fontsize=13)
fig.tight_layout()
out = os.path.join(BASE, "analysis_time_correlation.png")
fig.savefig(out, dpi=110)
plt.close(fig)

# 关键时间点对比：8 游戏发行年份的硬件水平
print("\n各游戏发行年份时的硬件水平:")
for appid, m in meta.items():
    name = m.get("name")
    rd = (m.get("release_date") or "").strip()
    # 解析年份
    try:
        year = int(rd.split(",")[-1].strip())
    except Exception:
        continue
    # 该年份 12 月的硬件分布
    snap = df[(df["date"].dt.year == year) & (df["category"] == "System RAM")]
    if len(snap):
        snap = snap[snap["date"] == snap["date"].max()]
        top_ram = snap.nlargest(1, "percentage")
        print(f"  {name:<22} {year} 年发行，当时主流内存: {top_ram['name'].iloc[0]} ({top_ram['percentage'].iloc[0]*100:.1f}%)")

print(f"\n图表已保存: {out}")
