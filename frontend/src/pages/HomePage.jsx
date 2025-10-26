import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import NicknameModal from '../components/NicknameModal'

function HomePage() {
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [userNickname, setUserNickname] = useState('')
  const [filterBy, setFilterBy] = useState('all')

  useEffect(() => {
    const nickname = localStorage.getItem('user_nickname')
    if (nickname) {
      setUserNickname(nickname)
    }
  }, [])

  useEffect(() => {
    if (userNickname) {
      loadStories()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userNickname, filterBy])

  const loadStories = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/api/stories?filter_by=${filterBy}&limit=50`)
      setStories(response.data)
      setError(null)
    } catch (err) {
      setError('加载故事失败,请稍后重试')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleNicknameComplete = (nickname) => {
    setUserNickname(nickname)
    loadStories()
  }

  const changeNickname = () => {
    const newNickname = prompt('请输入新昵称:', userNickname)
    if (newNickname && newNickname.trim()) {
      localStorage.setItem('user_nickname', newNickname.trim())
      setUserNickname(newNickname.trim())
    }
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

  return (
    <div className="min-h-screen py-8 px-4">
      {/* 昵称设置弹窗 */}
      <NicknameModal onComplete={handleNicknameComplete} />

      <div className="max-w-6xl mx-auto">
        {/* 头部 */}
        <header className="text-center mb-12">
          <div className="flex justify-between items-center mb-4 px-4">
            <div className="flex-1"></div>
            <h1 className="text-6xl font-bold text-white flex-1">
              🎬 StoryLink
            </h1>
            <div className="flex-1 text-right">
              {userNickname && (
                <button
                  onClick={changeNickname}
                  className="text-white/80 hover:text-white text-sm underline transition-colors"
                  title="点击修改昵称"
                >
                  👤 {userNickname}
                </button>
              )}
            </div>
          </div>
          
          <p className="text-xl text-white/80 mb-8">
            一句话,AI 自动编故事;喜欢的故事,自动生成短片
          </p>
          
          <Link
            to="/edit"
            className="inline-flex items-center px-8 py-4 bg-white text-purple-600 rounded-full font-bold text-lg hover:bg-purple-50 transition-all transform hover:scale-105 shadow-lg"
          >
            <span className="text-2xl mr-2">✨</span>
            写新故事
          </Link>
        </header>

        {/* 筛选栏 */}
        <div className="flex gap-4 mb-8 justify-center flex-wrap">
          {[
            { value: 'all', label: '全部故事', icon: '📖' },
            { value: 'with_video', label: '有视频', icon: '🎥' }
          ].map(filter => (
            <button
              key={filter.value}
              onClick={() => setFilterBy(filter.value)}
              className={`px-6 py-2 rounded-full font-medium transition-all ${
                filterBy === filter.value
                  ? 'bg-white text-purple-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              {filter.icon} {filter.label}
            </button>
          ))}
        </div>

        {/* 故事列表 */}
        <div className="space-y-6">

          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
              <p className="text-white mt-4">加载中...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-white">
              {error}
            </div>
          )}

          {!loading && !error && stories.length === 0 && (
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-12 text-center text-white">
              <p className="text-xl mb-4">还没有发布的故事</p>
              <p className="text-white/60">成为第一个创作者吧!</p>
            </div>
          )}

          {!loading && !error && stories.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {stories.map((story) => (
                <div
                  key={story.id}
                  className="bg-white/10 backdrop-blur-md rounded-2xl p-6 hover:bg-white/20 transition-all transform hover:scale-105 border border-white/20"
                >
                  {/* 标签 */}
                  <div className="flex gap-2 mb-3 flex-wrap">
                    {story.video_status === 'completed' && (
                      <span className="px-2 py-1 bg-pink-500/80 text-white text-xs rounded-full">
                        🎥 有视频
                      </span>
                    )}
                    
                    {story.video_status === 'generating' && (
                      <span className="px-2 py-1 bg-yellow-500/80 text-white text-xs rounded-full animate-pulse">
                        ⏳ 生成中
                      </span>
                    )}
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2 line-clamp-2">
                    {story.title}
                  </h3>
                  
                  <p className="text-white/60 text-sm mb-2">
                    👤 {story.author} · 📝 {story.fork_count}/{story.max_contributors} 人续写
                  </p>

                  <p className="text-white/80 text-sm mb-4 line-clamp-3">
                    {story.content}
                  </p>

                  <div className="flex gap-2">
                    <Link
                      to={`/story/${story.id}`}
                      className="flex-1 text-center px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors font-medium"
                    >
                      查看详情
                    </Link>
                    
                    {story.video_status === 'completed' && story.video_url && (
                      <Link
                        to={`/story/${story.id}`}
                        className="px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors font-medium"
                      >
                        ▶️
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 页脚 */}
        <footer className="text-center mt-16 text-white/60">
          <p>Made with ❤️ by StoryLink Team</p>
        </footer>
      </div>
    </div>
  )
}

export default HomePage

