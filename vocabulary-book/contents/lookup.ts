// contents/lookup.ts - 划词即查：选中文本后展示释义浮层，可一键加入词汇书
// P3-4: 比右键菜单少一步；仅对英文单词/短语触发，避免干扰正常浏览

const PANEL_ID = "vb-lookup-panel"
// 单词/短语：字母开头，可含空格、连字符、撇号，最长 64 字符
const WORD_RE = /^[A-Za-z][A-Za-z\s'-]{0,63}$/

let panel: HTMLElement | null = null

function removePanel() {
  if (panel) {
    panel.remove()
    panel = null
  }
}

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  styles: string,
  text?: string
) {
  const node = document.createElement(tag)
  node.style.cssText = styles
  if (text) node.textContent = text
  return node
}

function showPanel(word: string, rect: DOMRect) {
  removePanel()

  const root = el(
    "div",
    `position: fixed; z-index: 2147483647; width: 320px; max-width: 90vw;
     background: #ffffff; color: #1f2329; border-radius: 12px;
     box-shadow: 0 8px 32px rgba(0,0,0,0.18); font-family: -apple-system,
     BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif; font-size: 14px;
     line-height: 1.5; overflow: hidden;`
  )
  root.id = PANEL_ID

  const header = el(
    "div",
    "display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid #f0f1f3;"
  )
  header.appendChild(
    el(
      "span",
      "font-weight: 600; font-size: 16px; word-break: break-all;",
      word
    )
  )
  const closeBtn = el(
    "span",
    "cursor: pointer; color: #8a9099; font-size: 18px; padding: 0 4px; flex-shrink: 0;",
    "✕"
  )
  closeBtn.addEventListener("click", removePanel)
  header.appendChild(closeBtn)
  root.appendChild(header)

  const body = el("div", "padding: 10px 14px;")
  body.appendChild(el("div", "color: #8a9099;", "正在查询释义…"))
  root.appendChild(body)

  const footer = el("div", "padding: 0 14px 12px;")
  const addBtn = el(
    "button",
    `width: 100%; background: #07c160; color: #fff; border: none; border-radius: 8px;
     padding: 8px 0; font-size: 14px; cursor: pointer;`
  )
  addBtn.textContent = "加入词汇本"
  addBtn.addEventListener("click", () => {
    addBtn.textContent = "保存中…"
    chrome.runtime.sendMessage(
      { action: "saveVocabulary", data: word },
      (response) => {
        if (chrome.runtime.lastError || !response?.success) {
          addBtn.textContent = "加入词汇本"
          body.appendChild(
            el(
              "div",
              "color: #fa5151; margin-top: 8px; font-size: 12px;",
              response?.message || "保存失败，请稍后重试"
            )
          )
          return
        }
        addBtn.textContent = "✓ 已加入词汇本"
        addBtn.disabled = true
        addBtn.style.background = "#9be6bc"
      }
    )
  })
  footer.appendChild(addBtn)
  root.appendChild(footer)

  document.body.appendChild(root)

  // 定位：选区下方，超出视口时贴边
  const panelRect = root.getBoundingClientRect()
  let top = rect.bottom + 8
  let left = Math.min(rect.left, window.innerWidth - panelRect.width - 8)
  left = Math.max(8, left)
  if (top + panelRect.height > window.innerHeight - 8) {
    top = Math.max(8, rect.top - panelRect.height - 8)
  }
  root.style.top = `${top}px`
  root.style.left = `${left}px`

  chrome.runtime.sendMessage({ action: "lookupWord", word }, (response) => {
    // 浮层可能已被关闭或替换
    if (!panel || !document.contains(root)) return
    body.innerHTML = ""
    if (chrome.runtime.lastError || !response?.success) {
      body.appendChild(
        el(
          "div",
          "color: #8a9099;",
          response?.message || "释义查询失败，请稍后重试"
        )
      )
      return
    }
    const data = response.data
    if (!data || !data.definition) {
      body.appendChild(el("div", "color: #8a9099;", "未查询到该词的释义"))
      return
    }
    if (data.phonetic) {
      body.appendChild(
        el("div", "color: #8a9099; margin-bottom: 4px;", data.phonetic)
      )
    }
    body.appendChild(
      el(
        "div",
        "white-space: pre-line; max-height: 96px; overflow: hidden; word-break: break-word;",
        data.definition
      )
    )
  })

  panel = root
}

// 选中后延迟读取选区（等待选区稳定）
document.addEventListener(
  "mouseup",
  (event) => {
    if (panel && panel.contains(event.target as Node)) return
    window.setTimeout(() => {
      const selection = window.getSelection()
      const text = (selection?.toString() || "").trim()
      if (!WORD_RE.test(text)) {
        removePanel()
        return
      }
      const range = selection?.getRangeAt(0)
      if (!range) return
      showPanel(text, range.getBoundingClientRect())
    }, 10)
  },
  true
)

// 点击浮层外部关闭
document.addEventListener(
  "mousedown",
  (event) => {
    if (panel && !panel.contains(event.target as Node)) removePanel()
  },
  true
)

// Esc 关闭
document.addEventListener(
  "keydown",
  (event) => {
    if (event.key === "Escape") removePanel()
  },
  true
)

export {}
