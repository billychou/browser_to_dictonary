#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: app_config.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from pydantic_settings import SettingsConfigDict

from .deploy import DeploymentConfig
from .middleware import MiddlewareConfig


class AppConfig(DeploymentConfig, MiddlewareConfig):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )
