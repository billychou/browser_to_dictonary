const api = require("../../utils/request")
const { getUser, getToken, clearSession, isLoggedIn, redirectToLogin } = require("../../utils/auth")
const { getApiBase, setApiBase, DEFAULT_API_BASE } = require("../../config/api")
const review = require("../../utils/review")

Page({
  data: {
    avatarText: "词",
    displayName: "未登录",
    maskedPhone: "",
    stats: { total: 0, mastered: 0, streak: 0 },
    totalReviews: 0,
    apiBase: "",
    defaultApiBase: DEFAULT_API_BASE
  },

  onShow() {
    if (!isLoggedIn()) {
      redirectToLogin()
      return
    }
    this.renderUser()
    this.setData({ apiBase: getApiBase() })
    this.loadStats()
  },

  renderUser() {
    const user = getUser() || {}
    const phone = user.phone || ""
    const name = user.nickname || (phone ? "用户" + phone.slice(-4) : "用户")
    this.setData({
      displayName: name,
      avatarText: (name || "词").slice(0, 1).toUpperCase(),
      maskedPhone: phone ? phone.slice(0, 3) + "****" + phone.slice(7) : "—"
    })
  },

  async loadStats() {
    try {
      const words = await api.fetchAllWords()
      this.setData({
        stats: review.getStats(words),
        totalReviews: review.getTotalReviews(words)
      })
    } catch (err) {
      wx.showToast({ title: err.message, icon: "none" })
    }
  },

  onApiBaseInput(e) {
    this.setData({ apiBase: e.detail.value })
  },

  saveApiBase() {
    const url = this.data.apiBase.trim()
    if (url && !/^https?:\/\//.test(url)) {
      wx.showToast({ title: "地址需以 http:// 或 https:// 开头", icon: "none" })
      return
    }
    setApiBase(url)
    wx.showToast({ title: "已保存", icon: "success" })
  },

  /** 导出全部生词 CSV：下载后转发给用户保存 */
  exportCsv() {
    const token = getToken()
    if (!token) {
      redirectToLogin()
      return
    }
    wx.showLoading({ title: "导出中…" })
    wx.downloadFile({
      url: getApiBase() + "/api/word/export/",
      header: { Authorization: "Bearer " + token },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode !== 200) {
          wx.showToast({ title: "导出失败，请稍后重试", icon: "none" })
          return
        }
        wx.shareFileMessage({
          filePath: res.tempFilePath,
          fileName: "vocabulary.csv",
          success: () => wx.showToast({ title: "已发送，请在聊天中保存", icon: "none" }),
          fail: () => wx.showToast({ title: "取消发送", icon: "none" })
        })
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: "导出失败，请检查网络或服务地址", icon: "none" })
      }
    })
  },

  logout() {
    wx.showModal({
      title: "退出登录",
      content: "退出后需重新登录才能访问生词数据",
      confirmColor: "#fa5151",
      success: (res) => {
        if (!res.confirm) return
        clearSession()
        wx.reLaunch({ url: "/pages/login/login" })
      }
    })
  }
})
