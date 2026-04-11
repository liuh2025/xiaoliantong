<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-brand">校链通</div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="sidebar-link"
          active-class="sidebar-link--active"
        >
          <span class="sidebar-link-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>
    <div class="admin-main">
      <header class="admin-header">
        <h2 class="admin-page-title">{{ pageTitle }}</h2>
        <div class="admin-header-actions">
          <NotificationBell />
        </div>
      </header>
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NotificationBell from '../components/NotificationBell.vue'

const route = useRoute()

const menuItems = computed(() => {
  if (route.path.startsWith('/plat-admin')) {
    return [
      { path: '/plat-admin/dashboard', label: '数据大盘', icon: '📊' },
      { path: '/plat-admin/audit', label: '企业审核', icon: '✅' },
      { path: '/plat-admin/tenant', label: '企业租户', icon: '🏢' },
      { path: '/plat-admin/opportunity-manage', label: '商机管理', icon: '📋' },
      { path: '/plat-admin/feed-manage', label: '动态管理', icon: '📰' },
      { path: '/plat-admin/master-data', label: '基础数据', icon: '📚' },
      { path: '/plat-admin/rbac', label: '账号权限', icon: '🔒' },
      { path: '/plat-admin/settings', label: '系统设置', icon: '⚙️' },
    ]
  }
  return [
    { path: '/ent-admin/enterprise-info', label: '企业信息', icon: '🏢' },
    { path: '/ent-admin/employee', label: '员工管理', icon: '👥' },
    { path: '/ent-admin/my-opportunity', label: '商机管理', icon: '📋' },
  ]
})

const pageTitle = computed(() => {
  const item = menuItems.value.find((m) => route.path === m.path)
  return item?.label || ''
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: var(--sidebar-width);
  background: #1F2937;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  padding: 20px 24px;
  font-size: 1.25rem;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  padding: 12px 0;
  flex: 1;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: all 0.2s;
}

.sidebar-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-link--active {
  color: #fff;
  background: var(--color-primary);
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.admin-header {
  height: var(--header-height);
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
}

.admin-page-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

.admin-content {
  flex: 1;
  padding: var(--spacing-lg);
  background: var(--color-bg);
}
</style>
