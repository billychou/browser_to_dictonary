/**
 * 间隔复习调度（艾宾浩斯遗忘曲线简化版）。
 *
 * 后端词汇表目前只有 word + 时间戳，无进度字段，
 * 因此复习进度先记录在小程序本地（见 wechat-mini/README「已知限制」），
 * 后续后端补充进度字段后可平滑迁移为云端同步。
 *
 * 规则：
 * - 每个词有一个等级 stage（0-5），对应复习间隔 [当天, 1, 2, 4, 7, 15] 天
 * - 「认识」升一级并按新间隔排期；「模糊」10 分钟后重新出现；
 *   「不认识」回到 0 级并立即重新排队
 * - 到达最高级视为「已掌握」
 * - 从未复习过的新词视为当次到期
 */
const { DAY, todayKey } = require("./date")

const INTERVAL_DAYS = [0, 1, 2, 4, 7, 15]
const MASTERED_STAGE = INTERVAL_DAYS.length - 1
const FUZZY_DELAY = 10 * 60 * 1000

const MAP_KEY = "vb_review_map"
const LOG_KEY = "vb_study_log"

function loadMap() {
  return wx.getStorageSync(MAP_KEY) || {}
}

function saveMap(map) {
  wx.setStorageSync(MAP_KEY, map)
}

function loadLog() {
  return wx.getStorageSync(LOG_KEY) || {}
}

function getEntry(map, wordId) {
  return map[wordId] || null
}

/** 是否到期：从未复习过，或到期时间已过 */
function isDue(entry, now = Date.now()) {
  return !entry || (entry.due || 0) <= now
}

/**
 * 记录一次复习结果并持久化
 * @param result 'known' | 'fuzzy' | 'unknown'
 * @returns 更新后的 entry
 */
function applyResult(wordId, result) {
  const map = loadMap()
  const entry = map[wordId] || { stage: 0, due: 0, reviews: 0, lapses: 0, last: 0 }
  const now = Date.now()
  entry.reviews += 1
  entry.last = now
  if (result === "known") {
    entry.stage = Math.min(entry.stage + 1, MASTERED_STAGE)
    entry.due = now + INTERVAL_DAYS[entry.stage] * DAY
  } else if (result === "fuzzy") {
    entry.due = now + FUZZY_DELAY
  } else {
    entry.stage = 0
    entry.lapses += 1
    entry.due = now
  }
  map[wordId] = entry
  saveMap(map)
  logStudy()
  return entry
}

/** 删除词汇时同步清理本地复习记录 */
function removeEntry(wordId) {
  const map = loadMap()
  if (map[wordId]) {
    delete map[wordId]
    saveMap(map)
  }
}

/** 今日学习计数 +1 */
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
 * 基于全量词汇与本地记录计算学习进度
 * @param words 全量词汇列表（含 id、gmt_create）
 */
function getStats(words) {
  const map = loadMap()
  const now = Date.now()
  let mastered = 0
  let dueCount = 0
  for (const w of words) {
    const entry = map[w.id]
    if (entry && entry.stage >= MASTERED_STAGE) mastered += 1
    if (isDue(entry, now)) dueCount += 1
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

/** 累计复习次数 */
function getTotalReviews() {
  const map = loadMap()
  return Object.keys(map).reduce((sum, k) => sum + (map[k].reviews || 0), 0)
}

module.exports = {
  INTERVAL_DAYS,
  MASTERED_STAGE,
  loadMap,
  getEntry,
  isDue,
  applyResult,
  removeEntry,
  getStats,
  getStreak,
  getTotalReviews
}
