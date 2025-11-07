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
from typing import Optional, Dict

import jwt

from configs import app_config
from extensions.ext_redis import redis_client
from libs.client.sms_client import SmsClient
from libs.constants import CACHE_SMS_CODE_PREFIX
from libs.constants import CACHE_SMS_CODE_TIMEOUT
from models import db
from models.user import User


class UserService(object):
    def login_by_phone(self, phone: str, code: str) -> Optional[Dict]:
        """
        :param phone: 手机号
        :param code: 验证码
        :return:
        """
        if not phone or not code:
            raise Exception("手机号和验证码不能为空")

        exist_code: bytes = redis_client.get(f"{CACHE_SMS_CODE_PREFIX}:{phone}")
        exist_code_str = exist_code.decode("utf-8")
        if not exist_code_str:
            raise Exception("验证码已过期")

        if exist_code_str != code:
            raise Exception("无效的验证码")

        user = db.session.query(User).filter(User.phone == phone).first()
        # 当用户不存在的时候创建该用户
        if not user:
            user = User(phone=phone)
            db.session.add(user)
            db.session.flush()
            db.session.commit()
        token = self.generate_token(user.id)
        return token

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
        jwt_secret_key = app_config.JWT_SECRET_KEY
        token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')
        return token

    def verify_token(self, token):
        """
        :param token:
        :return:
        """
        try:
            # 使用配置文件中的密钥进行解码
            jwt_secret_key = app_config.JWT_SECRET_KEY
            payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
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

    @staticmethod
    def send_sms_code(phone: str):
        """
        发送短信验证码
        :param phone: 手机号码
        :return: 验证码
        """
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        print(f"Sending SMS code {code} to {phone}")
        SmsClient.send(code, phone)
        cache_key = f"{CACHE_SMS_CODE_PREFIX}:{phone}"
        redis_client.setex(cache_key, CACHE_SMS_CODE_TIMEOUT, code)

    def verify_sms_code(self, phone, code):
        """
        :param phone:
        :param code:
        :return:
        """
        pass
