import { useEffect, useState } from "react"

import "./style.css"

function IndexPopup() {
  const [data, setData] = useState("")
  const [returnData, setReturnData] = useState("")
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  const [showLogin, setShowLogin] = useState(true)
  const [loginMessage, setLoginMessage] = useState("")

  // 组件挂载时检查用户登录状态
  useEffect(() => {
    chrome.storage.local.get(["userInfo"], (result) => {
      if (result.userInfo) {
        setIsLoggedIn(true)
        setShowLogin(false)
      }
    })
  }, [])

  // 数据变化时保存到存储
  const handleSave = () => {
    chrome.storage.local.set({ savedData: data })

    // 发送数据到后台脚本，由后台脚本处理API请求
    chrome.runtime
      .sendMessage({
        action: "saveVocabulary",
        data: data
      })
      .then((response) => {
        if (response?.success) {
          console.log("API保存成功")
          setReturnData(response.data)
        } else {
          console.log("API保存失败:", response?.error)
        }
      })
      .catch((error) => {
        console.log("发送消息失败:", error)
      })
  }

  // 处理登录
  const handleLogin = () => {
    if (!phone) {
      setLoginMessage("请输入手机号")
      return
    }

    // 发送登录请求到后台
    chrome.runtime
      .sendMessage({
        action: "userLogin",
        phone: phone,
        code: code
      })
      .then((response) => {
        if (response?.success) {
          console.log("登录成功")
          // 保存用户信息到存储
          chrome.storage.local.set({ userInfo: response.data })
          setIsLoggedIn(true)
          setShowLogin(false)
          setLoginMessage("")
        } else {
          console.log("登录失败:", response?.message)
          setLoginMessage(response?.message || "登录失败")
        }
      })
      .catch((error) => {
        console.log("登录请求失败:", error)
        setLoginMessage("登录请求失败")
      })
  }

  // 获取验证码
  const handleGetCode = () => {
    if (!phone) {
      setLoginMessage("请输入手机号")
      return
    }

    // 发送获取验证码请求
    chrome.runtime
      .sendMessage({
        action: "getSmsCode",
        phone: phone
      })
      .then((response) => {
        if (response?.success) {
          console.log("验证码已发送")
          setLoginMessage("验证码已发送")
        } else {
          console.log("发送验证码失败:", response?.message)
          setLoginMessage(response?.message || "发送验证码失败")
        }
      })
      .catch((error) => {
        console.log("发送验证码失败:", error)
        setLoginMessage("发送验证码失败")
      })
  }

  // 显示登录页面
  const renderLoginPage = () => {
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

  // 显示保存单词页面
  const renderSavePage = () => {
    return (
      <div className="p-4 w-80">
        <h2 className="text-xl font-bold mb-4 text-center">词汇书</h2>
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
        <div className="mt-4 p-3 bg-gray-100 rounded-md text-left">
          <p className="text-sm text-gray-600">当前输入:</p>
          <p className="mt-1">{returnData}</p>
        </div>
      </div>
    )
  }

  return showLogin ? renderLoginPage() : renderSavePage()
}

export default IndexPopup
