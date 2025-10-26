import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { 
  getStory, 
  getFullStoryContent, 
  polishText, 
  generateVideo, 
  regenerateVideo, 
  checkCanFork,
  approveStory,
  publishStory 
} from '../api/api'

function StoryDetailPage() {
const { id } = useParams()
  const navigate = useNavigate()
  
  const [story, setStory] = useState(null)
  const [fullStory, setFullStory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [polishing, setPolishing] = useState(false)
  const [polishedContent, setPolishedContent] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [approving, setApproving] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [userNickname, setUserNickname] = useState('')
  const [canFork, setCanFork] = useState(true)

  useEffect(() => {
    loadStory()
    checkForkPermission()
    // 每 5 秒刷新一次(用于更新视频生成状态)
    const interval = setInterval(loadStory, 5000)
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const loadStory = async () => {
    try {
      setLoading(true)
      // 获取基础信息（用于视频状态等）
      const basicData = await getStory(id)
      setStory(basicData)
      
      // 获取完整内容（包含所有续写）
      const fullData = await getFullStoryContent(id)
      setFullStory(fullData)
      
      setError(null)
    } catch (err) {
      setError('加载故事失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const checkForkPermission = async () => {
    try {
      const data = await checkCanFork(id)
      setCanFork(data.can_fork)
    } catch (err) {
      console.error('检查续写权限失败:', err)
    }
  }

  const handlePolish = async () => {
    try {
      setPolishing(true)
      // 润色完整内容（原创+所有续写）
      const polished = await polishText(fullStory.full_content)
      setPolishedContent(polished)
    } catch (err) {
      alert('润色失败,请稍后重试')
      console.error(err)
    } finally {
      setPolishing(false)
    }
  }

  const handleGenerateVideo = async () => {
    if (!userNickname) {
      alert('请先设置昵称')
      navigate('/')
      return
    }

    if (fullStory.original_author !== userNickname) {
      alert(`只有原作者 ${fullStory.original_author} 可以生成视频`)
      return
    }

    const message = fullStory.contribution_count > 0
      ? `确认生成视频吗？视频将包含原创内容和所有${fullStory.contribution_count}个续写，生成可能需要几分钟。`
      : '确认生成视频吗？视频生成可能需要几分钟时间。'

    if (!confirm(message)) {
      return
    }

    try {
      setGenerating(true)
      await generateVideo(id, userNickname)
      const successMsg = fullStory.contribution_count > 0
        ? `视频生成已开始（包含${fullStory.contribution_count}个续写），请稍后查看！`
        : '视频生成已开始，请稍后查看！'
      alert(successMsg)
      await loadStory()
    } catch (err) {
      alert(err.response?.data?.detail || '生成视频失败，请稍后重试')
      console.error(err)
    } finally {
      setGenerating(false)
    }
  }

  const handlePublish = async () => {
    if (!confirm('确认直接发布故事吗?发布后将在首页展示。')) {
      return
    }

    try {
      setPublishing(true)
      await publishStory(id)
      alert('故事已发布!')
      await loadStory()
    } catch (err) {
      alert('发布失败,请稍后重试')
      console.error(err)
    } finally {
      setPublishing(false)
    }
  }

  const handleRegenerate = async () => {
    if (!userNickname) {
      alert('请先设置昵称')
      navigate('/')
      return
    }

    if (fullStory.original_author !== userNickname) {
      alert(`只有原作者 ${fullStory.original_author} 可以重新生成视频`)
      return
    }

    if (!confirm('确认重新生成视频吗？')) {
      return
    }

    try {
      setGenerating(true)
      await regenerateVideo(id, userNickname)
      alert('视频重新生成已开始！')
      await loadStory()
    } catch (err) {
      alert(err.response?.data?.detail || '重新生成失败')
      console.error(err)
    } finally {
      setGenerating(false)
    }
  }

  const handleFork = () => {
    if (!canFork) {
      alert(`该故事已达到续写人数上限（${fullStory.max_contributors}/${fullStory.max_contributors}）`)
      return
    }
    navigate(`/edit?parent_id=${id}&title=${encodeURIComponent(fullStory.title)}`)
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

  if (loading && !fullStory) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
          <p className="text-white mt-4">加载中...</p>
        </div>
      </div>
    )
  }

  if (error || !fullStory) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 text-white max-w-md">
          <p className="text-xl mb-4">{error || '故事不存在'}</p>
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
            {fullStory.title}
          </h1>
          
          <div className="flex items-center text-white/60 text-sm mb-2">
            <span className="mr-4">👤 原作者: {fullStory.original_author}</span>
            <span>🕐 {formatDate(fullStory.created_at)}</span>
          </div>

          <div className="flex items-center text-white/60 text-sm mb-6">
            <span>📝 续写情况: {fullStory.contribution_count}/{fullStory.max_contributors} 人</span>
          </div>

          {/* 原创内容 */}
          <div className="bg-white/5 rounded-xl p-6 mb-4">
            <h3 className="text-lg font-bold text-white mb-3">
              📖 {fullStory.original_author} 的原创内容
            </h3>
            <p className="text-white/90 text-base leading-relaxed whitespace-pre-wrap">
              {polishedContent || fullStory.original_content}
            </p>
          </div>

          {/* 续写内容列表 */}
          {fullStory.contributions && fullStory.contributions.length > 0 && (
            <div className="space-y-4 mb-6">
              {fullStory.contributions.map((contrib, index) => (
                <div 
                  key={contrib.id} 
                  className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-blue-300">
                      ✍️ {contrib.author} 的续写 #{index + 1}
                    </h3>
                    <span className="text-white/60 text-sm">
                      {formatDate(contrib.created_at)}
                    </span>
                  </div>
                  <p className="text-white/90 text-base leading-relaxed whitespace-pre-wrap">
                    {contrib.content}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* AI 润色结果 */}
          {polishedContent && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 mb-6">
              <p className="text-green-300 text-sm">
                ✨ 这是 AI 润色后的完整故事版本（包含所有续写）
              </p>
            </div>
          )}

          {/* 视频状态 */}
          {story.video_status === 'completed' && story.video_url && (
            <div className="bg-white/5 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-bold text-white mb-3">🎥 生成的视频</h3>
              <video
                src={story.video_url}
                controls
                className="w-full rounded-lg mb-4"
              />
              {fullStory.original_author === userNickname && (
                <button
                  onClick={handleRegenerate}
                  disabled={generating}
                  className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50"
                >
                  {generating ? '⏳ 生成中...' : '🔄 重新生成'}
                </button>
              )}
            </div>
          )}

          {story.video_status === 'generating' && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6 text-center mb-6">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-yellow-500 border-t-transparent mb-3"></div>
              <p className="text-yellow-300 font-medium">视频生成中，请稍候...</p>
              <p className="text-yellow-300/60 text-sm mt-2">预计需要 2-5 分钟</p>
            </div>
          )}

          {story.video_status === 'failed' && fullStory.original_author === userNickname && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 mb-6">
              <p className="text-red-300 mb-3">❌ 视频生成失败</p>
              <button
                onClick={handleRegenerate}
                disabled={generating}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
              >
                {generating ? '⏳ 重试中...' : '🔄 重试'}
              </button>
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
              disabled={!canFork}
              className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              🍴 Fork 并续写 {!canFork && '(已满)'}
            </button>

            {fullStory.original_author === userNickname && story.video_status === 'none' && (
              <button
                onClick={handleGenerateVideo}
                disabled={generating}
                className="px-6 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {generating ? '⏳ 生成中...' : `🎬 生成视频 ${fullStory.contribution_count > 0 ? `(含${fullStory.contribution_count}个续写)` : ''}`}
              </button>
            {!story.is_approved && (
              <>
                <button
                  onClick={handlePublish}
                  disabled={publishing}
                  className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {publishing ? '⏳ 发布中...' : '📢 直接发布'}
                </button>

                <button
                  onClick={handleApprove}
                  disabled={approving}
                  className="px-6 py-3 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {approving ? '⏳ 处理中...' : '🚀 发布为视频'}
                </button>
              </>
            )}
          </div>

          {/* 提示信息 */}
          {fullStory.original_author !== userNickname && story.video_status === 'none' && (
            <div className="mt-4 text-white/60 text-sm">
              ℹ️ 只有原作者 {fullStory.original_author} 可以生成视频
              {fullStory.contribution_count > 0 && ` (视频将包含所有${fullStory.contribution_count}个续写)`}
            </div>
          )}
          
          {canFork && fullStory.contribution_count < fullStory.max_contributors && (
            <div className="mt-4 text-green-300 text-sm">
              💡 还可以有 {fullStory.max_contributors - fullStory.contribution_count} 人续写这个故事
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default StoryDetailPage

