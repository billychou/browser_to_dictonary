// contents/highlight.ts - 内容脚本，用于高亮用户实际选中的文本
// P1-5: 优先基于真实选区（Selection/Range）高亮，避免全页字符串替换破坏页面结构；
// 仅当选区不可用时回退到按文本匹配高亮。

const STYLE_ID = "browser-extension-highlight-style"

function ensureStyle() {
  if (document.getElementById(STYLE_ID)) return
  const style = document.createElement("style")
  style.id = STYLE_ID
  style.textContent = `
    .browser-extension-highlight {
      background-color: lightcoral !important;
    }
  `
  document.head.appendChild(style)
}

function wrapTextRange(textNode: Text, startOffset: number, endOffset: number) {
  if (startOffset >= endOffset) return
  // splitText 切出目标片段后用 span 包裹，避免影响其它节点
  const target = textNode.splitText(startOffset)
  target.splitText(endOffset - startOffset)
  const span = document.createElement("span")
  span.className = "browser-extension-highlight"
  target.replaceWith(span)
  span.appendChild(target)
}

// 高亮当前选区：收集与选区相交的文本节点，逐个包裹相交部分
function highlightSelection(): boolean {
  const selection = window.getSelection()
  if (!selection || selection.rangeCount === 0 || selection.isCollapsed) {
    return false
  }
  const range = selection.getRangeAt(0)
  const ancestor = range.commonAncestorContainer
  const root =
    ancestor.nodeType === Node.TEXT_NODE ? ancestor.parentElement : ancestor
  if (!root) return false

  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      return range.intersectsNode(node)
        ? NodeFilter.FILTER_ACCEPT
        : NodeFilter.FILTER_REJECT
    }
  })

  // 先收集后修改，避免 mutation 影响遍历
  const textNodes: Text[] = []
  let node: Node | null
  while ((node = walker.nextNode())) {
    textNodes.push(node as Text)
  }
  if (textNodes.length === 0) return false

  for (const textNode of textNodes) {
    const length = textNode.textContent?.length ?? 0
    const startOffset =
      textNode === range.startContainer ? range.startOffset : 0
    const endOffset = textNode === range.endContainer ? range.endOffset : length
    wrapTextRange(
      textNode,
      Math.max(startOffset, 0),
      Math.min(endOffset, length)
    )
  }
  return true
}

// 兜底：无选区时按文本精确匹配高亮（保持旧行为，兼容右键菜单场景）
function highlightByText(selectedText: string) {
  if (!selectedText) return
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null
  )
  const targets: Text[] = []
  let node: Node | null
  while ((node = walker.nextNode())) {
    if (node.textContent?.includes(selectedText)) {
      targets.push(node as Text)
    }
  }
  for (const textNode of targets) {
    const text = textNode.textContent || ""
    let index = text.indexOf(selectedText)
    while (index !== -1) {
      wrapTextRange(textNode, index, index + selectedText.length)
      // splitText 后原文本节点只保留前半段，需要重新定位剩余部分
      const rest = textNode.nextSibling
      if (!rest || rest.nodeType !== Node.TEXT_NODE) break
      const restText = rest.textContent || ""
      const nextIndex = restText.indexOf(selectedText)
      if (nextIndex === -1) break
      index = nextIndex
    }
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "highlightText") {
    ensureStyle()
    if (!highlightSelection()) {
      highlightByText(request.text || "")
    }
    sendResponse({ success: true })
  }
})

export {}
