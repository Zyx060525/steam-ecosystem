# -*- coding: utf-8 -*-
"""生成多源数据关联图（数据血缘图）。"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data_lineage.png")

fig, ax = plt.subplots(figsize=(11, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
ax.axis("off")

# 节点布局 (x, y, 标签, 颜色)
nodes = {
    "center": (5, 3.5, "游戏实体\n(appid + 时间)", "#4c9aff"),
    "hw": (1.2, 5.8, "硬件调查\n(月度占比)", "#f9a900"),
    "online": (8.8, 5.8, "在线人数\n(分钟级)", "#4c9aff"),
    "review": (8.8, 1.2, "评论\n(好评率/时长)", "#51a8a6"),
    "meta": (1.2, 1.2, "游戏元数据\n(名称/类型/发行)", "#32CD32"),
    "news": (5, 6.6, "新闻/更新事件\n(时间+标签)", "#ff6b6b"),
}

for key, (x, y, label, color) in nodes.items():
    ax.add_patch(plt.Rectangle((x - 1.3, y - 0.55), 2.6, 1.1, color=color, alpha=0.9, zorder=2))
    ax.text(x, y, label, ha="center", va="center", fontsize=10, color="white", zorder=3, weight="bold")

# 边 + 关联维度标注
edges = [
    ("online", "center", "实体关联\n(appid)"),
    ("review", "center", "实体关联\n(appid)"),
    ("meta", "center", "实体关联\n(appid)"),
    ("news", "center", "实体+事件关联\n(appid+时间)"),
    ("hw", "center", "时间关联\n(月度)"),
    ("news", "online", "事件关联\n(更新→在线波动)"),
]

for src, dst, label in edges:
    x1, y1 = nodes[src][0], nodes[src][1]
    x2, y2 = nodes[dst][0], nodes[dst][1]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="gray", lw=1.5, zorder=1))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx + 0.15, my, label, fontsize=8, color="#333", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))

ax.set_title("多源数据关联图（数据血缘）", fontsize=15, weight="bold", pad=10)
fig.savefig(OUT, dpi=120, bbox_inches="tight")
plt.close(fig)
print(f"关联图已保存: {OUT}")
