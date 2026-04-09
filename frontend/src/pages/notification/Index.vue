<template>
  <div class="notification-page">
    <!-- Header -->
    <div class="notif-header">
      <h2>消息通知</h2>
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
          <div class="notif-dot" :class="{ active: !notif.is_read }" />
          <div class="notif-body">
            <div class="notif-title-row">
              <span class="notif-title">{{ notif.title }}</span>
              <span class="notif-time">{{ notif.created_at }}</span>
            </div>
            <p class="notif-content">{{ notif.content }}</p>
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
  padding: var(--spacing-md) var(--spacing-lg);
  cursor: pointer;
  transition: background-color 0.15s;
}

.notif-item:hover {
  background-color: var(--color-primary-bg);
}

.notif-item.unread {
  background-color: var(--color-primary-bg);
}

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
  margin-top: 6px;
  flex-shrink: 0;
}

.notif-dot.active {
  background: var(--color-primary);
}

.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.notif-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.notif-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  flex-shrink: 0;
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
