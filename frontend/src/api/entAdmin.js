import request from './request'

export const getMyEnterprise = () => request.get('/ent/enterprise/my')
export const updateMyEnterprise = (data) => request.put('/ent-admin/enterprise', data)
export const getEmployeeList = (params) => request.get('/ent-admin/employees', { params })
export const createEmployee = (data) => request.post('/ent-admin/employees', data)
export const updateEmployee = (id, data) => request.put(`/ent-admin/employees/${id}`, data)
export const resetEmployeePassword = (id) => request.post(`/ent-admin/employees/${id}/reset-password`)
export const disableEmployee = (id) => request.put(`/ent-admin/employees/${id}/disable`)
export const unbindEmployee = (id) => request.put(`/ent-admin/employees/${id}/unbind`)
export const getMyOpportunities = (params) => request.get('/ent-admin/my-opportunities', { params })
export const updateMyOpportunity = (id, data) => request.put(`/ent-admin/my-opportunities/${id}`, data)
export const offlineMyOpportunity = (id) => request.put(`/ent-admin/my-opportunities/${id}/offline`)
export const republishMyOpportunity = (id) => request.put(`/ent-admin/my-opportunities/${id}/republish`)
