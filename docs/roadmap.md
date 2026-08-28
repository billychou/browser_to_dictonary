# 后续优化思路

> 基于源码走读（2026-08）整理，按优先级分组。每项标注现状依据，便于排期与验收。

## P0 — 安全与正确性（应尽快修复）

### 1. 打通登录态与词汇数据（当前链路是断的）
- **现状**：登录成功拿到 JWT 后仅存入 `chrome.storage.local`；`background.ts` 保存单词时 `uid` 硬编码 `"123"`，请求不带 `Authorization`；后端 `/api/word/`、`/api/user/` 均无鉴权。
- **优化**：保存/查询/删除单词接口统一携带 JWT，后端用中间件校验并从 token 解析真实 `user_id`；`vocabulary_word.uid` 与 `users.id` 建立外键关系。这是"多用户产品"成立的前提。

### 2. 移除硬编码密钥与默认口令
- **现状**：`configs/middleware/database_config.py` 中 `DB_PASSWORD` 默认值为真实口令；`send_sms_code` 用 `print` 输出验证码。
- **优化**：敏感配置改为必填（无默认值）强制走 `.env`；删除验证码打印，改为受控日志；把 `.env` 加入 `.gitignore`（当前根 `.gitignore` 未覆盖）。

### 3. 接口地址与 CORS 可配置化
- **现状**：`background.ts` 中后端地址硬编码 `http://127.0.0.1:7001`；`app_factory.py` 中 CORS 硬编码单个扩展 ID。
- **优化**：扩展侧按构建环境注入 `API_BASE`（dev/prod）；生产必须 HTTPS（商店上架要求）。CORS 白名单改为配置项，支持多个扩展 ID。

### 4. 验证码防爆破
- **现状**：验证码 300s 有效，仅有"有效期内防重复发送"，无错误次数限制，6 位纯数字可枚举。
- **优化**：同一手机号验证码错误 ≥5 次即失效；可选增加图形验证或单号每日发送上限。

## P1 — 产品闭环（让用户真正"用起来"）

1. **词汇列表页**：把 `GET /api/word/` 从占位实现改为真实分页查询，在 popup（或独立 options 页）展示我的词汇书，支持搜索。
2. **删除与编辑**：`VocabularyService.delete/update` 已存在但未暴露为 API；补充 `DELETE /api/word/<id>`、`PUT /api/word/<id>` 与对应 UI。
3. **单词详情**：保存时接入词典 API（释义、音标、例句），保存的不再只是字符串，复习价值大幅提升。
4. **保存失败兜底**：当前后端不可达时单词直接丢失。增加本地待发队列（`chrome.storage`），恢复后自动重试；失败时给出红色 toast。
5. **高亮逻辑修正**：现实现对全页文本节点做字符串切分替换，可能破坏页面结构且会高亮所有同名词。改为仅高亮用户实际选区（基于 `Range`/`Selection` API）。
6. **登录态治理**：popup 仅凭 `userInfo` 是否存在判断登录；应校验 JWT 过期时间，过期自动回到登录页并清理存储。

## P2 — 工程质量

1. **统一请求层**：`background.ts` 中 4 段几乎相同的 `fetch` 模板收敛为 `apiRequest(action, payload)`；前后端约定统一的 `{success, message, data}` 类型（TypeScript 接口定义）。
2. **测试**：现有 `tests/` 依赖真实 MySQL/Redis（集成测试）。补充 mock 掉 DB/Redis/短信客户端的服务层单元测试；接入 GitHub Actions 跑 `pytest` 与 `tsc`/`prettier` 检查。
3. **统一响应与错误码**：后端用 `ExternalApi` 或装饰器统一包装响应与异常，避免各 Resource 手写 try/except。
4. **API 文档**：引入 OpenAPI/Swagger 自动生成（如 flask-smorest），替代手工维护的接口表。
5. **部署**：目前只有 `python app.py` 本地跑法。补 `gunicorn`/Dockerfile 与部署说明；规范 migrations 流程（当前已出现 merge 迁移文件）。
6. **限流**：对保存单词、发送短信接口做频控（Redis 计数器即可），防刷短信费用。
7. **微信登录收尾**：`WeChatService` 代码完整但未接路由；决策"接通"或"删除"，避免死代码。

## P3 — 增长与体验

1. **商店上架**：`submit.yml` 已具备 bpp 自动提交能力，补齐商店素材（截图、描述、隐私声明）后发布；同步考虑 Edge / Firefox。
2. **间隔复习**：小程序端（`wechat-mini`）已实现艾宾浩斯复习卡片（认识/模糊/不认识，间隔 当天→1→2→4→7→15 天），进度暂存本机；下一步把进度迁移到后端（`vocabulary_word` 增加等级/到期时间字段或新增复习记录表），实现跨设备同步；复习卡片同时依赖 P1-3 词典释义补全。
3. **数据导出**：支持导出 CSV / Anki 牌组，降低用户迁移顾虑。
4. **划词即查**：选中即弹出小浮层显示释义 + "加入词汇书"按钮，比右键菜单少一步。
5. **多端同步**：提供 Web 端词汇书页面，账号数据天然云端化（依赖 P0-1 完成）。
6. **小程序微信一键登录**：现有 `WeChatService` 是网站 OAuth 流程且未注册路由；为小程序新增 `jscode2session`（code2session → openid 登录/注册）接口后，小程序端可静默登录，免短信验证码。

## 建议落地顺序

```
P0-1 登录态打通 ──▶ P1-1/2 列表与删改 ──▶ P1-3 词典详情 ──▶ P3-2 复习
      │
      └─▶ P0-2/3/4 安全加固（可并行）
P2 工程项穿插在以上各阶段，作为每个功能的验收标准（测试 + CI）
```
