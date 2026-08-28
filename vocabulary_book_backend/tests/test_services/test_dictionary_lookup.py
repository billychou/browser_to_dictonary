#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_dictionary_lookup.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

词典查询接口（划词即查）集成测试：mock 词典 HTTP 与 Redis，真实用户鉴权（CI 提供 MySQL）。
"""
import pytest

import controllers.dictionary.views as dictionary_views_module
from app_factory import create_app
from models import db
from models.user import User

app = create_app()

TEST_PHONE = "13900000005"

FAKE_DEFINITION = {
    "phonetic": "/həˈləʊ/",
    "definition": "exclamation. Used to express a greeting.",
    "detail": [
        {
            "pos": "exclamation",
            "definitions": [{"definition": "Used to express a greeting."}],
        }
    ],
}


def _cleanup():
    with app.app_context():
        db.session.query(User).filter(User.phone == TEST_PHONE).delete()
        db.session.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_user_and_token():
    _cleanup()
    with app.app_context():
        from services.user_service import UserService

        user = User(phone=TEST_PHONE)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        setup_user_and_token.token = UserService().generate_token(user.id)
    yield
    _cleanup()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {setup_user_and_token.token}"}


@pytest.fixture(autouse=True)
def mock_lookup(monkeypatch):
    monkeypatch.setattr(
        dictionary_views_module.DictionaryClient,
        "lookup",
        staticmethod(lambda word: dict(FAKE_DEFINITION)),
    )


class TestDictionaryLookup:
    def test_lookup_success(self, client, auth_header):
        resp = client.get("/api/dictionary?word=hello", headers=auth_header)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["word"] == "hello"
        assert body["data"]["phonetic"] == "/həˈləʊ/"
        assert body["data"]["definition"].startswith("exclamation.")

    def test_lookup_not_found(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            dictionary_views_module.DictionaryClient,
            "lookup",
            staticmethod(lambda word: None),
        )
        resp = client.get("/api/dictionary?word=asdfqwerty", headers=auth_header)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"] is None
        assert "未查询到" in body["message"]

    def test_requires_auth(self, client):
        resp = client.get("/api/dictionary?word=hello")
        assert resp.status_code == 401

    def test_empty_word(self, client, auth_header):
        resp = client.get("/api/dictionary?word=%20%20", headers=auth_header)
        body = resp.get_json()
        assert body["success"] is False
        assert "单词不能为空" in body["message"]

    def test_rate_limited(self, client, auth_header, monkeypatch):
        from unittest.mock import MagicMock

        from libs.constants import DICT_LOOKUP_LIMIT_PER_MINUTE

        fake_redis = MagicMock()
        fake_redis.incr.return_value = DICT_LOOKUP_LIMIT_PER_MINUTE + 1
        monkeypatch.setattr(dictionary_views_module, "redis_client", fake_redis)

        resp = client.get("/api/dictionary?word=hello", headers=auth_header)
        assert resp.status_code == 400
        assert "查询过于频繁" in resp.get_json()["message"]
