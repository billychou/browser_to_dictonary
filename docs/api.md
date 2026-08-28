# API 参考

> 后端：`vocabulary_book_backend`（Flask + Flask-RESTful），默认端口 7001。
> 消费端：Chrome 扩展（`vocabulary-book/`）、微信小程序（`wechat-mini/`）。

## 通用约定

- **鉴权**：需要登录的接口携带 `Authorization: Bearer <JWT>`（HS256，30 天有效期，`POST /api/user/login/` 签发）。
- **统一响应结构**：`{ "success": bool, "message": string, "data": object | null }`。
- **状态码**：200 成功；400 业务错误（含统一响应体）；401 未登录/凭证失效；404 路由不存在。
- **时间字段**：ISO 8601（如 `2026-08-29T23:09:00`）。

## 词汇对象字段

| 字段 | 说明 |
| --- | --- |
| `id` / `uid` / `word` | 记录 ID / 属主用户 / 单词 |
| `stage` / `due` | 复习等级（0-5）/ 下次到期时间；`due` 为空表示新词（立即可复习） |
| `review_count` / `lapse_count` / `last_review` | 复习次数 / 忘记次数 / 最近复习时间 |
| `phonetic` / `definition` / `detail` | 音标 / 释义文本 / 结构化释义（词性+义项+例句） |
| `gmt_create` / `gmt_update` | 创建 / 更新时间 |

## 用户与登录

| 接口 | 鉴权 | 说明 |
| --- | --- | --- |
| `POST /api/user/login/sms_send/` | 否 | 发送短信验证码 `{phone}`。300s 防重发；同一手机号每日上限 10 次 |
| `POST /api/user/login/` | 否 | 手机号登录/注册 `{phone, code}` → `{user_info, token}` |
| `POST /api/user/login/wechat/` | 否 | 小程序一键登录 `{code}`（wx.login 凭证）→ `{user_info, token}`；未配置 `WECHAT_MINI_APP_ID/SECRET` 时返回业务错误 |
| `GET /api/user` | 是 | 当前用户信息（注意：无尾斜杠） |

## 词汇管理

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/word/` | GET | 分页列表 `?word=&page=&limit=`（`word` 为精确匹配；按 `gmt_update` 倒序；limit ≤ 200） |
| `/api/word/` | POST | 添加 `{word}`，按 `(uid, word)` 去重；自动尽力查询词典释义；每用户每分钟上限 120 次 |
| `/api/word/<id>` | PUT | 更新内容 `{word}` |
| `/api/word/<id>` | DELETE | 删除 |
| `/api/word/<id>/review` | PUT | 记录复习 `{result: known/fuzzy/unknown}`，服务端统一排期（间隔 当天→1→2→4→7→15 天） |
| `/api/word/<id>/definition` | PUT | 补查词典释义（保存时查询失败可重试） |
| `/api/word/export/` | GET | 导出本人全部词汇为 CSV（UTF-8 BOM，Excel/Anki 可导入） |

## 词典

| 接口 | 说明 |
| --- | --- |
| `GET /api/dictionary?word=` | 实时释义查询（不落库），每用户每分钟上限 30 次；无收录时 `success: true, data: null` |

## 环境变量

见 `vocabulary_book_backend/.env.example` 与 `docs/deployment.md`：`DB_*`、`REDIS_*`、`JWT_SECRET_KEY`（必填）、`ALIBABA_CLOUD_*`/`SMS_*`（短信）、`WECHAT_MINI_*`（小程序登录）、`DICTIONARY_*`（词典，可选）。
