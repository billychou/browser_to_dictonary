#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: user.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/11/05
Copyright: @sanfendi
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped

from .engine import db


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="user_pkid"),
        db.UniqueConstraint("phone", name="user_phone_unique"),
        db.UniqueConstraint("wechat_openid", name="user_wechat_openid_unique"),
    )
    
    id: Mapped[int] = db.Column(db.Integer, nullable=False, autoincrement=True)
    phone: Mapped[Optional[str]] = db.Column(db.String(20), nullable=True)
    wechat_openid: Mapped[Optional[str]] = db.Column(db.String(128), nullable=True)
    wechat_unionid: Mapped[Optional[str]] = db.Column(db.String(128), nullable=True)
    nickname: Mapped[Optional[str]] = db.Column(db.String(128), nullable=True)
    avatar: Mapped[Optional[str]] = db.Column(db.String(512), nullable=True)
    is_active: Mapped[bool] = db.Column(db.Boolean, nullable=False, default=True)
    gmt_create: Mapped[datetime] = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    gmt_update: Mapped[datetime] = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    def __repr__(self):
        return f"<User id={self.id}, phone={self.phone}, wechat_openid={self.wechat_openid}>"

    def to_dict(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "wechat_openid": self.wechat_openid,
            "wechat_unionid": self.wechat_unionid,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "is_active": self.is_active,
        }
