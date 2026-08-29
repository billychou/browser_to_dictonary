#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: ext_migrate.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/16
Copyright: @sanfendi
"""
from vb_app import VbApp


def init_app(app: VbApp):
    import flask_migrate  # type: ignore

    from extensions.ext_database import db

    flask_migrate.Migrate(app, db)
