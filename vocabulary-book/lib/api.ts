// lib/api.ts - 后端请求统一封装
// P0-3: API 地址可配置（构建时用 PLASMO_PUBLIC_API_BASE 覆盖，生产环境必须为 HTTPS）
// P0-1: 请求自动携带 JWT
// P1-4: 后端不可达时的离线待同步队列

const DEFAULT_API_BASE = "http://127.0.0.1:7001"

export const API_BASE = process.env.PLASMO_PUBLIC_API_BASE || DEFAULT_API_BASE

export type ApiResult<T = any> = {
  success?: boolean
  message?: string
  data?: T
  error?: string
}

export type UserInfo = {
  user_info?: {
    id?: number
    phone?: string
    nickname?: string
    avatar?: string
  }
  token?: string
}

const USER_INFO_KEY = "userInfo"
const PENDING_WORDS_KEY = "pendingWords"
// 离线队列上限，防止长期未登录或后端不可达时无限膨胀
const PENDING_WORDS_LIMIT = 200

export async function getUserInfo(): Promise<UserInfo | null> {
  const result = await chrome.storage.local.get(USER_INFO_KEY)
  return result[USER_INFO_KEY] || null
}

export async function setUserInfo(info: UserInfo): Promise<void> {
  await chrome.storage.local.set({ [USER_INFO_KEY]: info })
}

export async function clearUserInfo(): Promise<void> {
  await chrome.storage.local.remove(USER_INFO_KEY)
}

// P1-6: 解析 JWT 的 exp 判断登录态是否仍然有效
export function isTokenExpired(token?: string): boolean {
  if (!token) return true
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")
    const payload = JSON.parse(atob(base64))
    return typeof payload.exp !== "number" || payload.exp * 1000 <= Date.now()
  } catch {
    return true
  }
}

export async function isLoggedIn(): Promise<boolean> {
  const info = await getUserInfo()
  return !!info && !isTokenExpired(info.token)
}

export async function apiFetch<T = ApiResult>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const info = await getUserInfo()
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init?.headers as Record<string, string>) || {})
  }
  if (info?.token) {
    headers["Authorization"] = `Bearer ${info.token}`
  }
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers })
  if (response.status === 401) {
    // 登录态失效：清理本地用户信息，下次打开弹窗回到登录页
    await clearUserInfo()
    throw new Error("登录已过期，请重新登录")
  }
  // P2-1: 非 2xx 统一抛出并携带后端 message，调用方只需处理异常分支
  if (!response.ok) {
    let message = `请求失败（${response.status}）`
    try {
      const body = (await response.json()) as ApiResult
      if (body?.message) message = body.message
    } catch {
      // 非 JSON 响应体时保留默认提示
    }
    throw new Error(message)
  }
  return (await response.json()) as T
}

export async function getPendingWords(): Promise<string[]> {
  const result = await chrome.storage.local.get(PENDING_WORDS_KEY)
  return result[PENDING_WORDS_KEY] || []
}

export async function queuePendingWord(word: string): Promise<void> {
  const pending = await getPendingWords()
  if (!pending.includes(word)) {
    pending.push(word)
    await chrome.storage.local.set({
      [PENDING_WORDS_KEY]: pending.slice(-PENDING_WORDS_LIMIT)
    })
  }
}

export async function postWord(word: string): Promise<boolean> {
  try {
    const data = await apiFetch("/api/word/", {
      method: "POST",
      body: JSON.stringify({ word })
    })
    // 200 但 success=false 也视为失败，交由离线队列重试
    return data?.success !== false
  } catch {
    return false
  }
}

// 逐个重试离线队列中的单词，失败的留在队列中等待下次
export async function flushPendingWords(): Promise<number> {
  const pending = await getPendingWords()
  if (!pending.length) return 0
  const failed: string[] = []
  for (const word of pending) {
    const ok = await postWord(word)
    if (!ok) failed.push(word)
  }
  await chrome.storage.local.set({ [PENDING_WORDS_KEY]: failed })
  return pending.length - failed.length
}
