# -*- coding: utf-8 -*-
"""采集 Steam 游戏元数据（appdetails）与新闻事件（GetNewsForApp）。

数据源:
  - Steam 官方 Store API  appdetails  -> 游戏名称/类型/标签/发行日期/开发商/价格等
  - Steam 官方 ISteamNews GetNewsForApp -> 游戏更新公告/新闻事件（含时间、标签、正文）

用法:
  python collect_metadata_news.py              # 采集默认 8 个核心游戏
  python collect_metadata_news.py --all        # 采集 top100 热门游戏（需先有游戏列表）
"""
import argparse
import json
import os
import sys
import time
import urllib.request

# 8 个核心研究对象（当前在线人数跟踪的游戏）
CORE_GAMES = {
    730: "Counter-Strike 2",
    570: "Dota 2",
    1172470: "Apex Legends",
    578080: "PUBG: BATTLEGROUNDS",
    440: "Team Fortress 2",
    271590: "Grand Theft Auto V",
    252490: "Rust",
    1085660: "Destiny 2",
}

APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={appid}"
NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid={appid}&count=100&maxlength=500"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_DIR = os.path.join(BASE, "steam_metadata")
NEWS_DIR = os.path.join(BASE, "steam_news")

RETRIES = 5
RETRY_DELAY = 2
RATE_LIMIT = 1.2  # 每秒请求间隔（遵守访问频率限制）


def fetch_json(url):
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"    [warn] 第 {attempt}/{RETRIES} 次失败: {exc}", file=sys.stderr)
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY)
    return None


def collect_metadata(games):
    os.makedirs(META_DIR, exist_ok=True)
    result = {}
    print(f"采集游戏元数据（{len(games)} 个游戏）...")
    for appid, name in games.items():
        data = fetch_json(APP_DETAILS_URL.format(appid=appid))
        if data and str(appid) in data and data[str(appid)].get("success"):
            d = data[str(appid)]["data"]
            item = {
                "appid": appid,
                "name": d.get("name"),
                "type": d.get("type"),
                "is_free": d.get("is_free"),
                "genres": [g.get("description") for g in d.get("genres", [])],
                "categories": [c.get("description") for c in d.get("categories", [])],
                "release_date": (d.get("release_date") or {}).get("date"),
                "developers": d.get("developers"),
                "publishers": d.get("publishers"),
                "supported_languages": (d.get("supported_languages") or ""),
                "recommendations": d.get("recommendations", {}).get("total"),
                "price_usd": None,
            }
            if d.get("price_overview"):
                item["price_usd"] = d["price_overview"].get("final_formatted")
            result[str(appid)] = item
            print(f"  [ok] {item['name']:<22} 类型={item['genres']} 发行={item['release_date']}")
        else:
            print(f"  [skip] {name}({appid}) 元数据获取失败")
        time.sleep(RATE_LIMIT)

    out = os.path.join(META_DIR, "games_metadata.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"元数据已保存 -> {out}（{len(result)} 个游戏）")
    return result


def collect_news(games):
    os.makedirs(NEWS_DIR, exist_ok=True)
    print(f"\n采集游戏新闻事件（{len(games)} 个游戏）...")
    for appid, name in games.items():
        data = fetch_json(NEWS_URL.format(appid=appid))
        if data and "appnews" in data:
            items = data["appnews"]["newsitems"]
            # 只保留关键字段，减小体积
            clean = [
                {
                    "gid": i.get("gid"),
                    "appid": i.get("appid"),
                    "title": i.get("title"),
                    "author": i.get("author"),
                    "date": i.get("date"),
                    "feedlabel": i.get("feedlabel"),
                    "feedname": i.get("feedname"),
                    "tags": i.get("tags"),
                    "contents": i.get("contents"),
                }
                for i in items
            ]
            out = os.path.join(NEWS_DIR, f"{appid}.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(clean, f, ensure_ascii=False, indent=2)
            print(f"  [ok] {name:<22} {len(clean)} 条新闻 -> {appid}.json")
        else:
            print(f"  [skip] {name}({appid}) 新闻获取失败")
        time.sleep(RATE_LIMIT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=str, default="", help="逗号分隔 appid，留空用默认 8 个核心游戏")
    args = parser.parse_args()

    if args.games.strip():
        games = {int(x): f"appid_{x}" for x in args.games.split(",") if x.strip().isdigit()}
    else:
        games = dict(CORE_GAMES)

    collect_metadata(games)
    collect_news(games)
    print("\n全部完成。")


if __name__ == "__main__":
    main()
