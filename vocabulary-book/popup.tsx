import { useEffect, useState } from "react"

import "./style.css"

function IndexPopup() {
  const [data, setData] = useState("")

  // 组件挂载时从存储中获取数据
  useEffect(() => {
    console.log("useEffect")
    chrome.storage.local.get(["savedData"], (result) => {
      if (result.savedData) {
        setData(result.savedData)
      }
    })
  }, [])

  // 数据变化时保存到存储
  const handleSave = () => {
    console.log("handleSave")
    chrome.storage.local.set({ savedData: data })

    // 发送数据到后台脚本，由后台脚本处理API请求
    chrome.runtime
      .sendMessage({
        action: "getVocabulary",
        data: data
      })
      .then((response) => {
        if (response?.success) {
          console.log("API保存成功")
        } else {
          console.log("API保存失败:", response?.error)
        }
      })
      .catch((error) => {
        console.log("发送消息失败:", error)
      })
  }

  return (
    <div className="p-4 w-80">
      <h2 className="text-xl font-bold mb-4 text-left">词汇书</h2>
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
        <p className="mt-1">{data}</p>
      </div>
    </div>
  )
}

export default IndexPopup
