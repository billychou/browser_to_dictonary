#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: app_config.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from .deploy import DeploymentConfig
from .middleware import DatabaseConfig
from pydantic_settings import SettingsConfigDict


class AppConfig(DeploymentConfig, DatabaseConfig):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )


