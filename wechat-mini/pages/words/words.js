const api = require("../../utils/request")
const { isLoggedIn, redirectToLogin } = require("../../utils/auth")
const { formatRelative, daysAgo } = require("../../utils/date")
const PAGE_SIZE = 50

Page({
  data: {
    allWords: [],
    displayWords: [],
    filteredCount: 0,
    total: 0,
    weekNew: 0,
    keyword: "",
    newWord: "",
    loading: true,
    loadingMore: false,
    error: ""
  },

  filtered: [],
  searchTimer: null,

  onShow() {
    if (!isLoggedIn()) {
      redirectToLogin()
      return
    }
    this.loadWords()
  },

  onPullDownRefresh() {
    this.loadWords().finally(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    this.loadMore()
  },

  async loadWords() {
    this.setData({ loading: true, error: "" })
    try {
      const words = await api.fetchAllWords()
      words.sort(
        (a, b) => new Date(b.gmt_update) - new Date(a.gmt_update)
      )
      const weekNew = words.filter((w) => daysAgo(w.gmt_create) <= 6).length
      this.setData({ allWords: words, total: words.length, weekNew })
      this.applyFilter()
    } catch (err) {
      this.setData({ error: err.message })
    } finally {
      this.setData({ loading: false })
    }
  },

  /** 本地模糊过滤（后端 word 参数仅支持精确匹配，本地过滤体验更好） */
  applyFilter() {
    const kw = this.data.keyword.trim().toLowerCase()
    this.filtered = kw
      ? this.data.allWords.filter((w) => w.word.toLowerCase().includes(kw))
      : this.data.allWords.slice()
    const first = this.filtered.slice(0, PAGE_SIZE).map(this.decorate)
    this.setData({
      displayWords: first,
      filteredCount: this.filtered.length
    })
  },

  decorate(w) {
    return {
      ...w,
      relativeTime: formatRelative(w.gmt_update),
      defShort: (w.definition || "").split("\n")[0]
    }
  },

  loadMore() {
    const shown = this.data.displayWords.length
    if (shown >= this.filtered.length || this.data.loadingMore) return
    const more = this.filtered.slice(shown, shown + PAGE_SIZE).map(this.decorate)
    this.setData({
      displayWords: this.data.displayWords.concat(more),
      loadingMore: false
    })
  },

  onSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ keyword })
    if (this.searchTimer) clearTimeout(this.searchTimer)
    this.searchTimer = setTimeout(() => this.applyFilter(), 300)
  },

  onNewWordInput(e) {
    this.setData({ newWord: e.detail.value })
  },

  async addWord() {
    const word = this.data.newWord.trim()
    if (!word) return
    try {
      const saved = await api.addWord(word)
      // 后端按 (uid, word) 去重：已存在时更新并返回原记录，本地先去重再插入
      const rest = this.data.allWords.filter((w) => w.word !== saved.word)
      const weekNew =
        this.data.weekNew + (daysAgo(saved.gmt_create) <= 6 ? 1 : 0)
      this.setData({
        allWords: [saved, ...rest],
        newWord: "",
        total: rest.length + 1,
        weekNew
      })
      this.applyFilter()
      wx.showToast({ title: "已添加", icon: "success" })
    } catch (err) {
      wx.showToast({ title: err.message, icon: "none" })
    }
  },

  onWordTap(e) {
    const item = e.currentTarget.dataset.item
    wx.showActionSheet({
      itemList: ["编辑", "删除"],
      success: (res) => {
        if (res.tapIndex === 0) this.editWord(item)
        if (res.tapIndex === 1) this.confirmDelete(item)
      }
    })
  },

  editWord(item) {
    wx.showModal({
      title: "编辑生词",
      editable: true,
      content: item.word,
      placeholderText: "输入新的单词或短语",
      success: (res) => {
        const text = (res.content || "").trim()
        if (!res.confirm || !text || text === item.word) return
        api
          .updateWord(item.id, text)
          .then((updated) => {
            const allWords = this.data.allWords.map((w) =>
              w.id === updated.id ? updated : w
            )
            allWords.sort(
              (a, b) => new Date(b.gmt_update) - new Date(a.gmt_update)
            )
            this.setData({ allWords })
            this.applyFilter()
            wx.showToast({ title: "已更新", icon: "success" })
          })
          .catch((err) => wx.showToast({ title: err.message, icon: "none" }))
      }
    })
  },

  confirmDelete(item) {
    wx.showModal({
      title: "删除生词",
      content: "确定删除「" + item.word + "」吗？",
      confirmColor: "#fa5151",
      success: (res) => {
        if (!res.confirm) return
        api
          .deleteWord(item.id)
          .then(() => {
            const allWords = this.data.allWords.filter((w) => w.id !== item.id)
            const weekNew = Math.max(
              0,
              this.data.weekNew - (daysAgo(item.gmt_create) <= 6 ? 1 : 0)
            )
            this.setData({ allWords, total: allWords.length, weekNew })
            this.applyFilter()
            wx.showToast({ title: "已删除", icon: "success" })
          })
          .catch((err) => wx.showToast({ title: err.message, icon: "none" }))
      }
    })
  }
})
