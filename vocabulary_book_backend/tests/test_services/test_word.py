#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: test_word.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/15
Copyright: @sanfendi
"""
from sqlalchemy import select

from app_factory import create_app
from models.word import Word

app = create_app()
from models import db


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


def test_db_label():
    """
    db label
    :return:
    """
    with app.app_context():
        stmt = select(Word).where(Word.word == "hello")
        ret = db.session.execute(stmt).first()
        print(ret)
        word = db.session.scalars(select(Word).where(Word.word == "hello")).first()
        print(word)
