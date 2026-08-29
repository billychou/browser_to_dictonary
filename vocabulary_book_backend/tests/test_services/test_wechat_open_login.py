#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_wechat_open_login.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

微信开放平台扫码登录（Chrome 扩展）测试：
- 二维码链接构造、票据流转为纯单元测试，mock Redis/微信接口，不依赖 MySQL/Redis
- login_or_create_user 与 /api/user/login/wechat/ticket|callback 为集成测试，依赖 CI 中的 MySQL
"""
import json
from unittest.mock import MagicMock

import pytest

import services.user_service as user_service_module
from app_factory import create_app
from libs.constants import CACHE_WECHAT_LOGIN_TICKET_PREFIX
from libs.constants import CACHE_WECHAT_LOGIN_TICKET_TIMEOUT
from models import db
from models.user import User
from services.user_service import UserService
from services.wechat_service import WeChatService

app = create_app()

TEST_OPENID_OPEN = "test_openid_wechat_open"
TEST_UNIONID_OPEN = "test_unionid_wechat_open"
TEST_TICKET = "ticket-for-test"


def _ticket_key(ticket: str) -> str:
    return f"{CACHE_WECHAT_LOGIN_TICKET_PREFIX}:{ticket}"


@pytest.fixture
def open_config(monkeypatch):
    """在 app.config 中注入测试用开放平台配置"""
    monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_ID", "wx_open_test_app_id")
    monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_SECRET", "wx_open_test_secret")
    monkeypatch.setitem(
        app.config,
        "WECHAT_OPEN_REDIRECT_URI",
        "https://api.test.com/api/user/login/wechat/callback/",
    )


@pytest.fixture
def app_ctx():
    with app.app_context():
        yield


@pytest.fixture
def fake_redis(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(user_service_module, "redis_client", fake)
    return fake


class FakeRedis:
    """按 dict 存储的假 Redis，供接口级测试在 confirm 与 poll 间共享状态"""

    def __init__(self):
        self.store = {}

    def setex(self, key, timeout, value):
        self.store[key] = value

    def get(self, key):
        value = self.store.get(key)
        if isinstance(value, str):
            return value.encode("utf-8")
        return value

    def delete(self, key):
        self.store.pop(key, None)


class TestBuildQrconnectUrl:
    """官方扫码登录页 URL 构造：不需要数据库"""

    def test_url_contains_appid_state_and_redirect(self, open_config, app_ctx):
        url = WeChatService().build_qrconnect_url(state="state-123")
        assert url.startswith("https://open.weixin.qq.com/connect/qrconnect?")
        assert "appid=wx_open_test_app_id" in url
        assert "scope=snsapi_login" in url
        assert "state=state-123" in url
        assert "#wechat_redirect" in url
        # redirect_uri 必须 URL 编码
        assert "https%3A%2F%2Fapi.test.com%2Fapi%2Fuser%2Flogin%2Fwechat%2Fcallback%2F" in url

    def test_missing_app_config_raises(self, app_ctx, monkeypatch):
        monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_ID", "")
        monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_SECRET", "")
        with pytest.raises(Exception, match="微信扫码登录未开启"):
            WeChatService().build_qrconnect_url(state="state-123")

    def test_missing_redirect_uri_raises(self, app_ctx, monkeypatch):
        monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_ID", "wx_open_test_app_id")
        monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_SECRET", "secret")
        monkeypatch.setitem(app.config, "WECHAT_OPEN_REDIRECT_URI", "")
        with pytest.raises(Exception, match="WECHAT_OPEN_REDIRECT_URI"):
            WeChatService().build_qrconnect_url(state="state-123")


class TestLoginOrCreateUser:
    """unionid 优先匹配：集成测试，真实写库"""

    @pytest.fixture(autouse=True)
    def _setup(self, app_ctx):
        self._cleanup()
        yield
        self._cleanup()

    @staticmethod
    def _cleanup():
        db.session.query(User).filter(
            User.wechat_unionid.in_([TEST_UNIONID_OPEN, TEST_UNIONID_OPEN + "_2"])
        ).delete(synchronize_session=False)
        db.session.query(User).filter(
            User.wechat_openid.in_([TEST_OPENID_OPEN, TEST_OPENID_OPEN + "_2"])
        ).delete(synchronize_session=False)
        db.session.commit()

    def test_match_by_unionid_keeps_existing_openid(self):
        """小程序先注册（openid A），扩展扫码登录（openid B，同 unionid）应复用同一账号"""
        service = WeChatService()
        mini_user = service.login_or_create_user(
            {"openid": TEST_OPENID_OPEN, "unionid": TEST_UNIONID_OPEN}
        )
        open_user = service.login_or_create_user(
            {
                "openid": TEST_OPENID_OPEN + "_2",
                "unionid": TEST_UNIONID_OPEN,
                "nickname": "扩展用户",
            }
        )
        assert open_user.id == mini_user.id
        # 已有 openid 不被覆盖
        assert open_user.wechat_openid == TEST_OPENID_OPEN
        assert open_user.nickname == "扩展用户"

    def test_backfill_openid_when_missing(self):
        """仅有 unionid 的历史用户，登录时回填 openid"""
        user = User(wechat_unionid=TEST_UNIONID_OPEN + "_2")
        db.session.add(user)
        db.session.commit()

        found = WeChatService().login_or_create_user(
            {"openid": TEST_OPENID_OPEN, "unionid": TEST_UNIONID_OPEN + "_2"}
        )
        assert found.id == user.id
        assert found.wechat_openid == TEST_OPENID_OPEN

    def test_create_new_user_without_unionid(self):
        user = WeChatService().login_or_create_user({"openid": TEST_OPENID_OPEN})
        assert user.id is not None
        assert user.wechat_openid == TEST_OPENID_OPEN
        assert user.wechat_unionid is None


class TestWeChatLoginTicket:
    """票据生成/确认/轮询：mock Redis 与微信接口"""

    def test_create_ticket_stores_pending_and_returns_qrcode_url(
        self, fake_redis, monkeypatch
    ):
        monkeypatch.setattr(
            WeChatService,
            "build_qrconnect_url",
            lambda self, state: f"https://qr.example/{state}",
        )
        data = UserService().create_wechat_login_ticket()
        assert data["ticket"]
        assert data["qrcode_url"] == f"https://qr.example/{data['ticket']}"
        fake_redis.setex.assert_called_once_with(
            _ticket_key(data["ticket"]), CACHE_WECHAT_LOGIN_TICKET_TIMEOUT, "pending"
        )

    def test_confirm_ticket_stores_login_data(self, fake_redis, app_ctx, monkeypatch):
        fake_redis.get.return_value = b"pending"
        fake_user = MagicMock()
        fake_user.id = 1
        fake_user.to_dict.return_value = {"id": 1, "nickname": "tester"}
        monkeypatch.setattr(
            WeChatService, "process_wechat_login", lambda self, code: fake_user
        )
        data = UserService().confirm_wechat_login_by_ticket(TEST_TICKET, "wx-code")
        assert data["token"]
        assert data["user_info"]["nickname"] == "tester"

        key, timeout, payload = fake_redis.setex.call_args[0]
        assert key == _ticket_key(TEST_TICKET)
        assert timeout == CACHE_WECHAT_LOGIN_TICKET_TIMEOUT
        stored = json.loads(payload)
        assert stored["token"] == data["token"]

    def test_confirm_expired_ticket_raises(self, fake_redis, app_ctx):
        fake_redis.get.return_value = None
        with pytest.raises(Exception, match="二维码已过期"):
            UserService().confirm_wechat_login_by_ticket(TEST_TICKET, "wx-code")

    def test_confirm_empty_code_raises(self, fake_redis):
        with pytest.raises(Exception, match="微信授权码不能为空"):
            UserService().confirm_wechat_login_by_ticket(TEST_TICKET, "")

    def test_poll_pending(self, fake_redis):
        fake_redis.get.return_value = b"pending"
        assert UserService.poll_wechat_login_ticket(TEST_TICKET) == {
            "status": "pending"
        }
        fake_redis.delete.assert_not_called()

    def test_poll_confirmed_consumes_ticket(self, fake_redis):
        payload = json.dumps({"user_info": {"id": 1}, "token": "jwt-token"})
        fake_redis.get.return_value = payload.encode("utf-8")
        result = UserService.poll_wechat_login_ticket(TEST_TICKET)
        assert result["status"] == "confirmed"
        assert result["token"] == "jwt-token"
        fake_redis.delete.assert_called_once_with(_ticket_key(TEST_TICKET))

    def test_poll_expired(self, fake_redis):
        fake_redis.get.return_value = None
        assert UserService.poll_wechat_login_ticket(TEST_TICKET) == {
            "status": "expired"
        }
        assert UserService.poll_wechat_login_ticket("") == {"status": "expired"}


class TestWeChatLoginTicketEndpoints:
    """ticket/callback 接口集成测试：真实 MySQL，mock Redis 与微信接口"""

    @pytest.fixture(autouse=True)
    def _setup(self, open_config, monkeypatch):
        self.fake = FakeRedis()
        self._original_build_qrconnect_url = WeChatService.build_qrconnect_url
        monkeypatch.setattr(user_service_module, "redis_client", self.fake)
        monkeypatch.setattr(
            WeChatService,
            "build_qrconnect_url",
            lambda self, state: f"https://qr.example/{state}",
        )
        self._cleanup_user()
        self.client = app.test_client()
        yield
        self._cleanup_user()

    @staticmethod
    def _cleanup_user():
        with app.app_context():
            db.session.query(User).filter(
                User.wechat_openid == TEST_OPENID_OPEN
            ).delete(synchronize_session=False)
            db.session.commit()

    def _mock_process_login(self, monkeypatch):
        def _process(self, code):
            return WeChatService.login_or_create_user(
                self, {"openid": TEST_OPENID_OPEN, "unionid": TEST_UNIONID_OPEN}
            )

        monkeypatch.setattr(WeChatService, "process_wechat_login", _process)

    def test_full_scan_login_flow(self, monkeypatch):
        """创建票据 → 微信回调确认 → 轮询拿到 token → token 可用"""
        self._mock_process_login(monkeypatch)

        # 1. 扩展创建票据
        resp = self.client.post("/api/user/login/wechat/ticket/")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        ticket = body["data"]["ticket"]
        assert body["data"]["qrcode_url"] == f"https://qr.example/{ticket}"

        # 2. 未扫码前轮询为 pending
        resp = self.client.get(f"/api/user/login/wechat/ticket/{ticket}/")
        assert resp.get_json()["data"]["status"] == "pending"

        # 3. 微信扫码后回调确认（微信跳转用户浏览器至此，返回 HTML）
        resp = self.client.get(
            "/api/user/login/wechat/callback/",
            query_string={"code": "wx-code", "state": ticket},
        )
        assert resp.status_code == 200
        assert resp.content_type.startswith("text/html")
        assert "微信登录成功" in resp.get_data(as_text=True)

        # 4. 轮询拿到登录态
        resp = self.client.get(f"/api/user/login/wechat/ticket/{ticket}/")
        data = resp.get_json()["data"]
        assert data["status"] == "confirmed"
        assert data["token"]
        assert data["user_info"]["wechat_openid"] == TEST_OPENID_OPEN

        # 5. 票据只能消费一次
        resp = self.client.get(f"/api/user/login/wechat/ticket/{ticket}/")
        assert resp.get_json()["data"]["status"] == "expired"

        # 6. token 可正常访问受保护接口
        me = self.client.get(
            "/api/user", headers={"Authorization": f"Bearer {data['token']}"}
        )
        assert me.status_code == 200
        assert me.get_json()["data"]["id"] == data["user_info"]["id"]

    def test_callback_with_expired_ticket_shows_error_page(self):
        resp = self.client.get(
            "/api/user/login/wechat/callback/",
            query_string={"code": "wx-code", "state": "no-such-ticket"},
        )
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert "微信登录失败" in text
        assert "二维码已过期" in text

    def test_callback_wechat_error_shows_error_page(self, monkeypatch):
        def _fail(self, code):
            raise Exception("微信授权失败: errcode=40163, errmsg=code been used")

        monkeypatch.setattr(WeChatService, "process_wechat_login", _fail)
        self.fake.setex(_ticket_key(TEST_TICKET), 300, "pending")
        resp = self.client.get(
            "/api/user/login/wechat/callback/",
            query_string={"code": "used-code", "state": TEST_TICKET},
        )
        text = resp.get_data(as_text=True)
        assert "微信登录失败" in text
        assert "微信授权失败" in text

    def test_create_ticket_requires_open_config(self, monkeypatch):
        monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_ID", "")
        monkeypatch.setitem(app.config, "WECHAT_OPEN_APP_SECRET", "")
        monkeypatch.setattr(
            WeChatService,
            "build_qrconnect_url",
            self._original_build_qrconnect_url,
        )
        resp = self.client.post("/api/user/login/wechat/ticket/")
        body = resp.get_json()
        assert body["success"] is False
        assert "微信扫码登录未开启" in body["message"]

    def test_poll_unknown_ticket_is_expired(self):
        resp = self.client.get("/api/user/login/wechat/ticket/unknown-ticket/")
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["status"] == "expired"
