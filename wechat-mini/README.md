# 生词本 · 微信小程序端

浏览器插件的移动端伴侣：随时查看**我的生词**、利用碎片时间**间隔复习**、跟踪**学习进度**。
原生小程序实现，无第三方依赖、无构建步骤；与浏览器插件共用 `vocabulary_book_backend` 同一套账号与数据，手机号一致即自动同步。

## 功能

| 页面 | 功能 |
| --- | --- |
| 登录 | 微信一键登录（`wx.login` code → `jscode2session`，需后端配置小程序凭据）；未配置时回退手机号 + 短信验证码 |
| 生词本 | 全量词汇、本地模糊搜索、手动添加、编辑、删除、下拉刷新 |
| 复习 | 艾宾浩斯间隔复习卡片（认识 / 模糊 / 不认识），今日待复习/已复习统计 |
| 我的 | 用户信息、学习数据（总词数/已掌握/累计复习/连续天数）、服务地址配置、退出登录 |

## 目录结构

```
wechat-mini/
├── app.js / app.json / app.wxss   # 入口、路由与 tabBar、全局样式
├── config/api.js                  # 服务地址配置（dev 默认 http://127.0.0.1:7001）
├── utils/
│   ├── request.js                 # 统一请求层：JWT 注入、401 处理、业务接口封装
│   ├── auth.js                    # JWT 存取与本地过期判断
│   ├── review.js                  # 间隔复习调度与学习进度统计
│   └── date.js                    # 时间格式化
└── pages/                         # login / words / study / profile
```

## 本地运行

1. 启动后端：`cd vocabulary_book_backend && uv run python src/vocabulary_book_backend/app.py`（需 MySQL/Redis 与 `.env`）。
2. 微信开发者工具「导入项目」，目录选择 `wechat-mini/`（AppID 可用测试号）。
3. 详情 → 本地设置 → 勾选「不校验合法域名」（开发环境连本地 7001 必需）。
4. 编译后用手机号验证码登录，即可看到与浏览器插件一致的词汇。

## 依赖的后端接口

| 接口 | 说明 |
| --- | --- |
| `POST /api/user/login/wechat/` | 微信一键登录：`{code}` → `{user_info, token}`（按 openid 登录/注册） |
| `POST /api/user/login/sms_send/` | 发送短信验证码 |
| `POST /api/user/login/` | 手机号登录/注册，返回 `{user_info, token}` |
| `GET /api/word/?page=&limit=` | 分页词汇列表（JWT） |
| `POST /api/word/` · `PUT /api/word/<id>` · `DELETE /api/word/<id>` | 增/改/删（JWT） |

## 复习算法

等级 0-5 对应间隔 `当天 → 1 → 2 → 4 → 7 → 15` 天：「认识」升级排期，「模糊」10 分钟后重现，「不认识」回零级立即重排；达到 5 级计为「已掌握」。从未复习的新词自动进入当日队列。

## 已知限制与规划

- **学习进度存本机**（`wx.storage`）：后端词汇表暂无进度字段，跨设备同步待后端补充字段后迁移（见 `docs/roadmap.md`）。
- **微信一键登录依赖后端配置**：后端 `.env` 需配置 `WECHAT_MINI_APP_ID` / `WECHAT_MINI_APP_SECRET`（微信公众平台 → 开发管理获取）；未配置时该入口返回明确错误，用户可回退短信登录。
- **生产发布**：需将 `project.config.json` 中 `touristappid` 换成正式 AppID，服务端必须 HTTPS 并在微信公众平台配置 request 合法域名。
