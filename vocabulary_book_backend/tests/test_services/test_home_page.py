#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_home_page.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/9/1
Copyright: @sanfendi

落地页路由测试：纯静态页面，不查库、不依赖 MySQL/Redis。
"""
import pytest

from app_factory import create_app

app = create_app()

REPO_URL = "https://github.com/billychou/browser_to_dictonary"


@pytest.fixture
def client():
    return app.test_client()


class TestHomePage:
    def test_returns_html_with_utf8_charset(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        content_type = resp.headers["Content-Type"]
        assert "text/html" in content_type
        assert "charset=utf-8" in content_type

    def test_contains_key_content(self, client):
        text = client.get("/").get_data(as_text=True)
        assert "生词本" in text
        assert "选中网页单词，一键收入云端词汇书" in text
        assert REPO_URL in text
        assert "chrome://extensions" in text
        assert "wechat-mini" in text
        assert "dev.sh" in text
