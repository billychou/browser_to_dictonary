#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from flask import Blueprint

from libs.external_api import ExternalApi

bp = Blueprint("word", __name__, url_prefix="/api/word")
api = ExternalApi(bp)

from .views import WordResource

api.add_resource(WordResource, "/")
