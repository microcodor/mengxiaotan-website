import { Outlet, Link, useNavigate } from 'react-router-dom'
import { Menu, X, User, LogOut } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useAuthStore } from '@/lib/store'
import api from '@/lib/api'

export default function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [categories, setCategories] = useState<any[]>([])
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await api.get('/categories')
      // 只显示前6个启用的分类
      setCategories(response.items.filter((cat: any) => cat.is_active).slice(0, 6))
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navItems = [
    { name: '首页', path: '/' },
    ...categories.map(cat => ({
      name: cat.name,
      path: `/category/${cat.code}`
    })),
    { name: '订阅服务', path: '/subscription' },
  ]

  return (
    <div className="min-h-screen bg-dark-bg">
      {/* 导航栏 */}
      <nav className="glass-card sticky top-0 z-50 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-tech-cyan rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">蒙</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary-400 to-tech-cyan bg-clip-text text-transparent">
                蒙小碳·能源站
              </span>
            </Link>

            {/* 桌面导航 */}
            <div className="hidden md:flex items-center space-x-8">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className="text-gray-300 hover:text-primary-400 transition-colors"
                >
                  {item.name}
                </Link>
              ))}
            </div>

            {/* 用户菜单 */}
            <div className="hidden md:flex items-center space-x-4">
              {user ? (
                <>
                  <Link to="/profile" className="flex items-center space-x-2 text-gray-300 hover:text-primary-400">
                    <User className="w-5 h-5" />
                    <span>{user.nickname}</span>
                  </Link>
                  <button onClick={handleLogout} className="text-gray-300 hover:text-red-400">
                    <LogOut className="w-5 h-5" />
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="btn-secondary">登录</Link>
                  <Link to="/register" className="btn-primary">注册</Link>
                </>
              )}
            </div>

            {/* 移动端菜单按钮 */}
            <button
              className="md:hidden text-gray-300"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* 移动端菜单 */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-white/10">
            <div className="px-4 py-4 space-y-3">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className="block text-gray-300 hover:text-primary-400 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
              {user ? (
                <>
                  <Link to="/profile" className="block text-gray-300 hover:text-primary-400 py-2">
                    个人中心
                  </Link>
                  <button onClick={handleLogout} className="block text-red-400 py-2">
                    退出登录
                  </button>
                </>
              ) : (
                <div className="flex space-x-4 pt-2">
                  <Link to="/login" className="btn-secondary flex-1 text-center">登录</Link>
                  <Link to="/register" className="btn-primary flex-1 text-center">注册</Link>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* 主内容 */}
      <main>
        <Outlet />
      </main>

      {/* 页脚 */}
      <footer className="glass-card border-t border-white/10 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">关于蒙小碳</h3>
              <p className="text-gray-400 text-sm">
                专业的能源电力煤炭行业资讯订阅平台
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">快速链接</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/" className="hover:text-primary-400">首页</Link></li>
                <li><Link to="/subscription" className="hover:text-primary-400">订阅服务</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">联系我们</h3>
              <p className="text-gray-400 text-sm">
                邮箱: contact@mengxiaotan.com
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">数据来源</h3>
              <p className="text-gray-400 text-sm">
                国家发改委、能源局等权威机构
              </p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/10 text-center text-gray-400 text-sm">
            © 2026 蒙小碳·能源站 All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
