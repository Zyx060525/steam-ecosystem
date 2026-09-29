# -*- coding: utf-8 -*-
"""用 curl 断点续传下载 Kaggle 数据集归档（Python 只负责拿 URL，下载交给 curl，内存占用极小）。

下载目标: steam_reviews/1.archive（实际是 archive.zip，4.21GB）
"""
import os
import subprocess
import sys
import time

from kagglehub.clients import build_kaggle_client
from kagglehub.http_resolver import _build_dataset_download_request, _get_current_version
from kagglehub.handle import DatasetHandle

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "steam_reviews", "1.archive")

for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(line_buffering=True)
    except Exception:
        pass

print(f"[get-url] {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
h = DatasetHandle("artermiloff", "steam-games-reviews-2024")
with build_kaggle_client() as api_client:
    h = h.with_version(_get_current_version(api_client, h))
    r = _build_dataset_download_request(h, None)
    response = api_client.datasets.dataset_api_client.download_dataset(r)
    url = response.url
    total = response.headers.get("Content-Length")
    response.close()

print(f"[total] {int(total)/1024**3:.2f} GB", flush=True)

os.makedirs(os.path.dirname(OUT), exist_ok=True)

# curl -C - 续传（从已有文件末尾继续），-L 跟随重定向
cmd = ["curl.exe", "-C", "-", "-L", "--retry", "10", "--retry-delay", "5", "-o", OUT, url]
print(f"[curl] 启动下载（续传）-> {OUT}", flush=True)
ret = subprocess.run(cmd)
print(f"[curl-exit] {ret.returncode}", flush=True)
if ret.returncode == 0:
    print("DOWNLOAD_COMPLETE", flush=True)
