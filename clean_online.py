# -*- coding: utf-8 -*-
"""清洗 steam_online.csv：剔除 player_count 为 0 / 负数 / 空值的异常行。"""
import os
import shutil

import pandas as pd

BASE = r"d:\zyx百度备份dell宿舍\zyx百度网盘bak\08轩轩  参加的杂七杂八的活动\神秘大数据"
CSV = os.path.join(BASE, "steam_online", "steam_online.csv")
RAW = os.path.join(BASE, "steam_online", "steam_online_raw.csv")

df = pd.read_csv(CSV)
df["ts"] = pd.to_datetime(df["timestamp_local"])

print(f"原始行数: {len(df):,}")

zero = df["player_count"] == 0
neg = df["player_count"] < 0
nan = df["player_count"].isna()
print(f"  0 值行数: {zero.sum():,}")
print(f"  负值行数: {neg.sum():,}")
print(f"  空值行数: {nan.sum():,}")

if zero.sum():
    z = df[zero]
    print(f"\n0 值游戏分布: {z['game'].value_counts().to_dict()}")
    print(f"0 值时间范围: {z['ts'].min()} ~ {z['ts'].max()}")

# 备份原始文件（仅当备份不存在时）
if not os.path.exists(RAW):
    shutil.copy2(CSV, RAW)
    print(f"\n已备份原始数据 -> {os.path.basename(RAW)}")
else:
    print(f"\n备份已存在，跳过 -> {os.path.basename(RAW)}")

# 清洗
bad = zero | neg | nan
clean = df[~bad]
print(f"剔除异常行: {bad.sum():,}")
print(f"清洗后行数: {len(clean):,}")

clean.to_csv(CSV, index=False, encoding="utf-8-sig")
print(f"已写回清洗后数据 -> {os.path.basename(CSV)}")

# 验证
check = pd.read_csv(CSV)
print(f"\n验证: 清洗后最小 player_count = {check['player_count'].min():,}")
print(f"验证: 清洗后剩余 0 值 = {(check['player_count'] == 0).sum()}")
