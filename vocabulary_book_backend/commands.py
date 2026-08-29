#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: commands.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/16
Copyright: @sanfendi
"""
import logging
import pathlib
import sys

import click

current_pathlib = pathlib.Path(__file__).parent.absolute()

sys.path.append(current_pathlib)

from extensions.ext_redis import redis_client


@click.command("upgrade-db", help="Upgrade the database")
def upgrade_db():
    click.echo("Preparing database migration...")
    lock = redis_client.lock(name="db_upgrade_lock", timeout=60)
    if lock.acquire(blocking=False):
        try:
            click.echo(click.style("Starting database migration.", fg="green"))

            # run db migration
            import flask_migrate  # type: ignore

            flask_migrate.upgrade()

            click.echo(click.style("Database migration successful!", fg="green"))

        except Exception:
            logging.exception("Failed to execute database migration")
        finally:
            lock.release()
    else:
        click.echo("Database migration skipped")
