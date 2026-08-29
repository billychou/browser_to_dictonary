# 后端生产镜像：uv 安装依赖，gunicorn 启动，启动时自动执行数据库迁移
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 从官方镜像复制 uv 二进制，避免安装时联网下载
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先拷贝依赖清单利用构建缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-cache

# 应用代码与 pyproject 同级，无关文件由 .dockerignore 排除
COPY . .

EXPOSE 7001

ENTRYPOINT ["/app/deploy/docker-entrypoint.sh"]
