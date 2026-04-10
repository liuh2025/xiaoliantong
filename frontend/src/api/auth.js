import request from './request'

// POST /auth/register/
export function register(phone, code, password) {
  return request.post('/auth/register/', { phone, code, password })
}

// POST /auth/sms/send/
export function sendSmsCode(phone, type) {
  return request.post('/auth/sms/send/', { phone, type })
}

// POST /auth/sms/login/
export function smsLogin(phone, code, remember_me = false) {
  return request.post('/auth/sms/login/', { phone, code, remember_me })
}

// POST /auth/login/password/
export function passwordLogin(phone, password, remember_me = false) {
  return request.post('/auth/login/password/', { phone, password, remember_me })
}

// POST /auth/password/reset/verify
export function verifyResetCode(phone, code) {
  return request.post('/auth/password/reset/verify', { phone, code })
}

// POST /auth/password/reset
export function resetPassword(phone, verify_token, password) {
  return request.post('/auth/password/reset', { phone, verify_token, password })
}

// GET /auth/me
export function getUserInfo() {
  return request.get('/auth/me')
}

// POST /auth/refresh
export function refreshToken(refresh) {
  return request.post('/auth/refresh', { refresh })
}

// POST /auth/logout
export function logout(refresh) {
  return request.post('/auth/logout', { refresh })
}
