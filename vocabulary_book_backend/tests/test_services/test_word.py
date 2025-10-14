#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_word.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/15
Copyright: @sanfendi
"""
from app_factory import create_app
app = create_app()


def test_query_word():
    """
    test
    :return:
    """
    with app.app_context():
        from services.vocabulary_service import VocabularyService
        words = VocabularyService.query(word="hello")
        for i in words:
            print(i.name)
            print(i.word)


