/**
 * 统一请求层：包装 wx.request，自动附加 JWT，处理 401 与统一响应结构。
 * 后端响应约定：{ success, message, data }
 */
const { getApiBase } = require("../config/api")
const { getToken, clearSession, redirectToLogin } = require("./auth")

function request(path, options = {}) {
  const { method = "GET", data, auth = true } = options
  return new Promise((resolve, reject) => {
    const header = { "Content-Type": "application/json" }
    if (auth) {
      const token = getToken()
      if (!token) {
        clearSession()
        redirectToLogin()
        reject(new Error("未登录"))
        return
      }
      header.Authorization = "Bearer " + token
    }
    wx.request({
      url: getApiBase() + path,
      method,
      data,
      header,
      timeout: 10000,
      success(res) {
        if (res.statusCode === 401) {
          clearSession()
          redirectToLogin()
          reject(new Error("登录已过期，请重新登录"))
          return
        }
        const body = res.data || {}
        if (res.statusCode >= 200 && res.statusCode < 300 && body.success !== false) {
          resolve(body.data)
          return
        }
        reject(new Error(body.message || "请求失败（" + res.statusCode + "）"))
      },
      fail() {
        reject(new Error("网络异常，请检查网络或「我的-服务地址」配置"))
      }
    })
  })
}

/* ---------- 业务接口 ---------- */

// 发送短信验证码
function sendSmsCode(phone) {
  return request("/api/user/login/sms_send/", {
    method: "POST",
    data: { phone },
    auth: false
  })
}

// 微信一键登录：wx.login 的 code 换取 JWT（不存在自动注册）
function wechatLogin(code) {
  return request("/api/user/login/wechat/", {
    method: "POST",
    data: { code },
    auth: false
  })
}

// 手机号 + 验证码登录（不存在自动注册）
function login(phone, code) {
  return request("/api/user/login/", {
    method: "POST",
    data: { phone, code },
    auth: false
  })
}

// 当前用户信息（注意：该路由注册为 /api/user，无尾斜杠）
function fetchUserInfo() {
  return request("/api/user")
}

// 分页查询词汇列表（后端 word 参数为精确匹配）
function fetchWords({ word = "", page = 1, limit = 20 } = {}) {
  return request("/api/word/", { data: { word, page, limit } })
}

// 拉取全部词汇（复习用，最多 5 页 * 200 条）
async function fetchAllWords() {
  const items = []
  for (let page = 1; page <= 5; page++) {
    const data = await fetchWords({ page, limit: 200 })
    items.push(...(data.items || []))
    if (!data.items || data.items.length < 200 || items.length >= data.total) break
  }
  return items
}

function addWord(word) {
  return request("/api/word/", { method: "POST", data: { word } })
}

function updateWord(wordId, word) {
  return request("/api/word/" + wordId, { method: "PUT", data: { word } })
}

function deleteWord(wordId) {
  return request("/api/word/" + wordId, { method: "DELETE" })
}

module.exports = {
  request,
  sendSmsCode,
  wechatLogin,
  login,
  fetchUserInfo,
  fetchWords,
  fetchAllWords,
  addWord,
  updateWord,
  deleteWord
}
