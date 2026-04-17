import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { User, CreditCard, ShoppingCart, Bell, LogOut, LayoutDashboard, Building2, Briefcase, BarChart3, Zap, FileText, AlertTriangle } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function DashboardLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        setUser(JSON.parse(userStr))
      } catch (error) {
        console.error('解析用户信息失败:', error)
        navigate('/login')
      }
    }
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const menuItems = [
    { name: '工作台', path: '/dashboard', icon: LayoutDashboard },
    { name: '个人信息', path: '/dashboard/profile', icon: User },
    { name: '企业信息', path: '/dashboard/company', icon: Building2 },
    { name: '主营业务', path: '/dashboard/company/business', icon: Briefcase },
    { name: '企业画像', path: '/dashboard/company/profile', icon: BarChart3 },
    { name: '数字沙盘', path: '/dashboard/digital-twin', icon: Zap },
    { name: '定制报告', path: '/dashboard/reports', icon: FileText },
    { name: '监测预警', path: '/dashboard/monitoring', icon: AlertTriangle },
    { name: '我的订阅', path: '/dashboard/subscription', icon: CreditCard },
    { name: '我的订单', path: '/dashboard/orders', icon: ShoppingCart },
    { name: '推送设置', path: '/dashboard/push', icon: Bell },
  ]

  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard'
    }
    return location.pathname.startsWith(path)
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-dark-bg flex">
      {/* 侧边栏 */}
      <aside className="w-64 glass-card border-r border-white/10 flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-tech-cyan bg-clip-text text-transparent">
            用户中心
          </h1>
          <div className="mt-4 p-4 bg-white/5 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-tech-cyan rounded-full flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{user.nickname || user.phone}</p>
                <p className="text-xs text-gray-400">普通用户</p>
              </div>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'text-gray-300 hover:bg-white/5 hover:text-primary-400'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>

        {/* 管理员入口 */}
        {(user.role === 'admin' || user.role === 'editor') && (
          <div className="px-4 py-3 border-t border-white/10">
            <Link
              to="/admin"
              className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-primary-500/10 hover:text-primary-400 transition-colors"
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>管理后台</span>
            </Link>
          </div>
        )}

        {/* 退出登录 */}
        <div className="p-4 border-t border-white/10">
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-red-500/10 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>退出登录</span>
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 p-8 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
