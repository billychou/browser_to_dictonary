#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: ext_blueprints.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @三分地技术有限公司
"""

from flask import Flask


def init_app(app: Flask):
    """
    register blueprint routers
    """
    from controllers.console import bp as console_app_bp
    app.register_blueprint(console_app_bp)
