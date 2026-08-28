#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_api_response.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

统一响应包装装饰器单元测试，不依赖外部服务。
"""
from libs.api_response import api_handler


class TestApiHandler:
    def test_success_passthrough(self):
        @api_handler()
        def ok():
            return dict(success=True, message="success", data=1)

        assert ok() == dict(success=True, message="success", data=1)

    def test_exception_converted_to_unified_error(self):
        @api_handler()
        def fail():
            raise Exception("something wrong")

        body, status = fail()
        assert status == 400
        assert body == dict(success=False, message="something wrong", data=None)

    def test_custom_error_status(self):
        @api_handler(status_on_error=429)
        def fail():
            raise Exception("too many requests")

        body, status = fail()
        assert status == 429
        assert body["message"] == "too many requests"

    def test_tuple_return_passthrough(self):
        @api_handler()
        def custom():
            return dict(success=False, message="teapot", data=None), 418

        body, status = custom()
        assert status == 418

    def test_preserves_function_metadata(self):
        @api_handler()
        def named():
            """doc"""
            return None

        assert named.__name__ == "named"
        assert named.__doc__ == "doc"
