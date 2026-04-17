import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, ArrowRight, Sparkles, TrendingUp, Shield, Zap, Gift } from 'lucide-react'
import api from '@/lib/api'
import { useNavigate } from 'react-router-dom'

export default function Subscription() {
  const [selectedPlan, setSelectedPlan] = useState<any>(null)
  const [paymentCycle, setPaymentCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [contactInfo, setContactInfo] = useState({ name: '', phone: '', email: '' })
  const [remark, setRemark] = useState('')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: plans } = useQuery({
    queryKey: ['plans'],
    queryFn: () => api.get('/subscriptions/plans'),
  })

  const createOrderMutation = useMutation({
    mutationFn: (data: any) => api.post('/subscriptions/orders', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      alert('订单创建成功！请联系客服完成支付')
      navigate('/orders')
    },
  })

  const handleSubscribe = (plan: any) => {
    setSelectedPlan(plan)
  }

  const handleConfirmOrder = () => {
    if (!contactInfo.name || !contactInfo.phone) {
      alert('请填写联系方式')
      return
    }

    // 计算实际金额（如果是基础版且选择年付，则为468元）
    let actualAmount = selectedPlan.price
    let actualDuration = selectedPlan.duration_days
    
    if (selectedPlan.name === '基础版' && paymentCycle === 'yearly') {
      actualAmount = 468 // 年付价格（赠1个月）
      actualDuration = 365 // 一年
    }

    createOrderMutation.mutate({
      plan_id: selectedPlan.id,
      payment_method: 'offline',
      contact_info: contactInfo,
      remark: `${remark}\n支付周期: ${paymentCycle === 'monthly' ? '月付' : '年付'}`,
      amount: actualAmount,
      duration_days: actualDuration,
    })
  }

  // 获取套餐图标
  const getPlanIcon = (planName: string) => {
    if (planName === '免费订阅') return <Zap className="w-8 h-8 text-primary-400" />
    if (planName === '基础版') return <Sparkles className="w-8 h-8 text-primary-400" />
    return <TrendingUp className="w-8 h-8 text-primary-400" />
  }

  // 获取套餐标签
  const getPlanBadge = (planName: string) => {
    if (planName === '免费订阅') return <span className="inline-block px-3 py-1 bg-green-500/20 text-green-400 text-xs font-semibold rounded-full">7天免费试用</span>
    if (planName === '基础版') return <span className="inline-block px-3 py-1 bg-primary-500/20 text-primary-400 text-xs font-semibold rounded-full">推荐</span>
    return null
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面标题 */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">蒙小碳信息订阅服务</h1>
        <p className="text-gray-400 text-lg mb-2">两种模式，精准匹配需求</p>
        <p className="text-gray-500 text-sm">基于公开信息的精准赋能，让能源决策更智能</p>
      </div>

      {/* 套餐卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12 max-w-5xl mx-auto">
        {plans?.map((plan: any) => {
          const isFree = plan.name === '免费订阅'
          const isBasic = plan.name === '基础版'
          
          return (
            <div
              key={plan.id}
              className={`glass-card p-8 transition-all relative ${
                selectedPlan?.id === plan.id 
                  ? 'border-primary-500 ring-2 ring-primary-500/50' 
                  : 'hover:border-primary-500/50'
              } ${isBasic ? 'md:scale-105' : ''}`}
            >
              {/* 推荐标签 */}
              {isBasic && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="inline-block px-4 py-1 bg-gradient-to-r from-primary-500 to-primary-600 text-white text-sm font-semibold rounded-full shadow-lg">
                    ⭐ 推荐选择
                  </span>
                </div>
              )}

              {/* 套餐头部 */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getPlanIcon(plan.name)}
                  <h3 className="text-2xl font-bold">{plan.name}</h3>
                </div>
                {getPlanBadge(plan.name)}
              </div>

              {/* 价格 */}
              <div className="mb-6">
                {isFree ? (
                  <>
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold text-primary-400">免费</span>
                      <span className="text-gray-400 ml-2">/ 7天试用</span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">体验完整早报内容</p>
                  </>
                ) : (
                  <>
                    <div className="flex items-baseline">
                      <span className="text-4xl font-bold text-primary-400">¥39</span>
                      <span className="text-gray-400 ml-2">/ 月</span>
                    </div>
                    <div className="flex items-center space-x-2 mt-2">
                      <Gift className="w-4 h-4 text-green-400" />
                      <p className="text-sm text-green-400">年付 ¥468（赠1个月，相当于¥36/月）</p>
                    </div>
                  </>
                )}
              </div>

              {/* 功能列表 */}
              <ul className="space-y-3 mb-8">
                {plan.features && Object.entries(plan.features).map(([key, value]: any) => (
                  <li key={key} className="flex items-start space-x-2">
                    <Check className="w-5 h-5 text-primary-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="text-gray-300 text-sm font-medium">{key}</span>
                      {value && <p className="text-gray-500 text-xs mt-0.5">{value}</p>}
                    </div>
                  </li>
                ))}
              </ul>

              {/* 订阅按钮 */}
              <button
                onClick={() => handleSubscribe(plan)}
                className={`w-full ${isBasic ? 'btn-primary' : 'btn-secondary'} flex items-center justify-center space-x-2`}
              >
                <span>{isFree ? '立即试用' : '立即订阅'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )
        })}
      </div>

      {/* 功能对比表 */}
      <div className="glass-card p-8 mb-12 max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 text-center">功能详细对比</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">功能模块</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">免费订阅</th>
                <th className="text-center py-3 px-4 text-gray-400 font-medium">基础版</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              <tr>
                <td className="py-3 px-4 text-gray-300">政策速览</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">市场行情</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">热点聚焦</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">蒙小碳简评</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-green-400 mx-auto" /></td>
              </tr>
              <tr className="bg-primary-500/5">
                <td className="py-3 px-4 text-gray-300 font-medium">企业画像构建</td>
                <td className="py-3 px-4 text-center text-gray-500">-</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-primary-400 mx-auto" /></td>
              </tr>
              <tr className="bg-primary-500/5">
                <td className="py-3 px-4 text-gray-300 font-medium">战略级内参（2份/月）</td>
                <td className="py-3 px-4 text-center text-gray-500">-</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-primary-400 mx-auto" /></td>
              </tr>
              <tr className="bg-primary-500/5">
                <td className="py-3 px-4 text-gray-300 font-medium">数字分身沙盘</td>
                <td className="py-3 px-4 text-center text-gray-500">-</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-primary-400 mx-auto" /></td>
              </tr>
              <tr className="bg-primary-500/5">
                <td className="py-3 px-4 text-gray-300 font-medium">动态监测预警</td>
                <td className="py-3 px-4 text-center text-gray-500">-</td>
                <td className="py-3 px-4 text-center"><Check className="w-5 h-5 text-primary-400 mx-auto" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 使用场景 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12 max-w-5xl mx-auto">
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-6 h-6 text-green-400" />
            <h3 className="text-lg font-bold">选择免费订阅，如果你：</h3>
          </div>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✓ 需要了解行业整体动态</li>
            <li>✓ 关注政策和市场行情</li>
            <li>✓ 想快速获取每日要闻</li>
            <li>✓ 初次体验蒙小碳服务</li>
          </ul>
        </div>

        <div className="glass-card p-6 border-primary-500/30">
          <div className="flex items-center space-x-3 mb-4">
            <TrendingUp className="w-6 h-6 text-primary-400" />
            <h3 className="text-lg font-bold">选择基础版，如果你：</h3>
          </div>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✓ 需要针对企业的深度分析</li>
            <li>✓ 关注企业风险与机会</li>
            <li>✓ 需要战略决策支持</li>
            <li>✓ 想要定制化内参报告</li>
          </ul>
        </div>
      </div>

      {/* 订单确认弹窗 */}
      {selectedPlan && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-8 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">确认订单</h2>

            {/* 套餐信息 */}
            <div className="glass-card p-4 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-lg font-semibold">{selectedPlan.name}</span>
                <span className="text-2xl font-bold text-primary-400">
                  ¥{selectedPlan.name === '基础版' && paymentCycle === 'yearly' ? 468 : selectedPlan.price}
                </span>
              </div>
              <p className="text-sm text-gray-400">
                有效期: {selectedPlan.name === '基础版' && paymentCycle === 'yearly' ? '365天（赠1个月）' : `${selectedPlan.duration_days}天`}
              </p>
            </div>

            {/* 支付周期选择（仅基础版显示） */}
            {selectedPlan.name === '基础版' && (
              <div className="mb-6">
                <label className="block text-sm font-medium mb-3">支付周期</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setPaymentCycle('monthly')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      paymentCycle === 'monthly'
                        ? 'border-primary-500 bg-primary-500/10'
                        : 'border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="text-lg font-bold">月付</div>
                    <div className="text-2xl font-bold text-primary-400 my-1">¥39</div>
                    <div className="text-xs text-gray-400">按月订阅</div>
                  </button>
                  <button
                    onClick={() => setPaymentCycle('yearly')}
                    className={`p-4 rounded-lg border-2 transition-all relative ${
                      paymentCycle === 'yearly'
                        ? 'border-primary-500 bg-primary-500/10'
                        : 'border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                      省¥60
                    </div>
                    <div className="text-lg font-bold">年付</div>
                    <div className="text-2xl font-bold text-primary-400 my-1">¥468</div>
                    <div className="text-xs text-gray-400">赠1个月</div>
                  </button>
                </div>
                {paymentCycle === 'yearly' && (
                  <div className="mt-3 p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                    <p className="text-sm text-green-400 flex items-center space-x-2">
                      <Gift className="w-4 h-4" />
                      <span>年付优惠：相当于每月¥36，节省¥60/年</span>
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* 联系方式 */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2">姓名 *</label>
                <input
                  type="text"
                  value={contactInfo.name}
                  onChange={(e) => setContactInfo({ ...contactInfo, name: e.target.value })}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2"
                  placeholder="请输入您的姓名"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">手机号 *</label>
                <input
                  type="tel"
                  value={contactInfo.phone}
                  onChange={(e) => setContactInfo({ ...contactInfo, phone: e.target.value })}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2"
                  placeholder="请输入您的手机号"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">邮箱</label>
                <input
                  type="email"
                  value={contactInfo.email}
                  onChange={(e) => setContactInfo({ ...contactInfo, email: e.target.value })}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2"
                  placeholder="请输入您的邮箱（选填）"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">备注</label>
                <textarea
                  value={remark}
                  onChange={(e) => setRemark(e.target.value)}
                  className="w-full bg-dark-card border border-white/10 rounded-lg px-4 py-2 min-h-[80px]"
                  placeholder="如有特殊需求，请在此说明（选填）"
                />
              </div>
            </div>

            {/* 支付说明 */}
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-yellow-400 mb-2">支付说明</h4>
              <p className="text-sm text-gray-300">
                {selectedPlan.name === '免费订阅' 
                  ? '提交后即可开通7天免费试用，无需支付。'
                  : '提交订单后，我们的客服将在 24 小时内与您联系，确认支付方式和开通服务。'}
              </p>
            </div>

            {/* 按钮 */}
            <div className="flex space-x-3">
              <button
                onClick={handleConfirmOrder}
                disabled={createOrderMutation.isPending}
                className="flex-1 btn-primary flex items-center justify-center space-x-2"
              >
                <span>{createOrderMutation.isPending ? '提交中...' : '确认订单'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => setSelectedPlan(null)}
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
