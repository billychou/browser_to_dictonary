#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
短信验证码服务

File: sms_config.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/6
Copyright: @sanfendi
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class AlibabaCloudConfig(BaseSettings):
    """
    阿里云授权配置
    """
    ALIBABA_CLOUD_ACCESS_KEY_ID: str = Field(
        description="阿里云 Access Key ID",
        default="",
    )
    ALIBABA_CLOUD_ACCESS_KEY_SECRET: str = Field(
        description="阿里云 Access Key Secret",
        default="",
    )


class SmsConfig(BaseSettings):
    """
    SMS configuration settings
    """
    SMS_API_KEY: str = Field(
        description="SMS API key",
        default="",
    )
    SMS_API_SECRET: str = Field(
        description="SMS API secret",
        default="",
    )
