import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, Activity, Zap, Flame, Wind } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '@/lib/api'

export default function Dashboard() {
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/articles/dashboard-stats'),
  })

  // 模拟数据（实际应从API获取）
  const energyData = [
    { name: '周一', coal: 650, power: 820, newEnergy: 450 },
    { name: '周二', coal: 680, power: 850, newEnergy: 480 },
    { name: '周三', coal: 720, power: 880, newEnergy: 520 },
    { name: '周四', coal: 690, power: 860, newEnergy: 500 },
    { name: '周五', coal: 710, power: 900, newEnergy: 550 },
    { name: '周六', coal: 700, power: 870, newEnergy: 530 },
    { name: '周日', coal: 730, power: 920, newEnergy: 580 },
  ]

  const categoryData = [
    { name: '发改委', value: 156, color: '#3B82F6' },
    { name: '煤炭', value: 234, color: '#F59E0B' },
    { name: '电力', value: 189, color: '#EAB308' },
    { name: '新能源', value: 278, color: '#10B981' },
  ]

  const indicators = [
    {
      name: '煤炭价格指数',
      value: '652.8',
      change: '+2.3%',
      trend: 'up',
      icon: Flame,
      color: 'from-orange-500 to-red-500',
    },
    {
      name: '电力负荷',
      value: '8.6 GW',
      change: '+1.8%',
      trend: 'up',
      icon: Zap,
      color: 'from-yellow-500 to-orange-500',
    },
    {
      name: '新能源装机',
      value: '182 GW',
      change: '+5.2%',
      trend: 'up',
      icon: Wind,
      color: 'from-green-500 to-emerald-500',
    },
    {
      name: '绿电占比',
      value: '84.6%',
      change: '-0.5%',
      trend: 'down',
      icon: Activity,
      color: 'from-cyan-500 to-blue-500',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-tech-cyan bg-clip-text text-transparent">
        能源数据看板
      </h1>

      {/* 核心指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {indicators.map((indicator) => (
          <div key={indicator.name} className="glass-card p-6 neon-border-subtle">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 bg-gradient-to-br ${indicator.color} rounded-xl flex items-center justify-center`}>
                <indicator.icon className="w-6 h-6 text-white" />
              </div>
              <div className={`flex items-center space-x-1 text-sm ${
                indicator.trend === 'up' ? 'text-green-400' : 'text-red-400'
              }`}>
                {indicator.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span>{indicator.change}</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-1">{indicator.name}</p>
            <p className="text-3xl font-bold text-white">{indicator.value}</p>
          </div>
        ))}
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 近7日能源价格走势 */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-bold mb-4 text-primary-400">近7日能源价格走势</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={energyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(17, 24, 39, 0.9)',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="coal" stroke="#F59E0B" strokeWidth={2} name="煤炭" />
              <Line type="monotone" dataKey="power" stroke="#EAB308" strokeWidth={2} name="电力" />
              <Line type="monotone" dataKey="newEnergy" stroke="#10B981" strokeWidth={2} name="新能源" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 分类统计 */}
        <div className="glass-card p-6">
          <h2 className="text-xl font-bold mb-4 text-primary-400">资讯分类统计</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(17, 24, 39, 0.9)',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 每日发布量趋势 */}
      <div className="glass-card p-6">
        <h2 className="text-xl font-bold mb-4 text-primary-400">每日资讯发布量</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={energyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(17, 24, 39, 0.9)',
                border: '1px solid #374151',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Bar dataKey="coal" fill="#F59E0B" name="煤炭" radius={[8, 8, 0, 0]} />
            <Bar dataKey="power" fill="#EAB308" name="电力" radius={[8, 8, 0, 0]} />
            <Bar dataKey="newEnergy" fill="#10B981" name="新能源" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
