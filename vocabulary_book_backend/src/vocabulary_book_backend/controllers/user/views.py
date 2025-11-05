#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional

import jwt
from flask import current_app, request
from flask_restful import Resource
from flask_restful import reqparse

from models import User, db
from services import WeChatService, UserService


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
    
    def post(self):
        """用户登录"""
        parser = reqparse.RequestParser()
        parser.add_argument("login_type", type=str, required=True, location="json", 
                          help="登录类型必须提供: phone 或 wechat")
        parser.add_argument("phone", type=str, required=False, location="json")
        parser.add_argument("code", type=str, required=False, location="json")  # 短信验证码或微信授权码
        parser.add_argument("wechat_code", type=str, required=False, location="json")  # 微信授权码
        args = parser.parse_args()
        
        login_type = args.get("login_type")
        
        if login_type == "phone":
            return self._phone_login(args.get("phone"), args.get("code"))
        elif login_type == "wechat":
            return self._wechat_login(args.get("wechat_code"))
        else:
            return {
                "success": False,
                "message": "不支持的登录类型"
            }, 400
    
    def _phone_login(self, phone: str, code: str):
        """手机号登录"""
        if not phone or not code:
            return {
                "success": False,
                "message": "手机号和验证码不能为空"
            }, 400
            
        # 验证验证码逻辑（这里简化处理，实际应该查询验证码表）
        # if not self._verify_sms_code(phone, code):
        #     return {
        #         "success": False,
        #         "message": "验证码错误"
        #     }, 400
        
        # 查找或创建用户
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone)
            db.session.add(user)
            db.session.commit()
            
        # 生成token
        token = self._generate_token(user.id)
        
        return {
            "success": True,
            "message": "登录成功",
            "data": {
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "nickname": user.nickname,
                    "avatar": user.avatar
                },
                "token": token
            }
        }
    
    def _wechat_login(self, wechat_code: str):
        """微信登录"""
        if not wechat_code:
            return {
                "success": False,
                "message": "微信授权码不能为空"
            }, 400
            
        try:
            # 使用微信服务处理登录
            wechat_service = WeChatService()
            user = wechat_service.process_wechat_login(wechat_code)
            
            # 生成token
            token = self._generate_token(user.id)
            
            return {
                "success": True,
                "message": "登录成功",
                "data": {
                    "user": {
                        "id": user.id,
                        "phone": user.phone,
                        "nickname": user.nickname,
                        "avatar": user.avatar
                    },
                    "token": token
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"微信登录失败: {str(e)}"
            }, 400
    
    def _generate_token(self, user_id: int) -> str:
        """生成JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=30),  # 30天过期
            'iat': datetime.utcnow()
        }
        # 使用简单的密钥，实际应该使用配置文件中的密钥
        secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    
    def _verify_sms_code(self, phone: str, code: str) -> bool:
        """验证短信验证码"""
        # 实际应该查询数据库或缓存验证验证码
        # 这里简化处理，始终返回True
        return True
    
    def _get_wechat_user_info(self, code: str) -> Optional[dict]:
        """获取微信用户信息"""
        # 实际应该调用微信API获取用户信息
        # 这里简化处理，返回None
        return None