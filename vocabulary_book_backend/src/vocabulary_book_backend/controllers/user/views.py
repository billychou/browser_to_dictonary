#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""

from flask_restful import Resource
from flask_restful import reqparse

from services import UserService


class UserResource(Resource):
    """用户资源类"""
    
    def get(self):
        """获取当前用户信息"""
        # 这里应该从请求中获取用户身份信息
        # 暂时返回示例数据
        return {
            "success": True,
            "message": "获取用户信息成功",
            "data": {
                "id": 1,
                "phone": "13800138000",
                "nickname": "测试用户",
                "avatar": "",
                "is_active": True
            }
        }


class UserLoginResource(Resource):
    """用户登录资源类"""
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
    
    def post(self, action_type=None):
        """用户登录"""
        parser = reqparse.RequestParser()
        parser.add_argument("phone", type=str, required=True, location="json")
        parser.add_argument("code", type=str, required=False, location="json")  # 短信验证码或微信授权码
        args = parser.parse_args()
        
        try:
            if action_type == "sms_send":
                data = self.user_service.send_sms_code(phone=args.get("phone"))
                return {
                    "success": True,
                    "message": "发送成功",
                    "data": data
                }
            else:
                data = self.user_service.login_by_phone(phone=args.get("phone"), code=args.get("code"))
                return {
                    "success": True,
                    "message": "登录成功",
                    "data": data
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None
            }


