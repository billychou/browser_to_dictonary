#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: conftest.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/28
Copyright: @sanfendi

将后端源码目录加入 sys.path，使 `pytest tests/` 可直接导入应用模块。
"""
import pathlib
import sys

SRC_PATH = pathlib.Path(__file__).parent
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
