#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: __init__.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""
from flask import Blueprint

from libs.external_api import ExternalApi

bp = Blueprint("user", __name__, url_prefix="/api/user")
api = ExternalApi(bp)

from .views import UserLoginResource, UserResource
from .views import WeChatLoginCallbackResource
from .views import WeChatLoginTicketResource
from .views import WeChatLoginTicketStatusResource

api.add_resource(UserResource, "")
api.add_resource(UserLoginResource, "/login/", "/login/<action_type>/")
api.add_resource(WeChatLoginTicketResource, "/login/wechat/ticket/")
api.add_resource(
    WeChatLoginTicketStatusResource, "/login/wechat/ticket/<ticket>/"
)
api.add_resource(WeChatLoginCallbackResource, "/login/wechat/callback/")
