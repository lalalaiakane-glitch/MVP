import axios from 'axios'

export const api = axios.create({ baseURL: '/api' })

export const listContent = () => api.get('/content').then(r => r.data)
export const createContent = (payload) => api.post('/content', payload).then(r => r.data)
export const updateContent = (id, payload) => api.put(`/content/${id}`, payload).then(r => r.data)
export const deleteContent = (id) => api.delete(`/content/${id}`).then(r => r.data)

export const askQuestion = (question, product_id) =>
  api.post('/chat', { question, product_id }).then(r => r.data)

export const runEval = () => api.post('/eval/run').then(r => r.data)
export const listEvalQuestions = () => api.get('/eval/questions').then(r => r.data)
