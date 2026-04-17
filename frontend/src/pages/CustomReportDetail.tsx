import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowLeft, FileText, Clock, CheckCircle, XCircle,
  Download, Calendar, Building2, User, AlertCircle
} from 'lucide-react'
import api from '@/lib/api'

export default function CustomReportDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  // 获取申请详情
  const { data: detail, isLoading } = useQuery({
    queryKey: ['reportDetail', id],
    queryFn: () => api.get(`/reports/requests/${id}`),
  })

  const handleDownload = async (fileId: number, fileName: string) => {
    try {
      const response = await fetch(
        `/api/reports/requests/${id}/files/${fileId}/download`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('下载失败')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('下载失败，请稍后重试')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">加载中...</div>
      </div>
    )
  }

  const request = detail?.data

  if (!request) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-12 text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">申请不存在</h2>
          <button onClick={() => navigate('/dashboard/reports')} className="btn-primary mt-4">
            返回列表
          </button>
        </div>
      </div>
    )
  }

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
        return <CheckCircle className="w-6 h-6" />
      case 'in_progress':
      case 'assigned':
        return <Clock className="w-6 h-6" />
      case 'rejected':
        return <XCircle className="w-6 h-6" />
      default:
        return <FileText className="w-6 h-6" />
    }
  }

  const getReportTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      'tech_optimization': '技术路线优化',
      'market_layout': '区域市场布局',
      'policy_analysis': '政策影响分析',
      'competitor_analysis': '竞争对手分析',
      'investment_support': '投资决策支持',
    }
    return types[type] || type
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面头部 */}
      <div className="flex items-center space-x-4 mb-8">
        <button
          onClick={() => navigate('/dashboard/reports')}
          className="text-gray-400 hover:text-white"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{request.title}</h1>
          <p className="text-gray-400 mt-1">申请编号：#{request.id}</p>
        </div>
        <div className={`px-4 py-2 rounded-lg border flex items-center space-x-2 ${getStatusColor(request.status)}`}>
          {getStatusIcon(request.status)}
          <span className="font-semibold">{getStatusText(request.status)}</span>
        </div>
      </div>

      {/* 状态时间线 */}
      <div className="glass-card p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">申请进度</h3>
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-white/10"></div>
          
          <div className="space-y-6">
            {/* 已提交 */}
            <div className="relative flex items-start space-x-4">
              <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center z-10">
                <CheckCircle className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 pt-1">
                <div className="font-semibold">已提交</div>
                <div className="text-sm text-gray-400">
                  {new Date(request.created_at).toLocaleString('zh-CN')}
                </div>
              </div>
            </div>

            {/* 已分配 */}
            {request.assigned_at && (
              <div className="relative flex items-start space-x-4">
                <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center z-10">
                  <CheckCircle className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 pt-1">
                  <div className="font-semibold">已分配</div>
                  <div className="text-sm text-gray-400">
                    {new Date(request.assigned_at).toLocaleString('zh-CN')}
                  </div>
                </div>
              </div>
            )}

            {/* 已完成 */}
            {request.completed_at && (
              <div className="relative flex items-start space-x-4">
                <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center z-10">
                  <CheckCircle className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 pt-1">
                  <div className="font-semibold">已完成</div>
                  <div className="text-sm text-gray-400">
                    {new Date(request.completed_at).toLocaleString('zh-CN')}
                  </div>
                </div>
              </div>
            )}

            {/* 已拒绝 */}
            {request.status === 'rejected' && (
              <div className="relative flex items-start space-x-4">
                <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center z-10">
                  <XCircle className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 pt-1">
                  <div className="font-semibold">已拒绝</div>
                  {request.rejected_reason && (
                    <div className="text-sm text-red-400 mt-1">
                      原因：{request.rejected_reason}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 申请信息 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* 基本信息 */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">基本信息</h3>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-gray-400">报告类型</div>
                <div className="font-medium">{getReportTypeLabel(request.report_type)}</div>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <Building2 className="w-5 h-5 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-gray-400">申请企业</div>
                <div className="font-medium">{request.company_name}</div>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <User className="w-5 h-5 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-gray-400">申请人</div>
                <div className="font-medium">{request.user_name}</div>
              </div>
            </div>

            {request.expected_delivery_date && (
              <div className="flex items-start space-x-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm text-gray-400">期望交付时间</div>
                  <div className="font-medium">
                    {new Date(request.expected_delivery_date).toLocaleDateString('zh-CN')}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 需求描述 */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">需求描述</h3>
          <div className="text-gray-300 whitespace-pre-wrap">
            {request.description}
          </div>
          
          {request.additional_notes && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="text-sm text-gray-400 mb-2">附加说明</div>
              <div className="text-gray-300 whitespace-pre-wrap">
                {request.additional_notes}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 报告文件 */}
      {request.files && request.files.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">报告文件</h3>
          <div className="space-y-3">
            {request.files.map((file: any) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary-400" />
                  </div>
                  <div>
                    <div className="font-medium">{file.file_name}</div>
                    <div className="text-sm text-gray-400">
                      {(file.file_size / 1024 / 1024).toFixed(2)} MB · 
                      上传于 {new Date(file.created_at).toLocaleDateString('zh-CN')}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDownload(file.id, file.file_name)}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>下载</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 等待提示 */}
      {request.status === 'pending' && (
        <div className="glass-card p-6 bg-blue-500/5 border-blue-500/30">
          <div className="flex items-start space-x-3">
            <Clock className="w-6 h-6 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-300 mb-2">申请审核中</h3>
              <p className="text-sm text-blue-200">
                我们已收到您的申请，将在1个工作日内完成审核。审核通过后会立即安排报告编写，
                预计5-7个工作日完成。报告完成后会通过企业微信和邮件通知您。
              </p>
            </div>
          </div>
        </div>
      )}

      {request.status === 'in_progress' && (
        <div className="glass-card p-6 bg-blue-500/5 border-blue-500/30">
          <div className="flex items-start space-x-3">
            <Clock className="w-6 h-6 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-300 mb-2">报告编写中</h3>
              <p className="text-sm text-blue-200">
                您的报告正在编写中，我们会尽快完成。如有紧急需求，请联系客服。
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
