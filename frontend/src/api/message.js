import request from './request'

export const getNotifications = (params) => request.get('/msg/notifications', { params })
export const markRead = (id) => request.put(`/msg/notifications/${id}/read`)
export const markAllRead = () => request.put('/msg/notifications/read-all')
export const getRecentNotifications = () => request.get('/msg/notifications/recent')
