#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_wechat_login.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

微信小程序登录测试：
- code2session 为纯单元测试，mock 微信 HTTP 接口，不依赖 MySQL/Redis
- login_by_wechat 与 /api/user/login/wechat/ 为集成测试，依赖 CI 中的 MySQL
"""
from unittest.mock import MagicMock

import pytest

import services.wechat_service as wechat_service_module
from app_factory import create_app
from models import db
from models.user import User
from services.wechat_service import WeChatService

app = create_app()

TEST_OPENID = "test_openid_wechat_login"
TEST_UNIONID = "test_unionid_wechat_login"


@pytest.fixture
def wechat_config(monkeypatch):
    """在 app.config 中注入测试用小程序配置"""
    monkeypatch.setitem(app.config, "WECHAT_MINI_APP_ID", "wx_test_app_id")
    monkeypatch.setitem(app.config, "WECHAT_MINI_APP_SECRET", "wx_test_secret")


@pytest.fixture
def app_ctx():
    with app.app_context():
        yield


def _mock_wechat_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    return response


def _cleanup_test_user():
    with app.app_context():
        db.session.query(User).filter(User.wechat_openid == TEST_OPENID).delete()
        db.session.commit()


class TestCode2Session:
    """code2session 单元测试：mock requests，不需要数据库"""

    def test_success_returns_session_info(self, wechat_config, app_ctx, monkeypatch):
        monkeypatch.setattr(
            wechat_service_module.requests,
            "get",
            lambda url, params=None, timeout=None: _mock_wechat_response(
                {"openid": TEST_OPENID, "session_key": "sk", "unionid": TEST_UNIONID}
            ),
        )
        data = WeChatService().code2session("test-code")
        assert data["openid"] == TEST_OPENID
        assert data["unionid"] == TEST_UNIONID

    def test_wechat_error_raises(self, wechat_config, app_ctx, monkeypatch):
        monkeypatch.setattr(
            wechat_service_module.requests,
            "get",
            lambda url, params=None, timeout=None: _mock_wechat_response(
                {"errcode": 40029, "errmsg": "invalid code"}
            ),
        )
        with pytest.raises(Exception, match="微信授权失败"):
            WeChatService().code2session("bad-code")

    def test_network_error_raises(self, wechat_config, app_ctx, monkeypatch):
        def _raise(url, params=None, timeout=None):
            raise ConnectionError("network down")

        monkeypatch.setattr(wechat_service_module.requests, "get", _raise)
        with pytest.raises(Exception, match="请求微信接口失败"):
            WeChatService().code2session("test-code")

    def test_missing_config_raises(self, app_ctx, monkeypatch):
        monkeypatch.setitem(app.config, "WECHAT_MINI_APP_ID", "")
        monkeypatch.setitem(app.config, "WECHAT_MINI_APP_SECRET", "")
        with pytest.raises(Exception, match="微信登录未开启"):
            WeChatService().code2session("test-code")


class TestLoginByWechat:
    """login_by_wechat 集成测试：mock 微信接口，真实写库"""

    @pytest.fixture(autouse=True)
    def _setup(self, wechat_config, monkeypatch):
        _cleanup_test_user()
        monkeypatch.setattr(
            WeChatService,
            "code2session",
            lambda self, code: {"openid": TEST_OPENID, "unionid": TEST_UNIONID},
        )
        yield
        _cleanup_test_user()

    def test_new_user_created_and_token_returned(self, app_ctx):
        from services.user_service import UserService

        data = UserService().login_by_wechat(code="any-code")
        assert data["token"]
        assert data["user_info"]["wechat_openid"] == TEST_OPENID

        user = (
            db.session.query(User)
            .filter(User.wechat_openid == TEST_OPENID)
            .first()
        )
        assert user is not None
        assert user.wechat_unionid == TEST_UNIONID
        assert user.id == data["user_info"]["id"]

    def test_existing_user_reused_on_second_login(self, app_ctx):
        from services.user_service import UserService

        first = UserService().login_by_wechat(code="code-1")
        second = UserService().login_by_wechat(code="code-2")
        assert first["user_info"]["id"] == second["user_info"]["id"]
        count = (
            db.session.query(User)
            .filter(User.wechat_openid == TEST_OPENID)
            .count()
        )
        assert count == 1

    def test_empty_code_raises(self, app_ctx):
        from services.user_service import UserService

        with pytest.raises(Exception, match="微信授权码不能为空"):
            UserService().login_by_wechat(code="")

    def test_wechat_failure_propagates(self, app_ctx, monkeypatch):
        from services.user_service import UserService

        def _fail(self, code):
            raise Exception("微信授权失败: errcode=40029, errmsg=invalid code")

        monkeypatch.setattr(WeChatService, "code2session", _fail)
        with pytest.raises(Exception, match="微信授权失败"):
            UserService().login_by_wechat(code="bad-code")


class TestWeChatLoginEndpoint:
    """/api/user/login/wechat/ 接口集成测试"""

    @pytest.fixture(autouse=True)
    def _setup(self, wechat_config, monkeypatch):
        _cleanup_test_user()
        monkeypatch.setattr(
            WeChatService,
            "code2session",
            lambda self, code: {"openid": TEST_OPENID, "unionid": TEST_UNIONID},
        )
        self.client = app.test_client()
        yield
        _cleanup_test_user()

    def test_login_success_and_token_usable(self):
        resp = self.client.post("/api/user/login/wechat/", json={"code": "wx-code"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        token = body["data"]["token"]
        assert token
        assert body["data"]["user_info"]["wechat_openid"] == TEST_OPENID

        me = self.client.get(
            "/api/user", headers={"Authorization": f"Bearer {token}"}
        )
        me_body = me.get_json()
        assert me.status_code == 200
        assert me_body["success"] is True
        assert me_body["data"]["id"] == body["data"]["user_info"]["id"]

    def test_missing_code(self):
        resp = self.client.post("/api/user/login/wechat/", json={})
        body = resp.get_json()
        assert body["success"] is False
        assert "微信授权码不能为空" in body["message"]

    def test_wechat_error_returns_failure(self, monkeypatch):
        def _fail(self, code):
            raise Exception("微信授权失败: errcode=40163, errmsg=code been used")

        monkeypatch.setattr(WeChatService, "code2session", _fail)
        resp = self.client.post("/api/user/login/wechat/", json={"code": "used"})
        body = resp.get_json()
        assert body["success"] is False
        assert "微信授权失败" in body["message"]
