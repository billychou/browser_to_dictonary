// 创建上下文菜单项
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "saveVocabulary",
    title: "保存词汇到词汇书",
    contexts: ["selection"] // 只在选中文本时显示
  })
})

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "saveVocabulary") {
    // 获取选中的文本
    const selectedText = info.selectionText

    // 向内容脚本发送消息以高亮选中的文本
    if (tab && tab.id) {
      chrome.tabs.sendMessage(tab.id, {
        action: "highlightText",
        text: selectedText
      })
    }

    fetch("http://127.0.0.1:7001/api/word/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        word: selectedText,
        uid: "123"
      })
    })
      .then((response) => {
        if (response.ok) {
          console.log("单词已成功发送到API:", selectedText)

          // 可选：在页面上显示一个通知
          if (tab && tab.id) {
            chrome.tabs.sendMessage(tab.id, {
              action: "showNotification",
              message: `已保存词汇: ${selectedText}`
            })
          }
        } else {
          console.error("发送到API失败:", response.status)
        }
      })
      .catch((error) => {
        console.error("网络错误:", error)
      })
  }
})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "saveVocabulary") {
    // 模拟发送 POST 请求到 /api/ 端点
    fetch("http://127.0.0.1:7001/api/word/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        uid: "123",
        word: request.data
      })
    })
      .then((response) => {
        if (response.ok) {
          console.log("单词已成功发送到API")
          // chrome.tabs.sendMessage(tab.id, {
          //   action: "showNotification",
          //   message: `已保存词汇: ${selectedText}`
          // })
          sendResponse({ success: true })
        } else {
          console.error("发送到API失败:", response.status)
          sendResponse({ success: false, error: "Failed to save to API" })
        }
      })
      .catch((error) => {
        console.error("网络错误:", error)
        sendResponse({ success: false, error: error.message })
      })

    // 返回true表示异步响应
    return true
  } else if (request.action === "getVocabulary") {
    // 使用代理方式绕过 CORS 限制
    fetch(
      `http://127.0.0.1:7001/api/word/?word=${encodeURIComponent(request.data || "")}`
    )
      .then((response) => response.json())
      .then((data) => {
        console.log("从API获取的数据:", data)
        sendResponse(data)
      })
      .catch((error) => {
        console.error("获取数据失败:", error)
        sendResponse({ error: error.message })
      })
    return true
  } else if (request.action === "getSmsCode") {
    // 获取短信验证码
    fetch("http://127.0.0.1:7001/api/user/login/sms_send/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        phone: request.phone
      })
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("获取验证码结果:", data)
        sendResponse(data)
      })
      .catch((error) => {
        console.error("获取验证码失败:", error)
        sendResponse({ success: false, message: "获取验证码失败" })
      })
    return true
  } else if (request.action === "userLogin") {
    // 用户登录
    fetch("http://127.0.0.1:7001/api/user/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        phone: request.phone,
        code: request.code
      })
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("登录结果:", data)
        sendResponse(data)
      })
      .catch((error) => {
        console.error("登录失败:", error)
        sendResponse({ success: false, message: "登录失败" })
      })
    return true
  }
})
