import request from './request'

export const getEnterpriseList = (params) => request.get('/ent/enterprise/', { params })
export const getEnterpriseDetail = (id) => request.get(`/ent/enterprise/${id}/`)
export const createEnterprise = (data) => request.post('/ent/enterprise/create/', data)
export const claimEnterprise = (data) => request.post('/ent/enterprise/claim/', data)
export const getMyEnterprise = () => request.get('/ent/enterprise/my/')
export const updateEnterprise = (id, data) => request.put(`/ent/enterprise/${id}/`)
export const getDictIndustry = (params) => request.get('/ent/industry/', { params })
export const getDictCategory = (params) => request.get('/ent/category/')
export const getDictRegion = (params) => request.get('/ent/region/', { params })
export const getNewestEnterprise = () => request.get('/ent/enterprise/newest/')
export const getHomeStats = () => request.get('/ent/stats/')
