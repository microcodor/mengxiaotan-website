import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Clock, CheckCircle, XCircle, User, Upload, Calendar, Filter, Search } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

interface ReportRequest {
  id: number;
  user_id: number;
  company_id: number;
  company_name: string;
  user_name: string;
  report_type: string;
  report_type_display: string;
  title: string;
  description: string;
  expected_delivery_date: string | null;
  additional_notes: string | null;
  status: string;
  status_display: string;
  assigned_to: number | null;
  assigned_to_name: string | null;
  assigned_at: string | null;
  completed_at: string | null;
  rejected_reason: string | null;
  created_at: string;
  updated_at: string;
  files: any[];
}

interface Statistics {
  total: number;
  by_status: {
    pending: number;
    assigned: number;
    in_progress: number;
    completed: number;
    rejected: number;
  };
}

const AdminReports: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedRequest, setSelectedRequest] = useState<ReportRequest | null>(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [assignToUserId, setAssignToUserId] = useState<string>('');
  const [rejectReason, setRejectReason] = useState<string>('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  // 获取统计信息
  const { data: statistics } = useQuery<Statistics>({
    queryKey: ['admin-report-statistics'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/reports/admin/statistics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  });

  // 获取报告列表
  const { data: requestsData, isLoading } = useQuery({
    queryKey: ['admin-reports', selectedStatus, searchQuery],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (selectedStatus) params.append('status', selectedStatus);
      if (searchQuery) params.append('search', searchQuery);
      
      const response = await axios.get(
        `${API_BASE_URL}/reports/admin/requests?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    }
  });

  // 分配报告
  const assignMutation = useMutation({
    mutationFn: async ({ requestId, userId }: { requestId: number; userId: number }) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/reports/admin/requests/${requestId}/assign`,
        { assigned_to: userId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-reports'] });
      queryClient.invalidateQueries({ queryKey: ['admin-report-statistics'] });
      setShowAssignModal(false);
      setSelectedRequest(null);
      setAssignToUserId('');
    }
  });

  // 更新状态
  const updateStatusMutation = useMutation({
    mutationFn: async ({ requestId, status, reason }: { requestId: number; status: string; reason?: string }) => {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `${API_BASE_URL}/reports/admin/requests/${requestId}/status`,
        { status, rejected_reason: reason },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-reports'] });
      queryClient.invalidateQueries({ queryKey: ['admin-report-statistics'] });
      setShowRejectModal(false);
      setSelectedRequest(null);
      setRejectReason('');
    }
  });

  // 上传文件
  const uploadMutation = useMutation({
    mutationFn: async ({ requestId, file }: { requestId: number; file: File }) => {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(
        `${API_BASE_URL}/reports/admin/requests/${requestId}/upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-reports'] });
      setShowUploadModal(false);
      setSelectedRequest(null);
      setUploadFile(null);
    }
  });

  const handleAssign = () => {
    if (selectedRequest && assignToUserId) {
      assignMutation.mutate({
        requestId: selectedRequest.id,
        userId: parseInt(assignToUserId)
      });
    }
  };

  const handleReject = () => {
    if (selectedRequest && rejectReason) {
      updateStatusMutation.mutate({
        requestId: selectedRequest.id,
        status: 'rejected',
        reason: rejectReason
      });
    }
  };

  const handleUpload = () => {
    if (selectedRequest && uploadFile) {
      uploadMutation.mutate({
        requestId: selectedRequest.id,
        file: uploadFile
      });
    }
  };

  const handleStatusChange = (requestId: number, status: string) => {
    updateStatusMutation.mutate({ requestId, status });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'assigned':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-purple-100 text-purple-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'assigned':
      case 'in_progress':
        return <User className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'rejected':
        return <XCircle className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  const requests = requestsData?.requests || [];

  return (
    <div className="p-6">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">定制报告管理</h1>
        <p className="mt-2 text-gray-600">
          管理用户的定制报告申请，分配任务和上传报告
        </p>
      </div>

      {/* 统计卡片 */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">总申请数</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{statistics.total}</p>
              </div>
              <FileText className="w-8 h-8 text-gray-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">待处理</p>
                <p className="text-2xl font-bold text-yellow-600 mt-1">{statistics.by_status.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">已分配</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">{statistics.by_status.assigned}</p>
              </div>
              <User className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">进行中</p>
                <p className="text-2xl font-bold text-purple-600 mt-1">{statistics.by_status.in_progress}</p>
              </div>
              <User className="w-8 h-8 text-purple-400" />
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">已完成</p>
                <p className="text-2xl font-bold text-green-600 mt-1">{statistics.by_status.completed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
          </div>
        </div>
      )}

      {/* 筛选和搜索 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">状态：</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部</option>
              <option value="pending">待处理</option>
              <option value="assigned">已分配</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
              <option value="rejected">已拒绝</option>
            </select>
          </div>

          <div className="flex-1 flex items-center gap-2">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索企业名称或报告标题..."
              className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {(selectedStatus || searchQuery) && (
            <button
              onClick={() => {
                setSelectedStatus('');
                setSearchQuery('');
              }}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              清除筛选
            </button>
          )}
        </div>
      </div>

      {/* 报告列表 */}
      {requests.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">暂无报告申请</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  申请信息
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  企业/用户
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  分配情况
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  申请时间
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {requests.map((request: ReportRequest) => (
                <tr key={request.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{request.title}</div>
                      <div className="text-sm text-gray-500">{request.report_type_display}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm text-gray-900">{request.company_name}</div>
                      <div className="text-sm text-gray-500">{request.user_name}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded ${getStatusColor(request.status)}`}>
                      {getStatusIcon(request.status)}
                      {request.status_display}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {request.assigned_to_name || '未分配'}
                    </div>
                    {request.assigned_at && (
                      <div className="text-xs text-gray-500">
                        {formatDate(request.assigned_at)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(request.created_at)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {request.status === 'pending' && (
                        <>
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setShowAssignModal(true);
                            }}
                            className="text-sm text-blue-600 hover:text-blue-700"
                          >
                            分配
                          </button>
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setShowRejectModal(true);
                            }}
                            className="text-sm text-red-600 hover:text-red-700"
                          >
                            拒绝
                          </button>
                        </>
                      )}
                      {request.status === 'assigned' && (
                        <button
                          onClick={() => handleStatusChange(request.id, 'in_progress')}
                          className="text-sm text-purple-600 hover:text-purple-700"
                        >
                          开始编写
                        </button>
                      )}
                      {request.status === 'in_progress' && (
                        <button
                          onClick={() => {
                            setSelectedRequest(request);
                            setShowUploadModal(true);
                          }}
                          className="text-sm text-green-600 hover:text-green-700"
                        >
                          上传报告
                        </button>
                      )}
                      <button
                        onClick={() => window.open(`/dashboard/reports/${request.id}`, '_blank')}
                        className="text-sm text-gray-600 hover:text-gray-700"
                      >
                        查看详情
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 分配模态框 */}
      {showAssignModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">分配报告</h2>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">报告标题：</p>
              <p className="font-medium">{selectedRequest.title}</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                分配给用户ID <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={assignToUserId}
                onChange={(e) => setAssignToUserId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="输入用户ID"
              />
              <p className="mt-1 text-xs text-gray-500">
                请输入负责编写报告的用户ID
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowAssignModal(false);
                  setSelectedRequest(null);
                  setAssignToUserId('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={handleAssign}
                disabled={!assignToUserId || assignMutation.isPending}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {assignMutation.isPending ? '分配中...' : '确认分配'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 拒绝模态框 */}
      {showRejectModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">拒绝申请</h2>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">报告标题：</p>
              <p className="font-medium">{selectedRequest.title}</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                拒绝原因 <span className="text-red-500">*</span>
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="请说明拒绝原因..."
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setSelectedRequest(null);
                  setRejectReason('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={handleReject}
                disabled={!rejectReason || updateStatusMutation.isPending}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {updateStatusMutation.isPending ? '处理中...' : '确认拒绝'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 上传模态框 */}
      {showUploadModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">上传报告</h2>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">报告标题：</p>
              <p className="font-medium">{selectedRequest.title}</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                选择文件 <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                accept=".pdf,.doc,.docx"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-xs text-gray-500">
                支持PDF、Word格式，最大10MB
              </p>
            </div>

            {uploadFile && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-700">{uploadFile.name}</span>
                  <span className="text-xs text-gray-500">
                    ({(uploadFile.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setSelectedRequest(null);
                  setUploadFile(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={handleUpload}
                disabled={!uploadFile || uploadMutation.isPending}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {uploadMutation.isPending ? '上传中...' : '确认上传'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminReports;
