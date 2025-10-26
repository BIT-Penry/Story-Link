import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 获取已批准的故事列表
export const getApprovedStories = async () => {
  const response = await api.get('/stories?approved_only=true')
  return response.data
}

// 获取所有故事列表
export const getAllStories = async () => {
  const response = await api.get('/stories')
  return response.data
}

// 获取单个故事详情
export const getStory = async (id) => {
  const response = await api.get(`/stories/${id}`)
  return response.data
}

// 创建新故事
export const createStory = async (storyData) => {
  const response = await api.post('/stories', storyData)
  return response.data
}

// AI 文本润色
export const polishText = async (content) => {
  const response = await api.post('/polish', { content })
  return response.data.polished_content
}

// 生成视频（仅作者可用）
export const generateVideo = async (id, author) => {
  const response = await api.post(`/stories/${id}/generate-video`, { author })
  return response.data
}

// 重新生成视频
export const regenerateVideo = async (id, author) => {
  const response = await api.post(`/stories/${id}/generate-video`, { author })
  return response.data
}

// 检查是否可以续写
export const checkCanFork = async (id) => {
  const response = await api.get(`/stories/${id}/can-fork`)
  return response.data
}

// 获取故事完整内容（包含所有续写）
export const getFullStoryContent = async (id) => {
  const response = await api.get(`/stories/${id}/full-content`)
  return response.data
}

export default api

