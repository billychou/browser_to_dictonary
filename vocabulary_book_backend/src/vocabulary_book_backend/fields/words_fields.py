#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: words_fields.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/15
Copyright: @sanfendi
"""

from flask_restful import fields

word_fields = {
    "id": fields.Integer,
    "uid": fields.String,
    "word": fields.String,
    "gmt_create": fields.DateTime,
    "gmt_update": fields.DateTime,
}

word_post_resp_fields = {
    "success": fields.Boolean,
    "message": fields.String,
    "data": fields.Nested(word_fields),
}
