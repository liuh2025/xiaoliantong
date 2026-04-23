<template>
  <el-popover placement="bottom-end" :width="360" trigger="click" @show="handleShow">
    <template #reference>
      <el-badge :value="store.unreadCount" :hidden="store.unreadCount === 0" :max="99">
        <el-icon :size="20" style="cursor: pointer;"><Bell /></el-icon>
      </el-badge>
    </template>
    <div class="notif-panel">
      <div class="notif-header">
        <span>消息通知</span>
        <el-button link size="small" @click="handleMarkAllRead">全部已读</el-button>
      </div>
      <div class="notif-list">
        <div
          v-for="msg in store.recentMessages"
          :key="msg.id"
          class="notif-item"
          :class="{ 'notif-item--unread': !msg.is_read }"
          @click="store.markRead(msg.id)"
        >
          <div class="notif-title">{{ msg.title }}</div>
          <div class="notif-time">{{ msg.created_at }}</div>
        </div>
        <div v-if="store.recentMessages.length === 0" class="notif-empty">暂无消息</div>
      </div>
      <div class="notif-footer">
        <router-link to="/notification">查看全部</router-link>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { Bell } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useNotificationStore } from '../stores/notification'

const store = useNotificationStore()

function handleShow() {
  store.fetchRecent()
}

async function handleMarkAllRead() {
  await store.markAllRead()
  ElMessage.success('已全部已读')
}
</script>

<style scoped>
.notif-panel {
  margin: -12px;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  font-weight: var(--font-weight-semibold);
}

.notif-list {
  max-height: 320px;
  overflow-y: auto;
}

.notif-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border-light);
}

.notif-item:hover {
  background: var(--color-primary-bg);
}

.notif-item--unread {
  background: var(--color-primary-bg);
}

.notif-title {
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.notif-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.notif-empty {
  padding: 32px;
  text-align: center;
  color: var(--color-text-placeholder);
}

.notif-footer {
  padding: 12px 16px;
  text-align: center;
  border-top: 1px solid var(--color-border);
}
</style>
