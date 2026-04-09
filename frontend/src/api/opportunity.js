import request from './request'

export const getOpportunityList = (params) => request.get('/opp/opportunity', { params })
export const getOpportunityDetail = (id) => request.get(`/opp/opportunity/${id}`)
export const createOpportunity = (data) => request.post('/opp/opportunity', data)
export const updateOpportunity = (id, data) => request.put(`/opp/opportunity/${id}`, data)
export const deleteOpportunity = (id) => request.delete(`/opp/opportunity/${id}`)
export const toggleOffline = (id) => request.put(`/opp/opportunity/${id}/offline`)
export const getContact = (id) => request.post(`/opp/opportunity/${id}/contact`)
export const getRecommended = () => request.get('/opp/opportunity/recommended')
