import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  Plus, Play, Trash2, Copy, TrendingUp, AlertCircle,
  Settings, BarChart3, FileText, Download, Zap, DollarSign
} from 'lucide-react'
import api from '@/lib/api'
import { useNavigate } from 'react-router-dom'

interface Scenario {
  id: number
  company_id: number
  company_name: string
  name: string
  description: string
  time_range: number
  status: string
  created_at: string
  updated_at: string
}

export default function DigitalTwin() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)

  // 获取场景列表
  const { data: scenarios, isLoading } = useQuery({
    queryKey: ['scenarios'],
    queryFn: () => api.get('/simulation/scenarios'),
  })

  // 删除场景
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/simulation/scenarios/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
    },
  })

  const handleDelete = async (id: number) => {
    if (confirm('确定要删除这个场景吗？')) {
      try {
        await deleteMutation.mutateAsync(id)
        alert('场景删除成功')
      } catch (error) {
        alert('删除失败，请稍后重试')
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400 bg-green-500/10 border-green-500/30'
      case 'running':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      case 'failed':
        return 'text-red-400 bg-red-500/10 border-red-500/30'
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'running':
        return '运行中'
      case 'failed':
        return '失败'
      case 'draft':
        return '草稿'
      default:
        return status
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">加载中...</div>
      </div>
    )
  }

  const scenarioList = scenarios?.data || []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">数字分身沙盘</h1>
          <p className="text-gray-400">模拟政策和价格变化对企业的影响</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>创建场景</span>
        </button>
      </div>

      {/* 功能介绍卡片 */}
      {scenarioList.length === 0 && (
        <div className="glass-card p-8 mb-8">
          <div className="text-center">
            <BarChart3 className="w-16 h-16 text-primary-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-4">欢迎使用数字分身沙盘</h2>
            <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
              数字分身沙盘可以帮助您模拟各种政策和价格变化对企业经营的影响，
              为战略决策提供数据支持。
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="bg-white/5 rounded-lg p-6">
                <Zap className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">政策模拟</h3>
                <p className="text-sm text-gray-400">
                  模拟碳税、补贴、配额等政策对企业的影响
                </p>
              </div>
              
              <div className="bg-white/5 rounded-lg p-6">
                <DollarSign className="w-8 h-8 text-green-400 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">价格波动</h3>
                <p className="text-sm text-gray-400">
                  分析原材料、产品、能源价格变化的影响
                </p>
              </div>
              
              <div className="bg-white/5 rounded-lg p-6">
                <TrendingUp className="w-8 h-8 text-blue-400 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">趋势预测</h3>
                <p className="text-sm text-gray-400">
                  生成1-5年的财务指标趋势预测
                </p>
              </div>
            </div>
            
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary mt-8"
            >
              创建第一个场景
            </button>
          </div>
        </div>
      )}

      {/* 场景列表 */}
      {scenarioList.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scenarioList.map((scenario: Scenario) => (
            <div key={scenario.id} className="glass-card p-6 hover:border-primary-500/50 transition-colors">
              {/* 场景头部 */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">{scenario.name}</h3>
                  <p className="text-sm text-gray-400 line-clamp-2">
                    {scenario.description || '暂无描述'}
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded border ${getStatusColor(scenario.status)}`}>
                  {getStatusText(scenario.status)}
                </span>
              </div>

              {/* 场景信息 */}
              <div className="space-y-2 mb-4 text-sm">
                <div className="flex items-center justify-between text-gray-400">
                  <span>企业</span>
                  <span className="text-gray-300">{scenario.company_name}</span>
                </div>
                <div className="flex items-center justify-between text-gray-400">
                  <span>模拟年限</span>
                  <span className="text-gray-300">{scenario.time_range}年</span>
                </div>
                <div className="flex items-center justify-between text-gray-400">
                  <span>创建时间</span>
                  <span className="text-gray-300">
                    {new Date(scenario.created_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex space-x-2">
                <button
                  onClick={() => navigate(`/dashboard/digital-twin/${scenario.id}`)}
                  className="flex-1 btn-secondary text-sm py-2 flex items-center justify-center space-x-1"
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>查看详情</span>
                </button>
                <button
                  onClick={() => handleDelete(scenario.id)}
                  className="btn-secondary text-sm py-2 px-3 text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 创建场景模态框 */}
      {showCreateModal && (
        <CreateScenarioModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            queryClient.invalidateQueries({ queryKey: ['scenarios'] })
          }}
        />
      )}
    </div>
  )
}

// 创建场景模态框组件
function CreateScenarioModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    time_range: 3,
    policies: [] as any[],
    price_changes: [] as any[],
  })

  // 获取用户信息
  const { data: userInfo } = useQuery({
    queryKey: ['userInfo'],
    queryFn: () => api.get('/users/me'),
  })

  // 获取预设模板
  const { data: templates } = useQuery({
    queryKey: ['templates'],
    queryFn: () => api.get('/simulation/templates'),
  })

  // 创建场景
  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/simulation/scenarios', data),
    onSuccess: (response) => {
      const scenarioId = response.data.scenario_id
      // 立即执行模拟
      api.post(`/simulation/scenarios/${scenarioId}/simulate`)
        .then(() => {
          onSuccess()
          navigate(`/dashboard/digital-twin/${scenarioId}`)
        })
        .catch(() => {
          onSuccess()
          navigate(`/dashboard/digital-twin/${scenarioId}`)
        })
    },
  })

  const handleSubmit = async () => {
    if (!formData.name) {
      alert('请输入场景名称')
      return
    }

    if (!userInfo?.company_id) {
      alert('请先绑定企业信息')
      return
    }

    try {
      await createMutation.mutateAsync({
        company_id: userInfo.company_id,
        ...formData,
      })
    } catch (error: any) {
      alert(error.response?.data?.message || '创建失败，请稍后重试')
    }
  }

  const useTemplate = (template: any) => {
    setFormData({
      name: template.name,
      description: template.description,
      time_range: template.config.time_range,
      policies: template.config.policies,
      price_changes: template.config.price_changes,
    })
    setStep(2)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="glass-card max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* 模态框头部 */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold">创建模拟场景</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        {/* 步骤指示器 */}
        <div className="flex items-center justify-center space-x-4 p-6 border-b border-white/10">
          <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-primary-400' : 'text-gray-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-primary-500' : 'bg-gray-700'}`}>
              1
            </div>
            <span>选择模板</span>
          </div>
          <div className="w-12 h-0.5 bg-gray-700"></div>
          <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-primary-400' : 'text-gray-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-primary-500' : 'bg-gray-700'}`}>
              2
            </div>
            <span>配置参数</span>
          </div>
          <div className="w-12 h-0.5 bg-gray-700"></div>
          <div className={`flex items-center space-x-2 ${step >= 3 ? 'text-primary-400' : 'text-gray-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-primary-500' : 'bg-gray-700'}`}>
              3
            </div>
            <span>确认创建</span>
          </div>
        </div>

        {/* 模态框内容 */}
        <div className="p-6">
          {step === 1 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">选择预设模板或从空白开始</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 空白模板 */}
                <button
                  onClick={() => setStep(2)}
                  className="text-left p-4 border border-white/10 rounded-lg hover:border-primary-500/50 transition-colors"
                >
                  <Settings className="w-8 h-8 text-gray-400 mb-2" />
                  <h4 className="font-semibold mb-1">空白场景</h4>
                  <p className="text-sm text-gray-400">从头开始配置场景参数</p>
                </button>

                {/* 预设模板 */}
                {templates?.data?.map((template: any) => (
                  <button
                    key={template.id}
                    onClick={() => useTemplate(template)}
                    className="text-left p-4 border border-white/10 rounded-lg hover:border-primary-500/50 transition-colors"
                  >
                    <FileText className="w-8 h-8 text-primary-400 mb-2" />
                    <h4 className="font-semibold mb-1">{template.name}</h4>
                    <p className="text-sm text-gray-400">{template.description}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <ScenarioConfigForm
              formData={formData}
              onChange={setFormData}
              onNext={() => setStep(3)}
              onBack={() => setStep(1)}
            />
          )}

          {step === 3 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">确认场景信息</h3>
              <div className="space-y-4 mb-6">
                <div>
                  <label className="text-sm text-gray-400">场景名称</label>
                  <p className="text-lg">{formData.name}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-400">场景描述</label>
                  <p>{formData.description || '暂无描述'}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-400">模拟年限</label>
                  <p>{formData.time_range}年</p>
                </div>
                <div>
                  <label className="text-sm text-gray-400">政策配置</label>
                  <p>{formData.policies.length}个政策</p>
                </div>
                <div>
                  <label className="text-sm text-gray-400">价格配置</label>
                  <p>{formData.price_changes.length}个价格变化</p>
                </div>
              </div>

              <div className="flex space-x-3">
                <button onClick={() => setStep(2)} className="btn-secondary flex-1">
                  返回修改
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={createMutation.isPending}
                  className="btn-primary flex-1"
                >
                  {createMutation.isPending ? '创建中...' : '创建并模拟'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// 场景配置表单组件
function ScenarioConfigForm({ formData, onChange, onNext, onBack }: any) {
  const addPolicy = () => {
    onChange({
      ...formData,
      policies: [...formData.policies, { type: 'carbon_tax', rate: 50 }],
    })
  }

  const removePolicy = (index: number) => {
    onChange({
      ...formData,
      policies: formData.policies.filter((_: any, i: number) => i !== index),
    })
  }

  const updatePolicy = (index: number, field: string, value: any) => {
    const newPolicies = [...formData.policies]
    newPolicies[index] = { ...newPolicies[index], [field]: value }
    onChange({ ...formData, policies: newPolicies })
  }

  const addPriceChange = () => {
    onChange({
      ...formData,
      price_changes: [...formData.price_changes, { type: 'raw_material', change: 10 }],
    })
  }

  const removePriceChange = (index: number) => {
    onChange({
      ...formData,
      price_changes: formData.price_changes.filter((_: any, i: number) => i !== index),
    })
  }

  const updatePriceChange = (index: number, field: string, value: any) => {
    const newPriceChanges = [...formData.price_changes]
    newPriceChanges[index] = { ...newPriceChanges[index], [field]: value }
    onChange({ ...formData, price_changes: newPriceChanges })
  }

  return (
    <div className="space-y-6">
      {/* 基本信息 */}
      <div>
        <h3 className="text-lg font-semibold mb-4">基本信息</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">场景名称 *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => onChange({ ...formData, name: e.target.value })}
              className="input-field w-full"
              placeholder="例如：碳税政策影响分析"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">场景描述</label>
            <textarea
              value={formData.description}
              onChange={(e) => onChange({ ...formData, description: e.target.value })}
              className="input-field w-full"
              rows={3}
              placeholder="描述这个场景的目的和背景"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">模拟年限</label>
            <select
              value={formData.time_range}
              onChange={(e) => onChange({ ...formData, time_range: parseInt(e.target.value) })}
              className="input-field w-full"
            >
              <option value={1}>1年</option>
              <option value={3}>3年</option>
              <option value={5}>5年</option>
            </select>
          </div>
        </div>
      </div>

      {/* 政策配置 */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">政策配置</h3>
          <button onClick={addPolicy} className="btn-secondary text-sm">
            <Plus className="w-4 h-4 inline mr-1" />
            添加政策
          </button>
        </div>
        {formData.policies.length === 0 ? (
          <p className="text-gray-400 text-sm">暂无政策配置</p>
        ) : (
          <div className="space-y-3">
            {formData.policies.map((policy: any, index: number) => (
              <div key={index} className="bg-white/5 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <select
                    value={policy.type}
                    onChange={(e) => updatePolicy(index, 'type', e.target.value)}
                    className="input-field flex-1 mr-2"
                  >
                    <option value="carbon_tax">碳税政策</option>
                    <option value="subsidy">补贴政策</option>
                    <option value="quota">配额政策</option>
                    <option value="electricity_price">电价政策</option>
                  </select>
                  <button
                    onClick={() => removePolicy(index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {policy.type === 'carbon_tax' && (
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">税率(元/吨CO2)</label>
                      <input
                        type="number"
                        value={policy.rate || 50}
                        onChange={(e) => updatePolicy(index, 'rate', parseFloat(e.target.value))}
                        className="input-field w-full"
                      />
                    </div>
                  )}
                  {policy.type === 'subsidy' && (
                    <>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">补贴类型</label>
                        <select
                          value={policy.subsidy_type || 'production'}
                          onChange={(e) => updatePolicy(index, 'subsidy_type', e.target.value)}
                          className="input-field w-full"
                        >
                          <option value="production">生产补贴</option>
                          <option value="revenue">收入补贴</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">补贴标准</label>
                        <input
                          type="number"
                          value={policy.rate || 100}
                          onChange={(e) => updatePolicy(index, 'rate', parseFloat(e.target.value))}
                          className="input-field w-full"
                        />
                      </div>
                    </>
                  )}
                  {policy.type === 'quota' && (
                    <>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">配额(吨CO2)</label>
                        <input
                          type="number"
                          value={policy.quota || 1000000}
                          onChange={(e) => updatePolicy(index, 'quota', parseFloat(e.target.value))}
                          className="input-field w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">超额惩罚(元/吨)</label>
                        <input
                          type="number"
                          value={policy.penalty_rate || 100}
                          onChange={(e) => updatePolicy(index, 'penalty_rate', parseFloat(e.target.value))}
                          className="input-field w-full"
                        />
                      </div>
                    </>
                  )}
                  {policy.type === 'electricity_price' && (
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">电价变化(%)</label>
                      <input
                        type="number"
                        value={policy.change || 10}
                        onChange={(e) => updatePolicy(index, 'change', parseFloat(e.target.value))}
                        className="input-field w-full"
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 价格配置 */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">价格配置</h3>
          <button onClick={addPriceChange} className="btn-secondary text-sm">
            <Plus className="w-4 h-4 inline mr-1" />
            添加价格
          </button>
        </div>
        {formData.price_changes.length === 0 ? (
          <p className="text-gray-400 text-sm">暂无价格配置</p>
        ) : (
          <div className="space-y-3">
            {formData.price_changes.map((price: any, index: number) => (
              <div key={index} className="bg-white/5 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <select
                    value={price.type}
                    onChange={(e) => updatePriceChange(index, 'type', e.target.value)}
                    className="input-field flex-1 mr-2"
                  >
                    <option value="product">产品价格</option>
                    <option value="raw_material">原材料价格</option>
                    <option value="energy">能源价格</option>
                  </select>
                  <button
                    onClick={() => removePriceChange(index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1">价格变化(%)</label>
                  <input
                    type="number"
                    value={price.change || 10}
                    onChange={(e) => updatePriceChange(index, 'change', parseFloat(e.target.value))}
                    className="input-field w-full"
                    placeholder="正数表示上涨，负数表示下跌"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 操作按钮 */}
      <div className="flex space-x-3 pt-4 border-t border-white/10">
        <button onClick={onBack} className="btn-secondary flex-1">
          上一步
        </button>
        <button onClick={onNext} className="btn-primary flex-1">
          下一步
        </button>
      </div>
    </div>
  )
}
