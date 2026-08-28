/** 日期格式化工具 */
const DAY = 24 * 60 * 60 * 1000

function pad(n) {
  return n < 10 ? "0" + n : "" + n
}

/** 'YYYY-MM-DD' */
function todayKey(ts = Date.now()) {
  const d = new Date(ts)
  return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate())
}

/** 解析后端时间（'2026-08-29T01:00:00' 或 ISO 串）为时间戳 */
function parseTime(value) {
  if (!value) return 0
  const ts = new Date(String(value).replace(" ", "T")).getTime()
  return isNaN(ts) ? 0 : ts
}

/** 相对时间：刚刚 / x 分钟前 / x 小时前 / x 天前 / YYYY-MM-DD */
function formatRelative(value) {
  const ts = parseTime(value)
  if (!ts) return ""
  const diff = Date.now() - ts
  if (diff < 60 * 1000) return "刚刚"
  if (diff < 60 * 60 * 1000) return Math.floor(diff / 60000) + " 分钟前"
  if (diff < DAY) return Math.floor(diff / 3600000) + " 小时前"
  if (diff < 30 * DAY) return Math.floor(diff / DAY) + " 天前"
  const d = new Date(ts)
  return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate())
}

/** 距今天数（按自然日，今天=0） */
function daysAgo(value) {
  const ts = parseTime(value)
  if (!ts) return 0
  const a = new Date(ts)
  const b = new Date()
  const startA = new Date(a.getFullYear(), a.getMonth(), a.getDate()).getTime()
  const startB = new Date(b.getFullYear(), b.getMonth(), b.getDate()).getTime()
  return Math.max(0, Math.round((startB - startA) / DAY))
}

module.exports = { DAY, todayKey, parseTime, formatRelative, daysAgo }
