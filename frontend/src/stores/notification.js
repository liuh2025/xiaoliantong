import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../api/request'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)
  const recentMessages = ref([])

  async function fetchRecent() {
    const { data } = await request.get('/msg/notifications/recent')
    if (data.code === 200) {
      recentMessages.value = data.data.items || []
      unreadCount.value = data.data.unread_count || 0
    }
  }

  async function markRead(id) {
    await request.put(`/msg/notifications/${id}/read`)
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }

  async function markAllRead() {
    await request.put('/msg/notifications/read-all')
    unreadCount.value = 0
    recentMessages.value.forEach((m) => { m.is_read = true })
  }

  return { unreadCount, recentMessages, fetchRecent, markRead, markAllRead }
})
