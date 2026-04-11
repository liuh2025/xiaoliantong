<template>
  <div class="login-card">
    <h2 class="login-title">登录</h2>

    <!-- Tab switching -->
    <div class="login-tabs">
      <button
        class="login-tab"
        :class="{ active: activeTab === 'sms' }"
        @click="activeTab = 'sms'"
      >
        短信验证码登录
      </button>
      <button
        class="login-tab"
        :class="{ active: activeTab === 'password' }"
        @click="activeTab = 'password'"
      >
        密码登录
      </button>
    </div>

    <!-- SMS Login Form -->
    <el-form
      v-show="activeTab === 'sms'"
      ref="smsFormRef"
      :model="smsForm"
      :rules="smsRules"
      @submit.prevent="handleSmsLogin"
    >
      <el-form-item prop="phone">
        <el-input
          v-model="smsForm.phone"
          placeholder="请输入手机号"
          maxlength="11"
          :prefix-icon="Phone"
        />
      </el-form-item>
      <el-form-item prop="code">
        <div class="code-input-wrapper">
          <el-input
            v-model="smsForm.code"
            placeholder="请输入验证码"
            maxlength="6"
            :prefix-icon="Message"
          />
          <el-button
            type="primary"
            :disabled="smsCountdown.isCounting.value || !isSmsPhoneValid"
            :loading="sendingSms"
            @click="handleSendSms('login')"
          >
            {{ smsCountdown.isCounting.value ? `${smsCountdown.remaining.value}s` : '获取验证码' }}
          </el-button>
        </div>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="smsForm.rememberMe">7天内免登录</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          class="login-btn"
          :loading="loading"
          @click="handleSmsLogin"
        >
          登 录
        </el-button>
      </el-form-item>
    </el-form>

    <!-- Password Login Form -->
    <el-form
      v-show="activeTab === 'password'"
      ref="passwordFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      @submit.prevent="handlePasswordLogin"
    >
      <el-form-item prop="phone">
        <el-input
          v-model="passwordForm.phone"
          placeholder="请输入手机号"
          maxlength="11"
          :prefix-icon="Phone"
        />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="passwordForm.password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="请输入密码"
          :prefix-icon="Lock"
        >
          <template #suffix>
            <span class="password-toggle" @click="showPassword = !showPassword">
              <el-icon><component :is="showPassword ? Hide : View" /></el-icon>
            </span>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <div class="password-form-actions">
          <el-checkbox v-model="passwordForm.rememberMe">7天内免登录</el-checkbox>
          <el-link type="primary" :underline="false" @click="showForgotDialog = true">
            忘记密码？
          </el-link>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          class="login-btn"
          :loading="loading"
          @click="handlePasswordLogin"
        >
          登 录
        </el-button>
      </el-form-item>
    </el-form>

    <!-- Register link -->
    <div class="login-footer">
      还没有账号？
      <router-link to="/register">立即注册</router-link>
    </div>

    <!-- Forgot Password Dialog -->
    <el-dialog
      v-model="showForgotDialog"
      title="忘记密码"
      width="400px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-steps :active="forgotStep" align-center class="forgot-steps">
        <el-step title="验证手机" />
        <el-step title="设置新密码" />
      </el-steps>

      <!-- Step 1: Verify phone + code -->
      <el-form
        v-show="forgotStep === 0"
        ref="forgotVerifyRef"
        :model="forgotForm"
        :rules="forgotVerifyRules"
      >
        <el-form-item prop="phone">
          <el-input
            v-model="forgotForm.phone"
            placeholder="请输入手机号"
            maxlength="11"
            :prefix-icon="Phone"
          />
        </el-form-item>
        <el-form-item prop="code">
          <div class="code-input-wrapper">
            <el-input
              v-model="forgotForm.code"
              placeholder="请输入验证码"
              maxlength="6"
              :prefix-icon="Message"
            />
            <el-button
              type="primary"
              :disabled="forgotCountdown.isCounting.value || !isForgotPhoneValid"
              :loading="sendingForgotSms"
              @click="handleSendSms('reset')"
            >
              {{ forgotCountdown.isCounting.value ? `${forgotCountdown.remaining.value}s` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <!-- Step 2: Set new password -->
      <el-form
        v-show="forgotStep === 1"
        ref="forgotResetRef"
        :model="forgotResetForm"
        :rules="forgotResetRules"
      >
        <el-form-item prop="password">
          <el-input
            v-model="forgotResetForm.password"
            :type="showNewPassword ? 'text' : 'password'"
            placeholder="8-20位，字母数字组合"
            :prefix-icon="Lock"
          >
            <template #suffix>
              <span class="password-toggle" @click="showNewPassword = !showNewPassword">
                <el-icon><component :is="showNewPassword ? Hide : View" /></el-icon>
              </span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="forgotResetForm.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            placeholder="请确认新密码"
            :prefix-icon="Lock"
          >
            <template #suffix>
              <span class="password-toggle" @click="showConfirmPassword = !showConfirmPassword">
                <el-icon><component :is="showConfirmPassword ? Hide : View" /></el-icon>
              </span>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleForgotCancel">
          {{ forgotStep === 0 ? '取消' : '上一步' }}
        </el-button>
        <el-button
          type="primary"
          :loading="forgotLoading"
          @click="handleForgotNext"
        >
          {{ forgotStep === 0 ? '下一步' : '确认重置' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Message, Lock, View, Hide } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { sendSmsCode, verifyResetCode, resetPassword } from '../../api/auth'
import { useCountdown } from '../../composables/useCountdown'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Tab state
const activeTab = ref('sms')

// Loading state
const loading = ref(false)

// Countdown for SMS login
const smsCountdown = useCountdown(60)
// Countdown for forgot password
const forgotCountdown = useCountdown(60)

// SMS sending state
const sendingSms = ref(false)
const sendingForgotSms = ref(false)

// Password visibility
const showPassword = ref(false)

// --- SMS Login Form ---
const smsFormRef = ref(null)
const smsForm = ref({
  phone: '',
  code: '',
  rememberMe: false,
})

const phonePattern = /^1[3-9]\d{9}$/

const isSmsPhoneValid = computed(() => phonePattern.test(smsForm.value.phone))

const smsRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: phonePattern, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}

// --- Password Login Form ---
const passwordFormRef = ref(null)
const passwordForm = ref({
  phone: '',
  password: '',
  rememberMe: false,
})

const passwordRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: phonePattern, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度为8-20位', trigger: 'blur' },
  ],
}

