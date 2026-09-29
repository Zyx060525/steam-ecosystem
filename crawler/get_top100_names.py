# -*- coding: utf-8 -*-
"""批量获取 Top 100 游戏名称（appdetails），生成 appid -> name 映射。"""
import json
import time
import urllib.request

BASE = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
IDS_FILE = __import__("os").path.join(BASE, "top100_appids.txt")
OUT_FILE = __import__("os").path.join(BASE, "top100_games.json")

ids = [int(x) for x in open(IDS_FILE).read().split(",") if x.strip()]
result = {}
for i, appid in enumerate(ids):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    name = f"appid_{appid}"
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            d = data.get(str(appid), {}).get("data", {})
            name = d.get("name", f"appid_{appid}")
            break
        except Exception:
            time.sleep(2)
    result[str(appid)] = name
    if (i + 1) % 20 == 0:
        print(f"  {i + 1}/{len(ids)}")
    time.sleep(0.5)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"完成，保存 {len(result)} 个游戏名 -> {OUT_FILE}")
