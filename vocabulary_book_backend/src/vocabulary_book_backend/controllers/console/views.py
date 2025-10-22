#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from flask_restful import Resource
from flask_restful import reqparse


class HelloWorldResource(Resource):
    """ """

    def get(self):
        """
        get method
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            "word", type=str, required=False, default=None, location="args"
        )
        args = parser.parse_args()
        word = args.get("word")
        return dict(success=True, message="Hello World", data=f"backend_{word}")