// --- Forgot Password ---
const showForgotDialog = ref(false)
const forgotStep = ref(0)
const forgotLoading = ref(false)
const forgotVerifyRef = ref(null)
const forgotResetRef = ref(null)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const forgotForm = ref({
  phone: '',
  code: '',
})

const forgotResetForm = ref({
  password: '',
  confirmPassword: '',
})

const forgotVerifyToken = ref('')

const isForgotPhoneValid = computed(() => phonePattern.test(forgotForm.value.phone))

const forgotVerifyRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: phonePattern, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}

const forgotResetRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度为8-20位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== forgotResetForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// --- Send SMS ---
async function handleSendSms(type) {
  const phone = type === 'login' ? smsForm.value.phone : forgotForm.value.phone
  if (!phonePattern.test(phone)) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }

  const countdown = type === 'login' ? smsCountdown : forgotCountdown
  const sendingRef = type === 'login' ? sendingSms : sendingForgotSms

  try {
    sendingRef.value = true
    await sendSmsCode(phone, type)
    ElMessage.success('验证码已发送')
    countdown.start()
  } catch (error) {
    const msg = error.response?.data?.message || '发送验证码失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    sendingRef.value = false
  }
}

// --- SMS Login ---
async function handleSmsLogin() {
  const valid = await smsFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.loginBySms(
      smsForm.value.phone,
      smsForm.value.code,
      smsForm.value.rememberMe,
    )
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    const msg = error.response?.data?.message || '登录失败，请检查验证码是否正确'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

// --- Password Login ---
async function handlePasswordLogin() {
  const valid = await passwordFormRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.loginByPassword(
      passwordForm.value.phone,
      passwordForm.value.password,
      passwordForm.value.rememberMe,
    )
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    const msg = error.response?.data?.message || '登录失败，请检查手机号和密码'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

// --- Forgot Password ---
function handleForgotCancel() {
  if (forgotStep.value === 1) {
    forgotStep.value = 0
  } else {
    closeForgotDialog()
  }
}

function closeForgotDialog() {
  showForgotDialog.value = false
  forgotStep.value = 0
  forgotForm.value = { phone: '', code: '' }
  forgotResetForm.value = { password: '', confirmPassword: '' }
  forgotVerifyToken.value = ''
}

async function handleForgotNext() {
  if (forgotStep.value === 0) {
    // Step 1: Verify phone + code
    const valid = await forgotVerifyRef.value?.validate().catch(() => false)
    if (!valid) return

    forgotLoading.value = true
    try {
      const { data } = await verifyResetCode(forgotForm.value.phone, forgotForm.value.code)
      // Handle both code: 0 and code: 200 as success
      const resCode = data.code
      if (resCode === 0 || resCode === 200) {
        forgotVerifyToken.value = data.data.verify_token || data.data.verifyToken || ''
        forgotStep.value = 1
      } else {
        ElMessage.error(data.message || '验证失败')
      }
    } catch (error) {
      const msg = error.response?.data?.message || '验证失败，请检查验证码'
      ElMessage.error(msg)
    } finally {
      forgotLoading.value = false
    }
  } else {
    // Step 2: Reset password
    const valid = await forgotResetRef.value?.validate().catch(() => false)
    if (!valid) return

    forgotLoading.value = true
    try {
      const { data } = await resetPassword(
        forgotForm.value.phone,
        forgotVerifyToken.value,
        forgotResetForm.value.password,
      )
      const resCode = data.code
      if (resCode === 0 || resCode === 200) {
        ElMessage.success('密码重置成功，请使用新密码登录')
        closeForgotDialog()
        // Pre-fill phone and switch to password tab
        passwordForm.value.phone = forgotForm.value.phone
        activeTab.value = 'password'
      } else {
        ElMessage.error(data.message || '重置失败')
      }
    } catch (error) {
      const msg = error.response?.data?.message || '密码重置失败，请稍后重试'
      ElMessage.error(msg)
    } finally {
      forgotLoading.value = false
    }
  }
}
</script>

<style scoped>
.login-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-lg);
}

