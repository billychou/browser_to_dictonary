#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
统一响应包装

File: api_response.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi
"""
from functools import wraps


def api_handler(status_on_error: int = 400):
    """
    Resource 方法统一异常包装装饰器。
    业务异常转换为统一响应结构 {success, message, data}，
    避免各 Resource 手写 try/except。

    :param status_on_error: 业务异常时的 HTTP 状态码，默认 400
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                return (
                    dict(success=False, message=str(e), data=None),
                    status_on_error,
                )

        return wrapper

    return decorator
