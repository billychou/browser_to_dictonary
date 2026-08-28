/**
 * 间隔复习与学习进度。
 *
 * 进度数据（等级/到期时间/复习次数）由服务端统一维护
 * （PUT /api/word/<id>/review），随词汇列表下发，跨设备一致。
 * 本模块仅保留展示层的到期判断与「今日/连续天数」等本机活动统计。
 *
 * 服务端排期规则（与此一致）：等级 0-5 对应间隔 [当天, 1, 2, 4, 7, 15] 天，
 * 「认识」升级排期，「模糊」10 分钟后重现，「不认识」回零级立即重排，
 * 达到 5 级计为「已掌握」。
 */
const { DAY, todayKey, parseTime } = require("./date")

const INTERVAL_DAYS = [0, 1, 2, 4, 7, 15]
const MASTERED_STAGE = INTERVAL_DAYS.length - 1

const LOG_KEY = "vb_study_log"

function loadLog() {
  return wx.getStorageSync(LOG_KEY) || {}
}

/** 是否到期：从未复习过（due 为空），或到期时间已过 */
function isDueWord(word, now = Date.now()) {
  if (!word.due) return true
  const due = parseTime(word.due)
  return !due || due <= now
}

/** 记录一次本地学习活动（用于今日计数与连续天数） */
function logStudy() {
  const log = loadLog()
  const key = todayKey()
  log[key] = (log[key] || 0) + 1
  wx.setStorageSync(LOG_KEY, log)
}

/** 连续学习天数（今天未学时从昨天起算，不立即中断） */
function getStreak() {
  const log = loadLog()
  let streak = 0
  let cursor = Date.now()
  if (!log[todayKey(cursor)]) cursor -= DAY
  while (log[todayKey(cursor)]) {
    streak += 1
    cursor -= DAY
  }
  return streak
}

/**
 * 基于全量词汇（含服务端进度字段）计算学习进度
 * @param words 全量词汇列表
 */
function getStats(words) {
  const now = Date.now()
  let mastered = 0
  let dueCount = 0
  for (const w of words) {
    if ((w.stage || 0) >= MASTERED_STAGE) mastered += 1
    if (isDueWord(w, now)) dueCount += 1
  }
  const log = loadLog()
  return {
    total: words.length,
    mastered,
    dueCount,
    reviewedToday: log[todayKey()] || 0,
    streak: getStreak()
  }
}

/** 累计复习次数（服务端字段汇总） */
function getTotalReviews(words) {
  return words.reduce((sum, w) => sum + (w.review_count || 0), 0)
}

module.exports = {
  INTERVAL_DAYS,
  MASTERED_STAGE,
  isDueWord,
  logStudy,
  getStats,
  getStreak,
  getTotalReviews
}
