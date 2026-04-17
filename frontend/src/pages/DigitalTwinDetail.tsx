import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowLeft, TrendingUp, TrendingDown, DollarSign, 
  BarChart3, PieChart, Activity, Download, RefreshCw
} from 'lucide-react'
import api from '@/lib/api'
import {
  LineChart, Line, BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

export default function DigitalTwinDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  // 获取场景详情
  const { data: scenario, isLoading, refetch } = useQuery({
    queryKey: ['scenario', id],
    queryFn: () => api.get(`/simulation/scenarios/${id}`),
    refetchInterval: (data) => {
      // 如果状态是running，每3秒刷新一次
      return data?.data?.status === 'running' ? 3000 : false
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Activity className="w-8 h-8 text-primary-400 animate-pulse" />
        <span className="ml-2 text-gray-400">加载中...</span>
      </div>
    )
  }

  const scenarioData = scenario?.data
  const result = scenarioData?.result

  if (!scenarioData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">场景不存在</p>
        <button onClick={() => navigate('/dashboard/digital-twin')} className="btn-primary mt-4">
          返回列表
        </button>
      </div>
    )
  }

  // 如果还在运行中
  if (scenarioData.status === 'running') {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-12 text-center">
          <Activity className="w-16 h-16 text-primary-400 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold mb-2">正在模拟中...</h2>
          <p className="text-gray-400 mb-6">请稍候，模拟计算通常需要几秒钟</p>
          <button onClick={() => refetch()} className="btn-secondary">
            <RefreshCw className="w-4 h-4 inline mr-2" />
            刷新状态
          </button>
        </div>
      </div>
    )
  }

  // 如果模拟失败
  if (scenarioData.status === 'failed') {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-12 text-center">
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">❌</span>
          </div>
          <h2 className="text-2xl font-bold mb-2">模拟失败</h2>
          <p className="text-gray-400 mb-6">模拟过程中出现错误，请稍后重试</p>
          <div className="flex space-x-3 justify-center">
            <button onClick={() => navigate('/dashboard/digital-twin')} className="btn-secondary">
              返回列表
            </button>
            <button onClick={() => refetch()} className="btn-primary">
              重新模拟
            </button>
          </div>
        </div>
      </div>
    )
  }

  // 如果还没有结果
  if (!result) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-12 text-center">
          <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">尚未执行模拟</h2>
          <p className="text-gray-400 mb-6">请先执行模拟以查看结果</p>
          <button
            onClick={async () => {
              await api.post(`/simulation/scenarios/${id}/simulate`)
              refetch()
            }}
            className="btn-primary"
          >
            开始模拟
          </button>
        </div>
      </div>
    )
  }

  const baseCase = result.base_case
  const simulatedCase = result.simulated_case
  const impact = result.impact
  const timeSeries = result.time_series

  // 准备图表数据
  const costBreakdownData = [
    { name: '原材料', value: baseCase.cost_breakdown.raw_material, color: '#3b82f6' },
    { name: '人工', value: baseCase.cost_breakdown.labor, color: '#10b981' },
    { name: '能源', value: baseCase.cost_breakdown.energy, color: '#f59e0b' },
    { name: '其他', value: baseCase.cost_breakdown.other, color: '#6366f1' },
  ]

  const comparisonData = [
    {
      name: '基准情况',
      revenue: baseCase.revenue / 100000000,
      cost: baseCase.total_cost / 100000000,
      profit: baseCase.net_profit / 100000000,
    },
    {
      name: '模拟情况',
      revenue: simulatedCase.revenue / 100000000,
      cost: simulatedCase.total_cost / 100000000,
      profit: simulatedCase.net_profit / 100000000,
    },
  ]

  const timeSeriesData = timeSeries.map((item: any) => ({
    year: `第${item.year}年`,
    profit: item.profit / 100000000,
    roe: item.roe,
  }))

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面头部 */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/dashboard/digital-twin')}
            className="text-gray-400 hover:text-white"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-3xl font-bold">{scenarioData.name}</h1>
            <p className="text-gray-400 mt-1">{scenarioData.description}</p>
          </div>
        </div>
        <button className="btn-secondary flex items-center space-x-2">
          <Download className="w-4 h-4" />
          <span>导出报告</span>
        </button>
      </div>

      {/* 关键指标对比 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* 收入变化 */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">收入变化</span>
            <DollarSign className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold mb-1">
            {impact.revenue_change >= 0 ? '+' : ''}
            {(impact.revenue_change / 100000000).toFixed(2)}亿
          </div>
          <div className={`text-sm flex items-center ${impact.revenue_change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {impact.revenue_change_percent >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
            {impact.revenue_change_percent >= 0 ? '+' : ''}{impact.revenue_change_percent.toFixed(2)}%
          </div>
        </div>

        {/* 成本变化 */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">成本变化</span>
            <DollarSign className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold mb-1">
            {impact.cost_change >= 0 ? '+' : ''}
            {(impact.cost_change / 100000000).toFixed(2)}亿
          </div>
          <div className={`text-sm flex items-center ${impact.cost_change_percent <= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {impact.cost_change_percent >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
            {impact.cost_change_percent >= 0 ? '+' : ''}{impact.cost_change_percent.toFixed(2)}%
          </div>
        </div>

        {/* 利润变化 */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">利润变化</span>
            <TrendingUp className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold mb-1">
            {impact.profit_change >= 0 ? '+' : ''}
            {(impact.profit_change / 100000000).toFixed(2)}亿
          </div>
          <div className={`text-sm flex items-center ${impact.profit_change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {impact.profit_change_percent >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
            {impact.profit_change_percent >= 0 ? '+' : ''}{impact.profit_change_percent.toFixed(2)}%
          </div>
        </div>

        {/* ROE变化 */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">ROE变化</span>
            <BarChart3 className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-2xl font-bold mb-1">
            {impact.roe_change >= 0 ? '+' : ''}{impact.roe_change.toFixed(2)}%
          </div>
          <div className="text-sm text-gray-400">
            {baseCase.roe.toFixed(2)}% → {simulatedCase.roe.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* 详细对比 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 收入成本利润对比 */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">收入成本利润对比</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" label={{ value: '金额(亿元)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Legend />
              <Bar dataKey="revenue" name="收入" fill="#3b82f6" />
              <Bar dataKey="cost" name="成本" fill="#f59e0b" />
              <Bar dataKey="profit" name="利润" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 成本结构 */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">成本结构（基准情况）</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RechartsPieChart>
              <Pie
                data={costBreakdownData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {costBreakdownData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                formatter={(value: any) => `¥${(value / 100000000).toFixed(2)}亿`}
              />
            </RechartsPieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 时间序列趋势 */}
      <div className="glass-card p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">利润趋势预测（{scenarioData.time_range}年）</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9ca3af" />
            <YAxis
              yAxisId="left"
              stroke="#9ca3af"
              label={{ value: '利润(亿元)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#9ca3af"
              label={{ value: 'ROE(%)', angle: 90, position: 'insideRight', fill: '#9ca3af' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="profit"
              name="净利润(亿元)"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 4 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="roe"
              name="ROE(%)"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 详细数据表格 */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">详细财务数据</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">指标</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">基准情况</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">模拟情况</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">变化</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4">营业收入</td>
                <td className="text-right py-3 px-4">¥{(baseCase.revenue / 100000000).toFixed(2)}亿</td>
                <td className="text-right py-3 px-4">¥{(simulatedCase.revenue / 100000000).toFixed(2)}亿</td>
                <td className={`text-right py-3 px-4 ${impact.revenue_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {impact.revenue_change >= 0 ? '+' : ''}{(impact.revenue_change / 100000000).toFixed(2)}亿
                  ({impact.revenue_change_percent >= 0 ? '+' : ''}{impact.revenue_change_percent.toFixed(2)}%)
                </td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4">营业成本</td>
                <td className="text-right py-3 px-4">¥{(baseCase.total_cost / 100000000).toFixed(2)}亿</td>
                <td className="text-right py-3 px-4">¥{(simulatedCase.total_cost / 100000000).toFixed(2)}亿</td>
                <td className={`text-right py-3 px-4 ${impact.cost_change <= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {impact.cost_change >= 0 ? '+' : ''}{(impact.cost_change / 100000000).toFixed(2)}亿
                  ({impact.cost_change_percent >= 0 ? '+' : ''}{impact.cost_change_percent.toFixed(2)}%)
                </td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4">毛利润</td>
                <td className="text-right py-3 px-4">¥{(baseCase.gross_profit / 100000000).toFixed(2)}亿</td>
                <td className="text-right py-3 px-4">¥{(simulatedCase.gross_profit / 100000000).toFixed(2)}亿</td>
                <td className={`text-right py-3 px-4 ${(simulatedCase.gross_profit - baseCase.gross_profit) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {(simulatedCase.gross_profit - baseCase.gross_profit) >= 0 ? '+' : ''}
                  {((simulatedCase.gross_profit - baseCase.gross_profit) / 100000000).toFixed(2)}亿
                </td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4">净利润</td>
                <td className="text-right py-3 px-4">¥{(baseCase.net_profit / 100000000).toFixed(2)}亿</td>
                <td className="text-right py-3 px-4">¥{(simulatedCase.net_profit / 100000000).toFixed(2)}亿</td>
                <td className={`text-right py-3 px-4 ${impact.profit_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {impact.profit_change >= 0 ? '+' : ''}{(impact.profit_change / 100000000).toFixed(2)}亿
                  ({impact.profit_change_percent >= 0 ? '+' : ''}{impact.profit_change_percent.toFixed(2)}%)
                </td>
              </tr>
              <tr className="border-b border-white/5">
                <td className="py-3 px-4">ROE</td>
                <td className="text-right py-3 px-4">{baseCase.roe.toFixed(2)}%</td>
                <td className="text-right py-3 px-4">{simulatedCase.roe.toFixed(2)}%</td>
                <td className={`text-right py-3 px-4 ${impact.roe_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {impact.roe_change >= 0 ? '+' : ''}{impact.roe_change.toFixed(2)}%
                </td>
              </tr>
              <tr>
                <td className="py-3 px-4">ROI</td>
                <td className="text-right py-3 px-4">{baseCase.roi.toFixed(2)}%</td>
                <td className="text-right py-3 px-4">{simulatedCase.roi.toFixed(2)}%</td>
                <td className={`text-right py-3 px-4 ${impact.roi_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {impact.roi_change >= 0 ? '+' : ''}{impact.roi_change.toFixed(2)}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
