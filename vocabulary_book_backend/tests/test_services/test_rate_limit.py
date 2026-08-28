#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_rate_limit.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

接口频控单元测试：mock Redis 与短信客户端，不依赖真实服务。
"""
from unittest.mock import MagicMock

import pytest

import services.user_service as user_service_module
import services.vocabulary_service as vocabulary_service_module
from libs.constants import CACHE_SMS_DAILY_PREFIX
from libs.constants import CACHE_SMS_DAILY_TIMEOUT
from libs.constants import SMS_DAILY_LIMIT
from services.user_service import UserService

PHONE = "13800000009"


@pytest.fixture
def fake_redis(monkeypatch):
    fake = MagicMock()
    fake.get.return_value = None
    monkeypatch.setattr(user_service_module, "redis_client", fake)
    return fake


@pytest.fixture
def fake_sms(monkeypatch):
    sms = MagicMock()
    monkeypatch.setattr(user_service_module, "SmsClient", sms)
    return sms


class TestSmsDailyLimit:
    def test_within_limit_sends(self, fake_redis, fake_sms):
        fake_redis.incr.return_value = 1

        UserService.send_sms_code(PHONE)

        fake_sms.send.assert_called_once()

    def test_first_send_sets_expiry(self, fake_redis, fake_sms):
        fake_redis.incr.return_value = 1

        UserService.send_sms_code(PHONE)

        fake_redis.expire.assert_called_once_with(
            f"{CACHE_SMS_DAILY_PREFIX}:{PHONE}", CACHE_SMS_DAILY_TIMEOUT
        )

    def test_over_daily_limit_blocked_without_sending(self, fake_redis, fake_sms):
        fake_redis.incr.return_value = SMS_DAILY_LIMIT + 1

        with pytest.raises(Exception, match="次数过多"):
            UserService.send_sms_code(PHONE)

        fake_sms.send.assert_not_called()

    def test_at_limit_still_sends(self, fake_redis, fake_sms):
        fake_redis.incr.return_value = SMS_DAILY_LIMIT

        UserService.send_sms_code(PHONE)

        fake_sms.send.assert_called_once()


class TestWordAddLimit:
    def test_over_minute_limit_raises_before_db(self, monkeypatch):
        from libs.constants import WORD_ADD_LIMIT_PER_MINUTE

        fake = MagicMock()
        fake.incr.return_value = WORD_ADD_LIMIT_PER_MINUTE + 1
        monkeypatch.setattr(vocabulary_service_module, "redis_client", fake)

        from services.vocabulary_service import VocabularyService

        with pytest.raises(Exception, match="添加过于频繁"):
            VocabularyService.add(uid="1", word="hello")
