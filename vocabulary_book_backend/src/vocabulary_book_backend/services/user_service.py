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
        pass

    def send_sms_code(self, phone):
        """
        :param phone:
        :return:
        """
        # 生成6位随机验证码
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        # 这里应该调用实际的短信服务API发送验证码
        # 调用短信服务商发送验证码
        print(f"Sending SMS code {code} to {phone}")

        # 暂时只做模拟处理，实际项目中需要替换为真实的短信服务
        # TODO: 实际项目中应使用 Redis 或其他缓存系统存储验证码
        # key 设计采用统一前缀 + 手机号的形式，便于管理和清理
        # 过期时间设置为5分钟(300秒)，符合业界最佳实践
        cache_key = f"SMS_CODE:{phone}"
        redis_client.set(cache_key, code, timeout=300)
        return code

    def verify_sms_code(self, phone, code):
        """
        :param phone:
        :param code:
        :return:
        """
        pass
