chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "saveVocabulary") {
    // 模拟发送 POST 请求到 /api/ 端点
    fetch("/api/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        word: request.data,
        timestamp: new Date().toISOString()
      })
    })
      .then((response) => {
        if (response.ok) {
          console.log("单词已成功发送到API")
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
    fetch("http://127.0.0.1:7001/api/dictionary/hello")
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
  }
})
