#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @三分地技术有限公司
"""

from flask_restful import Resource
from flask_restful import marshal
from flask_restful import reqparse

from fields.words_fields import word_post_resp_fields
from services.vocabulary_service import VocabularyService


class WordResource(Resource):
    """
    单词接口
    """

    def get(self):
        """
        get
        :return:
        """
        return dict(success=True, message="Hello World", data="backend")

    def post(self):
        """
        add
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("uid", type=str, required=True, location="json")
        parser.add_argument("word", type=str, required=True, location="json")
        args = parser.parse_args()
        data = VocabularyService.add(uid=args["uid"], word=args["word"])
        return marshal(
            dict(success=True, message="success", data=data), word_post_resp_fields
        )
