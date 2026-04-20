import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach access_token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401 + token refresh
let isRefreshing = false
let pendingRequests = []

request.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Handle 401 (token expired) before normalizing other errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        clearAuth()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push(() => {
            originalRequest.headers.Authorization = `Bearer ${localStorage.getItem('access_token')}`
            resolve(request(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const { data: resp } = await axios.post('/api/v1/auth/refresh/', {
          refresh_token: refreshToken,
        })
        localStorage.setItem('access_token', resp.data.access_token)
        localStorage.setItem('refresh_token', resp.data.refresh_token)
        originalRequest.headers.Authorization = `Bearer ${resp.data.access_token}`
        pendingRequests.forEach((cb) => cb())
        pendingRequests = []
        return request(originalRequest)
      } catch {
        clearAuth()
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    // Normalize backend error responses into resolved promises
    // so frontend can consistently check res.code === 200
    if (error.response?.data && typeof error.response.data.code === 'number') {
      return Promise.resolve({ data: error.response.data })
    }

    return Promise.reject(error)
  },
)

function clearAuth() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_info')
}

export default request
export { clearAuth }
