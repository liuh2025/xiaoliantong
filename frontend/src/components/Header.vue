<template>
  <header class="header">
    <div class="header-inner">
      <div class="header-left">
        <router-link to="/" class="header-brand">校链通</router-link>
        <nav class="header-nav">
          <router-link to="/" class="nav-link" active-class="nav-link--active">首页</router-link>
          <router-link to="/opportunity" class="nav-link" active-class="nav-link--active">商机广场</router-link>
          <router-link to="/enterprise" class="nav-link" active-class="nav-link--active">企业名录</router-link>
          <router-link to="/feed" class="nav-link" active-class="nav-link--active">校友圈</router-link>
        </nav>
      </div>
      <div class="header-right">
        <div class="header-search" @click="$router.push('/search')">
          <el-icon><Search /></el-icon>
          <span>搜索</span>
        </div>
        <NotificationBell v-if="authStore.isLoggedIn" />
        <template v-if="authStore.isLoggedIn">
          <el-dropdown trigger="click">
            <span class="header-user">
              {{ authStore.userName || '用户' }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="authStore.hasEnterprise" @click="$router.push('/ent-admin')">
                  企业工作台
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="['platform_operator', 'super_admin'].includes(authStore.userRole)"
                  @click="$router.push('/plat-admin')"
                >
                  管理后台
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="header-login-btn">登录</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Search, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import NotificationBell from './NotificationBell.vue'

const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  window.location.href = '/login'
}
</script>

<style scoped>
.header {
  height: var(--header-height);
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-md);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.header-brand {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  text-decoration: none;
}

.header-nav {
  display: flex;
  gap: 24px;
}

.nav-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav-link:hover,
.nav-link--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-search {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--color-border-light);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.header-search:hover {
  background: var(--color-border);
}

.header-user {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.header-login-btn {
  padding: 6px 16px;
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  text-decoration: none;
}

.header-login-btn:hover {
  background: var(--color-primary-dark);
}
</style>
