#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_word_review.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

间隔复习接口集成测试：真实写库（CI 提供 MySQL），JWT 全链路。
"""
from datetime import datetime, timedelta

import pytest

from app_factory import create_app
from libs.constants import REVIEW_FUZZY_DELAY_MINUTES
from libs.constants import REVIEW_INTERVAL_DAYS
from libs.constants import REVIEW_MASTERED_STAGE
from models import db
from models.user import User
from models.word import Word

app = create_app()

TEST_PHONE = "13900000001"
TEST_UID = None
TEST_WORD = "review-test-word"


def _cleanup():
    with app.app_context():
        db.session.query(Word).filter(Word.word == TEST_WORD).delete()
        db.session.query(User).filter(User.phone == TEST_PHONE).delete()
        db.session.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_user_and_token():
    """创建测试用户并签发 JWT"""
    global TEST_UID
    _cleanup()
    with app.app_context():
        from services.user_service import UserService

        user = User(phone=TEST_PHONE)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        TEST_UID = str(user.id)
        setup_user_and_token.token = UserService().generate_token(user.id)
    yield
    _cleanup()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {setup_user_and_token.token}"}


@pytest.fixture
def word_id(auth_header):
    """每个用例新建一条词汇，用例后删除"""
    with app.app_context():
        db.session.query(Word).filter(Word.word == TEST_WORD).delete()
        db.session.commit()
    resp = app.test_client().post(
        "/api/word/", json={"word": TEST_WORD}, headers=auth_header
    )
    body = resp.get_json()
    assert body["success"] is True
    yield body["data"]["id"]
    with app.app_context():
        db.session.query(Word).filter(Word.word == TEST_WORD).delete()
        db.session.commit()


def _review(client, auth_header, word_id, result):
    return client.put(
        f"/api/word/{word_id}/review",
        json={"result": result},
        headers=auth_header,
    )


def _seconds(value):
    """解析响应中的时间字段"""
    return datetime.fromisoformat(str(value))


class TestWordReview:
    def test_requires_auth(self, client, word_id):
        resp = client.put(f"/api/word/{word_id}/review", json={"result": "known"})
        assert resp.status_code == 401

    def test_known_advances_stage_and_schedules_next(self, client, auth_header, word_id):
        resp = _review(client, auth_header, word_id, "known")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        data = body["data"]
        assert data["stage"] == 1
        assert data["review_count"] == 1
        due = _seconds(data["due"])
        expected = REVIEW_INTERVAL_DAYS[1]
        delta = (due - datetime.now()).total_seconds()
        assert (expected - 0.1) * 86400 < delta < (expected + 0.1) * 86400

    def test_known_to_mastered(self, client, auth_header, word_id):
        for i in range(REVIEW_MASTERED_STAGE + 1):
            resp = _review(client, auth_header, word_id, "known")
            assert resp.get_json()["success"] is True
        body = _review(client, auth_header, word_id, "known").get_json()
        # 已达最高级，继续「认识」保持最高级
        assert body["data"]["stage"] == REVIEW_MASTERED_STAGE

    def test_unknown_resets_stage_and_counts_lapse(self, client, auth_header, word_id):
        _review(client, auth_header, word_id, "known")
        _review(client, auth_header, word_id, "known")
        resp = _review(client, auth_header, word_id, "unknown")
        data = resp.get_json()["data"]
        assert data["stage"] == 0
        assert data["lapse_count"] == 1
        # 立即到期（重新排入队列）
        delta = (_seconds(data["due"]) - datetime.now()).total_seconds()
        assert abs(delta) < 60

    def test_fuzzy_keeps_stage_and_delays_minutes(self, client, auth_header, word_id):
        _review(client, auth_header, word_id, "known")
        resp = _review(client, auth_header, word_id, "fuzzy")
        data = resp.get_json()["data"]
        assert data["stage"] == 1
        delta = (_seconds(data["due"]) - datetime.now()).total_seconds()
        assert (REVIEW_FUZZY_DELAY_MINUTES - 1) * 60 < delta < (REVIEW_FUZZY_DELAY_MINUTES + 1) * 60

    def test_invalid_result(self, client, auth_header, word_id):
        resp = _review(client, auth_header, word_id, "maybe")
        assert resp.status_code == 400
        assert "无效的复习结果" in resp.get_json()["message"]

    def test_cannot_review_others_word(self, client, word_id):
        with app.app_context():
            from services.user_service import UserService

            other = User(phone="13900000002")
            db.session.add(other)
            db.session.flush()
            db.session.commit()
            other_token = UserService().generate_token(other.id)
            other_id = other.id
        try:
            resp = client.put(
                f"/api/word/{word_id}/review",
                json={"result": "known"},
                headers={"Authorization": f"Bearer {other_token}"},
            )
            assert resp.status_code == 400
            assert "无权操作" in resp.get_json()["message"]
        finally:
            with app.app_context():
                db.session.query(User).filter(User.id == other_id).delete()
                db.session.commit()

    def test_list_response_contains_progress_fields(self, client, auth_header, word_id):
        _review(client, auth_header, word_id, "known")
        resp = client.get("/api/word/", headers=auth_header)
        body = resp.get_json()
        assert body["success"] is True
        item = next(i for i in body["data"]["items"] if i["id"] == word_id)
        assert item["stage"] == 1
        assert item["review_count"] == 1
        assert item["due"] is not None
        assert item["last_review"] is not None
