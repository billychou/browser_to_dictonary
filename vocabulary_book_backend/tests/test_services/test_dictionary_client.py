#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_dictionary_client.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/8/29
Copyright: @sanfendi

词典客户端单元测试：mock HTTP，不依赖数据库与外部网络。
"""
from unittest.mock import MagicMock

import pytest

import libs.client.dictionary_client as dictionary_module
from libs.client.dictionary_client import DictionaryClient

ENTRIES = [
    {
        "word": "hello",
        "phonetic": "/həˈləʊ/",
        "phonetics": [{"text": "/həˈləʊ/", "audio": ""}],
        "meanings": [
            {
                "partOfSpeech": "exclamation",
                "definitions": [
                    {
                        "definition": "Used to express a greeting.",
                        "example": "hello there, Katie!",
                    },
                    {"definition": "second definition"},
                ],
            },
            {
                "partOfSpeech": "noun",
                "definitions": [{"definition": "An utterance of hello."}],
            },
        ],
    }
]


def _mock_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class TestNormalize:
    def test_full_structure(self):
        result = DictionaryClient.normalize(ENTRIES)
        assert result["phonetic"] == "/həˈləʊ/"
        assert result["definition"] == (
            "exclamation. Used to express a greeting.\nnoun. An utterance of hello."
        )
        assert len(result["detail"]) == 2
        assert result["detail"][0]["pos"] == "exclamation"
        assert result["detail"][0]["definitions"][0]["example"] == "hello there, Katie!"
        assert len(result["detail"][0]["definitions"]) == 2

    def test_phonetic_fallback_from_phonetics_list(self):
        entries = [dict(ENTRIES[0])]
        entries[0] = {k: v for k, v in entries[0].items() if k != "phonetic"}
        result = DictionaryClient.normalize(entries)
        assert result["phonetic"] == "/həˈləʊ/"

    def test_meanings_truncated_to_five(self):
        entries = [
            {
                "meanings": [
                    {
                        "partOfSpeech": f"pos{i}",
                        "definitions": [{"definition": f"def{i}"}],
                    }
                    for i in range(8)
                ]
            }
        ]
        result = DictionaryClient.normalize(entries)
        assert len(result["detail"]) == 5

    def test_empty_meanings_returns_none(self):
        assert DictionaryClient.normalize([{"meanings": []}]) is None


class TestLookup:
    def test_success(self, monkeypatch):
        monkeypatch.setattr(
            dictionary_module.requests,
            "get",
            lambda url, timeout=None: _mock_response(ENTRIES),
        )
        result = DictionaryClient.lookup("hello")
        assert result["definition"].startswith("exclamation.")

    def test_not_found_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            dictionary_module.requests,
            "get",
            lambda url, timeout=None: _mock_response(
                {"title": "No Definitions Found"}, status_code=404
            ),
        )
        assert DictionaryClient.lookup("asdfqwerty") is None

    def test_server_error_raises(self, monkeypatch):
        def _error(url, timeout=None):
            response = MagicMock()
            response.status_code = 500
            response.raise_for_status.side_effect = Exception("500 Server Error")
            return response

        monkeypatch.setattr(dictionary_module.requests, "get", _error)
        with pytest.raises(Exception):
            DictionaryClient.lookup("hello")

    def test_network_error_raises(self, monkeypatch):
        def _raise(url, timeout=None):
            raise ConnectionError("timeout")

        monkeypatch.setattr(dictionary_module.requests, "get", _raise)
        with pytest.raises(Exception):
            DictionaryClient.lookup("hello")

    def test_empty_word_returns_none(self, monkeypatch):
        assert DictionaryClient.lookup("   ") is None
