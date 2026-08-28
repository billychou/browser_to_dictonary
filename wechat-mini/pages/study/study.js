const api = require("../../utils/request")
const { isLoggedIn, redirectToLogin } = require("../../utils/auth")
const { daysAgo, parseTime } = require("../../utils/date")
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
    currentExample: "",
    defLoading: false,
    defFailed: false,
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
    this.queue = this.words.filter((w) => review.isDueWord(w))
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
    const stage = current.stage || 0
    const mastered = stage >= review.MASTERED_STAGE
    this.setData({
      current,
      revealed: false,
      currentDays: daysAgo(current.gmt_create),
      currentReviews: current.review_count || 0,
      currentStage: stage,
      currentExample: this.firstExample(current),
      defLoading: false,
      defFailed: false,
      stageTip: mastered
        ? "已达最高等级"
        : "认识后 " +
          review.INTERVAL_DAYS[Math.min(stage + 1, review.MASTERED_STAGE)] +
          " 天后再复习"
    })
  },

  /** 取释义详情中的第一个例句 */
  firstExample(word) {
    for (const meaning of word.detail || []) {
      for (const d of meaning.definitions || []) {
        if (d.example) return d.example
      }
    }
    return ""
  },

  /** 补查词典释义（保存时未查到或查询失败的词） */
  async fetchDefinition() {
    const current = this.queue[0]
    if (!current || this.data.defLoading) return
    this.setData({ defLoading: true })
    try {
      const updated = await api.refreshDefinition(current.id)
      Object.assign(current, updated)
      const idx = this.words.findIndex((w) => w.id === updated.id)
      if (idx >= 0) this.words[idx] = current
      this.setData({
        current: { ...current },
        currentExample: this.firstExample(current),
        defFailed: false
      })
    } catch (err) {
      this.setData({ defFailed: true })
      wx.showToast({ title: err.message, icon: "none" })
    } finally {
      this.setData({ defLoading: false })
    }
  },

  reveal() {
    if (!this.data.revealed) this.setData({ revealed: true })
  },

  async answer(e) {
    const result = e.currentTarget.dataset.result
    const current = this.queue[0]
    if (!current) return
    try {
      // 服务端记录进度并返回更新后的词汇（含最新排期）
      const updated = await api.reviewWord(current.id, result)
      Object.assign(current, updated)
      // 同步全量列表中的同一条记录，保持退出后统计准确
      const idx = this.words.findIndex((w) => w.id === updated.id)
      if (idx >= 0) this.words[idx] = current
    } catch (err) {
      wx.showToast({ title: err.message, icon: "none" })
      return
    }
    review.logStudy()
    this.setData({ sessionReviewed: this.data.sessionReviewed + 1 })

    if (result === "known") {
      this.queue.shift()
      const updates = { knownCount: this.data.knownCount + 1 }
      if ((current.stage || 0) >= review.MASTERED_STAGE) {
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
