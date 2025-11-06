#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: user_service.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/5
Copyright: @sanfendi
"""
import random
from datetime import datetime, timedelta
from typing import Optional

import jwt
from flask import current_app

from extensions.ext_redis import redis_client
from libs.constants import CACHE_SMS_CODE_PREFIX
from libs.constants import CACHE_SMS_CODE_TIMEOUT
from models import db
from models.user import User


class UserService(object):
    def login_by_phone(self, phone: str, code: str) -> Optional[User]:
        """
        :param phone: 手机号
        :param code: 验证码
        :return:
        """
        if not phone or not code:
            raise Exception("手机号和验证码不能为空")
        exist_code = redis_client.get(f"SMS_CODE:{phone}")
        if exist_code != code:
            raise Exception("验证码错误")
        user_info = self.get_user_by_phone(phone)
        return user_info

    @staticmethod
    def get_user_by_phone(phone: str) -> User:
        """
        :param phone: 手机号码
        :return:
        """
        user_info = db.session.query(User).filter(User.phone == phone).first()
        if not user_info:
            raise Exception("用户不存在")
        return user_info

    def get_user_info(self, token):
        """
        根据token获取用户信息
        :param token:
        :return:
        """

    def generate_token(self, user_id):
        """
        :param user_id:
        :return:
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(days=30),  # 10天过期
            'iat': datetime.now()
        }
        # 使用简单的密钥，实际应该使用配置文件中的密钥
        secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    def verify_token(self, token):
        """
        :param token:
        :return:
        """
        try:
            # 使用配置文件中的密钥进行解码
            secret_key = current_app.config.get('SECRET_KEY', 'default_secret_key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # 检查用户是否存在
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                return None
                
            return user
        except jwt.ExpiredSignatureError:
            # Token过期
            return None
        except jwt.InvalidTokenError:
            # Token无效
            return None

    def send_sms_code(self, phone):
        """
        发送短信验证码
        :param phone: 手机号码
        :return: 验证码
        """
        # 生成6位随机验证码
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        # 这里应该调用实际的短信服务API发送验证码
        # 调用短信服务商发送验证码
        print(f"Sending SMS code {code} to {phone}")
        # 暂时只做模拟处理，实际项目中需要替换为真实的短信服务
        # 验证码建议保存在缓存系统中（如Redis），而非数据库
        # 原因：1. 验证码时效性短，无需持久化存储
        #      2. 缓存系统支持自动过期，管理更方便
        #      3. 减少数据库压力，提高系统性能
        # key 设计采用统一前缀 + 手机号的形式，便于管理和清理
        # 过期时间设置为5分钟(300秒)，符合业界最佳实践
        cache_key = f"{CACHE_SMS_CODE_PREFIX}:{phone}"
        redis_client.set(cache_key, code, timeout=CACHE_SMS_CODE_TIMEOUT)
        return code

    def verify_sms_code(self, phone, code):
        """
        :param phone:
        :param code:
        :return:
        """
        pass
