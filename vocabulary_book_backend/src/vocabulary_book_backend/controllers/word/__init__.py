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

bp = Blueprint("word", __name__, url_prefix="/api/word/")
api = ExternalApi(bp)

from .views import (
    WordDefinitionResource,
    WordItemResource,
    WordResource,
    WordReviewResource,
)

api.add_resource(WordResource, "/")
api.add_resource(WordItemResource, "/<int:word_id>")
api.add_resource(WordReviewResource, "/<int:word_id>/review")
api.add_resource(WordDefinitionResource, "/<int:word_id>/definition")
