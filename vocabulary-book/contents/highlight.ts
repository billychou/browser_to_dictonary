// contents/highlight.ts - 内容脚本，用于高亮选中的文本

function highlightText(selectedText: string) {
  // 移除之前添加的样式
  const existingStyle = document.getElementById('browser-extension-highlight-style');
  if (existingStyle) {
    existingStyle.remove();
  }

  // 创建样式元素
  const style = document.createElement('style');
  style.id = 'browser-extension-highlight-style';
  style.textContent = `
    .browser-extension-highlight {
      background-color: red !important;
    }
  `;
  document.head.appendChild(style);

  // 查找所有包含选中文本的元素
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );

  const textNodes: Text[] = [];
  let node: Node | null;

  while (node = walker.nextNode()) {
    if (node.nodeType === Node.TEXT_NODE && node.textContent && node.textContent.includes(selectedText)) {
      textNodes.push(node as Text);
    }
  }

  // 高亮所有匹配的文本
  textNodes.forEach(textNode => {
    const text = textNode.textContent || "";
    if (text.includes(selectedText)) {
      const span = document.createElement("span");
      span.className = "browser-extension-highlight";
      span.textContent = selectedText;
      
      const parts = text.split(selectedText);
      const fragment = document.createDocumentFragment();
      
      for (let i = 0; i < parts.length; i++) {
        fragment.appendChild(document.createTextNode(parts[i]));
        if (i < parts.length - 1) {
          fragment.appendChild(span.cloneNode(true));
        }
      }
      
      textNode.parentNode?.replaceChild(fragment, textNode);
    }
  });
}

// 监听来自 background script 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "highlightText") {
    highlightText(request.text);
    sendResponse({ success: true });
  }
});

export {};