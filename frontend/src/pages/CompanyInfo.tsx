import { useState, useEffect } from 'react';
import api from '../lib/api';

interface CompanyData {
  name: string;
  short_name: string;
  unified_social_credit_code: string;
  legal_representative: string;
  registered_capital: string;
  establishment_date: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  province: string;
  city: string;
  district: string;
  address: string;
  employee_count: string;
  annual_revenue: string;
  industry: string;
  industry_category: string;
  description: string;
  website: string;
}

export default function CompanyInfo() {
  const [loading, setLoading] = useState(true);
  const [hasCompany, setHasCompany] = useState(false);
  const [options, setOptions] = useState<any>(null);
  const [formData, setFormData] = useState<CompanyData>({
    name: '',
    short_name: '',
    unified_social_credit_code: '',
    legal_representative: '',
    registered_capital: '',
    establishment_date: '',
    contact_person: '',
    contact_phone: '',
    contact_email: '',
    province: '',
    city: '',
    district: '',
    address: '',
    employee_count: '',
    annual_revenue: '',
    industry: '',
    industry_category: '',
    description: '',
    website: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 加载选项数据
      const optionsRes = await api.get('/company/options');
      setOptions(optionsRes);
      
      // 加载企业信息
      const companyRes = await api.get('/company/my');
      if (companyRes.company) {
        setHasCompany(true);
        setFormData({
          name: companyRes.company.name || '',
          short_name: companyRes.company.short_name || '',
          unified_social_credit_code: companyRes.company.unified_social_credit_code || '',
          legal_representative: companyRes.company.legal_representative || '',
          registered_capital: companyRes.company.registered_capital || '',
          establishment_date: companyRes.company.establishment_date || '',
          contact_person: companyRes.company.contact_person || '',
          contact_phone: companyRes.company.contact_phone || '',
          contact_email: companyRes.company.contact_email || '',
          province: companyRes.company.province || '',
          city: companyRes.company.city || '',
          district: companyRes.company.district || '',
          address: companyRes.company.address || '',
          employee_count: companyRes.company.employee_count || '',
          annual_revenue: companyRes.company.annual_revenue || '',
          industry: companyRes.company.industry || '',
          industry_category: companyRes.company.industry_category || '',
          description: companyRes.company.description || '',
          website: companyRes.company.website || ''
        });
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (hasCompany) {
        await api.put('/company/my', formData);
        alert('企业信息更新成功');
      } else {
        await api.post('/company/my', formData);
        alert('企业信息创建成功');
        setHasCompany(true);
      }
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    }
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
      <h1 className="text-3xl font-bold mb-8">企业信息</h1>

      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-6">
        {/* 基础信息 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">基础信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">企业名称 *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">企业简称</label>
              <input
                type="text"
                value={formData.short_name}
                onChange={(e) => setFormData({ ...formData, short_name: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">统一社会信用代码</label>
              <input
                type="text"
                value={formData.unified_social_credit_code}
                onChange={(e) => setFormData({ ...formData, unified_social_credit_code: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">法定代表人</label>
              <input
                type="text"
                value={formData.legal_representative}
                onChange={(e) => setFormData({ ...formData, legal_representative: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">注册资本</label>
              <input
                type="text"
                value={formData.registered_capital}
                onChange={(e) => setFormData({ ...formData, registered_capital: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="例如: 1000万元"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">成立日期</label>
              <input
                type="date"
                value={formData.establishment_date}
                onChange={(e) => setFormData({ ...formData, establishment_date: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
          </div>
        </div>

        {/* 联系信息 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">联系信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">联系人 *</label>
              <input
                type="text"
                value={formData.contact_person}
                onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">联系电话 *</label>
              <input
                type="tel"
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">联系邮箱</label>
              <input
                type="email"
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
          </div>
        </div>

        {/* 地址信息 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">地址信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">省份</label>
              <input
                type="text"
                value={formData.province}
                onChange={(e) => setFormData({ ...formData, province: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">城市</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">区县</label>
              <input
                type="text"
                value={formData.district}
                onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">详细地址</label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
            />
          </div>
        </div>

        {/* 企业规模 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">企业规模</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">员工人数</label>
              <select
                value={formData.employee_count}
                onChange={(e) => setFormData({ ...formData, employee_count: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              >
                <option value="">请选择</option>
                {options?.employee_count_options?.map((opt: string) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">年营业额</label>
              <select
                value={formData.annual_revenue}
                onChange={(e) => setFormData({ ...formData, annual_revenue: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              >
                <option value="">请选择</option>
                {options?.annual_revenue_options?.map((opt: string) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 行业信息 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">行业信息</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">所属行业</label>
              <input
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="例如: 煤炭开采和洗选业"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">行业类别</label>
              <select
                value={formData.industry_category}
                onChange={(e) => setFormData({ ...formData, industry_category: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
              >
                <option value="">请选择</option>
                {options?.industry_categories?.map((cat: any) => (
                  <option key={cat.code} value={cat.code}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 企业简介 */}
        <div>
          <h2 className="text-xl font-semibold mb-4">企业简介</h2>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
            rows={4}
            placeholder="请输入企业简介..."
          />
        </div>

        {/* 企业网站 */}
        <div>
          <label className="block text-sm font-medium mb-2">企业网站</label>
          <input
            type="url"
            value={formData.website}
            onChange={(e) => setFormData({ ...formData, website: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
            placeholder="https://www.example.com"
          />
        </div>

        {/* 提交按钮 */}
        <div className="flex justify-end space-x-4">
          <button
            type="submit"
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            {hasCompany ? '更新信息' : '创建企业'}
          </button>
        </div>
      </form>
    </div>
  );
}
