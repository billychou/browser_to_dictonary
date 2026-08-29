#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
微信小程序登录配置

File: wechat_config.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class WeChatMiniConfig(BaseSettings):
    """
    微信小程序配置（code2session 登录）。
    留空表示未开启微信登录，接口会返回明确错误，不影响短信登录。
    """

    WECHAT_MINI_APP_ID: str = Field(
        description="微信小程序 AppID",
        default="",
    )
    WECHAT_MINI_APP_SECRET: str = Field(
        description="微信小程序 AppSecret",
        default="",
    )
