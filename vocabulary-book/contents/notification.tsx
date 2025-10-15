// contents/notification.tsx - 内容脚本，用于在页面上显示通知

function showNotification(message: string) {
  // 创建通知元素
  const notification = document.createElement("div");
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    padding: 16px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    z-index: 10000;
    font-family: Arial, sans-serif;
  `;
  
  // 添加到页面
  document.body.appendChild(notification);
  
  // 3秒后自动移除通知
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 3000);
}

// 监听来自 background script 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "showNotification") {
    showNotification(request.message);
    sendResponse({ success: true });
  }
});

export {};