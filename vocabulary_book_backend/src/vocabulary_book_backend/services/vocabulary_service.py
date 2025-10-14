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
        word = Word(**kwargs)
        db.session.add(word)
        db.session.commit()
        return word

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
