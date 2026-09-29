# -*- coding: utf-8 -*-
"""核心研究问题分析 + 数据挖掘（相关性 + 聚类）。

问题1（评论 + 在线，实体关联）: 游戏口碑(好评率)能否解释其在线人气？
问题2（硬件 + 元数据，时间关联）: 见 time_correlation.py
问题3（新闻 + 在线，事件关联）: 见 event_correlation.py

数据挖掘: 对 8 个核心游戏按多维指标做 KMeans 聚类。
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE, "integrated", "games_overview.csv"))

print("=" * 66)
print("问题1：游戏口碑(好评率)能否解释在线人气？")
print("=" * 66)
for _, r in df.iterrows():
    print(f"  {r['game_name']:<24} 好评率 {r['positive_rate']*100:5.1f}%  在线均值 {r['online_mean']:>9,}")

corr = df["positive_rate"].corr(df["online_mean"])
peak_corr = df["positive_rate"].corr(df["online_peak"])
print(f"\n好评率 vs 在线均值  Pearson r = {corr:.3f}")
print(f"好评率 vs 在线峰值  Pearson r = {peak_corr:.3f}")
print("结论: 相关性很弱，说明口碑不是在线人气的唯一决定因素（PUBG 口碑最差但在线第三高）。")

# 散点图
fig, ax = plt.subplots(figsize=(9, 6))
for _, r in df.iterrows():
    ax.scatter(r["positive_rate"] * 100, r["online_mean"], s=200, alpha=0.7)
    ax.annotate(r["game_name"], (r["positive_rate"] * 100, r["online_mean"]),
                fontsize=8, xytext=(5, 5), textcoords="offset points")
ax.set_xlabel("positive review rate (%)")
ax.set_ylabel("mean players online")
ax.set_title("Q1: Does review reputation explain online popularity?")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "analysis_q1_reputation_vs_online.png"), dpi=110)
plt.close(fig)

# 相关性矩阵（多指标）
print()
print("=" * 66)
print("多维指标相关性矩阵")
print("=" * 66)
cols = ["positive_rate", "online_mean", "online_peak", "review_count",
        "avg_playtime_at_review_min", "news_count", "online_volatility"]
m = df[cols].corr()
print(m.round(3).to_string())

# 聚类
print()
print("=" * 66)
print("KMeans 聚类（8 游戏，多维指标）")
print("=" * 66)
feat_cols = ["positive_rate", "online_mean", "review_count", "avg_playtime_at_review_min"]
X = df[feat_cols].copy()
X = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=3, random_state=42, n_init=10)
df["cluster"] = km.fit_predict(X)
for c in sorted(df["cluster"].unique()):
    members = df[df["cluster"] == c]
    print(f"\n  聚类 {c}: {', '.join(members['game_name'].tolist())}")
    print(f"    好评率均值 {members['positive_rate'].mean()*100:.1f}% | 在线均值 {int(members['online_mean'].mean()):,} | 平均评论 {int(members['review_count'].mean()):,}")

print("\n图表已保存: analysis_q1_reputation_vs_online.png")
