import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getStory, polishText, approveStory, regenerateVideo } from '../api/api'

function StoryDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [story, setStory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [polishing, setPolishing] = useState(false)
  const [polishedContent, setPolishedContent] = useState(null)
  const [approving, setApproving] = useState(false)

  useEffect(() => {
    loadStory()
    // 每 5 秒刷新一次(用于更新视频生成状态)
    const interval = setInterval(loadStory, 5000)
    return () => clearInterval(interval)
  }, [id])

  const loadStory = async () => {
    try {
      setLoading(true)
      const data = await getStory(id)
      setStory(data)
      setError(null)
    } catch (err) {
      setError('加载故事失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handlePolish = async () => {
    try {
      setPolishing(true)
      const polished = await polishText(story.content)
      setPolishedContent(polished)
    } catch (err) {
      alert('润色失败,请稍后重试')
      console.error(err)
    } finally {
      setPolishing(false)
    }
  }

  const handleApprove = async () => {
    if (!confirm('确认发布为视频吗?视频生成可能需要几分钟时间。')) {
      return
    }

    try {
      setApproving(true)
      await approveStory(id)
      alert('视频生成已开始,请稍后查看!')
      await loadStory()
    } catch (err) {
      alert('发布失败,请稍后重试')
      console.error(err)
    } finally {
      setApproving(false)
    }
  }

  const handleRegenerate = async () => {
    if (!confirm('确认重新生成视频吗?')) {
      return
    }

    try {
      await regenerateVideo(id)
      alert('视频重新生成已开始!')
      await loadStory()
    } catch (err) {
      alert('重新生成失败')
      console.error(err)
    }
  }

  const handleFork = () => {
    navigate(`/edit?parent_id=${id}&title=${encodeURIComponent(story.title)}`)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading && !story) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
          <p className="text-white mt-4">加载中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 text-white max-w-md">
          <p className="text-xl mb-4">{error}</p>
          <Link to="/" className="text-white underline">返回首页</Link>
        </div>
      </div>
    )
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

        {/* 故事详情 */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <h1 className="text-4xl font-bold text-white mb-4">
            {story.title}
          </h1>
          
          <div className="flex items-center text-white/60 text-sm mb-6">
            <span className="mr-4">👤 {story.author}</span>
            <span>🕐 {formatDate(story.created_at)}</span>
          </div>

          {/* 故事内容 */}
          <div className="bg-white/5 rounded-xl p-6 mb-6">
            <h3 className="text-lg font-bold text-white mb-3">📖 故事内容</h3>
            <p className="text-white/90 text-base leading-relaxed whitespace-pre-wrap">
              {polishedContent || story.content}
            </p>
          </div>

          {/* AI 润色结果 */}
          {polishedContent && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 mb-6">
              <p className="text-green-300 text-sm">
                ✨ 这是 AI 润色后的版本,您可以点击"Fork 并续写"来使用它
              </p>
            </div>
          )}

          {/* 视频状态 */}
          {story.is_approved && (
            <div className="mb-6">
              {story.video_status === 'completed' && story.video_url && (
                <div className="bg-white/5 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-3">🎥 生成的视频</h3>
                  <video
                    src={story.video_url}
                    controls
                    className="w-full rounded-lg mb-4"
                  />
                  <button
                    onClick={handleRegenerate}
                    className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
                  >
                    🔄 重新生成
                  </button>
                </div>
              )}

              {story.video_status === 'generating' && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6 text-center">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-yellow-500 border-t-transparent mb-3"></div>
                  <p className="text-yellow-300 font-medium">视频生成中,请稍候...</p>
                </div>
              )}

              {story.video_status === 'failed' && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6">
                  <p className="text-red-300 mb-3">❌ 视频生成失败</p>
                  <button
                    onClick={handleRegenerate}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    🔄 重试
                  </button>
                </div>
              )}
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handlePolish}
              disabled={polishing}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {polishing ? '⏳ 润色中...' : '🤖 AI 润色'}
            </button>

            <button
              onClick={handleFork}
              className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
            >
              🍴 Fork 并续写
            </button>

            {!story.is_approved && (
              <button
                onClick={handleApprove}
                disabled={approving}
                className="px-6 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {approving ? '⏳ 处理中...' : '🚀 发布为视频'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StoryDetailPage

