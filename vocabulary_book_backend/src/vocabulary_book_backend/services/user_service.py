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
from typing import Optional, Dict, Any

import jwt

from configs import app_config
from extensions.ext_redis import redis_client
from libs.client.sms_client import SmsClient
from libs.constants import CACHE_SMS_CODE_ERR_MAX
from libs.constants import CACHE_SMS_CODE_ERR_PREFIX
from libs.constants import CACHE_SMS_CODE_PREFIX
from libs.constants import CACHE_SMS_CODE_TIMEOUT
from libs.constants import CACHE_SMS_DAILY_PREFIX
from libs.constants import CACHE_SMS_DAILY_TIMEOUT
from libs.constants import SMS_DAILY_LIMIT
from models import db
from models.user import User
from services.wechat_service import WeChatService


class UserService(object):
    def login_by_phone(self, phone: str, code: str) -> Optional[Dict[str, Any]]:
        """
        手机号 + 短信验证码登录，用户不存在时自动注册
        :param phone: 手机号
        :param code: 验证码
        :return:
        """
        if not phone or not code:
            raise Exception("手机号和验证码不能为空")

        self.verify_sms_code(phone, code)

        user = db.session.query(User).filter(User.phone == phone).first()
        # 当用户不存在的时候创建该用户
        if not user:
            user = User(phone=phone)
            db.session.add(user)
            db.session.flush()
            db.session.commit()
        token = self.generate_token(user.id)
        return dict(user_info=user.to_dict(), token=token)

    def login_by_wechat(self, code: str) -> Dict[str, Any]:
        """
        微信小程序一键登录：wx.login 的 code 换取 openid，
        按 openid 登录，用户不存在时自动注册
        :param code: 小程序 wx.login 返回的临时登录凭证
        :return: dict(user_info, token)
        """
        if not code:
            raise Exception("微信授权码不能为空")

        session_info = WeChatService().code2session(code)
        openid = session_info.get("openid")
        if not openid:
            raise Exception("微信授权失败：未获取到 openid")

        user = db.session.query(User).filter(User.wechat_openid == openid).first()
        if not user:
            user = User(
                wechat_openid=openid,
                wechat_unionid=session_info.get("unionid"),
            )
            db.session.add(user)
            db.session.flush()
            db.session.commit()

        token = self.generate_token(user.id)
        return dict(user_info=user.to_dict(), token=token)

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
            'exp': datetime.now() + timedelta(days=30),
            'iat': datetime.now()
        }
        jwt_secret_key = app_config.JWT_SECRET_KEY
        if not jwt_secret_key:
            raise Exception("服务端未配置 JWT_SECRET_KEY，禁止签发令牌")
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
        exist_code: bytes = redis_client.get(f"{CACHE_SMS_CODE_PREFIX}:{phone}")
        if exist_code:
            raise Exception("验证码已发送，请稍后再试")
        daily_key = f"{CACHE_SMS_DAILY_PREFIX}:{phone}"
        daily_count = redis_client.incr(daily_key)
        if int(daily_count) == 1:
            redis_client.expire(daily_key, CACHE_SMS_DAILY_TIMEOUT)
        if int(daily_count) > SMS_DAILY_LIMIT:
            raise Exception("今日验证码发送次数过多，请明天再试")
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        SmsClient.send(code, phone)
        cache_key = f"{CACHE_SMS_CODE_PREFIX}:{phone}"
        redis_client.setex(cache_key, CACHE_SMS_CODE_TIMEOUT, code)
        # 重新发送验证码时清空历史错误次数，允许用户重新尝试
        redis_client.delete(f"{CACHE_SMS_CODE_ERR_PREFIX}:{phone}")

    @staticmethod
    def verify_sms_code(phone: str, code: str) -> None:
        """
        校验短信验证码，校验失败时抛出异常。
        错误次数超过上限后，即使验证码正确也需重新获取，防止暴力枚举。
        :param phone: 手机号码
        :param code: 用户提交的验证码
        """
        err_key = f"{CACHE_SMS_CODE_ERR_PREFIX}:{phone}"
        err_count = redis_client.get(err_key)
        if err_count and int(err_count) >= CACHE_SMS_CODE_ERR_MAX:
            raise Exception("验证码错误次数过多，请重新获取验证码")

        exist_code = redis_client.get(f"{CACHE_SMS_CODE_PREFIX}:{phone}")
        exist_code_str = exist_code.decode("utf-8") if exist_code else ""
        if not exist_code_str:
            raise Exception("验证码已过期")

        if exist_code_str != code:
            # 记录一次错误尝试，有效期与验证码一致
            redis_client.incr(err_key)
            redis_client.expire(err_key, CACHE_SMS_CODE_TIMEOUT)
            raise Exception("无效的验证码")

        # 校验通过，清除错误计数并消费掉验证码，防止重放
        redis_client.delete(err_key)
        redis_client.delete(f"{CACHE_SMS_CODE_PREFIX}:{phone}")
