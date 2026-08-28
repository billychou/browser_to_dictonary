#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi
"""

from flask import g
from flask_restful import Resource
from flask_restful import reqparse

from extensions.ext_redis import redis_client
from libs.api_response import api_handler
from libs.auth import jwt_required
from libs.client.dictionary_client import DictionaryClient
from libs.constants import CACHE_DICT_LOOKUP_PREFIX
from libs.constants import CACHE_DICT_LOOKUP_TIMEOUT
from libs.constants import DICT_LOOKUP_LIMIT_PER_MINUTE


class DictionaryLookupResource(Resource):
    """词典释义查询（需登录，按用户频控）"""

    @api_handler()
    @jwt_required
    def get(self):
        """
        实时查询单词释义（不落库，供划词即查等场景）
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("word", type=str, required=True, location="args")
        args = parser.parse_args()
        word = (args["word"] or "").strip()
        if not word:
            raise Exception("单词不能为空")

        uid = str(g.current_user.id)
        lookup_key = f"{CACHE_DICT_LOOKUP_PREFIX}:{uid}"
        lookup_count = redis_client.incr(lookup_key)
        if int(lookup_count) == 1:
            redis_client.expire(lookup_key, CACHE_DICT_LOOKUP_TIMEOUT)
        if int(lookup_count) > DICT_LOOKUP_LIMIT_PER_MINUTE:
            raise Exception("查询过于频繁，请稍后再试")

        result = DictionaryClient.lookup(word)
        if not result:
            return dict(success=True, message="未查询到该词的释义", data=None)
        return dict(
            success=True, message="success", data=dict(word=word, **result)
        )
