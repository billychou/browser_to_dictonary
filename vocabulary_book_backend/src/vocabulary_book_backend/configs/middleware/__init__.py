#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""

from .database_config import DatabaseConfig
from .redis_config import RedisConfig


class MiddlewareConfig(DatabaseConfig, RedisConfig):
    """
    中间件配置
    """

    pass
