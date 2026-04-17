import { useState, useEffect } from 'react';
import api from '../../lib/api';

interface Category {
  id: number;
  code: string;
  name: string;
  description: string;
  sort_order: number;
  is_active: boolean;
  article_count: number;
  created_at: string;
  updated_at: string;
}

export default function Categories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    sort_order: 0,
    is_active: true
  });

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const response = await api.get('/categories?include_inactive=true');
      setCategories(response.items);
    } catch (error: any) {
      alert(error.response?.data?.message || '加载分类失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingCategory(null);
    setFormData({
      code: '',
      name: '',
      description: '',
      sort_order: 0,
      is_active: true
    });
    setShowModal(true);
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setFormData({
      code: category.code,
      name: category.name,
      description: category.description || '',
      sort_order: category.sort_order,
      is_active: category.is_active
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingCategory) {
        await api.put(`/categories/${editingCategory.id}`, formData);
        alert('分类更新成功');
      } else {
        await api.post('/categories', formData);
        alert('分类创建成功');
      }
      setShowModal(false);
      loadCategories();
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    }
  };

  const handleDelete = async (category: Category) => {
    if (!confirm(`确定要删除分类"${category.name}"吗？`)) {
      return;
    }

    try {
      await api.delete(`/categories/${category.id}`);
      alert('分类删除成功');
      loadCategories();
    } catch (error: any) {
      alert(error.response?.data?.message || '删除失败');
    }
  };

  const handleToggleActive = async (category: Category) => {
    try {
      await api.put(`/categories/${category.id}`, {
        is_active: !category.is_active
      });
      alert(category.is_active ? '已禁用' : '已启用');
      loadCategories();
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
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">分类管理</h1>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          + 新建分类
        </button>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold">排序</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">代码</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">名称</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">描述</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">文章数</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">状态</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {categories.map((category) => (
              <tr key={category.id} className="hover:bg-white/5">
                <td className="px-6 py-4 text-sm">{category.sort_order}</td>
                <td className="px-6 py-4 text-sm">
                  <code className="px-2 py-1 bg-white/5 rounded text-primary-400">
                    {category.code}
                  </code>
                </td>
                <td className="px-6 py-4 text-sm font-medium">{category.name}</td>
                <td className="px-6 py-4 text-sm text-gray-400 max-w-xs truncate">
                  {category.description}
                </td>
                <td className="px-6 py-4 text-sm">
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                    {category.article_count}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    category.is_active 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {category.is_active ? '启用' : '禁用'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => handleEdit(category)}
                      className="text-primary-400 hover:text-primary-300 transition-colors"
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleToggleActive(category)}
                      className="text-yellow-400 hover:text-yellow-300 transition-colors"
                    >
                      {category.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      onClick={() => handleDelete(category)}
                      className={`transition-colors ${
                        category.article_count > 0
                          ? 'text-gray-600 cursor-not-allowed'
                          : 'text-red-400 hover:text-red-300'
                      }`}
                      disabled={category.article_count > 0}
                      title={category.article_count > 0 ? '该分类下还有文章，无法删除' : '删除分类'}
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 创建/编辑模态框 */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-6">
              {editingCategory ? '编辑分类' : '新建分类'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">分类代码 *</label>
                  <input
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                    required
                    disabled={!!editingCategory}
                    placeholder="例如: steel, chemical"
                  />
                  {editingCategory && (
                    <p className="text-xs text-gray-500 mt-1">分类代码不可修改</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">分类名称 *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                    required
                    placeholder="例如: 钢铁、化工"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">描述</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                    rows={3}
                    placeholder="分类描述"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">排序</label>
                  <input
                    type="number"
                    value={formData.sort_order}
                    onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
                    placeholder="数字越小越靠前"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="mr-2 w-4 h-4"
                    id="is_active"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium cursor-pointer">
                    启用该分类
                  </label>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  {editingCategory ? '更新' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
