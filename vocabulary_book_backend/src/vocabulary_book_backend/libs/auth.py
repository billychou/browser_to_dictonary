#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: auth.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/28
Copyright: @sanfendi
"""
from functools import wraps

import jwt as pyjwt
from flask import g, request

from configs import app_config
from models import db
from models.user import User


def _unauthorized(message: str):
    return dict(success=False, message=message, data=None), 401


def jwt_required(fn):
    """
    Flask-RESTful 资源方法鉴权装饰器。
    从 Authorization: Bearer <token> 中解析 JWT，
    校验通过后将当前用户挂载到 flask.g.current_user。
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not app_config.JWT_SECRET_KEY:
            return dict(
                success=False, message="服务端未配置 JWT_SECRET_KEY", data=None
            ), 500
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return _unauthorized("未登录或登录凭证缺失")

        token = auth_header[len("Bearer "):].strip()
        try:
            payload = pyjwt.decode(
                token,
                app_config.JWT_SECRET_KEY,
                algorithms=[app_config.JWT_ALGORITHM],
            )
        except pyjwt.ExpiredSignatureError:
            return _unauthorized("登录已过期，请重新登录")
        except pyjwt.InvalidTokenError:
            return _unauthorized("无效的登录凭证")

        user = db.session.get(User, payload.get("user_id"))
        if not user or not user.is_active:
            return _unauthorized("用户不存在或已被禁用")

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
