#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/6
Copyright: @sanfendi
"""
from .sms_config import AlibabaCloudConfig
from .sms_config import SmsConfig


class ThirdConfig(SmsConfig, AlibabaCloudConfig):
    """
    第三方配置
    """
    pass


__all__ = [
    ThirdConfig,
    SmsConfig
]
