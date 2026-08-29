#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/6
Copyright: @sanfendi
"""
from .dictionary_config import DictionaryConfig
from .sms_config import AlibabaCloudConfig
from .sms_config import SmsConfig
from .wechat_config import WeChatMiniConfig
from .wechat_config import WeChatOpenConfig


class ThirdConfig(SmsConfig, AlibabaCloudConfig, WeChatMiniConfig, WeChatOpenConfig, DictionaryConfig):
    """
    第三方配置
    """
    pass


__all__ = [
    ThirdConfig,
    SmsConfig,
    WeChatMiniConfig,
    WeChatOpenConfig
]
