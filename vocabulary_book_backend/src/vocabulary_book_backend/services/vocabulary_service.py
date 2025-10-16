#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: vocabulary_service.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from typing import List

from sqlalchemy import select

from models import db
from models.word import Word


class VocabularyService:
    @staticmethod
    def add(**kwargs):
        """
        添加单词
        :param kwargs:
        :return:
        """
        uid = kwargs.get("uid", None)
        word = kwargs.get("word", None)
        if uid is None or word is None:
            raise Exception("Invalid parameters")
        word = db.session.execute(
            select(Word).where(Word.uid == uid, Word.word == word)
        ).first()
        if word:
            word.gmt_update = db.func.now()
            db.session.add(word)
            db.session.commit()
            return word
        word = Word(**kwargs)
        db.session.add(word)
        db.session.commit()
        return word

    @staticmethod
    def delete(id: int = None):
        """
        delete
        :return:
        """
        pass

    @staticmethod
    def update(**kwargs):
        pass

    @staticmethod
    def query(**kwargs) -> List[Word]:
        """
        query
        :param kwargs:
        :return:
        """
        filters = []
        for k, v in kwargs.items():
            if k == "uid":
                filters.append(Word.uid == v)
            elif k == "word":
                filters.append(Word.word == v)
        stmt = select(Word).where(*filters)
        words = db.session.execute(stmt).scalars().all()
        return words
