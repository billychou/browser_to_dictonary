#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: vocabulary_service.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func, select

from libs.constants import REVIEW_FUZZY_DELAY_MINUTES
from libs.constants import REVIEW_INTERVAL_DAYS
from libs.constants import REVIEW_MASTERED_STAGE
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

    @staticmethod
    def list_by_user(
        uid: str, word: str = None, page: int = 1, limit: int = 50
    ) -> tuple[List[Word], int]:
        """
        分页查询某个用户的词汇列表，按最近更新时间倒序
        :param uid: 用户ID（字符串）
        :param word: 可选，单词精确过滤
        :param page: 页码，从 1 开始
        :param limit: 每页条数
        :return: (当前页数据, 总数)
        """
        page = max(page, 1)
        limit = max(min(limit, 200), 1)
        filters = [Word.uid == uid]
        if word:
            filters.append(Word.word == word)
        total = db.session.execute(
            select(func.count(Word.id)).where(*filters)
        ).scalar() or 0
        stmt = (
            select(Word)
            .where(*filters)
            .order_by(Word.gmt_update.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        words = db.session.execute(stmt).scalars().all()
        return list(words), int(total)

    @staticmethod
    def get_owned(uid: str, word_id: int) -> Word:
        """
        获取属于该用户的词汇记录，不存在或不属于该用户时抛出异常
        :param uid: 用户ID（字符串）
        :param word_id: 词汇记录ID
        :return:
        """
        word = db.session.execute(
            select(Word).where(Word.id == word_id, Word.uid == uid)
        ).scalars().first()
        if not word:
            raise Exception("词汇不存在或无权操作")
        return word

    @staticmethod
    def delete_owned(uid: str, word_id: int) -> None:
        """
        删除属于该用户的词汇记录
        :param uid: 用户ID（字符串）
        :param word_id: 词汇记录ID
        """
        word = VocabularyService.get_owned(uid, word_id)
        db.session.delete(word)
        db.session.commit()

    @staticmethod
    def review_owned(uid: str, word_id: int, result: str) -> Word:
        """
        记录一次间隔复习结果并更新排期，规则与小程序端一致：
        - known   升一级（上限最高级），按新等级间隔排期，达到最高级即已掌握
        - fuzzy   等级不变，稍后（分钟级）重新复习
        - unknown 回到 0 级并立即重新排入队列
        :param uid: 用户ID（字符串）
        :param word_id: 词汇记录ID
        :param result: known | fuzzy | unknown
        :return: 更新后的词汇记录
        """
        if result not in ("known", "fuzzy", "unknown"):
            raise Exception("无效的复习结果")
        word = VocabularyService.get_owned(uid, word_id)
        now = datetime.now()
        word.review_count = (word.review_count or 0) + 1
        word.last_review = now
        if result == "known":
            word.stage = min((word.stage or 0) + 1, REVIEW_MASTERED_STAGE)
            word.due = now + timedelta(days=REVIEW_INTERVAL_DAYS[word.stage])
        elif result == "fuzzy":
            word.due = now + timedelta(minutes=REVIEW_FUZZY_DELAY_MINUTES)
        else:
            word.stage = 0
            word.lapse_count = (word.lapse_count or 0) + 1
            word.due = now
        db.session.add(word)
        db.session.commit()
        return word

    @staticmethod
    def update_owned(uid: str, word_id: int, word_text: str) -> Word:
        """
        更新属于该用户的词汇内容
        :param uid: 用户ID（字符串）
        :param word_id: 词汇记录ID
        :param word_text: 新的单词/短语内容
        :return:
        """
        if not word_text or not word_text.strip():
            raise Exception("词汇内容不能为空")
        word = VocabularyService.get_owned(uid, word_id)
        word.word = word_text.strip()
        word.gmt_update = db.func.now()
        db.session.add(word)
        db.session.commit()
        return word
