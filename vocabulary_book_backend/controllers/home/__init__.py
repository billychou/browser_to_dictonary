#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/9/1
Copyright: @sanfendi
"""
from flask import Blueprint

bp = Blueprint("home", __name__)

from . import views  # noqa: E402,F401
