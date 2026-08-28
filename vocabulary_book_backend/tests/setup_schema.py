#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: setup_schema.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

为测试环境创建数据库表（CI 中替代迁移流程）。
用法：uv run python tests/setup_schema.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src" / "vocabulary_book_backend"))

from app_factory import create_app
from models.engine import db

app = create_app()
with app.app_context():
    db.create_all()
print("test schema ready")
