import { useCallback, useEffect, useRef, useState } from "react"

import { isLoggedIn } from "~lib/api"

import "./style.css"

type WordItem = {
  id: number
  word: string
  gmt_update?: string
}

// 扫码等待上限：与后端票据有效期（300s）对齐
const POLL_INTERVAL_MS = 2000
const POLL_TIMEOUT_MS = 300 * 1000

function IndexPopup() {
  const [data, setData] = useState("")
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null)
  const [waitingScan, setWaitingScan] = useState(false)
  const [loginMessage, setLoginMessage] = useState("")
  const [pageMessage, setPageMessage] = useState("")
  const [words, setWords] = useState<WordItem[]>([])
  const [total, setTotal] = useState(0)
  const pollTimer = useRef<number | null>(null)
  const pollDeadline = useRef<number | null>(null)

  const stopPolling = useCallback(() => {
    if (pollTimer.current !== null) {
      window.clearInterval(pollTimer.current)
      pollTimer.current = null
    }
  }, [])

  // P1-6: 打开弹窗时基于 JWT 过期时间判断登录态
  useEffect(() => {
    isLoggedIn().then(setLoggedIn)
  }, [])

  // 关闭弹窗时停止轮询
  useEffect(() => stopPolling, [stopPolling])

  const loadWords = useCallback(() => {
    chrome.runtime.sendMessage({ action: "getVocabulary" }, (response) => {
      if (response?.success) {
        setWords(response.data?.items || [])
        setTotal(response.data?.total || 0)
      } else {
        setPageMessage(response?.message || "获取词汇列表失败")
      }
    })
  }, [])

  useEffect(() => {
    if (loggedIn) loadWords()
  }, [loggedIn, loadWords])

  const pollOnce = useCallback(
    (pollTicket: string) => {
      if (Date.now() > (pollDeadline.current || 0)) {
        stopPolling()
        setWaitingScan(false)
        setLoginMessage("二维码已过期，请重新发起微信登录")
        return
      }
      chrome.runtime.sendMessage(
        { action: "wechatLoginPoll", ticket: pollTicket },
        (response) => {
          const status = response?.data?.status
          if (response?.success && status === "confirmed") {
            stopPolling()
            setWaitingScan(false)
            setLoginMessage("")
            setLoggedIn(true)
          } else if (status === "expired") {
            stopPolling()
            setWaitingScan(false)
            setLoginMessage("二维码已过期，请重新发起微信登录")
          }
          // pending：继续等待，不做处理
        }
      )
    },
    [stopPolling]
  )

  const handleWechatLogin = () => {
    setLoginMessage("")
    chrome.runtime.sendMessage({ action: "wechatLoginStart" }, (response) => {
      if (response?.success) {
        const newTicket = response.data?.ticket || ""
        setWaitingScan(true)
        setLoginMessage("已在新标签页打开微信二维码，请用手机微信扫码并确认")
        stopPolling()
        pollDeadline.current = Date.now() + POLL_TIMEOUT_MS
        pollTimer.current = window.setInterval(
          () => pollOnce(newTicket),
          POLL_INTERVAL_MS
        )
      } else {
        setWaitingScan(false)
        setLoginMessage(response?.message || "发起微信登录失败")
      }
    })
  }

  const handleExport = () => {
    chrome.runtime.sendMessage({ action: "exportVocabulary" }, (response) => {
      if (response?.success) {
        const blob = new Blob([response.data], {
          type: "text/csv;charset=utf-8"
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `vocabulary_${new Date().toISOString().slice(0, 10)}.csv`
        a.click()
        URL.revokeObjectURL(url)
        setPageMessage("CSV 已开始下载")
      } else {
        setPageMessage(response?.message || "导出失败")
      }
    })
  }

  const handleSave = () => {
    const word = data.trim()
    if (!word) {
      setPageMessage("请输入单词或短语")
      return
    }
    chrome.runtime.sendMessage(
      { action: "saveVocabulary", data: word },
      (response) => {
        if (response?.success) {
          setData("")
          setPageMessage(`已保存: ${word}`)
          loadWords()
        } else {
          setPageMessage(response?.message || "保存失败")
        }
      }
    )
  }

  const handleDelete = (id: number) => {
    chrome.runtime.sendMessage(
      { action: "deleteVocabulary", id },
      (response) => {
        if (response?.success) {
          setPageMessage("已删除")
          loadWords()
        } else {
          setPageMessage(response?.message || "删除失败")
        }
      }
    )
  }

  const handleLogout = () => {
    chrome.storage.local.remove("userInfo", () => {
      setLoggedIn(false)
      setWords([])
      setLoginMessage("")
    })
  }

  if (loggedIn === null) return null

  if (!loggedIn) {
    return (
      <div className="p-4 w-80">
        <h2 className="text-xl font-bold mb-2 text-center">用户登录</h2>
        <p className="text-sm text-gray-400 text-center mb-4">
          使用微信扫码登录，与微信小程序共享词汇书
        </p>
        {waitingScan ? (
          <div className="mb-3 text-center">
            <div className="text-sm text-gray-600 animate-pulse">
              等待微信扫码确认…
            </div>
            <button
              onClick={handleWechatLogin}
              className="mt-3 text-xs text-blue-400 hover:text-blue-600">
              重新获取二维码
            </button>
          </div>
        ) : (
          <button
            onClick={handleWechatLogin}
            className="w-full bg-[#07C160] hover:bg-[#06ad56] text-white font-medium py-2 px-4 rounded-md transition duration-200">
            微信扫码登录
          </button>
        )}
        {loginMessage && (
          <div className="mt-3 text-red-500 text-sm">{loginMessage}</div>
        )}
      </div>
    )
  }

  return (
    <div className="p-4 w-80">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">词汇书</h2>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-500 hover:text-gray-700">
          退出登录
        </button>
      </div>
      <input
        onChange={(e) => setData(e.target.value)}
        value={data}
        placeholder="输入单词或短语"
        className="w-full px-3 py-2 border border-gray-300 rounded-md mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        onClick={handleSave}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition duration-200">
        保存
      </button>
      {pageMessage && (
        <div className="mt-3 text-sm text-gray-600">{pageMessage}</div>
      )}
      <div className="mt-4">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm text-gray-500">我的词汇（{total}）</p>
          <button
            onClick={handleExport}
            className="text-xs text-blue-400 hover:text-blue-600">
            导出 CSV
          </button>
        </div>
        {words.length === 0 ? (
          <p className="text-sm text-gray-400">还没有保存的词汇</p>
        ) : (
          <ul className="max-h-64 overflow-y-auto divide-y divide-gray-100">
            {words.map((item) => (
              <li
                key={item.id}
                className="flex items-center justify-between py-2">
                <span className="text-sm">{item.word}</span>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-xs text-red-400 hover:text-red-600">
                  删除
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default IndexPopup
