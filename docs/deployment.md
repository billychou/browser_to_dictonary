# 部署与运维指南

> 配套文档：[product.md](./product.md)、[roadmap.md](./roadmap.md)。

## 部署架构

```
Chrome 扩展 ──HTTPS──▶ Nginx(443) ──▶ gunicorn(7001) ──▶ Flask API
                                          │
                                 ┌────────┴────────┐
                               MySQL 8           Redis 7
```

- 后端为无状态 WSGI 应用，可水平扩容；会话凭证为 JWT，不依赖服务端 session。
- 数据库迁移通过 `upgrade-db` CLI 命令执行（Redis 分布式锁防并发），容器启动时自动运行。
- **扩展商店版本要求 HTTPS**：生产环境必须由 Nginx 等反代终结 TLS，并同步修改：
  - 后端 `.env` 的 `CORS_ORIGINS` 配置为正式扩展源；
  - 扩展构建时设置 `PLASMO_PUBLIC_API_BASE=https://api.your-domain.com`。

## 环境配置

复制 `vocabulary_book_backend/.env.example` 为 `src/vocabulary_book_backend/.env` 并填写：

| 必填 | 说明 |
|---|---|
| `DB_PASSWORD` / `DB_HOST` / `DB_DATABASE` | MySQL 连接 |
| `REDIS_HOST` / `REDIS_PORT` | Redis（验证码缓存、迁移锁） |
| `JWT_SECRET_KEY` | 随机长字符串（`openssl rand -hex 32`），未配置时接口直接报 500 |
| `ALIBABA_CLOUD_ACCESS_KEY_*` / `SMS_API_*` | 阿里云短信 |
| `WECHAT_MINI_APP_ID` / `WECHAT_MINI_APP_SECRET` | 可选，微信小程序一键登录；留空时仅短信登录可用 |
| `DICTIONARY_API_BASE` / `DICTIONARY_TIMEOUT` | 可选，词典释义查询（默认免费 Free Dictionary API）；生产机需可访问外网 |

## 方式一：Docker Compose（推荐）

```bash
cd vocabulary_book_backend
docker compose up -d --build     # MySQL + Redis + API，健康检查就绪后启动
docker compose logs -f api       # 查看迁移与启动日志
```

- 启动脚本 `deploy/docker-entrypoint.sh`：先 `flask upgrade-db` 迁移，再启动 gunicorn。
- 数据持久化在 `mysql_data` / `redis_data` 卷中。
- 升级流程：更新代码后 `docker compose up -d --build`，迁移自动执行。

## 方式二：裸机部署（systemd）

```bash
cd vocabulary_book_backend
uv sync --locked --no-install-project
cd src/vocabulary_book_backend
uv run flask --app wsgi.py upgrade-db        # 手动迁移
```

`/etc/systemd/system/vocabulary-book-api.service`：

```ini
[Unit]
Description=Vocabulary Book API
After=network.target mysql.service redis.service

[Service]
WorkingDirectory=/opt/browser_to_dictonary/vocabulary_book_backend
EnvironmentFile=/opt/browser_to_dictonary/vocabulary_book_backend/src/vocabulary_book_backend/.env
ExecStart=/opt/browser_to_dictonary/vocabulary_book_backend/.venv/bin/gunicorn -c deploy/gunicorn.conf.py wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

进程数用 `WEB_CONCURRENCY` 覆盖（默认 `2×CPU+1`），端口用 `BIND` 覆盖（默认 `0.0.0.0:7001`）。

## Nginx 反代示例

```nginx
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;
    # ssl_certificate / ssl_certificate_key ...

    location /api/ {
        proxy_pass http://127.0.0.1:7001;
        proxy_set_header Authorization $http_authorization;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

## 扩展发布

- `pnpm build && pnpm package` 生成 `build/chrome-mv3-prod.zip`。
- CI：`Frontend CI` 工作流每次构建上传 zip 产物；商店自动提交在仓库根 `.github/workflows/submit.yml`（手动触发，需配置 `SUBMIT_KEYS` secret）。

## 常用运维命令

```bash
uv run flask --app wsgi.py upgrade-db   # 手动执行迁移
uv run pytest tests/ -v                 # 运行测试（需 MySQL/Redis）
docker compose ps / logs / down         # 容器管理
```
