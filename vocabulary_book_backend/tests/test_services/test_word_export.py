#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_word_export.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

词汇 CSV 导出接口集成测试：mock 词典 HTTP，真实写库（CI 提供 MySQL）。
"""
import csv
import io

import pytest

import services.vocabulary_service as vocabulary_service_module
from app_factory import create_app
from models import db
from models.user import User
from models.word import Word

app = create_app()

TEST_PHONE = "13900000004"
TEST_WORDS = ["export-alpha", "export-beta"]

FAKE_DEFINITION = {
    "phonetic": "/ekˈspɔːt/",
    "definition": "noun. A test definition,\nwith multiple lines.",
    "detail": [
        {"pos": "noun", "definitions": [{"definition": "A test definition."}]}
    ],
}


def _cleanup():
    with app.app_context():
        db.session.query(Word).filter(Word.word.in_(TEST_WORDS)).delete(
            synchronize_session=False
        )
        db.session.query(User).filter(User.phone == TEST_PHONE).delete()
        db.session.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_user_and_token(monkeypatch_module=None):
    _cleanup()
    with app.app_context():
        from services.user_service import UserService

        user = User(phone=TEST_PHONE)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        setup_user_and_token.uid = str(user.id)
        setup_user_and_token.token = UserService().generate_token(user.id)
    yield
    _cleanup()


@pytest.fixture(autouse=True)
def mock_lookup(monkeypatch):
    monkeypatch.setattr(
        vocabulary_service_module.DictionaryClient,
        "lookup",
        staticmethod(lambda word: dict(FAKE_DEFINITION)),
    )


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def auth_header():
    return {"Authorization": f"Bearer {setup_user_and_token.token}"}


@pytest.fixture
def seeded_words(client, auth_header):
    ids = []
    for w in TEST_WORDS:
        resp = client.post("/api/word/", json={"word": w}, headers=auth_header)
        body = resp.get_json()
        assert body["success"] is True
        ids.append(body["data"]["id"])
    yield ids
    with app.app_context():
        db.session.query(Word).filter(Word.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.session.commit()


class TestWordExport:
    def test_export_csv_success(self, client, auth_header, seeded_words):
        resp = client.get("/api/word/export/", headers=auth_header)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["Content-Type"]
        assert "attachment" in resp.headers["Content-Disposition"]
        assert "vocabulary_" in resp.headers["Content-Disposition"]

        text = resp.get_data(as_text=True)
        assert text.startswith("\ufeff")
        rows = list(csv.reader(io.StringIO(text.lstrip("\ufeff"))))
        assert rows[0] == [
            "word",
            "phonetic",
            "definition",
            "stage",
            "review_count",
            "gmt_create",
        ]
        words_in_csv = {r[0] for r in rows[1:]}
        assert set(TEST_WORDS) <= words_in_csv
        row = next(r for r in rows[1:] if r[0] == "export-alpha")
        assert row[1] == "/ekˈspɔːt/"
        assert "A test definition," in row[2]

    def test_export_requires_auth(self, client):
        resp = client.get("/api/word/export/")
        assert resp.status_code == 401
