#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: user_service.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/5
Copyright: @sanfendi
"""
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
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
from libs.constants import CACHE_WECHAT_LOGIN_TICKET_PREFIX
from libs.constants import CACHE_WECHAT_LOGIN_TICKET_TIMEOUT
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
        unionid = session_info.get("unionid")

        # 优先按 unionid 匹配：小程序与扩展网站应用绑定同一开放平台账号时，
        # unionid 一致即可共享同一账号
        user = None
        if unionid:
            user = db.session.query(User).filter(
                User.wechat_unionid == unionid
            ).first()
        if not user:
            user = db.session.query(User).filter(
                User.wechat_openid == openid
            ).first()
        if not user:
            user = User(
                wechat_openid=openid,
                wechat_unionid=unionid,
            )
            db.session.add(user)
            db.session.flush()
            db.session.commit()
        elif not user.wechat_openid:
            user.wechat_openid = openid
            db.session.commit()

        token = self.generate_token(user.id)
        return dict(user_info=user.to_dict(), token=token)

    def create_wechat_login_ticket(self) -> Dict[str, Any]:
        """
        生成一次性微信扫码登录票据（Chrome 扩展扫码登录第一步）。
        票据初始值为 pending，用户扫码确认后由回调写入登录态，
        扩展端轮询 poll_wechat_login_ticket 获取结果。
        :return: dict(ticket, qrcode_url)
        """
        ticket = uuid.uuid4().hex
        qrcode_url = WeChatService().build_qrconnect_url(state=ticket)
        redis_client.setex(
            f"{CACHE_WECHAT_LOGIN_TICKET_PREFIX}:{ticket}",
            CACHE_WECHAT_LOGIN_TICKET_TIMEOUT,
            "pending",
        )
        return dict(ticket=ticket, qrcode_url=qrcode_url)

    def confirm_wechat_login_by_ticket(self, ticket: str, code: str) -> Dict[str, Any]:
        """
        微信扫码回调确认登录：校验票据有效后，用授权码完成
        网站应用登录并将 {user_info, token} 挂到票据上供扩展轮询消费。
        :param ticket: 一次性登录票据（即微信回调带回的 state）
        :param code: 微信授权码
        :return: dict(user_info, token)
        """
        if not ticket:
            raise Exception("登录票据不能为空")
        if not code:
            raise Exception("微信授权码不能为空")
        cache_key = f"{CACHE_WECHAT_LOGIN_TICKET_PREFIX}:{ticket}"
        if redis_client.get(cache_key) is None:
            raise Exception("二维码已过期，请在扩展中重新发起微信登录")

        user = WeChatService().process_wechat_login(code)
        token = self.generate_token(user.id)
        data = dict(user_info=user.to_dict(), token=token)
        # 覆盖写入登录态，沿用原有效期
        redis_client.setex(
            cache_key, CACHE_WECHAT_LOGIN_TICKET_TIMEOUT, json.dumps(data)
        )
        return data

    @staticmethod
    def poll_wechat_login_ticket(ticket: str) -> Dict[str, Any]:
        """
        扩展轮询扫码登录结果。确认成功后删除票据，只能兑换一次。
        :param ticket: 一次性登录票据
        :return: {"status": "pending" | "confirmed" | "expired", ...}
        """
        if not ticket:
            return dict(status="expired")
        cache_key = f"{CACHE_WECHAT_LOGIN_TICKET_PREFIX}:{ticket}"
        value = redis_client.get(cache_key)
        if value is None:
            # 票据不存在或已过期：扩展需引导用户重新获取二维码
            return dict(status="expired")
        if value == b"pending":
            return dict(status="pending")
        # 登录已确认：消费票据并返回登录态
        redis_client.delete(cache_key)
        data = json.loads(value)
        return dict(status="confirmed", **data)

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
        签发 JWT。exp/iat 必须使用 UTC 时间：PyJWT 将 naive 时间按 UTC 解释，
        若用本地时间签发，非 UTC 时区的机器会产生最多数小时的时钟偏差，
        导致校验端报 ImmatureSignatureError（无效的登录凭证）。
        :param user_id:
        :return:
        """
        now = datetime.now(timezone.utc)
        payload = {
            'user_id': user_id,
            'exp': now + timedelta(days=30),
            'iat': now
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
