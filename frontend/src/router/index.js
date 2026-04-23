import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/auth/Login.vue'),
    meta: { layout: 'auth', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../pages/auth/Register.vue'),
    meta: { layout: 'auth', guest: true },
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/public/Index.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/promotion',
    name: 'Promotion',
    component: () => import('../pages/public/Promotion.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../pages/public/Search.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/enterprise',
    name: 'Enterprise',
    component: () => import('../pages/enterprise/Index.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/opportunity',
    name: 'Opportunity',
    component: () => import('../pages/opportunity/Index.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/opportunity/:id',
    name: 'OpportunityDetail',
    component: () => import('../pages/opportunity/Detail.vue'),
    meta: { layout: 'default', auth: true },
  },
  {
    path: '/feed',
    name: 'Feed',
    component: () => import('../pages/feed/Index.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/notification',
    name: 'Notification',
    component: () => import('../pages/notification/Index.vue'),
    meta: { layout: 'default', auth: true },
  },
  {
    path: '/ent-admin',
    name: 'EntAdmin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { layout: 'admin', auth: true, role: 'enterprise_admin' },
    children: [
      { path: '', redirect: '/ent-admin/enterprise-info' },
      { path: 'enterprise-info', name: 'EnterpriseInfo', component: () => import('../pages/ent-admin/EnterpriseInfo.vue') },
      { path: 'employee', name: 'Employee', component: () => import('../pages/ent-admin/Employee.vue') },
      { path: 'my-opportunity', name: 'MyOpportunity', component: () => import('../pages/ent-admin/MyOpportunity.vue') },
    ],
  },
  {
    path: '/plat-admin',
    name: 'PlatAdmin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { layout: 'admin', auth: true, role: 'platform_operator' },
    children: [
      { path: '', redirect: '/plat-admin/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../pages/plat-admin/Dashboard.vue') },
      { path: 'audit', name: 'Audit', component: () => import('../pages/plat-admin/Audit.vue') },
      { path: 'tenant', name: 'Tenant', component: () => import('../pages/plat-admin/Tenant.vue') },
      { path: 'opportunity-manage', name: 'OpportunityManage', component: () => import('../pages/plat-admin/OpportunityManage.vue') },
      { path: 'feed-manage', name: 'FeedManage', component: () => import('../pages/plat-admin/FeedManage.vue') },
      { path: 'master-data', name: 'MasterData', component: () => import('../pages/plat-admin/MasterData.vue') },
      { path: 'rbac', name: 'Rbac', component: () => import('../pages/plat-admin/Rbac.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../pages/plat-admin/Settings.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const userInfo = localStorage.getItem('user_info')

  if (to.meta.auth && !token) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  if (to.meta.role && userInfo) {
    try {
      const user = JSON.parse(userInfo)
      if (to.meta.role === 'enterprise_admin' && (user.role_code !== 'enterprise_admin' || !user.enterprise_id)) {
        return next({ name: 'Home' })
      }
      if (to.meta.role === 'platform_operator' && user.role_code !== 'platform_operator' && user.role_code !== 'super_admin') {
        return next({ name: 'Home' })
      }
    } catch {
      return next({ name: 'Login' })
    }
  }

  if (to.meta.guest && token) {
    return next({ name: 'Home' })
  }

  next()
})

export default router
