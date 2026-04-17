import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Eye } from 'lucide-react';
import api from '../../lib/api';

interface Company {
  id: number;
  name: string;
  unified_social_credit_code: string;
  contact_person: string;
  contact_phone: string;
  industry_category: string;
  is_verified: boolean;
  status: string;
  creator_name: string;
  created_at: string;
}

export default function Companies() {
  const [loading, setLoading] = useState(true);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(20);
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedCompany, setSelectedCompany] = useState<any>(null);
  const [showDetail, setShowDetail] = useState(false);

  useEffect(() => {
    loadCompanies();
  }, [page, statusFilter]);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const params: any = { page, per_page: perPage };
      if (statusFilter) params.status = statusFilter;
      
      const response = await api.get('/company/admin/list', { params });
      setCompanies(response.items || []);
      setTotal(response.total || 0);
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (companyId: number, approved: boolean) => {
    if (!confirm(`确定要${approved ? '通过' : '拒绝'}该企业的认证吗？`)) return;
    
    try {
      await api.post(`/company/admin/${companyId}/verify`, { approved });
      alert(approved ? '认证通过' : '认证已拒绝');
      loadCompanies();
      if (showDetail && selectedCompany?.id === companyId) {
        setShowDetail(false);
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    }
  };

  const handleViewDetail = async (companyId: number) => {
    try {
      const response = await api.get(`/company/admin/${companyId}`);
      setSelectedCompany(response.company);
      setShowDetail(true);
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    }
  };

  const getStatusBadge = (status: string, isVerified: boolean) => {
    if (isVerified) {
      return <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">已认证</span>;
    }
    if (status === 'pending') {
      return <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded">待审核</span>;
    }
    if (status === 'inactive') {
      return <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">未通过</span>;
    }
    return <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded">未认证</span>;
  };

  const totalPages = Math.ceil(total / perPage);

  if (loading && companies.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">企业管理</h1>

      {/* 筛选器 */}
      <div className="glass-card p-4 mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium">状态筛选：</label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
          >
            <option value="">全部</option>
            <option value="pending">待审核</option>
            <option value="active">已认证</option>
            <option value="inactive">未通过</option>
          </select>
          <div className="flex-1"></div>
          <div className="text-sm text-gray-400">
            共 {total} 家企业
          </div>
        </div>
      </div>

      {/* 企业列表 */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  企业名称
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  信用代码
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  联系人
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  联系电话
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  行业
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  状态
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  创建时间
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {companies.map((company) => (
                <tr key={company.id} className="hover:bg-white/5">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">{company.name}</div>
                    {company.creator_name && (
                      <div className="text-xs text-gray-400">创建人: {company.creator_name}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {company.unified_social_credit_code || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {company.contact_person}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {company.contact_phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {company.industry_category || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(company.status, company.is_verified)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {new Date(company.created_at).toLocaleDateString('zh-CN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewDetail(company.id)}
                        className="text-primary-400 hover:text-primary-300"
                        title="查看详情"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                      {!company.is_verified && company.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleVerify(company.id, true)}
                            className="text-green-400 hover:text-green-300"
                            title="通过认证"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleVerify(company.id, false)}
                            className="text-red-400 hover:text-red-300"
                            title="拒绝认证"
                          >
                            <XCircle className="w-5 h-5" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 分页 */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-white/5 flex items-center justify-between">
            <div className="text-sm text-gray-400">
              第 {page} 页，共 {totalPages} 页
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-white/5 rounded-lg hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 bg-white/5 rounded-lg hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 详情弹窗 */}
      {showDetail && selectedCompany && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-card max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold">{selectedCompany.name}</h2>
                <button
                  onClick={() => setShowDetail(false)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-3">基础信息</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">企业简称：</span>
                      <span>{selectedCompany.short_name || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">信用代码：</span>
                      <span>{selectedCompany.unified_social_credit_code || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">法定代表人：</span>
                      <span>{selectedCompany.legal_representative || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">注册资本：</span>
                      <span>{selectedCompany.registered_capital || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">成立日期：</span>
                      <span>{selectedCompany.establishment_date || '-'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">员工人数：</span>
                      <span>{selectedCompany.employee_count || '-'}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">联系信息</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">联系人：</span>
                      <span>{selectedCompany.contact_person}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">联系电话：</span>
                      <span>{selectedCompany.contact_phone}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">联系邮箱：</span>
                      <span>{selectedCompany.contact_email || '-'}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">地址信息</h3>
                  <div className="text-sm">
                    <span className="text-gray-400">地址：</span>
                    <span>
                      {[selectedCompany.province, selectedCompany.city, selectedCompany.district, selectedCompany.address]
                        .filter(Boolean)
                        .join(' ') || '-'}
                    </span>
                  </div>
                </div>

                {selectedCompany.description && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3">企业简介</h3>
                    <p className="text-sm text-gray-300">{selectedCompany.description}</p>
                  </div>
                )}

                {!selectedCompany.is_verified && selectedCompany.status === 'pending' && (
                  <div className="flex justify-end space-x-4 pt-4 border-t border-white/10">
                    <button
                      onClick={() => handleVerify(selectedCompany.id, false)}
                      className="px-6 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                    >
                      拒绝认证
                    </button>
                    <button
                      onClick={() => handleVerify(selectedCompany.id, true)}
                      className="px-6 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors"
                    >
                      通过认证
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
