<template>
  <div class="register-card">
    <h2 class="register-title">注册</h2>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      @submit.prevent="handleRegister"
    >
      <el-form-item prop="phone">
        <el-input
          v-model="form.phone"
          placeholder="请输入手机号"
          maxlength="11"
          :prefix-icon="Phone"
        />
      </el-form-item>

      <el-form-item prop="code">
        <div class="code-input-wrapper">
          <el-input
            v-model="form.code"
            placeholder="请输入验证码"
            maxlength="6"
            :prefix-icon="Message"
          />
          <el-button
            type="primary"
            :disabled="countdown.isCounting.value || !isPhoneValid"
            :loading="sendingSms"
            @click="handleSendSms"
          >
            {{ countdown.isCounting.value ? `${countdown.remaining.value}s` : '获取验证码' }}
          </el-button>
        </div>
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="请设置登录密码（8-20位）"
          :prefix-icon="Lock"
        >
          <template #suffix>
            <span class="password-toggle" @click="showPassword = !showPassword">
              <el-icon><component :is="showPassword ? Hide : View" /></el-icon>
            </span>
          </template>
        </el-input>
        <!-- Password strength indicator -->
        <div v-if="form.password" class="password-strength">
          <div class="strength-bars">
            <div class="strength-bar" :class="{ active: passwordStrength >= 1 }" />
            <div class="strength-bar" :class="{ active: passwordStrength >= 2 }" />
            <div class="strength-bar" :class="{ active: passwordStrength >= 3 }" />
          </div>
          <span class="strength-text" :class="strengthClass">{{ strengthLabel }}</span>
        </div>
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          :type="showConfirm ? 'text' : 'password'"
          placeholder="请确认密码"
          :prefix-icon="Lock"
        >
          <template #suffix>
            <span class="password-toggle" @click="showConfirm = !showConfirm">
              <el-icon><component :is="showConfirm ? Hide : View" /></el-icon>
            </span>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item prop="agreement">
        <el-checkbox v-model="form.agreement">
          我已阅读并同意
          <el-link type="primary" :underline="false">《校链通用户协议》</el-link>
          和
          <el-link type="primary" :underline="false">《隐私政策》</el-link>
        </el-checkbox>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          class="register-btn"
          :loading="loading"
          @click="handleRegister"
        >
          立即注册
        </el-button>
      </el-form-item>
    </el-form>

    <div class="register-footer">
      已有账号？
      <router-link to="/login">立即登录</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Message, Lock, View, Hide } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { sendSmsCode } from '../../api/auth'
import { useCountdown } from '../../composables/useCountdown'

const router = useRouter()
const authStore = useAuthStore()
const countdown = useCountdown(60)

const formRef = ref(null)
const loading = ref(false)
const sendingSms = ref(false)
const showPassword = ref(false)
const showConfirm = ref(false)

const form = ref({
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
  agreement: false,
})

const phonePattern = /^1[3-9]\d{9}$/

const isPhoneValid = computed(() => phonePattern.test(form.value.phone))

// --- Password Strength ---
const passwordStrength = computed(() => {
  const pwd = form.value.password
  if (!pwd) return 0
  let strength = 0
  if (pwd.length >= 6) strength++
  if (/[a-zA-Z]/.test(pwd) && /\d/.test(pwd)) strength++
  if (/[^a-zA-Z0-9]/.test(pwd)) strength++
  return strength
})

const strengthLabel = computed(() => {
  const labels = ['', '弱', '中', '强']
  return labels[passwordStrength.value]
})

const strengthClass = computed(() => {
  const classes = ['', 'strength-weak', 'strength-medium', 'strength-strong']
  return classes[passwordStrength.value]
})

// --- Validation Rules ---
const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: phonePattern, message: '请输入正确的手机号', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度为8-20位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  agreement: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请先同意用户协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

// --- Send SMS ---
async function handleSendSms() {
  if (!isPhoneValid.value) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }

  try {
    sendingSms.value = true
    await sendSmsCode(form.value.phone, 'register')
    ElMessage.success('验证码已发送')
    countdown.start()
  } catch (error) {
    const msg = error.response?.data?.message || '发送验证码失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    sendingSms.value = false
  }
}

// --- Register ---
async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.register(form.value.phone, form.value.code, form.value.password)
    ElMessage.success('注册成功')
    router.push('/')
  } catch (error) {
    const msg = error.response?.data?.message || '注册失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-lg);
}

.register-title {
  text-align: center;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
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

/* Password strength indicator */
.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.strength-bars {
  display: flex;
  gap: 4px;
}

.strength-bar {
  width: 32px;
  height: 4px;
  border-radius: 2px;
  background: var(--color-border);
  transition: background 0.2s;
}

.strength-bar.active:nth-child(1) {
  background: var(--color-error);
}

.strength-bar.active:nth-child(2) {
  background: var(--color-warning);
}

.strength-bar.active:nth-child(3) {
  background: var(--color-success);
}

.strength-text {
  font-size: var(--font-size-xs);
}

.strength-weak {
  color: var(--color-error);
}

.strength-medium {
  color: var(--color-warning);
}

.strength-strong {
  color: var(--color-success);
}

/* Register button */
.register-btn {
  width: 100%;
}

/* Footer */
.register-footer {
  text-align: center;
  margin-top: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.register-footer a {
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

.register-footer a:hover {
  text-decoration: underline;
}

/* Element Plus overrides for auth card */
.register-card :deep(.el-input__wrapper) {
  border-radius: var(--radius-sm);
}

.register-card :deep(.el-form-item) {
  margin-bottom: 20px;
}

.register-card :deep(.el-button--primary) {
  border-radius: var(--radius-sm);
}

.register-card :deep(.el-checkbox__label) {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}
</style>
