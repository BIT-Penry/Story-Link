import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { createStory, getStory } from '../api/api'

function EditPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  const parentId = searchParams.get('parent_id')
  const defaultTitle = searchParams.get('title')
  
  const [formData, setFormData] = useState({
    title: defaultTitle ? `${defaultTitle} (续)` : '',
    author: '',
    content: '',
  })
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [parentStory, setParentStory] = useState(null)

  useEffect(() => {
    if (parentId) {
      loadParentStory()
    }
  }, [parentId])

  const loadParentStory = async () => {
    try {
      const data = await getStory(parentId)
      setParentStory(data)
    } catch (err) {
      console.error('加载父故事失败:', err)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // 验证
    if (!formData.title.trim()) {
      setError('请输入标题')
      return
    }
    if (!formData.author.trim()) {
      setError('请输入昵称')
      return
    }
    if (!formData.content.trim()) {
      setError('请输入故事内容')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      const storyData = {
        ...formData,
        parent_id: parentId ? parseInt(parentId) : null
      }
      
      const newStory = await createStory(storyData)
      alert('故事创建成功!')
      navigate(`/story/${newStory.id}`)
    } catch (err) {
      setError('创建失败,请稍后重试')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* 返回按钮 */}
        <Link
          to="/"
          className="inline-flex items-center text-white mb-6 hover:text-white/80 transition-colors"
        >
          <span className="mr-2">←</span>
          返回首页
        </Link>

        {/* 表单 */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h1 className="text-4xl font-bold text-white mb-2">
            {parentId ? '🍴 Fork 并续写' : '✨ 写新故事'}
          </h1>
          <p className="text-white/60 mb-8">
            {parentId ? '在原故事基础上创作你的版本' : '开启一个全新的故事世界'}
          </p>

          {/* 显示父故事 */}
          {parentStory && (
            <div className="bg-white/5 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-white mb-3">📖 原故事</h3>
              <p className="text-white/90 text-sm mb-2">
                <strong>{parentStory.title}</strong> - {parentStory.author}
              </p>
              <p className="text-white/70 text-sm line-clamp-3">
                {parentStory.content}
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-white mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 昵称 */}
            <div>
              <label className="block text-white font-medium mb-2">
                👤 昵称 <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                name="author"
                value={formData.author}
                onChange={handleChange}
                placeholder="请输入你的昵称"
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20"
                required
              />
            </div>

            {/* 标题 */}
            <div>
              <label className="block text-white font-medium mb-2">
                📝 标题 <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="给你的故事起个吸引人的标题"
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20"
                required
              />
            </div>

            {/* 正文 */}
            <div>
              <label className="block text-white font-medium mb-2">
                📖 故事内容 <span className="text-red-400">*</span>
              </label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleChange}
                placeholder="在这里开始你的创作..."
                rows={12}
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 resize-y"
                required
              />
              <p className="text-white/40 text-sm mt-2">
                {formData.content.length} 字
              </p>
            </div>

            {/* 提交按钮 */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-bold text-lg transform hover:scale-105"
              >
                {loading ? '⏳ 提交中...' : '🚀 提交故事'}
              </button>
              
              <Link
                to="/"
                className="px-8 py-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors font-medium flex items-center justify-center"
              >
                取消
              </Link>
            </div>
          </form>
        </div>

        {/* 提示 */}
        <div className="mt-6 bg-white/5 backdrop-blur-md rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-bold text-white mb-3">💡 创作提示</h3>
          <ul className="text-white/70 space-y-2 text-sm">
            <li>• 提交后可以使用 AI 润色功能优化文本</li>
            <li>• 点击"发布为视频"可以将故事转换为短片</li>
            <li>• 其他人可以 Fork 你的故事继续创作</li>
            <li>• 发挥想象,创作精彩故事!</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default EditPage

