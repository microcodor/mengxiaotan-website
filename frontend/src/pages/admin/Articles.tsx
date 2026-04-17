import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, X, Trash2, Eye, Search, Filter, CheckSquare, Square, RefreshCw } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function AdminArticles() {
  const queryClient = useQueryClient()
  const [searchKeyword, setSearchKeyword] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [page, setPage] = useState(1)
  const perPage = 20

  const { data: articlesData, isLoading } = useQuery({
    queryKey: ['admin-articles', page, searchKeyword, filterCategory, filterStatus],
    queryFn: () => api.get('/admin/articles', {
      params: {
        page,
        per_page: perPage,
        keyword: searchKeyword || undefined,
        category: filterCategory || undefined,
        status: filterStatus || undefined,
      }
    }),
  })

  const articles = articlesData?.items || []
  const total = articlesData?.total || 0
  const totalPages = Math.ceil(total / perPage)

  const reviewMutation = useMutation({
    mutationFn: (id: number) => api.post(`/admin/articles/${id}/review`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-articles'] })
      showToast('审核成功', 'success')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/admin/articles/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-articles'] })
      setSelectedIds(prev => prev.filter(selectedId => selectedId !== id))
      showToast('删除成功', 'success')
    },
    onError: (error: any) => {
      showToast(error.response?.data?.message || '删除失败', 'error')
    }
  })

  const batchReviewMutation = useMutation({
    mutationFn: (ids: number[]) => api.post('/admin/articles/batch-review', { ids }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-articles'] })
      setSelectedIds([])
      showToast('批量审核成功', 'success')
    },
  })

  const batchDeleteMutation = useMutation({
    mutationFn: (ids: number[]) => api.post('/admin/articles/batch-delete', { ids }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-articles'] })
      setSelectedIds([])
      showToast('批量删除成功', 'success')
    },
    onError: (error: any) => {
      showToast(error.response?.data?.message || '批量删除失败', 'error')
    }
  })

  const showToast = (message: string, type: 'success' | 'error') => {
    const toast = document.createElement('div')
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in ${
      type === 'success' ? 'bg-green-500/90 text-white' : 'bg-red-500/90 text-white'
    }`
    toast.textContent = message
    document.body.appendChild(toast)
    setTimeout(() => {
      toast.classList.add('animate-fade-out')
      setTimeout(() => document.body.removeChild(toast), 300)
    }, 2000)
  }

  const handleSelectAll = () => {
    if (selectedIds.length === articles.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(articles.map((a: any) => a.id))
    }
  }

  const handleSelectOne = (id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(selectedId => selectedId !== id) : [...prev, id]
    )
  }

  const handleSearch = () => {
    setPage(1)
    queryClient.invalidateQueries({ queryKey: ['admin-articles'] })
  }

  const handleBatchReview = () => {
    if (selectedIds.length === 0) {
      showToast('请先选择文章', 'error')
      return
    }
    if (confirm(`确定要审核通过选中的 ${selectedIds.length} 篇文章吗？`)) {
      batchReviewMutation.mutate(selectedIds)
    }
  }

  const handleBatchDelete = () => {
    if (selectedIds.length === 0) {
      showToast('请先选择文章', 'error')
      return
    }
    if (confirm(`确定要删除选中的 ${selectedIds.length} 篇文章吗？此操作不可恢复！`)) {
      batchDeleteMutation.mutate(selectedIds)
    }
  }

  // 获取所有分类
  const categories = Array.from(new Set(articles.map((a: any) => a.category).filter(Boolean)))

  return (
    <div className="p-8">
      {/* 页面标题 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">文章管理</h1>
        <p className="text-gray-400">共 {total} 篇文章</p>
      </div>

      {/* 搜索和筛选 */}
      <div className="glass-card p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* 关键词搜索 */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-2">关键词搜索</label>
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="搜索标题、内容..."
                  className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
              </div>
              <button
                onClick={handleSearch}
                className="btn-primary px-4 py-2"
              >
                搜索
              </button>
            </div>
          </div>

          {/* 分类筛选 */}
          <div>
            <label className="block text-sm font-medium mb-2">分类筛选</label>
            <select
              value={filterCategory}
              onChange={(e) => { setFilterCategory(e.target.value); setPage(1) }}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            >
              <option value="">全部分类</option>
              {categories.map((cat: string) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* 状态筛选 */}
          <div>
            <label className="block text-sm font-medium mb-2">审核状态</label>
            <select
              value={filterStatus}
              onChange={(e) => { setFilterStatus(e.target.value); setPage(1) }}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            >
              <option value="">全部状态</option>
              <option value="reviewed">已审核</option>
              <option value="pending">待审核</option>
            </select>
          </div>
        </div>
      </div>

      {/* 批量操作 */}
      {selectedIds.length > 0 && (
        <div className="glass-card p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm">已选择 <span className="text-primary-400 font-semibold">{selectedIds.length}</span> 篇文章</span>
            <button
              onClick={() => setSelectedIds([])}
              className="text-sm text-gray-400 hover:text-white"
            >
              取消选择
            </button>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleBatchReview}
              disabled={batchReviewMutation.isPending}
              className="btn-primary flex items-center gap-2 px-4 py-2"
            >
              <Check className="w-4 h-4" />
              批量审核
            </button>
            <button
              onClick={handleBatchDelete}
              disabled={batchDeleteMutation.isPending}
              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              批量删除
            </button>
          </div>
        </div>
      )}

      {/* 文章列表 */}
      <div className="glass-card overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-primary-400" />
            <p className="text-gray-400">加载中...</p>
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400">暂无文章</p>
          </div>
        ) : (
          <>
            <table className="w-full">
              <thead className="bg-white/5">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <button
                      onClick={handleSelectAll}
                      className="flex items-center gap-2 hover:text-primary-400 transition-colors"
                    >
                      {selectedIds.length === articles.length ? (
                        <CheckSquare className="w-5 h-5" />
                      ) : (
                        <Square className="w-5 h-5" />
                      )}
                    </button>
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">标题</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">来源</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">分类</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">状态</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">发布时间</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {articles.map((article: any) => (
                  <tr key={article.id} className="hover:bg-white/5">
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleSelectOne(article.id)}
                        className="hover:text-primary-400 transition-colors"
                      >
                        {selectedIds.includes(article.id) ? (
                          <CheckSquare className="w-5 h-5 text-primary-400" />
                        ) : (
                          <Square className="w-5 h-5" />
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4 text-sm max-w-md">
                      <div className="truncate" title={article.title}>
                        {article.title}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">{article.source}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                        {article.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {article.is_reviewed ? (
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs flex items-center gap-1 w-fit">
                          <Check className="w-3 h-3" />
                          已审核
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs flex items-center gap-1 w-fit">
                          <X className="w-3 h-3" />
                          待审核
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">
                      {formatDate(article.published_at, 'yyyy-MM-dd HH:mm')}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">
                        <Link
                          to={`/articles/${article.id}`}
                          className="p-1.5 hover:bg-blue-500/20 rounded transition-colors"
                          title="查看详情"
                        >
                          <Eye className="w-4 h-4 text-blue-400" />
                        </Link>
                        {!article.is_reviewed && (
                          <button
                            onClick={() => reviewMutation.mutate(article.id)}
                            disabled={reviewMutation.isPending}
                            className="p-1.5 hover:bg-green-500/20 rounded transition-colors"
                            title="审核通过"
                          >
                            <Check className="w-4 h-4 text-green-400" />
                          </button>
                        )}
                        <button
                          onClick={() => {
                            if (confirm('确定要删除这篇文章吗？')) {
                              deleteMutation.mutate(article.id)
                            }
                          }}
                          disabled={deleteMutation.isPending}
                          className="p-1.5 hover:bg-red-500/20 rounded transition-colors"
                          title="删除"
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-white/10 flex items-center justify-between">
                <div className="text-sm text-gray-400">
                  第 {page} / {totalPages} 页，共 {total} 条
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                  >
                    上一页
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 bg-white/5 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                  >
                    下一页
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
