import { useState, useEffect } from 'react';
import { User, Save } from 'lucide-react';
import api from '../lib/api';

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [formData, setFormData] = useState({
    nickname: '',
    position: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users/profile');
      setUser(response);
      setFormData({
        nickname: response.nickname || '',
        position: response.position || ''
      });
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      await api.put('/users/profile', formData);
      alert('个人信息更新成功');
      loadProfile();
    } catch (error: any) {
      alert(error.response?.data?.message || '更新失败');
    } finally {
      setSaving(false);
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
      <h1 className="text-3xl font-bold mb-8">个人信息</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 用户头像 */}
        <div className="glass-card p-6">
          <div className="flex flex-col items-center">
            <div className="w-32 h-32 bg-gradient-to-br from-primary-500 to-tech-cyan rounded-full flex items-center justify-center mb-4">
              <User className="w-16 h-16 text-white" />
            </div>
            <h2 className="text-xl font-bold">{user?.nickname || '未设置昵称'}</h2>
            <p className="text-gray-400 mt-1">{user?.phone}</p>
            <div className="mt-4 px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm">
              {user?.role === 'admin' ? '管理员' : user?.role === 'editor' ? '编辑' : '普通用户'}
            </div>
          </div>
        </div>

        {/* 个人信息表单 */}
        <div className="lg:col-span-2 glass-card p-6">
          <h3 className="text-xl font-bold mb-6">基本信息</h3>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">手机号</label>
              <input
                type="text"
                value={user?.phone || ''}
                disabled
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-gray-400 cursor-not-allowed"
              />
              <p className="text-xs text-gray-500 mt-1">手机号不可修改</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">昵称</label>
              <input
                type="text"
                value={formData.nickname}
                onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="请输入昵称"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">职位</label>
              <input
                type="text"
                value={formData.position}
                onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                placeholder="请输入职位，例如：总经理、技术总监"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">注册时间</label>
              <input
                type="text"
                value={user?.created_at ? new Date(user.created_at).toLocaleString('zh-CN') : ''}
                disabled
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-gray-400 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">最后登录</label>
              <input
                type="text"
                value={user?.last_login ? new Date(user.last_login).toLocaleString('zh-CN') : '从未登录'}
                disabled
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-gray-400 cursor-not-allowed"
              />
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className="flex items-center space-x-2 px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-5 h-5" />
                <span>{saving ? '保存中...' : '保存修改'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
