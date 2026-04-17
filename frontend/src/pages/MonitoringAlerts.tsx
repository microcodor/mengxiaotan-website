import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, AlertCircle, CheckCircle, Clock, ExternalLink, Filter } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

interface MonitoringAlert {
  id: number;
  rule_id: number;
  rule_name: string;
  title: string;
  content: string;
  level: string;
  level_display: string;
  source_type: string;
  source_id: number;
  status: string;
  status_display: string;
  sent_at: string | null;
  created_at: string;
}

interface Statistics {
  total: number;
  unread: number;
  by_level: {
    high: number;
    medium: number;
    low: number;
  };
  today: number;
}

const MonitoringAlerts: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedLevel, setSelectedLevel] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<MonitoringAlert | null>(null);

  // 获取统计信息
  const { data: statistics } = useQuery<Statistics>({
    queryKey: ['alert-statistics'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/monitoring/alerts/statistics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  // 获取预警列表
  const { data: alertsData, isLoading } = useQuery({
    queryKey: ['monitoring-alerts', selectedLevel, selectedStatus],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (selectedLevel) params.append('level', selectedLevel);
      if (selectedStatus) params.append('status', selectedStatus);
      
      const response = await axios.get(
        `${API_BASE_URL}/monitoring/alerts?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    }
  });

  // 标记为已读
  const markReadMutation = useMutation({
    mutationFn: async (id: number) => {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/monitoring/alerts/${id}/read`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring-alerts'] });
      queryClient.invalidateQueries({ queryKey: ['alert-statistics'] });
    }
  });

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getLevelBadgeColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleAlertClick = (alert: MonitoringAlert) => {
    setSelectedAlert(alert);
    if (alert.status === 'pending') {
      markReadMutation.mutate(alert.id);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) {
      const minutes = Math.floor(diff / (1000 * 60));
      return `${minutes}分钟前`;
    } else if (hours < 24) {
      return `${hours}小时前`;
    } else {
      return date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  const alerts = alertsData?.alerts || [];

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">预警中心</h1>
        <p className="mt-2 text-gray-600">
          查看和管理所有监测预警信息
        </p>
      </div>

      {/* 统计卡片 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">总预警数</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{statistics.total}</p>
              </div>
              <Bell className="w-8 h-8 text-gray-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">未读预警</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">{statistics.unread}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-orange-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">今日预警</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">{statistics.today}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">高级预警</p>
                <p className="text-2xl font-bold text-red-600 mt-1">{statistics.by_level.high}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
          </div>
        </div>
      )}

      {/* 筛选栏 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">预警等级：</span>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部</option>
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">状态：</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部</option>
              <option value="pending">未读</option>
              <option value="read">已读</option>
            </select>
          </div>

          {(selectedLevel || selectedStatus) && (
            <button
              onClick={() => {
                setSelectedLevel('');
                setSelectedStatus('');
              }}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              清除筛选
            </button>
          )}
        </div>
      </div>

      {/* 预警列表 */}
      {alerts.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">暂无预警信息</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert: MonitoringAlert) => (
            <div
              key={alert.id}
              onClick={() => handleAlertClick(alert)}
              className={`bg-white rounded-lg border p-4 cursor-pointer hover:shadow-md transition-shadow ${
                alert.status === 'pending' ? 'border-l-4' : ''
              } ${getLevelColor(alert.level)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* 标题和等级 */}
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${getLevelBadgeColor(alert.level)}`}>
                      {alert.level_display}
                    </span>
                    {alert.status === 'pending' && (
                      <span className="px-2 py-0.5 bg-orange-100 text-orange-800 text-xs font-medium rounded">
                        未读
                      </span>
                    )}
                    <span className="text-xs text-gray-500">{formatDate(alert.created_at)}</span>
                  </div>

                  {/* 预警标题 */}
                  <h3 className="font-semibold text-gray-900 mb-2">{alert.title}</h3>

                  {/* 预警内容预览 */}
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {alert.content.split('\n')[0]}
                  </p>

                  {/* 规则名称 */}
                  <div className="mt-2 text-xs text-gray-500">
                    触发规则：{alert.rule_name}
                  </div>
                </div>

                {/* 状态图标 */}
                <div className="ml-4">
                  {alert.status === 'read' ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-orange-500" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 预警详情模态框 */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {/* 头部 */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getLevelBadgeColor(selectedAlert.level)}`}>
                    {selectedAlert.level_display}预警
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(selectedAlert.created_at).toLocaleString('zh-CN')}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-gray-900">{selectedAlert.title}</h2>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* 规则信息 */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">
                <span className="font-medium">触发规则：</span>
                {selectedAlert.rule_name}
              </div>
            </div>

            {/* 预警内容 */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">预警详情</h3>
              <div className="text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg">
                {selectedAlert.content}
              </div>
            </div>

            {/* 来源链接 */}
            {selectedAlert.source_type === 'article' && selectedAlert.source_id && (
              <div className="mb-6">
                <a
                  href={`/articles/${selectedAlert.source_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700"
                >
                  <ExternalLink className="w-4 h-4" />
                  查看相关文章
                </a>
              </div>
            )}

            {/* 关闭按钮 */}
            <div className="flex justify-end">
              <button
                onClick={() => setSelectedAlert(null)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MonitoringAlerts;
