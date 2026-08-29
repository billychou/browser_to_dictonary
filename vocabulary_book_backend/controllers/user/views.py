#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""

from flask import g, make_response, request
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


# 微信扫码登录回调结果页（微信跳转回后端时用户可见，返回 HTML 而非 JSON）
_CALLBACK_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ margin: 0; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         background: #f6f7f9; color: #1f2329; }}
  .card {{ max-width: 420px; margin: 120px auto; padding: 32px 24px; text-align: center;
           background: #fff; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,.06); }}
  .icon {{ font-size: 40px; margin-bottom: 12px; }}
  h1 {{ font-size: 18px; margin: 0 0 8px; }}
  p {{ font-size: 14px; color: #8a9099; margin: 0; }}
</style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{title}</h1>
    <p>{message}</p>
  </div>
</body>
</html>
"""


def _callback_page(success: bool, message: str):
    """构造扫码回调结果页响应（HTML）"""
    html = _CALLBACK_PAGE_TEMPLATE.format(
        icon="✅" if success else "⚠️",
        title="微信登录成功" if success else "微信登录失败",
        message=message,
    )
    response = make_response(html)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


class WeChatLoginTicketResource(Resource):
    """微信扫码登录票据：扩展发起扫码登录（第一步）"""

    def __init__(self):
        super().__init__()
        self.user_service = UserService()

    @api_handler()
    def post(self):
        """生成一次性票据与官方二维码页链接"""
        data = self.user_service.create_wechat_login_ticket()
        return {
            "success": True,
            "message": "二维码已生成，请打开二维码页面并使用微信扫码",
            "data": data,
        }


class WeChatLoginTicketStatusResource(Resource):
    """微信扫码登录票据状态：扩展轮询扫码结果（第四步）"""

    @api_handler()
    def get(self, ticket=None):
        """轮询票据状态：pending 等待扫码 / confirmed 已登录 / expired 已过期"""
        data = UserService.poll_wechat_login_ticket(ticket or "")
        return {"success": True, "message": "ok", "data": data}


class WeChatLoginCallbackResource(Resource):
    """微信扫码登录授权回调（第二步/第三步）：微信服务器跳转用户浏览器至此"""

    def __init__(self):
        super().__init__()
        self.user_service = UserService()

    def get(self):
        """处理微信回调：code + state(票据) 换取登录态，挂到票据上"""
        code = request.args.get("code", "")
        ticket = request.args.get("state", "")
        try:
            self.user_service.confirm_wechat_login_by_ticket(ticket, code)
        except Exception as e:
            return _callback_page(False, str(e))
        return _callback_page(True, "请关闭此页面，回到浏览器扩展继续使用。")
