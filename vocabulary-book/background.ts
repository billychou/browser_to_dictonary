import {
  API_BASE,
  apiFetch,
  flushPendingWords,
  getUserInfo,
  postWord,
  queuePendingWord,
  setUserInfo
} from "~lib/api"

// 创建上下文菜单项
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "saveVocabulary",
    title: "保存词汇到词汇书",
    contexts: ["selection"] // 只在选中文本时显示
  })
})

async function notifyTab(tabId: number, message: object) {
  try {
    await chrome.tabs.sendMessage(tabId, message)
  } catch {
    // 页面内容脚本未就绪时忽略
  }
}

// 保存单词：成功顺带冲刷离线队列，失败进入队列等待重试（P1-4）
async function saveWord(word: string, tabId?: number) {
  const ok = await postWord(word)
  if (ok) {
    await flushPendingWords()
    if (tabId) {
      await notifyTab(tabId, {
        action: "showNotification",
        message: `已保存词汇: ${word}`
      })
    }
  } else {
    await queuePendingWord(word)
    if (tabId) {
      await notifyTab(tabId, {
        action: "showNotification",
        messageType: "warn",
        message: `后端暂不可用，「${word}」已加入待同步队列`
      })
    }
  }
  return ok
}

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== "saveVocabulary") return
  const selectedText = (info.selectionText || "").trim()
  if (!selectedText) return

  // 向内容脚本发送消息以高亮选中的文本
  if (tab?.id) {
    chrome.tabs.sendMessage(tab.id, {
      action: "highlightText",
      text: selectedText
    })
  }
  saveWord(selectedText, tab?.id)
})

// 浏览器启动时重试离线队列中的单词
chrome.runtime.onStartup.addListener(() => {
  flushPendingWords()
})

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  ;(async () => {
    switch (request.action) {
      case "saveVocabulary": {
        const word = (request.data || "").trim()
        if (!word) {
          sendResponse({ success: false, message: "词汇内容不能为空" })
          return
        }
        const ok = await saveWord(word)
        if (ok) {
          sendResponse({ success: true, data: word })
        } else {
          sendResponse({
            success: false,
            message: "后端暂不可用，已加入待同步队列"
          })
        }
        break
      }
      case "getVocabulary": {
        try {
          const params = new URLSearchParams()
          if (request.word) params.set("word", request.word)
          params.set("page", String(request.page || 1))
          params.set("limit", String(request.limit || 50))
          const data = await apiFetch(`/api/word/?${params.toString()}`)
          sendResponse(data)
        } catch (error) {
          sendResponse({ success: false, message: (error as Error).message })
        }
        break
      }
      case "deleteVocabulary": {
        try {
          const data = await apiFetch(`/api/word/${request.id}`, {
            method: "DELETE"
          })
          sendResponse(data)
        } catch (error) {
          sendResponse({ success: false, message: (error as Error).message })
        }
        break
      }
      case "updateVocabulary": {
        try {
          const data = await apiFetch(`/api/word/${request.id}`, {
            method: "PUT",
            body: JSON.stringify({ word: request.word })
          })
          sendResponse(data)
        } catch (error) {
          sendResponse({ success: false, message: (error as Error).message })
        }
        break
      }
      case "getSmsCode": {
        try {
          const data = await apiFetch("/api/user/login/sms_send/", {
            method: "POST",
            body: JSON.stringify({ phone: request.phone })
          })
          sendResponse(data)
        } catch (error) {
          sendResponse({ success: false, message: (error as Error).message })
        }
        break
      }
      case "userLogin": {
        try {
          const data = await apiFetch("/api/user/login/", {
            method: "POST",
            body: JSON.stringify({ phone: request.phone, code: request.code })
          })
          // 登录成功后持久化用户信息（含 JWT）
          if (data?.success && data.data) {
            await setUserInfo(data.data)
          }
          sendResponse(data)
        } catch (error) {
          sendResponse({ success: false, message: (error as Error).message })
        }
        break
      }
      case "exportVocabulary": {
        // 导出 CSV 为文本流，直接 fetch 而非走 JSON 封装
        try {
          const info = await getUserInfo()
          const response = await fetch(`${API_BASE}/api/word/export/`, {
            headers: info?.token
              ? { Authorization: `Bearer ${info.token}` }
              : {}
          })
          if (!response.ok) {
            throw new Error("导出失败，请稍后重试")
          }
          const csv = await response.text()
          sendResponse({ success: true, data: csv })
        } catch (error) {
          sendResponse({ success: false, message: (error as Error).message })
        }
        break
      }
      default:
        sendResponse({ success: false, message: "未知操作" })
    }
  })()

  // 返回 true 表示异步响应
  return true
})
