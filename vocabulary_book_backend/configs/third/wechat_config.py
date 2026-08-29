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


class WeChatOpenConfig(BaseSettings):
    """
    微信开放平台「网站应用」配置（Chrome 扩展扫码登录）。
    扩展端走官方扫码登录流程：
    1. 扩展请求后端生成一次性登录票据，并打开官方二维码页面；
    2. 用户手机微信扫码确认后，微信携带 code 回调 REDIRECT_URI；
    3. 后端用 code 换 openid/用户信息，签发 JWT 挂在票据上；
    4. 扩展轮询票据拿到登录态。
    留空表示未开启扩展微信登录，接口会返回明确错误。
    """

    WECHAT_OPEN_APP_ID: str = Field(
        description="微信开放平台网站应用 AppID",
        default="",
    )
    WECHAT_OPEN_APP_SECRET: str = Field(
        description="微信开放平台网站应用 AppSecret",
        default="",
    )
    WECHAT_OPEN_REDIRECT_URI: str = Field(
        description=(
            "微信扫码登录授权回调地址，须与开放平台配置的回调域名一致，"
            "如 https://api.your-domain.com/api/user/login/wechat/callback/"
        ),
        default="",
    )
