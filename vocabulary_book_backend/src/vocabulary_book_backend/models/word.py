#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: word.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped

from .engine import db


class Word(db.Model):
    __tablename__ = "vocabulary_word"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="vocabulary_pkid"),
        db.UniqueConstraint("uid", "word", name="vocabulary_unique"),
    )
    id: Mapped[int] = db.Column(db.Integer, nullable=False, autoincrement=True)
    uid: Mapped[str] = db.Column(db.String(64), nullable=False)
    word: Mapped[str] = db.Column(db.String(64), nullable=False)
    # 间隔复习进度（艾宾浩斯），由 /api/word/<id>/review 维护
    stage: Mapped[int] = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    due: Mapped[Optional[datetime]] = db.Column(db.DateTime, nullable=True)
    review_count: Mapped[int] = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    lapse_count: Mapped[int] = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    last_review: Mapped[Optional[datetime]] = db.Column(db.DateTime, nullable=True)
    # 词典释义（保存时尽力而为查询，可经接口补查）
    phonetic: Mapped[Optional[str]] = db.Column(db.String(128), nullable=True)
    definition: Mapped[Optional[str]] = db.Column(db.Text, nullable=True)
    detail: Mapped[Optional[dict]] = db.Column(db.JSON, nullable=True)
    gmt_create: Mapped[datetime] = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    gmt_update: Mapped[datetime] = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self):
        return f"<VocabularyWord id={self.id}>"
