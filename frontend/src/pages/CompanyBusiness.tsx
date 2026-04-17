import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Star } from 'lucide-react';
import api from '../lib/api';

interface Business {
  id: number;
  business_type: string;
  business_name: string;
  business_scope: string;
  annual_output: string;
  market_share: string;
  service_area: string;
  core_products: string[];
  certifications: string[];
  sort_order: number;
  is_primary: boolean;
  is_active: boolean;
}

interface Options {
  business_types: Record<string, { name: string; subtypes: string[] }>;
}

export default function CompanyBusiness() {
  const [loading, setLoading] = useState(true);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [options, setOptions] = useState<Options | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    business_type: '',
    business_name: '',
    business_scope: '',
    annual_output: '',
    market_share: '',
    service_area: '',
    core_products: [] as string[],
    certifications: [] as string[],
    is_primary: false,
    is_active: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [businessesRes, optionsRes] = await Promise.all([
        api.get('/company/my/businesses'),
        api.get('/company/options')
      ]);
      setBusinesses(businessesRes.items || []);
      setOptions(optionsRes);
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingId) {
        await api.put(`/company/my/businesses/${editingId}`, formData);
        alert('业务更新成功');
      } else {
        await api.post('/company/my/businesses', formData);
        alert('业务创建成功');
      }
      setShowForm(false);
      setEditingId(null);
      resetForm();
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    }
  };

  const handleEdit = (business: Business) => {
    setEditingId(business.id);
    setFormData({
      business_type: business.business_type,
      business_name: business.business_name,
      business_scope: business.business_scope || '',
      annual_output: business.annual_output || '',
      market_share: business.market_share || '',
      service_area: business.service_area || '',
      core_products: business.core_products || [],
      certifications: business.certifications || [],
      is_primary: business.is_primary,
      is_active: business.is_active
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个业务吗？')) return;
    
    try {
      await api.delete(`/company/my/businesses/${id}`);
      alert('业务删除成功');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '删除失败');
    }
  };

  const handleSetPrimary = async (id: number) => {
    try {
      await api.post(`/company/my/businesses/${id}/set-primary`);
      alert('已设置为主营业务');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    }
  };

  const resetForm = () => {
    setFormData({
      business_type: '',
      business_name: '',
      business_scope: '',
      annual_output: '',
      market_share: '',
      service_area: '',
      core_products: [],
      certifications: [],
      is_primary: false,
      is_active: true
    });
  };

  const handleAddProduct = () => {
    const product = prompt('请输入核心产品名称：');
    if (product) {
      setFormData({ ...formData, core_products: [...formData.core_products, product] });
    }
  };

  const handleRemoveProduct = (index: number) => {
    setFormData({
      ...formData,
      core_products: formData.core_products.filter((_, i) => i !== index)
    });
  };

  const handleAddCertification = () => {
    const cert = prompt('请输入资质认证名称：');
    if (cert) {
      setFormData({ ...formData, certifications: [...formData.certifications, cert] });
    }
  };

  const handleRemoveCertification = (index: number) => {
    setFormData({
      ...formData,
      certifications: formData.certifications.filter((_, i) => i !== index)
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">主营业务管理</h1>
        <button
          onClick={() => {
            resetForm();
            setEditingId(null);
            setShowForm(true);
          }}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>添加业务</span>
        </button>
      </div>

      {/* 业务列表 */}
      {!showForm && (
        <div className="space-y-4">
          {businesses.length === 0 ? (
            <div className="glass-card p-8 text-center text-gray-400">
              暂无业务信息，点击"添加业务"开始添加
            </div>
          ) : (
            businesses.map((business) => (
              <div key={business.id} className="glass-card p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-xl font-semibold">{business.business_name}</h3>
                    {business.is_primary && (
                      <span className="px-2 py-1 bg-primary-500/20 text-primary-400 text-xs rounded">
                        主营业务
                      </span>
                    )}
                    {!business.is_active && (
                      <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded">
                        已停用
                      </span>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    {!business.is_primary && (
                      <button
                        onClick={() => handleSetPrimary(business.id)}
                        className="p-2 text-yellow-400 hover:bg-yellow-400/10 rounded-lg transition-colors"
                        title="设为主营"
                      >
                        <Star className="w-5 h-5" />
                      </button>
                    )}
                    <button
                      onClick={() => handleEdit(business)}
                      className="p-2 text-primary-400 hover:bg-primary-400/10 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(business.id)}
                      className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">业务类型：</span>
                    <span className="text-gray-200">
                      {options?.business_types[business.business_type]?.name || business.business_type}
                    </span>
                  </div>
                  {business.annual_output && (
                    <div>
                      <span className="text-gray-400">年产量/产能：</span>
                      <span className="text-gray-200">{business.annual_output}</span>
                    </div>
                  )}
                  {business.market_share && (
                    <div>
                      <span className="text-gray-400">市场份额：</span>
                      <span className="text-gray-200">{business.market_share}</span>
                    </div>
                  )}
                  {business.service_area && (
                    <div>
                      <span className="text-gray-400">服务区域：</span>
                      <span className="text-gray-200">{business.service_area}</span>
                    </div>
                  )}
                </div>

                {business.business_scope && (
                  <div className="mt-4">
                    <span className="text-gray-400">业务范围：</span>
                    <p className="text-gray-200 mt-1">{business.business_scope}</p>
                  </div>
                )}

                {business.core_products && business.core_products.length > 0 && (
                  <div className="mt-4">
                    <span className="text-gray-400">核心产品：</span>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {business.core_products.map((product, index) => (
                        <span key={index} className="px-3 py-1 bg-white/5 rounded-full text-sm">
                          {product}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {business.certifications && business.certifications.length > 0 && (
                  <div className="mt-4">
                    <span className="text-gray-400">资质认证：</span>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {business.certifications.map((cert, index) => (
                        <span key={index} className="px-3 py-1 bg-primary-500/10 text-primary-400 rounded-full text-sm">
                          {cert}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* 业务表单 */}
      {showForm && (
        <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">{editingId ? '编辑业务' : '添加业务'}</h2>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setEditingId(null);
                resetForm();
              }}
              className="text-gray-400 hover:text-white"
            >
              取消
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">业务类型 *</label>
              <select
                value={formData.business_type}
                onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                required
              >
                <option value="">请选择</option>
                {options && Object.entries(options.business_types).map(([code, type]) => (
                  <option key={code} value={code}>{type.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">业务名称 *</label>
              <input
                type="text"
                value={formData.business_name}
                onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">年产量/产能</label>
              <input
                type="text"
                value={formData.annual_output}
                onChange={(e) => setFormData({ ...formData, annual_output: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="例如: 年产煤炭500万吨"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">市场份额</label>
              <input
                type="text"
                value={formData.market_share}
                onChange={(e) => setFormData({ ...formData, market_share: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="例如: 区域市场占有率15%"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">服务区域</label>
              <input
                type="text"
                value={formData.service_area}
                onChange={(e) => setFormData({ ...formData, service_area: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="例如: 华北地区、全国"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">业务范围描述</label>
            <textarea
              value={formData.business_scope}
              onChange={(e) => setFormData({ ...formData, business_scope: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              rows={3}
              placeholder="请描述业务范围..."
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium">核心产品</label>
              <button
                type="button"
                onClick={handleAddProduct}
                className="text-sm text-primary-400 hover:text-primary-300"
              >
                + 添加产品
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.core_products.map((product, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-white/5 rounded-full text-sm flex items-center space-x-2"
                >
                  <span>{product}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveProduct(index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium">资质认证</label>
              <button
                type="button"
                onClick={handleAddCertification}
                className="text-sm text-primary-400 hover:text-primary-300"
              >
                + 添加认证
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.certifications.map((cert, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-500/10 text-primary-400 rounded-full text-sm flex items-center space-x-2"
                >
                  <span>{cert}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveCertification(index)}
                    className="text-red-400 hover:text-red-300"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.is_primary}
                onChange={(e) => setFormData({ ...formData, is_primary: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-sm">设为主营业务</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-sm">启用</span>
            </label>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setEditingId(null);
                resetForm();
              }}
              className="px-6 py-2 bg-white/5 text-white rounded-lg hover:bg-white/10 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              {editingId ? '更新' : '创建'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
