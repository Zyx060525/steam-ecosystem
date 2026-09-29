# -*- coding: utf-8 -*-
"""跨源关联：以 appid 为实体键，融合 5 个数据源为一张「游戏维度」总表。

关联维度:
  实体关联: appid -> 元数据 / 在线人数 / 评论 / 新闻
  时间关联: 各源时间戳统一（后续脚本处理）

输出: integrated/games_overview.csv（每游戏一行）
"""
import glob
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CORE = [730, 570, 1172470, 578080, 440, 271590, 252490, 1085660]

META = os.path.join(BASE, "steam_metadata", "games_metadata.json")
ONLINE = os.path.join(BASE, "steam_online", "steam_online.csv")
REVIEWS_DIR = os.path.join(BASE, "steam_reviews", "SteamReviews2024")
NEWS_DIR = os.path.join(BASE, "steam_news")
OUT_DIR = os.path.join(BASE, "integrated")


def load_meta():
    with open(META, encoding="utf-8") as f:
        return json.load(f)


def online_summary():
    df = pd.read_csv(ONLINE)
    rows = []
    for appid, grp in df.groupby("appid"):
        rows.append(
            {
                "appid": appid,
                "online_peak": int(grp["player_count"].max()),
                "online_mean": int(grp["player_count"].mean()),
                "online_valley": int(grp["player_count"].min()),
                "online_volatility": round(grp["player_count"].std() / grp["player_count"].mean(), 4),
                "online_samples": len(grp),
            }
        )
    return pd.DataFrame(rows)


def review_summary():
    """分块统计评论指标，避免大文件占内存。"""
    rows = []
    for appid in CORE:
        f = os.path.join(REVIEWS_DIR, f"{appid}.csv")
        if not os.path.exists(f):
            rows.append({"appid": appid, "review_count": 0})
            continue
        total = 0
        pos = 0
        votes_up_sum = 0
        playtime_sum = 0
        lang_counter = {}
        for chunk in pd.read_csv(f, usecols=["voted_up", "votes_up", "author_playtime_at_review", "language"], chunksize=200000):
            total += len(chunk)
            pos += int(chunk["voted_up"].sum())
            votes_up_sum += int(chunk["votes_up"].sum())
            playtime_sum += int(chunk["author_playtime_at_review"].fillna(0).sum())
            for lang, cnt in chunk["language"].value_counts().items():
                lang_counter[lang] = lang_counter.get(lang, 0) + cnt
        top_lang = max(lang_counter, key=lang_counter.get) if lang_counter else None
        rows.append(
            {
                "appid": appid,
                "review_count": total,
                "positive_rate": round(pos / total, 4) if total else None,
                "avg_votes_up": round(votes_up_sum / total, 2) if total else None,
                "avg_playtime_at_review_min": int(playtime_sum / total) if total else None,
                "top_language": top_lang,
            }
        )
        print(f"  评论 {appid}: {total:,} 条, 好评率 {rows[-1]['positive_rate']}")
    return pd.DataFrame(rows)


def news_summary():
    rows = []
    for appid in CORE:
        f = os.path.join(NEWS_DIR, f"{appid}.json")
        if not os.path.exists(f):
            rows.append({"appid": appid, "news_count": 0})
            continue
        with open(f, encoding="utf-8") as fp:
            items = json.load(fp)
        dates = [i.get("date") for i in items if i.get("date")]
        tags = set()
        for i in items:
            tags.update(i.get("tags") or [])
        rows.append(
            {
                "appid": appid,
                "news_count": len(items),
                "news_last_date": pd.to_datetime(max(dates), unit="s") if dates else None,
                "news_tags": ",".join(sorted(tags)),
            }
        )
    return pd.DataFrame(rows)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    meta = load_meta()

    print("汇总在线人数...")
    online = online_summary()
    print("汇总评论（分块）...")
    reviews = review_summary()
    print("汇总新闻...")
    news = news_summary()

    # 元数据转 DataFrame
    meta_rows = []
    for appid in CORE:
        m = meta.get(str(appid), {})
        meta_rows.append(
            {
                "appid": appid,
                "game_name": m.get("name"),
                "genres": ",".join(m.get("genres", [])),
                "release_date": m.get("release_date"),
                "is_free": m.get("is_free"),
                "developers": ",".join(m.get("developers") or []),
            }
        )
    meta_df = pd.DataFrame(meta_rows)

    # 依次按 appid 关联
    merged = meta_df.merge(online, on="appid", how="left")
    merged = merged.merge(reviews, on="appid", how="left")
    merged = merged.merge(news, on="appid", how="left")

    out = os.path.join(OUT_DIR, "games_overview.csv")
    merged.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n融合完成 -> {out}")
    print(f"融合表: {merged.shape[0]} 行 × {merged.shape[1]} 列")
    print("\n融合结果预览:")
    cols = ["game_name", "genres", "review_count", "positive_rate", "online_peak", "online_mean", "news_count"]
    print(merged[cols].to_string(index=False))


if __name__ == "__main__":
    main()
