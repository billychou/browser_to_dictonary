#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_word_definition.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

词典释义落库链路集成测试：mock 词典 HTTP，真实写库（CI 提供 MySQL）。
"""
import pytest

import services.vocabulary_service as vocabulary_service_module
from app_factory import create_app
from models import db
from models.user import User
from models.word import Word

app = create_app()

TEST_PHONE = "13900000003"
TEST_WORD = "definition-test-word"

FAKE_DEFINITION = {
    "phonetic": "/test/",
    "definition": "noun. A word used in tests.",
    "detail": [
        {
            "pos": "noun",
            "definitions": [{"definition": "A word used in tests."}],
        }
    ],
}


def _cleanup():
    with app.app_context():
        db.session.query(Word).filter(Word.word == TEST_WORD).delete()
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
        setup_user_and_token.uid = str(user.id)
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
def mock_lookup(monkeypatch):
    """默认 mock 为查询成功，可在用例中覆盖返回值/异常"""
    monkeypatch.setattr(
        vocabulary_service_module.DictionaryClient,
        "lookup",
        staticmethod(lambda word: dict(FAKE_DEFINITION)),
    )


def _delete_test_word():
    with app.app_context():
        db.session.query(Word).filter(Word.word == TEST_WORD).delete()
        db.session.commit()


class TestAddWithDefinition:
    def test_add_enriches_definition(self, mock_lookup):
        _delete_test_word()
        with app.app_context():
            from services.vocabulary_service import VocabularyService

            word = VocabularyService.add(
                uid=setup_user_and_token.uid, word=TEST_WORD
            )
            assert word.phonetic == "/test/"
            assert word.definition == "noun. A word used in tests."
            assert word.detail[0]["pos"] == "noun"
        _delete_test_word()

    def test_add_survives_dictionary_failure(self, monkeypatch):
        def _fail(word):
            raise ConnectionError("network down")

        monkeypatch.setattr(
            vocabulary_service_module.DictionaryClient,
            "lookup",
            staticmethod(_fail),
        )
        _delete_test_word()
        with app.app_context():
            from services.vocabulary_service import VocabularyService

            word = VocabularyService.add(
                uid=setup_user_and_token.uid, word=TEST_WORD
            )
            assert word.id is not None
            assert word.definition is None
        _delete_test_word()

    def test_add_without_definition_when_not_found(self, monkeypatch):
        monkeypatch.setattr(
            vocabulary_service_module.DictionaryClient,
            "lookup",
            staticmethod(lambda word: None),
        )
        _delete_test_word()
        with app.app_context():
            from services.vocabulary_service import VocabularyService

            word = VocabularyService.add(
                uid=setup_user_and_token.uid, word=TEST_WORD
            )
            assert word.definition is None
        _delete_test_word()


class TestDefinitionEndpoint:
    @pytest.fixture(autouse=True)
    def _word(self, auth_header, mock_lookup):
        _delete_test_word()
        resp = app.test_client().post(
            "/api/word/", json={"word": TEST_WORD}, headers=auth_header
        )
        body = resp.get_json()
        assert body["success"] is True
        self.word_id = body["data"]["id"]
        yield
        _delete_test_word()

    def test_post_response_contains_definition(self, client, auth_header):
        resp = client.get(
            "/api/word/", data={"word": TEST_WORD}, headers=auth_header
        )
        body = resp.get_json()
        item = body["data"]["items"][0]
        assert item["phonetic"] == "/test/"
        assert item["definition"] == "noun. A word used in tests."
        assert item["detail"][0]["pos"] == "noun"

    def test_refresh_definition_success(self, client, auth_header, monkeypatch):
        # 模拟首次查询失败后补查成功
        with app.app_context():
            word = db.session.get(Word, self.word_id)
            word.definition = None
            word.phonetic = None
            word.detail = None
            db.session.commit()
        resp = client.put(
            f"/api/word/{self.word_id}/definition", headers=auth_header
        )
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["definition"] == "noun. A word used in tests."

    def test_refresh_definition_not_found(self, client, auth_header, monkeypatch):
        monkeypatch.setattr(
            vocabulary_service_module.DictionaryClient,
            "lookup",
            staticmethod(lambda word: None),
        )
        resp = client.put(
            f"/api/word/{self.word_id}/definition", headers=auth_header
        )
        assert resp.status_code == 400
        assert "未查询到该词的释义" in resp.get_json()["message"]

    def test_refresh_definition_network_error(self, client, auth_header, monkeypatch):
        def _fail(word):
            raise ConnectionError("timeout")

        monkeypatch.setattr(
            vocabulary_service_module.DictionaryClient,
            "lookup",
            staticmethod(_fail),
        )
        resp = client.put(
            f"/api/word/{self.word_id}/definition", headers=auth_header
        )
        assert resp.status_code == 400
        assert "释义查询失败" in resp.get_json()["message"]

    def test_requires_auth(self, client):
        resp = client.put(f"/api/word/{self.word_id}/definition")
        assert resp.status_code == 401
