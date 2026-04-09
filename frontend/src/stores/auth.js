import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { smsLogin, passwordLogin, getUserInfo, logout as logoutApi } from '../api/auth'
import { clearAuth } from '../api/request'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)
  const userName = computed(() => user.value?.username || '')
  const userRole = computed(() => user.value?.role_code || 'guest')
  const enterpriseId = computed(() => user.value?.enterprise_id || null)
  const hasEnterprise = computed(() => !!enterpriseId.value)

  async function loginBySms(phone, code, rememberMe = false) {
    const { data } = await smsLogin(phone, code, rememberMe)
    _setTokens(data.data)
    await fetchUser()
  }

  async function loginByPassword(phone, password, rememberMe = false) {
    const { data } = await passwordLogin(phone, password, rememberMe)
    _setTokens(data.data)
    await fetchUser()
  }

  async function fetchUser() {
    const { data } = await getUserInfo()
    user.value = data.data
    localStorage.setItem('user_info', JSON.stringify(data.data))
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await logoutApi(refreshToken.value)
      }
    } finally {
      clearAuth()
      accessToken.value = ''
      refreshToken.value = ''
      user.value = null
    }
  }

  function _setTokens(tokenData) {
    accessToken.value = tokenData.access || ''
    refreshToken.value = tokenData.refresh || ''
    localStorage.setItem('access_token', tokenData.access || '')
    localStorage.setItem('refresh_token', tokenData.refresh || '')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoggedIn,
    userName,
    userRole,
    enterpriseId,
    hasEnterprise,
    loginBySms,
    loginByPassword,
    fetchUser,
    logout,
  }
})
