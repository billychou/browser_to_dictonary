const api = require("../../utils/request")
const { setSession } = require("../../utils/auth")

Page({
  data: {
    phone: "",
    code: "",
    countdown: 0,
    loading: false,
    wxLoading: false,
    message: ""
  },

  timer: null,

  onUnload() {
    if (this.timer) clearInterval(this.timer)
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value, message: "" })
  },

  onCodeInput(e) {
    this.setData({ code: e.detail.value, message: "" })
  },

  /** 微信一键登录：wx.login 拿 code → 后端 code2session → JWT */
  wechatLogin() {
    this.setData({ wxLoading: true, message: "" })
    wx.login({
      success: (res) => {
        if (!res.code) {
          this.setData({ wxLoading: false, message: "微信授权失败，请重试" })
          return
        }
        api
          .wechatLogin(res.code)
          .then((data) => {
            setSession(data.token, data.user_info)
            wx.reLaunch({ url: "/pages/words/words" })
          })
          .catch((err) => {
            // 后端未配置小程序凭据时微信登录不可用，引导走短信登录
            this.setData({ message: err.message })
          })
          .finally(() => this.setData({ wxLoading: false }))
      },
      fail: () => {
        this.setData({ wxLoading: false, message: "微信授权失败，请检查网络" })
      }
    })
  },

  validPhone() {
    if (!/^1\d{10}$/.test(this.data.phone)) {
      this.setData({ message: "请输入正确的 11 位手机号" })
      return false
    }
    return true
  },

  sendCode() {
    if (this.data.countdown > 0 || !this.validPhone()) return
    api
      .sendSmsCode(this.data.phone)
      .then(() => {
        wx.showToast({ title: "验证码已发送", icon: "none" })
        this.setData({ countdown: 60 })
        this.timer = setInterval(() => {
          const next = this.data.countdown - 1
          this.setData({ countdown: next })
          if (next <= 0) clearInterval(this.timer)
        }, 1000)
      })
      .catch((err) => this.setData({ message: err.message }))
  },

  submit() {
    if (!this.validPhone()) return
    if (!/^\d{4,6}$/.test(this.data.code)) {
      this.setData({ message: "请输入验证码" })
      return
    }
    this.setData({ loading: true, message: "" })
    api
      .login(this.data.phone, this.data.code)
      .then((data) => {
        setSession(data.token, data.user_info)
        wx.reLaunch({ url: "/pages/words/words" })
      })
      .catch((err) => this.setData({ message: err.message }))
      .finally(() => this.setData({ loading: false }))
  }
})
