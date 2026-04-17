import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Clock, CheckCircle, XCircle, Upload } from 'lucide-react'
import api from '@/lib/api'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function Orders() {
  const queryClient = useQueryClient()

  const { data: orders, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => api.get('/subscriptions/orders'),
  })

  const cancelMutation = useMutation({
    mutationFn: (orderId: number) => api.post(`/subscriptions/orders/${orderId}/cancel`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
  })

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: { text: '待支付', class: 'bg-yellow-500/20 text-yellow-400', icon: Clock },
      paid: { text: '已支付', class: 'bg-green-500/20 text-green-400', icon: CheckCircle },
      cancelled: { text: '已取消', class: 'bg-gray-500/20 text-gray-400', icon: XCircle },
      refunded: { text: '已退款', class: 'bg-red-500/20 text-red-400', icon: XCircle },
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

  const getPaymentMethod = (method: string) => {
    const methods: Record<string, string> = {
      offline: '线下支付',
      alipay: '支付宝',
      wechat: '微信支付',
    }
    return methods[method] || method
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">加载中...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">我的订单</h1>
        <p className="text-gray-400">查看和管理您的订单</p>
      </div>

      {!orders || orders.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <p className="text-gray-400 mb-4">暂无订单</p>
          <a href="/subscription" className="btn-primary inline-block">
            立即订阅
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order: any) => (
            <div key={order.id} className="glass-card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{order.plan?.name}</h3>
                    {getStatusBadge(order.payment_status)}
                  </div>
                  <p className="text-sm text-gray-400">订单号: {order.order_no}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-400">¥{order.amount}</div>
                  <div className="text-sm text-gray-400">{getPaymentMethod(order.payment_method)}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                  <span className="text-gray-400">创建时间：</span>
                  <span>{format(new Date(order.created_at), 'yyyy-MM-dd HH:mm', { locale: zhCN })}</span>
                </div>
                {order.payment_time && (
                  <div>
                    <span className="text-gray-400">支付时间：</span>
                    <span>{format(new Date(order.payment_time), 'yyyy-MM-dd HH:mm', { locale: zhCN })}</span>
                  </div>
                )}
                {order.contact_info && (
                  <div className="md:col-span-2">
                    <span className="text-gray-400">联系方式：</span>
                    <span>{JSON.stringify(order.contact_info)}</span>
                  </div>
                )}
                {order.remark && (
                  <div className="md:col-span-2">
                    <span className="text-gray-400">备注：</span>
                    <span>{order.remark}</span>
                  </div>
                )}
                {order.admin_note && (
                  <div className="md:col-span-2">
                    <span className="text-gray-400">管理员备注：</span>
                    <span className="text-yellow-400">{order.admin_note}</span>
                  </div>
                )}
              </div>

              {order.payment_status === 'pending' && (
                <div className="flex space-x-3">
                  <button className="btn-primary flex items-center space-x-2">
                    <Upload className="w-4 h-4" />
                    <span>上传支付凭证</span>
                  </button>
                  <button
                    onClick={() => cancelMutation.mutate(order.id)}
                    disabled={cancelMutation.isPending}
                    className="btn-secondary"
                  >
                    取消订单
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
