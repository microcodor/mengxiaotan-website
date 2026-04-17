import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, FileText, Clock, CheckCircle, XCircle, 
  Download, Eye, AlertCircle
} from 'lucide-react'
import api from '@/lib/api'
import { useNavigate } from 'react-router-dom'

interface ReportRequest {
  id: number
  company_name: string
  report_type: string
  title: string
  description: string
  expected_delivery_date: string | null
  status: string
  created_at: string
}

export default function CustomReports() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('')

  // 获取配额
  const { data: quota } = useQuery({
    queryKey: ['reportQuota'],
    queryFn: () => api.get('/reports/quota'),
  })

  // 获取申请列表
  const { data: requests, isLoading } = useQuery({
    queryKey: ['reportRequests', statusFilter],
    queryFn: () => {
      const url = statusFilter 
        ? `/reports/requests?status=${statusFilter}`
        : '/reports/requests'
      return api.get(url)
    },
  })

  // 获取统计数据
  const { data: statistics } = useQuery({
    queryKey: ['reportStatistics'],
    queryFn: () => api.get('/reports/statistics'),
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400 bg-green-500/10 border-green-500/30'
      case 'in_progress':
      case 'assigned':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      case 'rejected':
        return 'text-red-400 bg-red-500/10 border-red-500/30'
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '待处理'
      case 'assigned':
        return '已分配'
      case 'in_progress':
        return '进行中'
      case 'completed':
        return '已完成'
      case 'rejected':
        return '已拒绝'
      default:
        return status
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5" />
      case 'in_progress':
      case 'assigned':
        return <Clock className="w-5 h-5" />
      case 'rejected':
        return <XCircle className="w-5 h-5" />
      default:
        return <FileText className="w-5 h-5" />
    }
  }

  const quotaData = quota?.data || { used_quota: 0, total_quota: 2, remaining_quota: 2 }
  const requestList = requests?.data || []
  const stats = statistics?.data || { total: 0, pending: 0, in_progress: 0, completed: 0 }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">加载中...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">定制报告</h1>
          <p className="text-gray-400">申请专业的行业分析报告</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          disabled={quotaData.remaining_quota <= 0}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-5 h-5" />
          <span>申请报告</span>
        </button>
      </div>

      {/* 配额和统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* 配额卡片 */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">本月配额</span>
            <FileText className="w-5 h-5 text-primary-400" />
          </div>
          <div className="text-3xl font-bold mb-1">
            {quotaData.remaining_quota}/{quotaData.total_quota}
          </div>
          <div className="text-sm text-gray-400">
            已使用 {quotaData.used_quota} 份
          </div>
        </div>

        {/* 统计卡片 */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">待处理</span>
            <Clock className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="text-3xl font-bold">{stats.pending}</div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">进行中</span>
            <Clock className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-3xl font-bold">{stats.in_progress}</div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">已完成</span>
            <CheckCircle className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-3xl font-bold">{stats.completed}</div>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="flex items-center space-x-4 mb-6">
        <span className="text-sm text-gray-400">状态筛选：</span>
        <div className="flex space-x-2">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              statusFilter === '' 
                ? 'bg-primary-500 text-white' 
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            全部
          </button>
          <button
            onClick={() => setStatusFilter('pending')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              statusFilter === 'pending' 
                ? 'bg-primary-500 text-white' 
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            待处理
          </button>
          <button
            onClick={() => setStatusFilter('in_progress')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              statusFilter === 'in_progress' 
                ? 'bg-primary-500 text-white' 
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            进行中
          </button>
          <button
            onClick={() => setStatusFilter('completed')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              statusFilter === 'completed' 
                ? 'bg-primary-500 text-white' 
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            已完成
          </button>
        </div>
      </div>

      {/* 申请列表 */}
      {requestList.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">暂无报告申请</h2>
          <p className="text-gray-400 mb-6">
            {quotaData.remaining_quota > 0 
              ? '点击"申请报告"按钮创建您的第一份定制报告申请'
              : '本月配额已用完，下月1号自动重置'}
          </p>
          {quotaData.remaining_quota > 0 && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              申请报告
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {requestList.map((request: ReportRequest) => (
            <div key={request.id} className="glass-card p-6 hover:border-primary-500/50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{request.title}</h3>
                    <span className={`text-xs px-3 py-1 rounded-full border flex items-center space-x-1 ${getStatusColor(request.status)}`}>
                      {getStatusIcon(request.status)}
                      <span>{getStatusText(request.status)}</span>
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                    {request.description}
                  </p>
                  
                  <div className="flex items-center space-x-6 text-sm text-gray-400">
                    <div>
                      <span className="text-gray-500">企业：</span>
                      {request.company_name}
                    </div>
                    <div>
                      <span className="text-gray-500">申请时间：</span>
                      {new Date(request.created_at).toLocaleDateString('zh-CN')}
                    </div>
                    {request.expected_delivery_date && (
                      <div>
                        <span className="text-gray-500">期望交付：</span>
                        {new Date(request.expected_delivery_date).toLocaleDateString('zh-CN')}
                      </div>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={() => navigate(`/dashboard/reports/${request.id}`)}
                  className="btn-secondary ml-4 flex items-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>查看详情</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 创建申请模态框 */}
      {showCreateModal && (
        <CreateReportModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['reportRequests'] })
            queryClient.invalidateQueries({ queryKey: ['reportQuota'] })
            queryClient.invalidateQueries({ queryKey: ['reportStatistics'] })
          }}
        />
      )}
    </div>
  )
}

// 创建报告申请模态框
function CreateReportModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    report_type: '',
    title: '',
    description: '',
    expected_delivery_date: '',
    additional_notes: '',
  })

  // 获取报告类型
  const { data: reportTypes } = useQuery({
    queryKey: ['reportTypes'],
    queryFn: () => api.get('/reports/types'),
  })

  // 创建申请
  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/reports/requests', data),
    onSuccess: () => {
      alert('申请提交成功！我们会尽快处理您的申请。')
      onSuccess()
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.report_type || !formData.title || !formData.description) {
      alert('请填写必填字段')
      return
    }

    try {
      await createMutation.mutateAsync(formData)
    } catch (error: any) {
      alert(error.response?.data?.message || '提交失败，请稍后重试')
    }
  }

  const types = reportTypes?.data || []
  const selectedType = types.find((t: any) => t.value === formData.report_type)

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="glass-card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* 模态框头部 */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold">申请定制报告</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* 报告类型 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              报告类型 <span className="text-red-400">*</span>
            </label>
            <select
              value={formData.report_type}
              onChange={(e) => setFormData({ ...formData, report_type: e.target.value })}
              className="input-field w-full"
              required
            >
              <option value="">请选择报告类型</option>
              {types.map((type: any) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {selectedType && (
              <p className="text-sm text-gray-400 mt-2">{selectedType.description}</p>
            )}
          </div>

          {/* 报告标题 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              报告标题 <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input-field w-full"
              placeholder="例如：煤制油与绿氢耦合经济性对比分析"
              required
            />
          </div>

          {/* 需求描述 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              需求描述 <span className="text-red-400">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input-field w-full"
              rows={6}
              placeholder="请详细描述您的报告需求，包括：&#10;1. 分析的重点和目标&#10;2. 需要对比的方案或技术&#10;3. 关注的关键指标&#10;4. 其他特殊要求"
              required
            />
          </div>

          {/* 期望交付时间 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              期望交付时间
            </label>
            <input
              type="date"
              value={formData.expected_delivery_date}
              onChange={(e) => setFormData({ ...formData, expected_delivery_date: e.target.value })}
              className="input-field w-full"
              min={new Date().toISOString().split('T')[0]}
            />
            <p className="text-sm text-gray-400 mt-2">
              通常需要5-7个工作日完成，紧急需求请在附加说明中注明
            </p>
          </div>

          {/* 附加说明 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              附加说明
            </label>
            <textarea
              value={formData.additional_notes}
              onChange={(e) => setFormData({ ...formData, additional_notes: e.target.value })}
              className="input-field w-full"
              rows={3}
              placeholder="其他需要说明的内容（可选）"
            />
          </div>

          {/* 提示信息 */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-300">
                <p className="font-semibold mb-1">温馨提示</p>
                <ul className="list-disc list-inside space-y-1 text-blue-200">
                  <li>提交申请后将消耗1份月度配额</li>
                  <li>我们会在1个工作日内审核您的申请</li>
                  <li>报告完成后会通过企业微信和邮件通知您</li>
                  <li>如有疑问，请联系客服</li>
                </ul>
              </div>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex space-x-3 pt-4 border-t border-white/10">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              取消
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="btn-primary flex-1"
            >
              {createMutation.isPending ? '提交中...' : '提交申请'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
