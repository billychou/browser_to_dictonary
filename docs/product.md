# 产品文档：Vocabulary Book（browser_to_dictonary）

> 基于仓库源码（截至 2026-08 主分支）整理。配套文档：[后续优化思路](./roadmap.md)。

## 1. 产品定位

**一句话描述**：浏览网页时选中单词，一键收入个人云端"词汇书"，并可通过手机号登录在多端沉淀自己的词汇本。

- **目标用户**：英语学习者、需要积累专业术语的阅读者。
- **核心价值**：把"遇到生词 → 记下来"的路径压缩到一次右键点击，不打断阅读流程。
- **产品形态**：Chrome 扩展（Manifest V3）+ 自建后端 API。

## 2. 功能清单（现状）

| 功能 | 入口 | 状态 |
|---|---|---|
| 右键保存选中文本到词汇书 | 网页右键菜单"保存词汇到词汇书" | ✅ 可用 |
| 保存后页面高亮选中文本 | 自动触发（内容脚本 `contents/highlight.ts`） | ✅ 可用（实现较粗糙） |
| 保存成功页面通知 | 右上角绿色 toast，3 秒自动消失 | ✅ 可用 |
| 弹窗手动输入单词保存 | 扩展 popup"词汇书"页 | ✅ 可用 |
| 微信扫码登录（Chrome 扩展） | 扩展 popup 登录页（微信开放平台网站应用） | ✅ 可用，首次登录自动注册；需配置 `WECHAT_OPEN_*` |
| 微信一键登录（小程序） | 小程序登录页（`wx.login` → code2session） | ✅ 可用；需配置 `WECHAT_MINI_*`，未配置回退短信登录 |
| 手机号 + 短信验证码登录 | 小程序登录页兜底（阿里云短信） | ✅ 可用，首次登录自动注册 |
| JWT 令牌签发 | 登录成功后返回，业务接口 `Bearer` 鉴权 | ✅ 可用 |
| 词汇列表展示 / 删除 / 编辑 | 无前端界面 | ❌ 服务层已有 `query/delete/update`，未暴露为完整 API 与 UI |

## 3. 典型用户旅程

1. 用户在任意网页选中一个单词 → 右键"保存词汇到词汇书"。
2. 扩展后台（service worker）将文本 `POST /api/word/`，同时通知内容脚本高亮该文本。
3. 后端按 `(uid, word)` 去重：已存在则刷新 `gmt_update`，否则新增记录。
4. 页面弹出"已保存词汇: xxx"通知。
5. 用户打开 popup：未登录显示登录页（手机号 → 获取验证码 → 登录）；登录后显示手动保存页。

## 4. 系统架构

```
┌────────────────────────────── Chrome Extension (Plasmo MV3) ──────────────────────────────┐
│  popup.tsx (React)          background.ts (service worker)        contents/               │
│  - 登录 / 手动保存界面   ──消息──>  统一代理所有 fetch 请求   ──消息──>  highlight.ts     │
│  - chrome.storage.local         （绕过 CORS）                           notification.ts   │
└───────────────────────────────────────┬───────────────────────────────────────────────────┘
                                        │ HTTP (当前硬编码 http://127.0.0.1:7001)
┌───────────────────────────────────────▼───────────────────────────────────────────────────┐
│  Flask 3 + Flask-RESTful（vocabulary_book_backend）                                        │
│  controllers/（REST 资源） → services/（业务逻辑） → models/（SQLAlchemy ORM）              │
│  extensions/：ext_database / ext_redis / ext_migrate / ext_blueprints / ext_commands       │
│  configs/：pydantic-settings，从 .env 加载（DB_* / REDIS_* / JWT_* / 阿里云短信 AK）        │
└───────────┬───────────────────────────┬───────────────────────────┬───────────────────────┘
            │                           │                           │
        MySQL (vocabulary_word,      Redis (验证码缓存、        阿里云短信服务
        users 表, Flask-Migrate)      迁移分布式锁)            (dysmsapi)
```

**要点**：
- 所有跨域请求集中在 `background.ts` 发起；后端 CORS 仅放行扩展源 `chrome-extension://bpcmapeoloepbomiddaidikkbbaeodjn`。
- 后端采用工厂模式 `app_factory.create_app()` 组装应用；`VbApp` 为自定义 Flask 子类。
- 数据库迁移走 Flask-Migrate（Alembic），CLI 命令 `upgrade-db` 用 Redis 锁防止并发迁移。

## 5. API 接口

统一前缀 `/api`（管理端 `/console/api`），响应大体遵循 `{success, message, data}`。

| 方法 | 路径 | 说明 | 请求体/参数 |
|---|---|---|---|
| POST | `/api/user/login/sms_send/` | 发送短信验证码（6 位数字，Redis 缓存 300s，有效期内防重复发送） | `{"phone": "138..."}` |
| POST | `/api/user/login/` | 校验验证码并登录；用户不存在则自动注册，返回 `user_info` + JWT | `{"phone": "...", "code": "..."}` |
| GET | `/api/user/` | 获取当前用户信息 | ⚠️ 目前返回 mock 数据，未接 JWT 鉴权 |
| POST | `/api/word/` | 保存单词，按 `(uid, word)` 去重 | `{"uid": "...", "word": "..."}` |
| GET | `/api/word/?word=` | 查询单词 | ⚠️ 当前实现为占位（返回 Hello World），真实查询逻辑在 `VocabularyService.query` |
| GET | `/console/api/demo?word=` | 控制台演示接口 | `word` 查询参数 |

## 6. 数据模型

- **users**：`id`、`phone`（唯一）、`wechat_openid`（唯一）、`wechat_unionid`、`nickname`、`avatar`、`is_active`、`gmt_create`、`gmt_update`。
- **vocabulary_word**：`id`、`uid`、`word`、`gmt_create`、`gmt_update`；`(uid, word)` 联合唯一。
  ⚠️ 目前 `uid` 由前端硬编码 `"123"`，与登录用户未关联。

## 7. 关键配置（后端 `.env`）

| 变量组 | 示例变量 | 用途 |
|---|---|---|
| 部署 | `APPLICATION_NAME`、`DEBUG`、`DEPLOY_ENV` | 运行环境 |
| 数据库 | `DB_HOST`、`DB_PORT`、`DB_USERNAME`、`DB_PASSWORD`、`DB_DATABASE` | MySQL（pymysql） |
| Redis | `REDIS_HOST`、`REDIS_PORT`、`REDIS_PASSWORD`、哨兵/集群可选项 | 验证码缓存、迁移锁 |
| JWT | `JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_EXPIRATION_TIME` | 令牌签发/校验 |
| 短信 | `ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`、`SMS_API_KEY`、`SMS_API_SECRET` | 阿里云短信 |

## 8. 技术栈速览

| 层 | 技术 |
|---|---|
| 扩展 | Plasmo 0.90（MV3）、React 18、TypeScript 5、Tailwind CSS 3、pnpm |
| 后端 | Python ≥3.9、Flask 3、Flask-RESTful、Flask-SQLAlchemy、Flask-Migrate、PyJWT、pydantic-settings |
| 存储 | MySQL、Redis |
| 三方服务 | 阿里云短信（dysmsapi）、微信开放平台（小程序 code2session + 网站应用扫码登录）、免费词典 API |
| CI | `.github/workflows/submit.yml`：`pnpm build` + `pnpm package` + bpp 自动提交商店（手动触发） |
