import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Trash2, Power, PowerOff, AlertTriangle, TrendingUp, FileText } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

interface MonitoringRule {
  id: number;
  name: string;
  type: string;
  type_display: string;
  keywords: string[];
  threshold: number | null;
  level: string;
  level_display: string;
  channels: string[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

const Monitoring: React.FC = () => {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingRule, setEditingRule] = useState<MonitoringRule | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'policy',
    keywords: '',
    threshold: '',
    level: 'medium',
    channels: ['system']
  });

  // 获取规则列表
  const { data: rulesData, isLoading } = useQuery({
    queryKey: ['monitoring-rules'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/monitoring/rules`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  // 创建规则
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_BASE_URL}/monitoring/rules`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      setShowCreateModal(false);
      resetForm();
    }
  });

  // 更新规则
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      const token = localStorage.getItem('token');
      const response = await axios.put(`${API_BASE_URL}/monitoring/rules/${id}`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
      setEditingRule(null);
      resetForm();
    }
  });

  // 删除规则
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_BASE_URL}/monitoring/rules/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
    }
  });

  // 启用/禁用规则
  const toggleMutation = useMutation({
    mutationFn: async ({ id, enabled }: { id: number; enabled: boolean }) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/monitoring/rules/${id}/toggle`,
        { enabled },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-rules'] });
    }
  });

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'policy',
      keywords: '',
      threshold: '',
      level: 'medium',
      channels: ['system']
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const submitData = {
      name: formData.name,
      type: formData.type,
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k),
      threshold: formData.threshold ? parseFloat(formData.threshold) : null,
      level: formData.level,
      channels: formData.channels
    };

    if (editingRule) {
      updateMutation.mutate({ id: editingRule.id, data: submitData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleEdit = (rule: MonitoringRule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      type: rule.type,
      keywords: rule.keywords.join(', '),
      threshold: rule.threshold?.toString() || '',
      level: rule.level,
      channels: rule.channels
    });
    setShowCreateModal(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('确定要删除这个监测规则吗？')) {
      deleteMutation.mutate(id);
    }
  };

  const handleToggle = (id: number, enabled: boolean) => {
    toggleMutation.mutate({ id, enabled: !enabled });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'policy':
        return <FileText className="w-5 h-5" />;
      case 'price':
        return <TrendingUp className="w-5 h-5" />;
      case 'industry':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-red-600 bg-red-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  const rules = rulesData?.rules || [];

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">动态监测预警</h1>
        <p className="mt-2 text-gray-600">
          配置监测规则，实时监测政策变化、价格波动和行业动态
        </p>
      </div>

      {/* 操作栏 */}
      <div className="mb-6 flex justify-between items-center">
        <div className="text-sm text-gray-600">
          共 {rules.length} 条规则，其中 {rules.filter((r: MonitoringRule) => r.enabled).length} 条已启用
        </div>
        <button
          onClick={() => {
            setEditingRule(null);
            resetForm();
            setShowCreateModal(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          创建规则
        </button>
      </div>

      {/* 规则列表 */}
      {rules.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">还没有创建任何监测规则</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            创建第一条规则
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rules.map((rule: MonitoringRule) => (
            <div
              key={rule.id}
              className={`bg-white rounded-lg border p-4 ${
                rule.enabled ? 'border-gray-200' : 'border-gray-100 opacity-60'
              }`}
            >
              {/* 规则头部 */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="text-blue-600">{getTypeIcon(rule.type)}</div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{rule.name}</h3>
                    <p className="text-xs text-gray-500">{rule.type_display}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleToggle(rule.id, rule.enabled)}
                  className={`p-1 rounded ${
                    rule.enabled ? 'text-green-600 hover:bg-green-50' : 'text-gray-400 hover:bg-gray-50'
                  }`}
                  title={rule.enabled ? '点击禁用' : '点击启用'}
                >
                  {rule.enabled ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
                </button>
              </div>

              {/* 预警等级 */}
              <div className="mb-3">
                <span className={`inline-block px-2 py-1 text-xs font-medium rounded ${getLevelColor(rule.level)}`}>
                  {rule.level_display}预警
                </span>
              </div>

              {/* 关键词 */}
              <div className="mb-3">
                <div className="text-xs text-gray-500 mb-1">监测关键词：</div>
                <div className="flex flex-wrap gap-1">
                  {rule.keywords.slice(0, 3).map((keyword, index) => (
                    <span key={index} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                      {keyword}
                    </span>
                  ))}
                  {rule.keywords.length > 3 && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded">
                      +{rule.keywords.length - 3}
                    </span>
                  )}
                </div>
              </div>

              {/* 阈值 */}
              {rule.threshold && (
                <div className="mb-3 text-xs text-gray-600">
                  预警阈值：±{rule.threshold}%
                </div>
              )}

              {/* 操作按钮 */}
              <div className="flex gap-2 pt-3 border-t border-gray-100">
                <button
                  onClick={() => handleEdit(rule)}
                  className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded"
                >
                  <Edit2 className="w-3 h-3" />
                  编辑
                </button>
                <button
                  onClick={() => handleDelete(rule.id)}
                  className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded"
                >
                  <Trash2 className="w-3 h-3" />
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 创建/编辑规则模态框 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingRule ? '编辑监测规则' : '创建监测规则'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* 规则名称 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  规则名称 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="例如：煤炭价格预警"
                  required
                />
              </div>

              {/* 监测类型 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  监测类型 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="policy">政策监测</option>
                  <option value="price">价格监测</option>
                  <option value="industry">行业动态</option>
                </select>
              </div>

              {/* 关键词 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  监测关键词 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.keywords}
                  onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="多个关键词用逗号分隔，例如：煤炭,动力煤"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">
                  多个关键词用逗号分隔
                </p>
              </div>

              {/* 预警阈值 */}
              {formData.type === 'price' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    预警阈值（%）
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.threshold}
                    onChange={(e) => setFormData({ ...formData, threshold: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="例如：10"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    价格波动超过此百分比时触发预警
                  </p>
                </div>
              )}

              {/* 预警等级 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  预警等级 <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.level}
                  onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="high">高（立即推送）</option>
                  <option value="medium">中（汇总推送）</option>
                  <option value="low">低（每日推送）</option>
                </select>
              </div>

              {/* 按钮 */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingRule(null);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {createMutation.isPending || updateMutation.isPending ? '保存中...' : '保存'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Monitoring;
