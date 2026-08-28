#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi
"""
from flask import Blueprint

from libs.external_api import ExternalApi

bp = Blueprint("dictionary", __name__, url_prefix="/api/dictionary")
api = ExternalApi(bp)

from .views import DictionaryLookupResource

api.add_resource(DictionaryLookupResource, "")
