#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
File: views.py
Author: songchuan.zhou(651265044@qq.com)
Date: 2026/9/1
Copyright: @sanfendi
"""
from flask import Response, make_response

from controllers.home import bp

REPO_URL = "https://github.com/billychou/browser_to_dictonary"

# 单文件自包含落地页：内联 CSS，无外部资源、无 JS、无模板占位符（纯静态字符串，勿用 .format()，CSS 大括号会冲突）
_LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>生词本 · Vocabulary Book</title>
<meta name="description" content="选中网页单词，一键收入云端词汇书。Chrome 扩展 + 微信小程序 + Flask 后端，多端同步，间隔复习。">
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         background: #f6f7f9; color: #1f2329; line-height: 1.7; }
  a { color: #4361ee; }
  .container { max-width: 960px; margin: 0 auto; padding: 0 20px; }

  .hero { padding: 72px 0 48px; text-align: center; }
  .hero-icon { width: 76px; height: 76px; margin: 0 auto 20px; display: block; }
  .hero h1 { font-size: 34px; margin: 0 0 12px; letter-spacing: .5px; }
  .hero .tagline { font-size: 17px; color: #5a6472; margin: 0 auto 30px; max-width: 560px; }
  .actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
  .btn { display: inline-block; padding: 11px 26px; border-radius: 10px; text-decoration: none;
         font-size: 15px; font-weight: 600; transition: opacity .15s ease; }
  .btn:hover { opacity: .88; }
  .btn-primary { background: #4361ee; color: #fff; }
  .btn-secondary { background: #fff; color: #1f2329; border: 1px solid #d8dde5; }

  section { margin: 48px 0; }
  h2 { font-size: 22px; text-align: center; margin: 0 0 26px; }

  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
  .card { background: #fff; border-radius: 12px; padding: 22px 20px;
          box-shadow: 0 2px 10px rgba(15, 23, 42, .05); }
  .card .icon { font-size: 26px; line-height: 1; }
  .card h3 { font-size: 16px; margin: 12px 0 6px; }
  .card p { font-size: 14px; color: #5a6472; margin: 0; }

  .install-block { background: #fff; border-radius: 12px; padding: 24px 26px;
                   box-shadow: 0 2px 10px rgba(15, 23, 42, .05); margin-bottom: 16px; }
  .install-block h3 { font-size: 17px; margin: 0 0 12px; }
  .install-block ol { margin: 0; padding-left: 22px; font-size: 14.5px; color: #3c4350; }
  .install-block li { margin-bottom: 6px; }
  .install-block .note { font-size: 13px; color: #8a9099; margin: 10px 0 0; }
  pre { background: #1f2329; color: #e8eaed; padding: 14px 16px; border-radius: 8px;
        overflow-x: auto; font-size: 13px; line-height: 1.6; margin: 12px 0 0; }
  code { font-family: "SF Mono", Menlo, Consolas, monospace; }
  p code, li code, .note code { background: #eef0f4; border-radius: 4px; padding: 1px 6px;
        font-size: .92em; color: #333c4d; }

  .tech { text-align: center; }
  .badge { display: inline-block; background: #eef1ff; color: #4361ee; border-radius: 999px;
           padding: 5px 14px; font-size: 13px; margin: 4px 3px; }

  footer { padding: 36px 0 52px; text-align: center; color: #8a9099; font-size: 13.5px; }
  footer .links { margin-bottom: 10px; }
  footer .links a { margin: 0 10px; text-decoration: none; }

  @media (max-width: 600px) {
    .hero { padding: 48px 0 32px; }
    .hero h1 { font-size: 27px; }
    .install-block { padding: 20px 18px; }
  }
</style>
</head>
<body>
  <header class="hero">
    <div class="container">
      <svg class="hero-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="生词本图标">
        <rect width="64" height="64" rx="14" fill="#4361ee"/>
        <path d="M32 20.5c-3.1-2.3-7.2-3.5-11.5-3.5V43c4.3 0 8.4 1.2 11.5 3.5 3.1-2.3 7.2-3.5 11.5-3.5V17c-4.3 0-8.4 1.2-11.5 3.5z" fill="#ffffff" opacity=".95"/>
        <path d="M32 20.5V46.5" stroke="#4361ee" stroke-width="2"/>
      </svg>
      <h1>生词本 · Vocabulary Book</h1>
      <p class="tagline">选中网页单词，一键收入云端词汇书。Chrome 扩展划词收藏，微信小程序间隔复习，多端数据实时同步。</p>
      <div class="actions">
        <a class="btn btn-primary" href="#install">安装指南</a>
        <a class="btn btn-secondary" href="__REPO_URL__" target="_blank" rel="noopener">GitHub 仓库</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section id="features">
      <h2>核心功能</h2>
      <div class="grid">
        <div class="card">
          <div class="icon">✍️</div>
          <h3>划词收藏</h3>
          <p>网页上选中单词即弹出浮层，展示音标与释义，右键或点击按钮一键保存。</p>
        </div>
        <div class="card">
          <div class="icon">✨</div>
          <h3>即时反馈</h3>
          <p>保存成功后页面高亮已收藏单词并弹出提示，收藏状态一目了然。</p>
        </div>
        <div class="card">
          <div class="icon">☁️</div>
          <h3>多端同步</h3>
          <p>Chrome 扩展与微信小程序共用同一账号，生词数据云端同步，随时随地查看。</p>
        </div>
        <div class="card">
          <div class="icon">🔁</div>
          <h3>间隔复习</h3>
          <p>艾宾浩斯记忆曲线安排复习（当天 → 1 → 2 → 4 → 7 → 15 天），卡片式作答巩固记忆。</p>
        </div>
        <div class="card">
          <div class="icon">📤</div>
          <h3>数据导出</h3>
          <p>生词一键导出为 CSV，兼容 Excel 与 Anki，数据自由迁移。</p>
        </div>
        <div class="card">
          <div class="icon">🔐</div>
          <h3>账号体系</h3>
          <p>微信扫码 / 手机号登录，JWT 鉴权，词汇增删改查安全可靠。</p>
        </div>
      </div>
    </section>

    <section id="install">
      <h2>安装指南</h2>

      <div class="install-block">
        <h3>1. Chrome 扩展</h3>
        <ol>
          <li>从 <a href="__REPO_URL__" target="_blank" rel="noopener">GitHub 仓库</a> 下载源码（或 GitHub Actions 中的构建产物 zip）并解压；</li>
          <li>在 <code>vocabulary-book/</code> 目录构建扩展：<pre><code>git clone __REPO_URL__.git
cd browser_to_dictonary/vocabulary-book
pnpm install &amp;&amp; pnpm build</code></pre></li>
          <li>打开 <code>chrome://extensions</code>，开启右上角「开发者模式」；</li>
          <li>点击「加载已解压的扩展程序」，选择构建产物目录 <code>build/chrome-mv3-prod</code>。</li>
        </ol>
        <p class="note">安装后登录账号即可使用；商店版本上架后将在此补充商店链接。</p>
      </div>

      <div class="install-block">
        <h3>2. 微信小程序</h3>
        <ol>
          <li>打开微信开发者工具，选择「导入项目」；</li>
          <li>目录选择仓库内的 <code>wechat-mini/</code>（测试 AppID 即可）；</li>
          <li>本地调试请勾选「不校验合法域名」，服务地址指向 <code>http://127.0.0.1:7001</code>。</li>
        </ol>
        <p class="note">与扩展使用同一账号，生词数据自动同步。</p>
      </div>

      <div class="install-block">
        <h3>3. 后端服务</h3>
        <ol>
          <li>依赖 Python ≥ 3.9、uv、Homebrew 版 MySQL 与 Redis；</li>
          <li>一键启动（自动拉起 MySQL/Redis、生成 <code>.env</code>、执行迁移并监听 <code>:7001</code>）：<pre><code>cd vocabulary_book_backend
./dev.sh</code></pre></li>
          <li>验证服务：<code>curl http://127.0.0.1:7001/console/api/demo</code>。</li>
        </ol>
        <p class="note">手动配置与生产部署分别见 <a href="__REPO_URL__/blob/main/docs/local-development.md" target="_blank" rel="noopener">本地开发文档</a> 与 <a href="__REPO_URL__/blob/main/docs/deployment.md" target="_blank" rel="noopener">部署文档</a>。</p>
      </div>
    </section>

    <section class="tech">
      <h2>技术栈</h2>
      <span class="badge">Plasmo (MV3)</span>
      <span class="badge">React</span>
      <span class="badge">TypeScript</span>
      <span class="badge">Tailwind CSS</span>
      <span class="badge">Flask</span>
      <span class="badge">SQLAlchemy</span>
      <span class="badge">MySQL</span>
      <span class="badge">Redis</span>
    </section>
  </main>

  <footer>
    <div class="links">
      <a href="__REPO_URL__" target="_blank" rel="noopener">GitHub</a>
      <a href="__REPO_URL__/blob/main/docs/api.md" target="_blank" rel="noopener">API 文档</a>
      <a href="__REPO_URL__/blob/main/docs/local-development.md" target="_blank" rel="noopener">本地开发</a>
      <a href="__REPO_URL__/blob/main/docs/deployment.md" target="_blank" rel="noopener">部署</a>
    </div>
    <p>生词本 Vocabulary Book · 网页划词取词，云端词汇管理</p>
  </footer>
</body>
</html>
""".replace("__REPO_URL__", REPO_URL)


@bp.route("/", methods=["GET"])
def index() -> Response:
    """项目落地页：介绍生词本功能与安装方式"""
    response = make_response(_LANDING_PAGE_HTML)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response
