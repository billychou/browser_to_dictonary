#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""

from flask import g
from flask_restful import Resource
from flask_restful import reqparse

from libs.api_response import api_handler
from libs.auth import jwt_required
from services import UserService


class UserResource(Resource):
    """用户资源类"""

    @jwt_required
    def get(self):
        """获取当前登录用户信息"""
        return {
            "success": True,
            "message": "获取用户信息成功",
            "data": g.current_user.to_dict()
        }


class UserLoginResource(Resource):
    """用户登录资源类"""
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
    
    @api_handler()
    def post(self, action_type=None):
        """用户登录"""
        parser = reqparse.RequestParser()
        parser.add_argument("phone", type=str, required=False, location="json")
        parser.add_argument("code", type=str, required=False, location="json")  # 短信验证码或微信授权码
        args = parser.parse_args()

        if action_type == "sms_send":
            if not args.get("phone"):
                raise Exception("手机号不能为空")
            data = self.user_service.send_sms_code(phone=args.get("phone"))
            return {
                "success": True,
                "message": "发送成功",
                "data": data
            }
        elif action_type == "wechat":
            data = self.user_service.login_by_wechat(code=args.get("code"))
            return {
                "success": True,
                "message": "登录成功",
                "data": data
            }
        else:
            if not args.get("phone"):
                raise Exception("手机号不能为空")
            data = self.user_service.login_by_phone(phone=args.get("phone"), code=args.get("code"))
            return {
                "success": True,
                "message": "登录成功",
                "data": data
            }


