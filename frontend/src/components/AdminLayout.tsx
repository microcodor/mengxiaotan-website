import { Outlet, Link, useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, Users, Activity, Send, ShoppingCart, LogOut, Home, FolderTree, Building2, Clock, BarChart3, FileCheck, Settings } from 'lucide-react'
import { useEffect, useState } from 'react'

export default function AdminLayout() {
  const navigate = useNavigate()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        setUser(JSON.parse(userStr))
      } catch (error) {
        console.error('解析用户信息失败:', error)
      }
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const menuItems = [
    { name: '仪表盘', path: '/admin', icon: LayoutDashboard },
    { name: '文章管理', path: '/admin/articles', icon: FileText },
    { name: '分类管理', path: '/admin/categories', icon: FolderTree },
    { name: '用户管理', path: '/admin/users', icon: Users },
    { name: '企业管理', path: '/admin/companies', icon: Building2 },
    { name: '订单管理', path: '/admin/orders', icon: ShoppingCart },
    { name: '报告管理', path: '/admin/reports', icon: FileCheck },
    { name: '推送管理', path: '/admin/broadcast', icon: Send },
    { name: '推送配置', path: '/admin/push', icon: Settings },
    { name: '爬虫管理', path: '/admin/crawler', icon: Activity },
    { name: '定时任务', path: '/admin/scheduler', icon: Clock },
    { name: '监控告警', path: '/admin/monitor', icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-dark-bg flex">
      {/* 侧边栏 */}
      <aside className="w-64 glass-card border-r border-white/10 flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-tech-cyan bg-clip-text text-transparent">
            管理后台
          </h1>
          {user && (
            <div className="mt-4 text-sm text-gray-400">
              <p>欢迎，{user.nickname || user.phone}</p>
              <p className="text-xs text-gray-500 mt-1">
                {user.role === 'admin' ? '超级管理员' : '编辑'}
              </p>
            </div>
          )}
        </div>
        
        <nav className="flex-1 px-4 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-white/5 hover:text-primary-400 transition-colors"
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>

        {/* 返回用户中心 */}
        <div className="px-4 py-3 border-t border-white/10">
          <Link
            to="/dashboard"
            className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-white/5 hover:text-primary-400 transition-colors"
          >
            <Home className="w-5 h-5" />
            <span>用户中心</span>
          </Link>
        </div>
        
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
