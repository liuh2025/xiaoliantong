<template>
  <div class="notification-page">
    <!-- Header -->
    <div class="notif-header">
      <h2>通知消息</h2>
      <el-button type="primary" text :disabled="!hasUnread" @click="handleMarkAllRead">
        全部已读
      </el-button>
    </div>

    <!-- Notification List -->
    <div v-loading="loading">
      <div v-if="notifications.length" class="notif-list">
        <div
          v-for="notif in notifications"
          :key="notif.id"
          class="notif-item"
          :class="{ unread: !notif.is_read }"
          @click="handleMarkRead(notif)"
        >
          <div class="notif-icon" :class="getNotifIconClass(notif)">
            {{ getNotifIconEmoji(notif) }}
          </div>
          <div class="notif-body">
            <div class="notif-title">{{ notif.title }}</div>
            <p class="notif-content">{{ notif.content }}</p>
            <div class="notif-meta">
              <el-tag v-if="getNotifTag(notif)" :type="getNotifTag(notif).type" size="small" class="notif-tag">
                {{ getNotifTag(notif).label }}
              </el-tag>
              <span class="notif-time">{{ notif.created_at }}</span>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无消息" />
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadNotifications"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getNotifications, markRead, markAllRead } from '../../api/message'
import { useNotificationStore } from '../../stores/notification'

const notificationStore = useNotificationStore()

const notifications = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const hasUnread = computed(() => notifications.value.some((n) => !n.is_read))

async function loadNotifications() {
  loading.value = true
  try {
    const { data } = await getNotifications({
      page: currentPage.value,
      page_size: pageSize.value,
    })
    if (data.code === 200) {
      notifications.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function handleMarkRead(notif) {
  if (notif.is_read) return
  try {
    await markRead(notif.id)
    notif.is_read = true
    notificationStore.fetchRecent()
  } catch {
    // silently fail
  }
}

async function handleMarkAllRead() {
  try {
    await markAllRead()
    notifications.value.forEach((n) => { n.is_read = true })
    notificationStore.fetchRecent()
    ElMessage.success('已全部标记为已读')
  } catch {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadNotifications()
})

function getNotifIconClass(notif) {
  const title = notif.title || ''
  if (title.includes('通过审核') || title.includes('已通过')) return 'audit-approved'
  if (title.includes('未通过') || title.includes('拒绝') || title.includes('驳回')) return 'audit-rejected'
  if (title.includes('查看请求') || title.includes('联系方式') || title.includes('商机')) return 'contact-received'
  return 'system'
}

function getNotifIconEmoji(notif) {
  const title = notif.title || ''
  if (title.includes('通过审核') || title.includes('已通过')) return '✓'
  if (title.includes('未通过') || title.includes('拒绝') || title.includes('驳回')) return '✕'
  if (title.includes('查看请求') || title.includes('联系方式') || title.includes('商机')) return '📞'
  return '⚙'
}

function getNotifTag(notif) {
  const title = notif.title || ''
  if (title.includes('通过审核') || title.includes('已通过')) return { label: '审核通过', type: 'success' }
  if (title.includes('未通过') || title.includes('拒绝') || title.includes('驳回')) return { label: '审核未通过', type: 'danger' }
  if (title.includes('查看请求') || title.includes('联系方式') || title.includes('商机')) return { label: '商机查看', type: '' }
  if (title.includes('系统')) return { label: '系统通知', type: 'info' }
  return null
}
</script>

<style scoped>
.notification-page {
  max-width: 700px;
  margin: 0 auto;
  padding-bottom: var(--spacing-2xl);
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.notif-header h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.notif-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--color-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background-color 0.15s;
}

.notif-item:last-child {
  border-bottom: none;
}

.notif-item:hover {
  background-color: var(--color-primary-bg);
}

.notif-item.unread {
  background-color: rgba(30, 136, 229, 0.03);
}

.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.notif-icon.audit-approved {
  background: rgba(76, 175, 80, 0.1);
  color: var(--color-success);
}

.notif-icon.audit-rejected {
  background: rgba(244, 67, 54, 0.1);
  color: var(--color-error);
}

.notif-icon.contact-received {
  background: rgba(30, 136, 229, 0.1);
  color: var(--color-primary);
}

.notif-icon.system {
  background: rgba(158, 158, 158, 0.1);
  color: #9e9e9e;
}

.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-title {
  font-size: 0.9375rem;
  font-weight: 500;
  margin-bottom: 4px;
}

.notif-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}

.notif-tag {
  font-size: 0.6875rem;
}

.notif-time {
  font-size: 0.75rem;
  color: var(--color-text-placeholder);
}

.notif-content {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}
</style>
