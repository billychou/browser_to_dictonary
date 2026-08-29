#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: ext_database.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""

from models import db
from vb_app import VbApp


def init_app(app: VbApp):
    db.init_app(app)
