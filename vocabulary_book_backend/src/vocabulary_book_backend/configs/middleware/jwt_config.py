#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: jwt_config.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/6
Copyright: @sanfendi
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class JwtConfig(BaseSettings):
    """
    JWT 配置
    """

    JWT_SECRET_KEY: str = Field(
        description="JWT 密钥",
        default="default_secret_key",
    )

    JWT_ALGORITHM: str = Field(
        description="JWT 算法",
        default="HS256",
    )

    JWT_EXPIRATION_TIME: int = Field(
        description="JWT 过期时间（秒）",
        default=3600,
    )
