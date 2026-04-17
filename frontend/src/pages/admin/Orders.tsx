import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, XCircle, Clock, Eye } from 'lucide-react'
import api from '@/lib/api'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function AdminOrders() {
  const [filter, setFilter] = useState<string>('all')
  const [selectedOrder, setSelectedOrder] = useState<any>(null)
  const [rejectReason, setRejectReason] = useState('')
  const queryClient = useQueryClient()

  const { data: ordersData, isLoading } = useQuery({
    queryKey: ['admin-orders', filter],
    queryFn: () => api.get(`/admin/orders${filter !== 'all' ? `?status=${filter}` : ''}`),
  })

  const confirmMutation = useMutation({
    mutationFn: (orderId: number) => api.post(`/admin/orders/${orderId}/confirm`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] })
      alert('订单确认成功')
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ orderId, reason }: { orderId: number; reason: string }) =>
      api.post(`/admin/orders/${orderId}/reject`, { admin_note: reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] })
      setSelectedOrder(null)
      setRejectReason('')
      alert('订单已拒绝')
    },
  })

  const orders = ordersData?.items || []

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: { text: '待确认', class: 'bg-yellow-500/20 text-yellow-400' },
      paid: { text: '已支付', class: 'bg-green-500/20 text-green-400' },
      cancelled: { text: '已取消', class: 'bg-gray-500/20 text-gray-400' },
      refunded: { text: '已退款', class: 'bg-red-500/20 text-red-400' },
    }
    const badge = badges[status as keyof typeof badges] || badges.pending
    return <span className={`px-3 py-1 rounded-full text-sm ${badge.class}`}>{badge.text}</span>
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
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">订单管理</h1>

        {/* 筛选器 */}
        <div className="flex space-x-2">
          {[
            { value: 'all', label: '全部' },
            { value: 'pending', label: '待确认' },
            { value: 'paid', label: '已支付' },
            { value: 'cancelled', label: '已取消' },
          ].map((item) => (
            <button
              key={item.value}
              onClick={() => setFilter(item.value)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filter === item.value
                  ? 'bg-primary-500 text-white'
                  : 'glass-card hover:bg-white/10'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* 订单列表 */}
      <div className="space-y-4">
        {orders.length === 0 ? (
          <div className="glass-card p-12 text-center text-gray-400">暂无订单</div>
        ) : (
          orders.map((order: any) => (
            <div key={order.id} className="glass-card p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{order.plan?.name}</h3>
                    {getStatusBadge(order.payment_status)}
                  </div>
                  <div className="text-sm text-gray-400 space-y-1">
                    <div>订单号: {order.order_no}</div>
                    <div>
                      用户: {order.user?.nickname || order.user?.phone} ({order.user?.phone})
                    </div>
                    <div>
                      创建时间: {format(new Date(order.created_at), 'yyyy-MM-dd HH:mm', { locale: zhCN })}
                    </div>
                    {order.payment_time && (
                      <div>
                        支付时间: {format(new Date(order.payment_time), 'yyyy-MM-dd HH:mm', { locale: zhCN })}
                      </div>
                    )}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-400 mb-1">¥{order.amount}</div>
                  <div className="text-sm text-gray-400">{getPaymentMethod(order.payment_method)}</div>
                </div>
              </div>

              {/* 联系方式和备注 */}
              {(order.contact_info || order.remark || order.admin_note) && (
                <div className="border-t border-white/10 pt-4 mb-4 space-y-2 text-sm">
                  {order.contact_info && (
                    <div>
                      <span className="text-gray-400">联系方式: </span>
                      <span>{JSON.stringify(order.contact_info)}</span>
                    </div>
                  )}
                  {order.remark && (
                    <div>
                      <span className="text-gray-400">用户备注: </span>
                      <span>{order.remark}</span>
                    </div>
                  )}
                  {order.admin_note && (
                    <div>
                      <span className="text-gray-400">管理员备注: </span>
                      <span className="text-yellow-400">{order.admin_note}</span>
                    </div>
                  )}
                </div>
              )}

              {/* 支付凭证 */}
              {order.payment_proof && (
                <div className="border-t border-white/10 pt-4 mb-4">
                  <div className="text-sm text-gray-400 mb-2">支付凭证:</div>
                  <img
                    src={order.payment_proof}
                    alt="支付凭证"
                    className="max-w-xs rounded-lg border border-white/10"
                  />
                </div>
              )}

              {/* 操作按钮 */}
              {order.payment_status === 'pending' && (
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      if (confirm('确认该订单已支付？')) {
                        confirmMutation.mutate(order.id)
                      }
                    }}
                    disabled={confirmMutation.isPending}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>确认支付</span>
                  </button>
                  <button
                    onClick={() => setSelectedOrder(order)}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>拒绝订单</span>
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* 拒绝订单弹窗 */}
      {selectedOrder && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">拒绝订单</h3>
            <p className="text-gray-400 mb-4">订单号: {selectedOrder.order_no}</p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="请输入拒绝原因..."
              className="w-full bg-dark-card border border-white/10 rounded-lg p-3 mb-4 min-h-[100px]"
            />
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  if (rejectReason.trim()) {
                    rejectMutation.mutate({ orderId: selectedOrder.id, reason: rejectReason })
                  } else {
                    alert('请输入拒绝原因')
                  }
                }}
                disabled={rejectMutation.isPending}
                className="btn-primary flex-1"
              >
                确认拒绝
              </button>
              <button
                onClick={() => {
                  setSelectedOrder(null)
                  setRejectReason('')
                }}
                className="btn-secondary flex-1"
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
