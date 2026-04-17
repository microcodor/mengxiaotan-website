import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users, FileText, TrendingUp, Activity, AlertTriangle, CheckCircle, Bell, RefreshCw, DollarSign, Package, Zap } from 'lucide-react'
import api from '@/lib/api'

export default function AdminDashboard() {
  const [autoRefresh, setAutoRefresh] = useState(true)

  const { data: dashboard } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => api.get('/admin/dashboard'),
  })

  // 监控数据
  const { data: monitorData, refetch: refetchMonitor } = useQuery({
    queryKey: ['dashboard-monitor'],
    queryFn: async () => {
      const [stats, health, failures] = await Promise.all([
        api.get('/monitor/statistics?days=7'),
        api.get('/monitor/health'),
        api.get('/monitor/failures?limit=5')
      ])
      return { stats, health, failures: failures.failures || [] }
    },
    refetchInterval: autoRefresh ? 60000 : false, // 自动刷新间隔1分钟
  })

  const stats = [
    { name: '总用户数', value: dashboard?.total_users || 0, icon: Users, color: 'from-blue-500 to-cyan-500' },
    { name: '总文章数', value: dashboard?.total_articles || 0, icon: FileText, color: 'from-green-500 to-emerald-500' },
    { name: '今日文章', value: dashboard?.today_articles || 0, icon: TrendingUp, color: 'from-orange-500 to-red-500' },
    { 
      name: '爬虫成功率', 
      value: `${monitorData?.stats?.success_rate || 0}%`, 
      icon: Activity, 
      color: (monitorData?.stats?.success_rate || 0) >= 90 ? 'from-green-500 to-emerald-500' : 'from-yellow-500 to-orange-500'
    },
  ]

  // 业务指标
  const businessMetrics = monitorData?.stats?.business_metrics

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">仪表盘</h1>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            自动刷新
          </label>
          <button
            onClick={() => refetchMonitor()}
            className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            刷新
          </button>
        </div>
      </div>

      {/* 系统健康状态 */}
      {monitorData?.health && (
        <div className="glass-card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold flex items-center gap-2">
              {monitorData.health.is_healthy ? (
                <CheckCircle className="w-6 h-6 text-green-400" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-red-400" />
              )}
              系统健康状态
            </h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              monitorData.health.is_healthy 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-red-500/20 text-red-400'
            }`}>
              {monitorData.health.is_healthy ? '健康' : '异常'}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                {monitorData.health.db_healthy ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                )}
                <span className="text-sm text-gray-400">数据库</span>
              </div>
              <p className="text-lg font-bold">
                {monitorData.health.db_healthy ? '正常' : '异常'}
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-blue-400" />
                <span className="text-sm text-gray-400">最近1小时运行</span>
              </div>
              <p className="text-lg font-bold">{monitorData.health.recent_runs || 0} 次</p>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className={`w-5 h-5 ${monitorData.health.error_sources > 0 ? 'text-red-400' : 'text-gray-400'}`} />
                <span className="text-sm text-gray-400">错误爬虫</span>
              </div>
              <p className={`text-lg font-bold ${monitorData.health.error_sources > 0 ? 'text-red-400' : ''}`}>
                {monitorData.health.error_sources || 0} 个
              </p>
            </div>
            <div className="bg-white/5 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-5 h-5 text-primary-400" />
                <span className="text-sm text-gray-400">爬虫成功率</span>
              </div>
              <p className="text-lg font-bold text-primary-400">
                {monitorData.stats?.success_rate || 0}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 核心指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm mb-1">{stat.name}</p>
                <p className="text-3xl font-bold">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 业务指标概览 */}
      {businessMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* 用户指标 */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-400" />
              用户指标
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">新增用户</span>
                <span className="text-lg font-bold text-green-400">{businessMetrics.users?.new || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">活跃用户</span>
                <span className="text-lg font-bold text-blue-400">{businessMetrics.users?.active || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">活跃率</span>
                <span className="text-lg font-bold text-primary-400">{businessMetrics.users?.active_rate || 0}%</span>
              </div>
            </div>
          </div>

          {/* 订阅指标 */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Package className="w-5 h-5 text-purple-400" />
              订阅指标
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">活跃订阅</span>
                <span className="text-lg font-bold text-green-400">{businessMetrics.subscriptions?.active || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">新增订阅</span>
                <span className="text-lg font-bold text-blue-400">{businessMetrics.subscriptions?.new || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">即将到期</span>
                <span className="text-lg font-bold text-yellow-400">{businessMetrics.subscriptions?.expiring_soon || 0}</span>
              </div>
            </div>
          </div>

          {/* 订单指标 */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-400" />
              订单指标
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">待处理</span>
                <span className="text-lg font-bold text-yellow-400">{businessMetrics.orders?.pending || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">已支付</span>
                <span className="text-lg font-bold text-green-400">{businessMetrics.orders?.paid || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">总收入</span>
                <span className="text-lg font-bold text-primary-400">¥{(businessMetrics.orders?.revenue || 0).toFixed(0)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 最近失败记录 */}
      {monitorData?.failures && monitorData.failures.length > 0 && (
        <div className="glass-card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <Bell className="w-6 h-6 text-red-400" />
              最近告警
            </h2>
            <span className="text-sm text-gray-400">显示最近 5 条</span>
          </div>
          <div className="space-y-3">
            {monitorData.failures.map((failure: any, index: number) => (
              <div key={index} className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-red-400">{failure.spider_name}</span>
                      <span className="text-xs text-gray-400">
                        {new Date(failure.failed_at).toLocaleString('zh-CN')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 break-words">
                      {failure.error_msg || '未知错误'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 分类统计 */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold mb-4">分类统计</h2>
        <div className="space-y-4">
          {dashboard?.category_stats?.map((stat: any) => (
            <div key={stat.category} className="flex items-center justify-between">
              <span className="text-gray-300">{stat.category}</span>
              <span className="text-primary-400 font-semibold">{stat.count} 篇</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
