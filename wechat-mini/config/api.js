/**
 * 服务端地址配置。
 * 与浏览器插件共用同一个 vocabulary_book_backend 服务。
 *
 * - 开发：微信开发者工具中勾选「不校验合法域名」，默认连本地 7001 端口
 * - 生产：小程序要求 HTTPS，需在微信公众平台配置 request 合法域名，
 *   并把 PROD_API_BASE 改为线上域名
 */
const DEFAULT_API_BASE = "http://127.0.0.1:7001"
const PROD_API_BASE = ""

const STORAGE_KEY = "vb_api_base"

function getApiBase() {
  const custom = wx.getStorageSync(STORAGE_KEY)
  if (custom) return custom.replace(/\/+$/, "")
  if (PROD_API_BASE) return PROD_API_BASE.replace(/\/+$/, "")
  return DEFAULT_API_BASE
}

function setApiBase(url) {
  wx.setStorageSync(STORAGE_KEY, (url || "").trim())
}

module.exports = { getApiBase, setApiBase, DEFAULT_API_BASE }
