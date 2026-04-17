import { useQuery } from '@tanstack/react-query'
import { FileText, CreditCard, Bell, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '@/lib/api'

export default function UserDashboard() {
  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    },
  })

  const { data: subscriptions } = useQuery({
    queryKey: ['mySubscriptions'],
    queryFn: () => api.get('/subscriptions/my'),
  })

  const { data: orders } = useQuery({
    queryKey: ['myOrders'],
    queryFn: () => api.get('/subscriptions/orders'),
  })

  const activeSubscription = subscriptions?.items?.find((s: any) => s.status === 'active')
  const pendingOrders = orders?.items?.filter((o: any) => o.payment_status === 'pending')?.length || 0

  return (
    <div className="space-y-8">
      {/* 欢迎信息 */}
      <div className="glass-card p-8">
        <h1 className="text-3xl font-bold mb-2">
          欢迎回来，{user?.nickname || user?.phone}！
        </h1>
        <p className="text-gray-400">
          这是您的个人工作台，您可以在这里管理订阅、查看订单和设置推送。
        </p>
      </div>

      {/* 快捷卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link to="/dashboard/subscription" className="glass-card p-6 hover:bg-white/5 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <CreditCard className="w-8 h-8 text-primary-400" />
            <span className="text-2xl font-bold text-primary-400">
              {activeSubscription ? '1' : '0'}
            </span>
          </div>
          <h3 className="font-semibold mb-1">我的订阅</h3>
          <p className="text-sm text-gray-400">
            {activeSubscription ? `${activeSubscription.plan_name} 已激活` : '暂无订阅'}
          </p>
        </Link>

        <Link to="/dashboard/orders" className="glass-card p-6 hover:bg-white/5 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <FileText className="w-8 h-8 text-blue-400" />
            <span className="text-2xl font-bold text-blue-400">
              {orders?.items?.length || 0}
            </span>
          </div>
          <h3 className="font-semibold mb-1">我的订单</h3>
          <p className="text-sm text-gray-400">
            {pendingOrders > 0 ? `${pendingOrders} 个待处理` : '全部已处理'}
          </p>
        </Link>

        <Link to="/dashboard/push" className="glass-card p-6 hover:bg-white/5 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <Bell className="w-8 h-8 text-green-400" />
            <span className="text-2xl font-bold text-green-400">
              {activeSubscription ? '已开启' : '未开启'}
            </span>
          </div>
          <h3 className="font-semibold mb-1">推送设置</h3>
          <p className="text-sm text-gray-400">
            {activeSubscription ? '每日简报推送' : '订阅后可用'}
          </p>
        </Link>

        <Link to="/articles" className="glass-card p-6 hover:bg-white/5 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp className="w-8 h-8 text-yellow-400" />
            <span className="text-2xl font-bold text-yellow-400">浏览</span>
          </div>
          <h3 className="font-semibold mb-1">资讯中心</h3>
          <p className="text-sm text-gray-400">查看最新能源资讯</p>
        </Link>
      </div>

      {/* 订阅状态 */}
      {activeSubscription ? (
        <div className="glass-card p-6">
          <h2 className="text-xl font-bold mb-4">当前订阅</h2>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-primary-400">
                {activeSubscription.plan_name}
              </h3>
              <p className="text-sm text-gray-400 mt-1">
                有效期至：{new Date(activeSubscription.end_date).toLocaleDateString('zh-CN')}
              </p>
            </div>
            <Link
              to="/dashboard/subscription"
              className="btn-primary"
            >
              管理订阅
            </Link>
          </div>
        </div>
      ) : (
        <div className="glass-card p-8 text-center">
          <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">开启您的能源资讯之旅</h2>
          <p className="text-gray-400 mb-6">
            订阅我们的服务，获取每日能源简报、AI分析和个性化推送
          </p>
          <Link to="/subscription" className="btn-primary inline-block">
            立即订阅
          </Link>
        </div>
      )}

      {/* 待处理订单提醒 */}
      {pendingOrders > 0 && (
        <div className="glass-card p-6 border-l-4 border-yellow-400">
          <div className="flex items-start space-x-4">
            <FileText className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold mb-1">您有 {pendingOrders} 个订单待处理</h3>
              <p className="text-sm text-gray-400 mb-3">
                订单提交后，管理员会在24小时内审核确认
              </p>
              <Link to="/dashboard/orders" className="text-primary-400 hover:text-primary-300 text-sm">
                查看订单 →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
