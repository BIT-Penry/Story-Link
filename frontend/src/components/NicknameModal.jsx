import { useState, useEffect } from 'react'

export default function NicknameModal({ onComplete }) {
  const [nickname, setNickname] = useState('')
  const [show, setShow] = useState(false)

  useEffect(() => {
    // 检查是否已设置昵称
    const savedNickname = localStorage.getItem('user_nickname')
    if (!savedNickname) {
      setShow(true)
    } else {
      onComplete(savedNickname)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!nickname.trim()) {
      alert('请输入昵称')
      return
    }
    
    if (nickname.length > 20) {
      alert('昵称不能超过20个字符')
      return
    }
    
    // 保存昵称到 localStorage
    localStorage.setItem('user_nickname', nickname.trim())
    setShow(false)
    onComplete(nickname.trim())
  }

  if (!show) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl animate-fade-in">
        <h2 className="text-3xl font-bold text-gray-800 mb-4 text-center">
          👋 欢迎来到 MovieHub
        </h2>
        
        <p className="text-gray-600 mb-6 text-center">
          请设置您的昵称以开始创作
        </p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="输入您的昵称"
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none text-lg mb-4"
            maxLength={20}
            autoFocus
          />
          
          <button
            type="submit"
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-bold text-lg hover:shadow-lg transition-all transform hover:scale-105"
          >
            开始创作
          </button>
        </form>
        
        <p className="text-sm text-gray-500 mt-4 text-center">
          昵称会保存在本地，您随时可以更改
        </p>
      </div>
    </div>
  )
}

