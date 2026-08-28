# 商店上架素材包（Chrome Web Store）

> `submit.yml` 的构建与发布链路已就绪（`pnpm build` → `pnpm package` → bpp 自动提交）。
> 本文档提供全部**文案类素材**；截图与密钥需人工准备（清单见文末）。

## 基本信息

| 项 | 内容 |
| --- | --- |
| 名称 | 生词本 - 划词收藏与复习 |
| 英文名 | Vocabulary Book - Collect & Review Words |
| 一句话简介 | 网页划词一键收藏生词，云端同步，间隔复习 |
| 分类 | Productivity / Education |
| 语言 | 中文（简体）、English |

## 详细描述（中文）

生词本是一个帮助你积累英语词汇的浏览器工具：

- **划词收藏**：在任意网页选中单词或短语，浮层即刻显示音标与释义，一键加入你的生词本；也可以右键「保存词汇到词汇书」。
- **云端同步**：手机号或微信登录，词汇在浏览器扩展、微信小程序之间实时同步，换设备不丢词。
- **间隔复习**：基于艾宾浩斯遗忘曲线（当天 → 1 → 2 → 4 → 7 → 15 天）自动安排复习，小程序端随时刷卡片。
- **数据属于你**：支持一键导出 CSV（Excel/Anki 可导入），随时备份、随时离开。

## Detailed Description (EN)

Vocabulary Book helps you build your vocabulary while browsing:

- **Select-to-save**: select any word or phrase on a page — pronunciation and definitions appear instantly, one click to save. Right-click "Save to vocabulary book" also works.
- **Cloud sync**: sign in with phone or WeChat; your words stay in sync between the extension and the WeChat mini-program.
- **Spaced repetition**: reviews scheduled on an Ebbinghaus curve (today → 1 → 2 → 4 → 7 → 15 days).
- **Your data, yours**: export everything as CSV (Excel/Anki compatible) at any time.

## 权限说明（审核备注用）

| 权限 | 用途 |
| --- | --- |
| `https://*/*`（host） | 在用户浏览的页面上识别选中文本、展示划词浮层与保存通知；向用户自配置的后端地址提交词汇 |
| `storage` | 本地保存登录凭证（JWT）与后端不可达时的待同步队列 |
| `contextMenus` | 右键菜单「保存词汇到词汇书」 |

扩展不注入广告、不收集浏览内容；仅在用户主动划词/右键时处理选中文本。

## 隐私政策（草案）

**生词本隐私政策**

1. 我们收集的数据：注册/登录所需的手机号，你主动收藏的词汇及其释义查询结果，复习进度记录。
2. 用途：仅用于提供词汇收藏、跨端同步与复习提醒功能。
3. 共享：我们不出售、不向第三方共享你的个人数据；释义查询通过匿名请求发送至词典服务，不包含你的身份信息。
4. 存储与安全：数据存储在你自行部署/我们运营的后端数据库，访问需登录凭证；短信验证码与登录令牌均设置有效期。
5. 删除：你可以随时在应用内删除任意词汇；注销/删除账号请联系（此处填写联系邮箱）。
6. 变更：政策如有更新将在本页面公示。

## 待人工准备清单

- [ ] **截图**（1280×800 或 640×400，PNG/JPEG，1-5 张），建议场景：
  1. 网页划词浮层（选中单词，显示释义 + 「加入词汇本」）
  2. 扩展弹窗（词汇列表 + 导出按钮）
  3. 右键菜单保存
  4. 登录页
  5. 小程序复习卡片（可选，拼图）
- [ ] **隐私政策公开网址**（商店要求可访问的 URL，可将上文发布到任意静态页）
- [ ] **联系邮箱**（商店资料 + 隐私政策删除条款）
- [ ] **`SUBMIT_KEYS` secret**（GitHub 仓库 Settings → Secrets）：bpp 格式
  `{"chrome": {"extensionId": "<ID>", "clientId": "...", "clientSecret": "...", "refreshToken": "..."}}`，
  凭据获取见 <https://github.com/fregante/browser-platform-publish>；首次需在开发者后台手动上传一次拿到 extensionId。
- [ ] 在 Actions 中手动运行 `Submit to Web Store` 工作流。
