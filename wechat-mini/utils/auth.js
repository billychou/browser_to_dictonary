/**
 * 登录态管理：JWT 与用户信息的本地存取、过期判断。
 * 与浏览器插件使用同一套 JWT（HS256，payload.user_id，30 天有效期），
 * 同一手机号登录两端，词汇数据天然一致。
 */
const TOKEN_KEY = "vb_token"
const USER_KEY = "vb_user"

function getToken() {
  return wx.getStorageSync(TOKEN_KEY) || ""
}

function getUser() {
  return wx.getStorageSync(USER_KEY) || null
}

function setSession(token, userInfo) {
  wx.setStorageSync(TOKEN_KEY, token)
  wx.setStorageSync(USER_KEY, userInfo || {})
}

function clearSession() {
  wx.removeStorageSync(TOKEN_KEY)
  wx.removeStorageSync(USER_KEY)
}

/** 解析 JWT payload（不做签名校验，仅用于本地过期判断） */
function parseJwt(token) {
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")
    const padded = base64 + "=".repeat((4 - (base64.length % 4)) % 4)
    const binary = wx.base64ToArrayBuffer(padded)
    const bytes = new Uint8Array(binary)
    let str = ""
    for (let i = 0; i < bytes.length; i++) {
      str += String.fromCharCode(bytes[i])
    }
    // payload 为纯 ASCII（user_id/exp/iat），UTF-8 解码失败不影响解析
    try {
      str = decodeURIComponent(escape(str))
    } catch (e) {}
    return JSON.parse(str)
  } catch (e) {
    return null
  }
}

/** 本地判断登录态：有 token 且未过期 */
function isLoggedIn() {
  const token = getToken()
  if (!token) return false
  const payload = parseJwt(token)
  if (!payload || !payload.exp) return false
  return payload.exp * 1000 > Date.now()
}

/** 未登录或登录过期时跳转到登录页（避免重复跳转） */
function redirectToLogin() {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]
  if (current && current.route === "pages/login/login") return
  wx.reLaunch({ url: "/pages/login/login" })
}

module.exports = {
  getToken,
  getUser,
  setSession,
  clearSession,
  parseJwt,
  isLoggedIn,
  redirectToLogin
}
