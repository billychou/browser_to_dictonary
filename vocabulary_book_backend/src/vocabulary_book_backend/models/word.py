#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: word.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @三分地技术有限公司
"""
from .engine import db


class Word(db.Model):
    __tablename__ = "vocabulary_word"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="vocabulary_pkid"),
    )
    id = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.String(64), nullable=False)
    word = db.Column(db.String(64), nullable=False)
    gmt_create = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    gmt_update = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

