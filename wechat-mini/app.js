const { isLoggedIn, clearSession } = require("./utils/auth")

App({
  onLaunch() {
    // 启动时清理过期登录态，避免带无效 JWT 请求
    if (!isLoggedIn()) {
      clearSession()
    }
  }
})
