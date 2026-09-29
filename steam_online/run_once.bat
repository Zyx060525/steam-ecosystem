@echo off
rem 采集一次 Steam 同时在线快照并追加到 steam_online.csv
rem 用法: 在 Windows 任务计划程序里新建任务，触发器设为"每分钟重复"，操作指向本 bat
cd /d "%~dp0"
python steam_online_crawler.py --once
