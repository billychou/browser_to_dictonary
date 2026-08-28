import { useCallback, useEffect, useState } from "react"

import { isLoggedIn } from "~lib/api"

import "./style.css"

type WordItem = {
  id: number
  word: string
  gmt_update?: string
}

function IndexPopup() {
  const [data, setData] = useState("")
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null)
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  const [loginMessage, setLoginMessage] = useState("")
  const [pageMessage, setPageMessage] = useState("")
  const [words, setWords] = useState<WordItem[]>([])
  const [total, setTotal] = useState(0)

  // P1-6: 打开弹窗时基于 JWT 过期时间判断登录态
  useEffect(() => {
    isLoggedIn().then(setLoggedIn)
  }, [])

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

  const handleLogin = () => {
    if (!phone) {
      setLoginMessage("请输入手机号")
      return
    }
    if (!code) {
      setLoginMessage("请输入验证码")
      return
    }
    chrome.runtime.sendMessage(
      { action: "userLogin", phone, code },
      (response) => {
        if (response?.success) {
          setLoggedIn(true)
          setLoginMessage("")
        } else {
          setLoginMessage(response?.message || "登录失败")
        }
      }
    )
  }

  const handleGetCode = () => {
    if (!phone) {
      setLoginMessage("请输入手机号")
      return
    }
    chrome.runtime.sendMessage({ action: "getSmsCode", phone }, (response) => {
      if (response?.success) {
        setLoginMessage("验证码已发送")
      } else {
        setLoginMessage(response?.message || "发送验证码失败")
      }
    })
  }

  if (loggedIn === null) return null

  if (!loggedIn) {
    return (
      <div className="p-4 w-80">
        <h2 className="text-xl font-bold mb-4 text-center">用户登录</h2>
        <div className="mb-3">
          <input
            onChange={(e) => setPhone(e.target.value)}
            value={phone}
            placeholder="请输入手机号"
            className="w-full px-3 py-2 border border-gray-300 rounded-md mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex">
            <input
              onChange={(e) => setCode(e.target.value)}
              value={code}
              placeholder="请输入验证码"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md mr-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleGetCode}
              className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition duration-200">
              获取验证码
            </button>
          </div>
        </div>
        {loginMessage && (
          <div className="mb-3 text-red-500 text-sm">{loginMessage}</div>
        )}
        <button
          onClick={handleLogin}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition duration-200">
          登录
        </button>
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
