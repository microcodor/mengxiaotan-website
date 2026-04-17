import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn } from 'lucide-react'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/store'

export default function Login() {
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await api.post('/auth/login', { phone, password })
      console.log('登录返回数据:', data)
      console.log('用户信息:', data.user)
      console.log('用户角色:', data.user?.role)
      
      setAuth(data.user, data.access_token)
      
      // 根据用户角色跳转到不同页面
      if (data.user.role === 'admin' || data.user.role === 'editor') {
        console.log('管理员登录，跳转到 /admin')
        navigate('/admin')  // 管理员跳转到管理后台
      } else {
        console.log('普通用户登录，跳转到 /dashboard')
        navigate('/dashboard')  // 普通用户跳转到用户工作台
      }
    } catch (err: any) {
      console.error('登录错误:', err)
      setError(err.response?.data?.message || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="glass-card p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-tech-cyan rounded-2xl flex items-center justify-center mx-auto mb-4">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold">登录</h2>
          <p className="text-gray-400 mt-2">欢迎回到蒙小碳·能源站</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">手机号</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-primary-500 transition-colors"
              placeholder="请输入手机号"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:border-primary-500 transition-colors"
              placeholder="请输入密码"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary disabled:opacity-50"
          >
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-400">
          还没有账号？
          <Link to="/register" className="text-primary-400 hover:text-primary-300 ml-2">
            立即注册
          </Link>
        </div>
      </div>
    </div>
  )
}
