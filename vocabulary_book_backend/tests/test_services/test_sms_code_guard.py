#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_sms_code_guard.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/28
Copyright: @sanfendi

短信验证码校验逻辑单元测试：mock Redis，不依赖真实 MySQL/Redis。
"""
from unittest.mock import MagicMock

import pytest

import services.user_service as user_service_module
from libs.constants import CACHE_SMS_CODE_ERR_MAX
from libs.constants import CACHE_SMS_CODE_ERR_PREFIX
from libs.constants import CACHE_SMS_CODE_PREFIX
from libs.constants import CACHE_SMS_CODE_TIMEOUT
from services.user_service import UserService

PHONE = "13800000000"
CODE = "123456"


def _code_key(phone: str) -> str:
    return f"{CACHE_SMS_CODE_PREFIX}:{phone}"


def _err_key(phone: str) -> str:
    return f"{CACHE_SMS_CODE_ERR_PREFIX}:{phone}"


@pytest.fixture
def fake_redis(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(user_service_module, "redis_client", fake)
    return fake


def _stub_get(fake_redis, stored_code: bytes = None, err_count: bytes = None):
    def get(key):
        if key == _code_key(PHONE):
            return stored_code
        if key == _err_key(PHONE):
            return err_count
        return None

    fake_redis.get.side_effect = get


class TestVerifySmsCode:
    def test_verify_success_consumes_code_and_clears_error_count(self, fake_redis):
        _stub_get(fake_redis, stored_code=CODE.encode("utf-8"))

        UserService.verify_sms_code(PHONE, CODE)

        fake_redis.delete.assert_any_call(_err_key(PHONE))
        fake_redis.delete.assert_any_call(_code_key(PHONE))
        fake_redis.incr.assert_not_called()

    def test_wrong_code_increments_error_count(self, fake_redis):
        _stub_get(fake_redis, stored_code=CODE.encode("utf-8"))

        with pytest.raises(Exception, match="无效的验证码"):
            UserService.verify_sms_code(PHONE, "000000")

        fake_redis.incr.assert_called_once_with(_err_key(PHONE))
        fake_redis.expire.assert_called_once_with(
            _err_key(PHONE), CACHE_SMS_CODE_TIMEOUT
        )

    def test_lockout_after_max_wrong_attempts_even_with_correct_code(self, fake_redis):
        _stub_get(
            fake_redis,
            stored_code=CODE.encode("utf-8"),
            err_count=str(CACHE_SMS_CODE_ERR_MAX).encode("utf-8"),
        )

        with pytest.raises(Exception, match="错误次数过多"):
            UserService.verify_sms_code(PHONE, CODE)

        fake_redis.incr.assert_not_called()

    def test_expired_or_missing_code(self, fake_redis):
        _stub_get(fake_redis, stored_code=None)

        with pytest.raises(Exception, match="验证码已过期"):
            UserService.verify_sms_code(PHONE, CODE)
