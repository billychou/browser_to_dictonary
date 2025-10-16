#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: app_factory.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2025/10/14
Copyright: @sanfendi
"""
import logging
import time

from flask_cors import CORS

from configs import app_config
from vb_app import VbApp


def create_flask_app_with_configs() -> VbApp:
    """
    create a raw flask app
    with configs loaded from .env file
    """
    vb_app = VbApp(__name__)
    vb_app.config.from_mapping(app_config.model_dump())
    return vb_app


def cors_app(app: VbApp):
    """
    add cors to app
    :param app:
    :return:
    """
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "chrome-extension://bpcmapeoloepbomiddaidikkbbaeodjn",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "Accept"],
                "supports_credentials": True,
            }
        },
    )


def initialize_extensions(app: VbApp):
    from extensions import (
        ext_database,
        ext_blueprints,
        ext_commands,
        ext_redis,
        ext_migrate,
    )

    extensions = [ext_database, ext_blueprints, ext_commands, ext_redis, ext_migrate]
    for ext in extensions:
        short_name = ext.__name__.split(".")[-1]
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True
        if not is_enabled:
            if app_config.DEBUG:
                logging.info(f"Skipped {short_name}")
            continue

        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if app_config.DEBUG:
            logging.info(
                f"Loaded {short_name} ({round((end_time - start_time) * 1000, 2)} ms)"
            )


def create_migrations_app():
    app = create_flask_app_with_configs()
    from extensions import ext_database, ext_migrate

    # Initialize only required extensions
    ext_database.init_app(app)
    ext_migrate.init_app(app)

    return app


def create_app() -> VbApp:
    """
    Create app
    :return: VbApp
    """
    start_time = time.perf_counter()
    app = create_flask_app_with_configs()
    cors_app(app)
    initialize_extensions(app)
    end_time = time.perf_counter()
    if app_config.DEBUG:
        logging.info(
            f"Finished create_app ({round((end_time - start_time) * 1000, 2)} ms)"
        )
    return app
