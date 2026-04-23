import request from './request'

export const getFeedList = (params) => request.get('/feed/feed/', { params })
export const getFeedDetail = (id) => request.get(`/feed/feed/${id}/`)
export const createFeed = (data) => request.post('/feed/feed/', data)
export const deleteFeed = (id) => request.delete(`/feed/feed/${id}/`)
export const toggleFeedOffline = (id) => request.put(`/feed/feed/${id}/offline/`)
export const getNewestFeed = () => request.get('/feed/feed/newest/')
