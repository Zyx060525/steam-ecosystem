# -*- coding: utf-8 -*-
"""
Steam 同时在线人数（分钟级）采集器
数据源: Steamworks Web API - ISteamUserStats/GetNumberOfCurrentPlayers

说明:
    官方 Steamworks API 只能拿到【当前瞬时在线人数快照】，没有自带历史分钟存档；
    分钟级历史时序数据需要本脚本定时轮询 API 并逐行追加保存到 CSV。

用法示例:
    # 1) 只采集一次快照后退出（推荐配合 Windows 任务计划程序，每分钟触发一次）
    python steam_online_crawler.py --once

    # 2) 常驻运行，每 60 秒轮询一次（Ctrl+C 停止）
    python steam_online_crawler.py --interval 60

    # 3) 指定游戏 appid（逗号分隔；留空则用默认列表）
    python steam_online_crawler.py --once --appids 730,570,1172470

    # 4) 自定义输出文件
    python steam_online_crawler.py --once --out my_steam_online.csv

输出 CSV 字段:
    timestamp_utc    采集时刻（UTC，YYYY-MM-DD HH:MM:SS）
    timestamp_local  采集时刻（本地时间）
    appid           游戏 appid
    game            游戏名（未知 appid 显示为 appid_xxx）
    player_count    当前在线人数
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.request

# 输出重定向到文件时改为行缓冲，保证日志实时可读
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(line_buffering=True)
    except Exception:
        pass

API_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid={appid}"

# 默认关注的游戏 appid（可自行增删）
DEFAULT_APPIDS = {
    730: "Counter-Strike 2",
    570: "Dota 2",
    1172470: "Apex Legends",
    578080: "PUBG: BATTLEGROUNDS",
    440: "Team Fortress 2",
    271590: "Grand Theft Auto V",
    252490: "Rust",
    1085660: "Destiny 2",
}

REQUEST_TIMEOUT = 15   # 单次请求超时（秒）
RETRY_TIMES = 3        # 单个 appid 失败重试次数
RETRY_DELAY = 2        # 重试间隔（秒）

FIELD_NAMES = [
    "timestamp_utc",
    "timestamp_local",
    "appid",
    "game",
    "player_count",
]


def fetch_player_count(appid):
    """请求单个 appid 的当前在线人数。

    返回 (appid, player_count)；失败时返回 (appid, None)。
    """
    url = API_URL.format(appid=appid)
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return appid, int(data["response"]["player_count"])
        except Exception as exc:  # 网络异常 / 结构异常 / 超时等
            print(
                f"[warn] appid={appid} 第 {attempt}/{RETRY_TIMES} 次请求失败: {exc}",
                file=sys.stderr,
            )
            if attempt < RETRY_TIMES:
                time.sleep(RETRY_DELAY)
    return appid, None


def append_rows(csv_path, rows):
    """把 rows（list[dict]）逐行追加写入 CSV；文件不存在时先写表头。"""
    new_file = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
        if new_file:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def collect_once(appids, csv_path):
    """采集一轮快照（同一轮内所有 appid 共用同一采集时刻）。"""
    timestamp_utc = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    timestamp_local = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    rows = []
    for appid, game in appids.items():
        _, count = fetch_player_count(appid)
        if count is None:
            print(f"[skip] {game}({appid}) 无数据")
            continue
        rows.append(
            {
                "timestamp_utc": timestamp_utc,
                "timestamp_local": timestamp_local,
                "appid": appid,
                "game": game,
                "player_count": count,
            }
        )
        print(f"[ok] {game}({appid}) -> {count:,}")
        time.sleep(0.5)  # 限速，避免请求过快

    if rows:
        append_rows(csv_path, rows)
        print(f"[saved] 本轮共 {len(rows)} 条 -> {csv_path}")
    else:
        print("[warn] 本轮未采集到任何数据")
    return len(rows)


def run_loop(appids, csv_path, interval):
    """常驻循环：每 interval 秒采集一轮，Ctrl+C 停止。"""
    print(f"[loop] 每 {interval} 秒轮询一次，按 Ctrl+C 停止")
    while True:
        try:
            collect_once(appids, csv_path)
        except KeyboardInterrupt:
            print("\n[stop] 已停止")
            break
        except Exception as exc:
            print(f"[error] 本轮采集异常: {exc}", file=sys.stderr)
        time.sleep(interval)


def parse_appids(raw):
    """解析 --appids 参数，返回 {appid: game_name}。"""
    appids = {}
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit():
            appids[int(token)] = f"appid_{token}"
    return appids


def load_games_file(path):
    """从 JSON 文件读取 {appid: name} 映射（appid 为字符串键）。"""
    import json

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


def main():
    parser = argparse.ArgumentParser(description="Steam 同时在线人数采集器")
    parser.add_argument("--once", action="store_true", help="只采集一次快照后退出")
    parser.add_argument(
        "--interval", type=int, default=60, help="循环模式下轮询间隔（秒），默认 60"
    )
    parser.add_argument(
        "--appids", type=str, default="", help="逗号分隔的 appid 列表，留空用默认列表"
    )
    parser.add_argument(
        "--games-file", type=str, default="", help="JSON 文件路径（{appid: name}），优先于 --appids"
    )
    parser.add_argument(
        "--out", type=str, default="steam_online.csv", help="输出 CSV 路径"
    )
    args = parser.parse_args()

    if args.games_file.strip():
        appids = load_games_file(args.games_file)
    elif args.appids.strip():
        appids = parse_appids(args.appids)
    else:
        appids = dict(DEFAULT_APPIDS)
    csv_path = os.path.abspath(args.out)

    if args.once:
        collect_once(appids, csv_path)
    else:
        run_loop(appids, csv_path, args.interval)


if __name__ == "__main__":
    main()
