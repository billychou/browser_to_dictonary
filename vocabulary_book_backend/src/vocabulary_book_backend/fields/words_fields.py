#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: words_fields.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/15
Copyright: @sanfendi
"""

from flask_restful import fields

# 统一 ISO 8601 输出（flask_restful 默认 RFC 822），便于前端 Date 解析与测试断言
_iso = fields.DateTime(dt_format="iso8601")

word_fields = {
    "id": fields.Integer,
    "uid": fields.String,
    "word": fields.String,
    "stage": fields.Integer,
    "due": _iso,
    "review_count": fields.Integer,
    "lapse_count": fields.Integer,
    "last_review": _iso,
    "gmt_create": _iso,
    "gmt_update": _iso,
}

word_post_resp_fields = {
    "success": fields.Boolean,
    "message": fields.String,
    "data": fields.Nested(word_fields),
}

word_list_data_fields = {
    "total": fields.Integer,
    "page": fields.Integer,
    "limit": fields.Integer,
    "items": fields.List(fields.Nested(word_fields)),
}

word_list_resp_fields = {
    "success": fields.Boolean,
    "message": fields.String,
    "data": fields.Nested(word_list_data_fields),
}
