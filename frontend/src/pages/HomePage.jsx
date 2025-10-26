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
      const params = new URLSearchParams({ filter_by: filterBy, limit: 50 })
      
      // 如果是"我的故事"，传递作者参数
      if (filterBy === 'my' && userNickname) {
        params.append('author', userNickname)
      }
      
      const response = await axios.get(`/api/stories?${params}`)
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
              🎬 MovieHub
            </h1>
            <div className="flex-1 flex justify-end">
              {userNickname && (
                <div className="bg-white/20 backdrop-blur-md rounded-full px-5 py-3 border border-white/30 shadow-lg hover:bg-white/30 transition-all group">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white text-base font-bold shadow-md">
                      {userNickname.charAt(0).toUpperCase()}
                    </div>
                    <div className="text-left">
                      <div className="text-white font-semibold text-sm leading-tight">
                        {userNickname}
                      </div>
                      <button 
                        onClick={changeNickname}
                        className="text-white/70 hover:text-white text-xs underline transition-colors leading-tight"
                      >
                        切换
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <p className="text-xl text-white/80 mb-8">
            欢迎来到影视创作版 Github，携手共创下一个经典
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
            { value: 'my', label: '我的故事', icon: '📁' },
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
                  className="bg-white/10 backdrop-blur-md rounded-2xl overflow-hidden border border-white/20 hover:border-white/40 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/20 group"
                >
                  {/* 顶部标签栏 */}
                  <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 px-4 py-3 border-b border-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 flex-wrap">
                        {/* 原创或Fork标签 */}
                        {story.forked_from ? (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-500/90 text-white text-xs font-medium rounded-full shadow-lg">
                            <span>🍴</span>
                            Fork
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-500/90 text-white text-xs font-medium rounded-full shadow-lg">
                            <span>✨</span>
                            原创
                          </span>
                        )}
                        
                        {/* 视频状态标签 */}
                        {story.video_status === 'completed' && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-pink-500/90 text-white text-xs font-medium rounded-full shadow-lg">
                            <span>🎥</span>
                            有视频
                          </span>
                        )}
                        
                        {story.video_status === 'generating' && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-500/90 text-white text-xs font-medium rounded-full shadow-lg animate-pulse">
                            <span>⏳</span>
                            生成中
                          </span>
                        )}
                      </div>
                      
                      <span className="text-white/40 text-xs font-mono whitespace-nowrap ml-2">
                        #{story.id}
                      </span>
                    </div>
                  </div>

                  {/* 内容区域 */}
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-white mb-3 line-clamp-2 group-hover:text-purple-300 transition-colors min-h-[3.5rem] flex items-center">
                      {story.title}
                    </h3>
                    
                    <div className="flex items-center justify-between text-white/70 text-sm mb-4 py-3 px-3 bg-white/5 rounded-lg border border-white/10">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">👤</span>
                        <span className="font-semibold text-white/90">{story.author}</span>
                      </div>
                      <div className="w-px h-5 bg-white/20"></div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg">📝</span>
                        <span className="font-medium text-white/90">{story.fork_count}/{story.max_contributors} 续写</span>
                      </div>
                    </div>

                    <p className="text-white/70 text-sm leading-relaxed mb-6 line-clamp-3 min-h-[4.5rem]">
                      {story.content}
                    </p>

                    <div className="flex gap-2">
                      <Link
                        to={`/story/${story.id}`}
                        className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl hover:shadow-purple-500/50 transform hover:scale-105"
                      >
                        查看详情
                        <span className="group-hover:translate-x-1 transition-transform">→</span>
                      </Link>
                      
                      {story.video_status === 'completed' && story.video_url && (
                        <Link
                          to={`/story/${story.id}`}
                          className="px-4 py-2.5 bg-pink-500/80 text-white rounded-xl hover:bg-pink-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl hover:shadow-pink-500/50 transform hover:scale-105 flex items-center justify-center"
                          title="观看视频"
                        >
                          ▶️
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 页脚 */}
        <footer className="text-center mt-16 text-white/60">
          <p>Made with ❤️ by MovieHub Team</p>
        </footer>
      </div>
    </div>
  )
}

export default HomePage

