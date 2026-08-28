#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: wsgi.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

生产 WSGI 入口，供 gunicorn 加载：
    gunicorn -c deploy/gunicorn.conf.py wsgi:app
"""
from app_factory import create_app

app = create_app()
