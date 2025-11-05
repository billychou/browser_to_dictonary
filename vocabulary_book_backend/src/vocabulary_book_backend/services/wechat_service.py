#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: wechat_service.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""
from typing import Optional, Dict, Any

import requests
from flask import current_app

from models import User, db


class WeChatService:
    """
    微信服务类，处理微信相关的业务逻辑
    网站登录
    """

    def get_access_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        通过授权码获取微信access_token
        :param code: 微信授权码
        :return: 包含access_token等信息的字典
        """
        # 从配置中获取微信相关参数
        app_id = current_app.config.get('WECHAT_APP_ID')
        app_secret = current_app.config.get('WECHAT_APP_SECRET')
        
        if not app_id or not app_secret:
            raise Exception("微信配置缺失，请检查WECHAT_APP_ID和WECHAT_APP_SECRET配置")
        
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            "appid": app_id,
            "secret": app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 检查是否有错误
            if 'errcode' in data:
                raise Exception(f"获取微信access_token失败: errcode={data['errcode']}, errmsg={data['errmsg']}")
                
            return data
        except Exception as e:
            raise Exception(f"请求微信接口失败: {str(e)}")

    def get_user_info(self, access_token: str, openid: str) -> Optional[Dict[str, Any]]:
        """
        获取微信用户信息
        :param access_token: 微信access_token
        :param openid: 用户openid
        :return: 用户信息字典
        """
        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 检查是否有错误
            if 'errcode' in data:
                raise Exception(f"获取微信用户信息失败: errcode={data['errcode']}, errmsg={data['errmsg']}")
                
            return data
        except Exception as e:
            raise Exception(f"请求微信用户信息接口失败: {str(e)}")

    def login_or_create_user(self, wechat_user_info: Dict[str, Any]) -> User:
        """
        根据微信用户信息登录或创建用户
        :param wechat_user_info: 微信用户信息
        :return: User对象
        """
        openid = wechat_user_info.get('openid')
        if not openid:
            raise Exception("微信用户信息中缺少openid")
        
        # 查找用户
        user = User.query.filter_by(wechat_openid=openid).first()
        
        if not user:
            # 创建新用户
            user = User(
                wechat_openid=openid,
                wechat_unionid=wechat_user_info.get('unionid'),
                nickname=wechat_user_info.get('nickname'),
                avatar=wechat_user_info.get('headimgurl')
            )
            db.session.add(user)
            db.session.commit()
        else:
            # 更新用户信息
            user.nickname = wechat_user_info.get('nickname', user.nickname)
            user.avatar = wechat_user_info.get('headimgurl', user.avatar)
            user.wechat_unionid = wechat_user_info.get('unionid', user.wechat_unionid)
            db.session.commit()
            
        return user

    def process_wechat_login(self, code: str) -> User:
        """
        处理微信登录完整流程
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