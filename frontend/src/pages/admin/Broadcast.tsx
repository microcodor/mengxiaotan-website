import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Send, Clock, CheckCircle, XCircle, Eye } from 'lucide-react'
import api from '@/lib/api'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function AdminBroadcast() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [targetType, setTargetType] = useState('all')
  const queryClient = useQueryClient()

  const { data: tasksData, isLoading } = useQuery({
    queryKey: ['broadcast-tasks'],
    queryFn: () => api.get('/push/broadcast/list'),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/push/broadcast', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['broadcast-tasks'] })
      setShowCreateModal(false)
      setTitle('')
      setContent('')
      alert('推送任务创建成功')
    },
  })

  const pushDailyBriefMutation = useMutation({
    mutationFn: () => api.post('/push/daily-brief'),
    onSuccess: (data: any) => {
      alert(`每日简报推送成功！共推送 ${data.total_users} 个用户`)
    },
    onError: () => {
      alert('每日简报推送失败，请检查简报是否已生成')
    },
  })

  const handleCreate = () => {
    if (!title || !content) {
      alert('请填写标题和内容')
      return
    }

    createMutation.mutate({
      title,
      content,
      target_type: targetType,
      channel: 'enterprise_wechat'
    })
  }

  const tasks = tasksData?.items || []

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: { text: '待发送', class: 'bg-yellow-500/20 text-yellow-400', icon: Clock },
      sending: { text: '发送中', class: 'bg-blue-500/20 text-blue-400', icon: Send },
      completed: { text: '已完成', class: 'bg-green-500/20 text-green-400', icon: CheckCircle },
      failed: { text: '失败', class: 'bg-red-500/20 text-red-400', icon: XCircle },
    }
    const badge = badges[status as keyof typeof badges] || badges.pending
    const Icon = badge.icon
    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm ${badge.class}`}>
        <Icon className="w-4 h-4" />
        <span>{badge.text}</span>
      </span>
    )
  }

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">推送管理</h1>

        <div className="flex space-x-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>创建推送</span>
          </button>
          <button
            onClick={() => pushDailyBriefMutation.mutate()}
            disabled={pushDailyBriefMutation.isPending}
            className="btn-secondary flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>{pushDailyBriefMutation.isPending ? '推送中...' : '推送今日简报'}</span>
          </button>
        </div>
      </div>

      {/* 推送任务列表 */}
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <div className="glass-card p-12 text-center text-gray-400">
            暂无推送任务
          </div>
        ) : (
          tasks.map((task: any) => (
            <div key={task.id} className="glass-card p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{task.title}</h3>
                    {getStatusBadge(task.status)}
                  </div>
                  <p className="text-sm text-gray-400 line-clamp-2">{task.content}</p>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm text-gray-400">
                <div className="space-x-4">
                  <span>目标: {task.target_type === 'all' ? '所有用户' : '指定用户'}</span>
                  <span>渠道: 企业微信</span>
                </div>
                <div>
                  创建时间: {format(new Date(task.created_at), 'yyyy-MM-dd HH:mm', { locale: zhCN })}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 创建推送弹窗 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">创建推送任务</h2>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2">标题 *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2"
                  placeholder="请输入推送标题"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">内容 *</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2 min-h-[150px]"
                  placeholder="请输入推送内容"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">推送对象</label>
                <select
                  value={targetType}
                  onChange={(e) => setTargetType(e.target.value)}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2"
                >
                  <option value="all">所有订阅用户</option>
                  <option value="plan">指定套餐用户</option>
                  <option value="custom">自定义用户</option>
                </select>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleCreate}
                disabled={createMutation.isPending}
                className="flex-1 btn-primary"
              >
                {createMutation.isPending ? '创建中...' : '立即发送'}
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setTitle('')
                  setContent('')
                }}
                className="flex-1 btn-secondary"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
