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
    def add(**kwargs) -> Word:
        """
        添加单词
        :param kwargs:
        :return:
        """
        uid = kwargs.get("uid", None)
        word = kwargs.get("word", None)
        if uid is None or word is None:
            raise Exception("Invalid parameters")
        result = db.session.execute(
            select(Word).where(Word.uid == uid, Word.word == word)
        ).scalars().first()
        if result:
            result.gmt_update = db.func.now()
            db.session.add(result)
            db.session.commit()
            return result
        word = Word(**kwargs)
        db.session.add(word)
        db.session.commit()
        return word

    @staticmethod
    def delete(id: int):
        """
        delete
        :param id: int
        :return:
        """
        result = db.session.execute(select(Word).where(Word.id == id)).first()
        if not result:
            raise Exception("word not exist")
        word = result[0] if isinstance(result, tuple) else result
        db.session.delete(word)
        db.session.commit()

    @staticmethod
    def update(**kwargs) -> Word:
        """
        update
        :param kwargs:
        :return:
        """
        vocabulary_id = kwargs.get("id", None)
        if vocabulary_id is None:
            raise Exception("Invalid parameters")
        result = db.session.execute(select(Word).where(Word.id == vocabulary_id)).first()
        if not result:
            raise Exception("word not exist")
        
        word = result[0] if isinstance(result, tuple) else result

        for key, value in kwargs.items():
            if key == "id":
                continue
            setattr(word, key, value)
        word.gmt_update = db.func.now()
        db.session.add(word)
        db.session.commit()
        return word

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
