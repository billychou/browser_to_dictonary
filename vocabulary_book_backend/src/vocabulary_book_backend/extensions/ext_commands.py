#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: ext_commands.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/16
Copyright: @sanfendi
"""
from vb_app import VbApp


def init_app(app: VbApp):
    from commands import (
        upgrade_db,
    )

    cmds_to_register = [
        upgrade_db,
    ]
    for cmd in cmds_to_register:
        app.cli.add_command(cmd)
