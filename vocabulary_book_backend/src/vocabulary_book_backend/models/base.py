#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: base.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from sqlalchemy.orm import declarative_base

from models.engine import metadata

Base = declarative_base(metadata=metadata)
