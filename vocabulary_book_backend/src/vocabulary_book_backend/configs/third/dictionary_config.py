#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
词典服务配置

File: dictionary_config.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class DictionaryConfig(BaseSettings):
    """
    词典查询配置。默认使用免费的 Free Dictionary API（英文），
    置空 DICTIONARY_API_BASE 可关闭释义查询。
    """

    DICTIONARY_API_BASE: str = Field(
        description="词典 API 地址（按路径拼接单词）",
        default="https://api.dictionaryapi.dev/api/v2/entries/en",
    )
    DICTIONARY_TIMEOUT: int = Field(
        description="词典查询超时（秒），保存单词为尽力而为查询",
        default=5,
    )
