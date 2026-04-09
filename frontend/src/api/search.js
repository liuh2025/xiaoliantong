import request from './request'

export const search = (params) => request.get('/search', { params })
