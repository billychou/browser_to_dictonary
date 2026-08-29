# 本地开发指南（非 Docker）

> 面向 macOS（Homebrew）；Linux 安装方式不同但流程一致。
> 生产/容器化部署见 `docs/deployment.md`。

## 1. 前置工具

| 工具 | 安装 | 说明 |
| --- | --- | --- |
| Homebrew | <https://brew.sh> | macOS 包管理 |
| Python ≥ 3.12 | `brew install python` | 后端运行时 |
| uv | `brew install uv` | 后端依赖管理（推荐） |
| Node.js ≥ 22 + pnpm | `brew install node pnpm` | 扩展构建 |
| 微信开发者工具 | <https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html> | 仅小程序需要 |

## 2. MySQL 与 Redis

```bash
brew install mysql redis
brew services start mysql    # 后台启动
brew services start redis

# 建库（默认库名 sanfendi，与 .env.example 一致）
mysql -uroot -e "CREATE DATABASE IF NOT EXISTS sanfendi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

为 root 设置密码（或创建专用账号），并记入 `.env` 的 `DB_PASSWORD`：

```bash
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'your-db-password';"
```

验证：`mysql -uroot -p -e "SELECT 1"`、`redis-cli ping`（应返回 `PONG`）。

## 3. 后端

```bash
cd vocabulary_book_backend
uv sync                                  # 安装依赖到 .venv

# 配置文件（.env 已被 .gitignore 忽略，切勿提交）
cp .env.example .env
```

编辑 `.env`：

- `DB_PASSWORD`：与上一步 MySQL 密码一致
- `JWT_SECRET_KEY`：必填，`openssl rand -hex 32` 生成；缺失时接口直接 500
- 可选：`WECHAT_OPEN_*`（扩展微信扫码登录）、`WECHAT_MINI_*`（小程序微信登录）、`ALIBABA_CLOUD_*` / `SMS_*`（短信登录）、`DICTIONARY_*`（词典，默认免费源）

```bash
uv run flask --app wsgi.py upgrade-db    # 数据库迁移（首次必做）
uv run python app.py                     # 启动，监听 7001
```

冒烟检查：

```bash
curl http://127.0.0.1:7001/console/api/demo   # 返回 hello 类响应即正常
```

## 4. Chrome 扩展

```bash
cd vocabulary-book
pnpm install
pnpm dev                                 # 产物在 build/chrome-mv3-dev（热重载）
```

Chrome 打开 `chrome://extensions` → 开启「开发者模式」→「加载已解压的扩展程序」→ 选择 `vocabulary-book/build/chrome-mv3-dev`。

扩展默认请求 `http://127.0.0.1:7001`；如需指向其它地址，构建时注入环境变量 `PLASMO_PUBLIC_API_BASE`。

扩展使用微信扫码登录：点击弹窗「微信扫码登录」→ 新标签页打开微信官方二维码页 → 手机微信扫码确认。依赖后端配置 `WECHAT_OPEN_APP_ID` / `WECHAT_OPEN_APP_SECRET` / `WECHAT_OPEN_REDIRECT_URI`（微信开放平台「网站应用」，需公网可访问的回调地址，本地开发可用内网穿透）；未配置时发起登录会提示「微信扫码登录未开启」。未登录时保存的单词会暂存在本地，登录成功后自动同步。

## 5. 微信小程序

1. 微信开发者工具「导入项目」→ 目录选择 `wechat-mini/`（AppID 可用测试号）。
2. 详情 → 本地设置 → 勾选「不校验合法域名…」（本地联调 7001 必需）。
3. 编译后即可登录（短信登录需后端配置阿里云短信密钥）。

## 6. 运行测试

```bash
cd vocabulary_book_backend
uv run python tests/setup_schema.py      # 建表（首次或新库）
uv run pytest tests/ -v                  # 需 MySQL/Redis 运行中
```

纯 mock 的单元测试（短信防爆破、微信 code2session、词典客户端、限流、响应包装）不依赖外部服务。

## 7. 常见问题

| 现象 | 排查 |
| --- | --- |
| 7001 端口被占用 | `lsof -i :7001` 找到进程并结束，或改 `.env` 端口配置 |
| MySQL 连接被拒 | 核对 `.env` 的 `DB_*`；确认 `brew services list` 中 mysql 为 started |
| 登录接口 500 | 未配置 `JWT_SECRET_KEY` |
| 扩展微信登录提示未开启 | 未配置 `WECHAT_OPEN_*`；开放平台网站应用需公网回调地址，本地联调需内网穿透并把穿透域名填入回调配置 |
| 短信验证码发不出 | 本地无 mock，需真实阿里云短信密钥；仅验证词汇接口可跳过登录流程直接造数据 |
| 小程序请求失败 | 未勾选「不校验合法域名」，或服务地址配置错误（我的 → 服务地址） |
| 划词浮层不出现 | 检查扩展是否加载 `chrome-mv3-dev` 产物；仅英文单词/短语会触发 |