.login-title {
  text-align: center;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

/* Custom Tabs */
.login-tabs {
  display: flex;
  margin-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-border-light);
}

.login-tab {
  flex: 1;
  padding: 10px 0;
  background: none;
  border: none;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.login-tab:hover {
  color: var(--color-primary);
}

.login-tab.active {
  color: var(--color-primary);
}

.login-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-primary);
  border-radius: 1px;
}

/* Code input */
.code-input-wrapper {
  display: flex;
  width: 100%;
  gap: var(--spacing-sm);
}

.code-input-wrapper .el-input {
  flex: 1;
}

.code-input-wrapper .el-button {
  white-space: nowrap;
  min-width: 110px;
}

/* Password toggle */
.password-toggle {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  color: var(--color-text-placeholder);
}

.password-toggle:hover {
  color: var(--color-text-secondary);
}

/* Password form actions */
.password-form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* Login button */
.login-btn {
  width: 100%;
}

/* Footer */
.login-footer {
  text-align: center;
  margin-top: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.login-footer a {
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

.login-footer a:hover {
  text-decoration: underline;
}

/* Forgot password steps */
.forgot-steps {
  margin-bottom: var(--spacing-lg);
}

/* Element Plus overrides for auth card */
.login-card :deep(.el-input__wrapper) {
  border-radius: var(--radius-sm);
}

.login-card :deep(.el-form-item) {
  margin-bottom: 20px;
}

.login-card :deep(.el-button--primary) {
  border-radius: var(--radius-sm);
}
</style>
