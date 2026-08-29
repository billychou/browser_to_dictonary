#!/usr/bin/env bash
# 容器启动脚本：先执行数据库迁移，再启动 gunicorn
set -euo pipefail

cd /app

echo "==> Running database migrations (upgrade-db)..."
uv run flask --app wsgi.py upgrade-db

echo "==> Starting gunicorn..."
exec uv run gunicorn -c /app/deploy/gunicorn.conf.py wsgi:app
