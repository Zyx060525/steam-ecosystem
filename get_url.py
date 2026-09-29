# -*- coding: utf-8 -*-
"""临时脚本：获取 Kaggle 数据集的真实下载 URL（用于 curl 续传）。"""
from kagglehub.clients import build_kaggle_client
from kagglehub.http_resolver import _build_dataset_download_request, _get_current_version
from kagglehub.handle import DatasetHandle

h = DatasetHandle("artermiloff", "steam-games-reviews-2024")
with build_kaggle_client() as api_client:
    h = h.with_version(_get_current_version(api_client, h))
    r = _build_dataset_download_request(h, None)
    response = api_client.datasets.dataset_api_client.download_dataset(r)
    print("URL:", response.url)
    print("STATUS:", response.status_code)
    print("ACCEPT_RANGES:", response.headers.get("Accept-Ranges"))
    print("CONTENT_LENGTH:", response.headers.get("Content-Length"))
    response.close()
