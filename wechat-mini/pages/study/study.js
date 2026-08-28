const api = require("../../utils/request")
const { isLoggedIn, redirectToLogin } = require("../../utils/auth")
const { daysAgo } = require("../../utils/date")
const review = require("../../utils/review")

Page({
  data: {
    view: "home", // home | session | done
    loading: true,
    stats: { total: 0, mastered: 0, dueCount: 0, reviewedToday: 0, streak: 0 },
    masteredPercent: 0,
    // 会话状态
    sessionSize: 0,
    knownCount: 0,
    current: null,
    currentDays: 0,
    currentReviews: 0,
    currentStage: 0,
    stageTip: "",
    revealed: false,
    sessionReviewed: 0,
    sessionMastered: 0
  },

  words: [],
  queue: [],

  onShow() {
    if (!isLoggedIn()) {
      redirectToLogin()
      return
    }
    this.refresh()
  },

  async refresh() {
    this.setData({ loading: true })
    try {
      this.words = await api.fetchAllWords()
      const stats = review.getStats(this.words)
      const masteredPercent = stats.total
        ? Math.round((stats.mastered / stats.total) * 100)
        : 0
      this.setData({ stats, masteredPercent })
    } catch (err) {
      wx.showToast({ title: err.message, icon: "none" })
    } finally {
      this.setData({ loading: false })
    }
  },

  startSession() {
    const map = review.loadMap()
    this.queue = this.words.filter((w) => review.isDue(review.getEntry(map, w.id)))
    if (this.queue.length === 0) {
      wx.showToast({ title: "暂时没有待复习的词", icon: "none" })
      return
    }
    this.setData(
      {
        view: "session",
        sessionSize: this.queue.length,
        knownCount: 0,
        sessionReviewed: 0,
        sessionMastered: 0,
        revealed: false
      },
      () => this.showCurrent()
    )
  },

  showCurrent() {
    const current = this.queue[0]
    if (!current) {
      this.finishSession()
      return
    }
    const entry = review.getEntry(review.loadMap(), current.id)
    this.setData({
      current,
      revealed: false,
      currentDays: daysAgo(current.gmt_create),
      currentReviews: entry ? entry.reviews : 0,
      currentStage: entry ? entry.stage : 0,
      stageTip: entry && entry.stage >= review.MASTERED_STAGE
        ? "已达最高等级"
        : "下次间隔 " + review.INTERVAL_DAYS[Math.min((entry ? entry.stage : 0) + 1, review.MASTERED_STAGE)] + " 天"
    })
  },

  reveal() {
    if (!this.data.revealed) this.setData({ revealed: true })
  },

  answer(e) {
    const result = e.currentTarget.dataset.result
    const current = this.queue[0]
    if (!current) return
    const entry = review.applyResult(current.id, result)
    this.setData({ sessionReviewed: this.data.sessionReviewed + 1 })

    if (result === "known") {
      this.queue.shift()
      const updates = { knownCount: this.data.knownCount + 1 }
      if (entry.stage >= review.MASTERED_STAGE) {
        updates.sessionMastered = this.data.sessionMastered + 1
      }
      this.setData(updates, () => this.showCurrent())
    } else {
      // 模糊/不认识：放到队尾，本轮继续
      this.queue.push(this.queue.shift())
      this.showCurrent()
    }
  },

  finishSession() {
    this.setData({ view: "done" })
    this.refresh()
  },

  exitSession() {
    wx.showModal({
      title: "退出复习",
      content: "本轮进度已保存，确定退出吗？",
      success: (res) => {
        if (res.confirm) this.backHome()
      }
    })
  },

  backHome() {
    this.setData({ view: "home", current: null, revealed: false })
    this.refresh()
  }
})
