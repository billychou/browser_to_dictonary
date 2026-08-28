#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: gunicorn.conf.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

生产环境 gunicorn 配置。从仓库的 vocabulary_book_backend/ 目录启动：
    gunicorn -c deploy/gunicorn.conf.py wsgi:app
"""
import multiprocessing
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 应用位于 src/vocabulary_book_backend，统一切换工作目录保证相对导入与 .env 加载正确
chdir = str(BASE_DIR / "src" / "vocabulary_book_backend")

bind = os.environ.get("BIND", "0.0.0.0:7001")
# 可用 WEB_CONCURRENCY 覆盖，默认 (2 x CPU) + 1
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive = 5

# 请求日志输出到 stdout，交给容器/日志采集系统收集
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")

# 定期重启 worker，规避长驻进程的内存累积
max_requests = 1000
max_requests_jitter = 100
