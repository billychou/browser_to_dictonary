#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: wechat_service.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""
from typing import Dict, Any
from urllib.parse import urlencode

import requests
from flask import current_app

from models import User, db


class WeChatService:
    """
    微信服务类，处理微信相关的业务逻辑
    网站登录（开放平台扫码）/ 小程序登录
    """

    # 微信开放平台官方扫码登录页
    QRCONNECT_URL = "https://open.weixin.qq.com/connect/qrconnect"

    def code2session(self, code: str) -> Dict[str, Any]:
        """
        小程序登录凭证校验：wx.login 的 code 换取 openid/unionid/session_key
        :param code: 小程序 wx.login 返回的临时登录凭证
        :return: 微信返回的会话信息，至少包含 openid
        """
        app_id = current_app.config.get("WECHAT_MINI_APP_ID")
        app_secret = current_app.config.get("WECHAT_MINI_APP_SECRET")
        if not app_id or not app_secret:
            raise Exception(
                "微信登录未开启：服务端未配置 WECHAT_MINI_APP_ID / WECHAT_MINI_APP_SECRET"
            )

        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": app_id,
            "secret": app_secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
        except Exception as e:
            raise Exception(f"请求微信接口失败: {str(e)}")

        if data.get("errcode"):
            raise Exception(
                f"微信授权失败: errcode={data.get('errcode')}, errmsg={data.get('errmsg')}"
            )
        return data

    def build_qrconnect_url(self, state: str) -> str:
        """
        构造微信开放平台官方扫码登录页 URL（网站应用）。
        用户手机微信扫码确认后，微信会携带 code 与 state 跳转回
        WECHAT_OPEN_REDIRECT_URI（须与开放平台配置的回调域名一致）。
        :param state: 一次性登录票据，回调时原样带回，防 CSRF
        :return: 官方扫码登录页完整 URL
        """
        app_id = current_app.config.get("WECHAT_OPEN_APP_ID")
        redirect_uri = current_app.config.get("WECHAT_OPEN_REDIRECT_URI")
        if not app_id or not current_app.config.get("WECHAT_OPEN_APP_SECRET"):
            raise Exception(
                "微信扫码登录未开启：服务端未配置 WECHAT_OPEN_APP_ID / WECHAT_OPEN_APP_SECRET"
            )
        if not redirect_uri:
            raise Exception(
                "微信扫码登录未开启：服务端未配置 WECHAT_OPEN_REDIRECT_URI"
            )
        query = urlencode({
            "appid": app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_login",
            "state": state,
        })
        return f"{self.QRCONNECT_URL}?{query}#wechat_redirect"

    def get_access_token(self, code: str) -> Dict[str, Any]:
        """
        通过授权码获取微信 access_token（网站应用）
        :param code: 微信扫码登录回调带回的授权码
        :return: 包含 access_token/openid/unionid 等信息的字典
        """
        app_id = current_app.config.get('WECHAT_OPEN_APP_ID')
        app_secret = current_app.config.get('WECHAT_OPEN_APP_SECRET')

        if not app_id or not app_secret:
            raise Exception(
                "微信扫码登录未开启：服务端未配置 WECHAT_OPEN_APP_ID / WECHAT_OPEN_APP_SECRET"
            )

        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            "appid": app_id,
            "secret": app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            # 检查是否有错误
            if 'errcode' in data:
                raise Exception(f"获取微信access_token失败: errcode={data['errcode']}, errmsg={data['errmsg']}")

            return data
        except Exception as e:
            raise Exception(f"请求微信接口失败: {str(e)}")

    def get_user_info(self, access_token: str, openid: str) -> Dict[str, Any]:
        """
        获取微信用户信息
        :param access_token: 微信access_token
        :param openid: 微信openid
        :return: 微信用户信息字典
        """
        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            # 检查是否有错误
            if 'errcode' in data:
                raise Exception(f"获取微信用户信息失败: errcode={data['errcode']}, errmsg={data['errmsg']}")

            return data
        except Exception as e:
            raise Exception(f"请求微信用户信息接口失败: {str(e)}")

    def login_or_create_user(self, wechat_user_info: Dict[str, Any]) -> User:
        """
        根据微信用户信息登录或创建用户。
        优先按 unionid 匹配：网站应用与小程序绑定同一开放平台账号时
        unionid 一致，可让 Chrome 扩展与微信小程序共享同一账号。
        :param wechat_user_info: 微信用户信息
        :return: User对象
        """
        openid = wechat_user_info.get('openid')
        if not openid:
            raise Exception("微信用户信息中缺少openid")
        unionid = wechat_user_info.get('unionid')

        # 查找用户：优先 unionid，其次 openid
        user = None
        if unionid:
            user = User.query.filter_by(wechat_unionid=unionid).first()
        if not user:
            user = User.query.filter_by(wechat_openid=openid).first()

        if not user:
            # 创建新用户
            user = User(
                wechat_openid=openid,
                wechat_unionid=unionid,
                nickname=wechat_user_info.get('nickname'),
                avatar=wechat_user_info.get('headimgurl')
            )
            db.session.add(user)
            db.session.commit()
        else:
            # 更新用户信息；openid 仅在缺失时回填，避免多端互相覆盖
            user.nickname = wechat_user_info.get('nickname', user.nickname)
            user.avatar = wechat_user_info.get('headimgurl', user.avatar)
            if unionid:
                user.wechat_unionid = unionid
            if not user.wechat_openid:
                user.wechat_openid = openid
            db.session.commit()

        return user

    def process_wechat_login(self, code: str) -> User:
        """
        处理网站应用扫码登录完整流程：
        code 换 access_token → 拉取用户信息 → 登录或创建用户
        :param code: 微信授权码
        :return: User对象
        """
        # 1. 获取access_token
        token_info = self.get_access_token(code)
        if not token_info:
            raise Exception("获取微信授权失败")

        access_token = token_info.get('access_token')
        openid = token_info.get('openid')

        # 2. 获取用户信息
        wechat_user_info = self.get_user_info(access_token, openid)
        if not wechat_user_info:
            raise Exception("获取微信用户信息失败")

        # 3. 登录或创建用户
        user = self.login_or_create_user(wechat_user_info)

        return user
