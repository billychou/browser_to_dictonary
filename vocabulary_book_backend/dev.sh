#!/usr/bin/env bash
# 本地开发一键启动：MySQL + Redis + 依赖安装 + 迁移 + API（:7001）
# 用法：在 vocabulary_book_backend/ 下执行 ./dev.sh，Ctrl+C 停止
# 首次运行会自动生成 .env（JWT 密钥自动填充），填好 DB_PASSWORD 后重跑
set -euo pipefail
cd "$(dirname "$0")"

MYSQL_PORT=3306
REDIS_PORT=6379
MYSQL_FORMULAS=(mysql mysql@8.4 mysql@8.0)
REDIS_FORMULAS=(redis redis@8.0 redis@7)

log() { echo "==> $*"; }
die() { echo "错误：$*" >&2; exit 1; }

port_open() { nc -z 127.0.0.1 "$1" 2>/dev/null; }

command -v uv >/dev/null 2>&1 || die "未找到 uv，请先安装：brew install uv"

brew_formula_installed() { brew list --versions "$1" >/dev/null 2>&1; }

# 端口已开则跳过；否则用给定的 brew formula 依次尝试拉起服务并等待就绪
ensure_service() {
    local port=$1 name=$2
    shift 2
    if port_open "$port"; then
        log "$name 已在运行"
        return 0
    fi
    command -v brew >/dev/null 2>&1 || die "$name 未运行，且未安装 Homebrew，请手动启动 $name"
    local formula
    for formula in "$@"; do
        if brew_formula_installed "$formula"; then
            log "启动 $name（brew services start $formula）..."
            brew services start "$formula" >/dev/null
            for _ in $(seq 1 30); do
                port_open "$port" && { log "$name 已就绪"; return 0; }
                sleep 1
            done
            die "$name 启动超时，请检查：brew services list"
        fi
    done
    die "$name 未运行，也未安装相关 formula（$*），请先 brew install $1"
}

ensure_service "$MYSQL_PORT" "MySQL" "${MYSQL_FORMULAS[@]}"
ensure_service "$REDIS_PORT" "Redis" "${REDIS_FORMULAS[@]}"

# 首次运行：从模板生成 .env 并自动填充 JWT 密钥
if [[ ! -f .env ]]; then
    log "未找到 .env，从 .env.example 生成"
    cp .env.example .env
    if command -v openssl >/dev/null 2>&1; then
        jwt_secret=$(openssl rand -hex 32)
        sed -i '' "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$jwt_secret|" .env
        log "JWT_SECRET_KEY 已自动生成"
    fi
    echo "请编辑 .env，将 DB_PASSWORD 改为 MySQL 密码后重新运行本脚本。"
    exit 0
fi

env_value() { sed -n "s/^$1=//p" .env | head -n1; }

db_password=$(env_value DB_PASSWORD)
[[ -n "$db_password" && "$db_password" != "your-db-password" ]] \
    || die ".env 的 DB_PASSWORD 未配置，请填写 MySQL 密码后重试"
db_host=$(env_value DB_HOST); db_host=${db_host:-localhost}
db_user=$(env_value DB_USERNAME); db_user=${db_user:-root}
db_name=$(env_value DB_DATABASE); db_name=${db_name:-sanfendi}

log "安装依赖（uv sync）..."
uv sync --quiet

# 确保数据库存在；找不到 mysql 客户端时跳过，交由迁移步骤暴露错误
mysql_client=""
if command -v mysql >/dev/null 2>&1; then
    mysql_client=mysql
elif command -v brew >/dev/null 2>&1; then
    for formula in "${MYSQL_FORMULAS[@]}"; do
        if brew_formula_installed "$formula" && [[ -x "$(brew --prefix "$formula")/bin/mysql" ]]; then
            mysql_client="$(brew --prefix "$formula")/bin/mysql"
            break
        fi
    done
fi
if [[ -n "$mysql_client" ]]; then
    log "确保数据库 $db_name 存在..."
    MYSQL_PWD="$db_password" "$mysql_client" -u"$db_user" -h"$db_host" \
        -e "CREATE DATABASE IF NOT EXISTS \`$db_name\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
else
    log "未找到 mysql 客户端，跳过建库检查"
fi

log "执行数据库迁移..."
uv run flask --app wsgi.py upgrade-db

log "启动 API（端口 7001，Ctrl+C 停止）"
exec uv run python app.py
