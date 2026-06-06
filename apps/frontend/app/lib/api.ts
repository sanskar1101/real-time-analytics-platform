import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL ?? BASE_URL.replace(/^http/, 'ws')

const TOKEN_COOKIE_MAX_AGE = 60 * 60 * 24 // 1 day

export function setTokens(access: string, refresh: string) {
  if (typeof window === 'undefined') return
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
  // Cookie lets the middleware read auth state without touching localStorage (server-only)
  document.cookie = `access_token=${access}; path=/; max-age=${TOKEN_COOKIE_MAX_AGE}; SameSite=Lax`
}

export function clearTokens() {
  if (typeof window === 'undefined') return
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  document.cookie = 'access_token=; path=/; max-age=0'
}

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        const refresh = localStorage.getItem('refresh_token')
        if (refresh && !error.config._retried) {
          error.config._retried = true
          try {
            const { data } = await axios.post(`${BASE_URL}/api/v1/auth/refresh`, {
              refresh_token: refresh,
            })
            setTokens(data.access_token, data.refresh_token)
            error.config.headers.Authorization = `Bearer ${data.access_token}`
            return api(error.config)
          } catch {
            clearTokens()
          }
        }
      }
    }
    return Promise.reject(error)
  },
)

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export function getWsUrl(): string {
  const token = getAccessToken()
  return `${WS_BASE_URL}/api/v1/ws/notifications${token ? `?token=${token}` : ''}`
}
