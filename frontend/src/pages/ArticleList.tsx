import { useQuery } from '@tanstack/react-query'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { TrendingUp, Zap, Flame, Wind, BarChart3, Folder } from 'lucide-react'
import api from '@/lib/api'
import { formatDate, getCategoryName } from '@/lib/utils'

export default function ArticleList() {
  const { category } = useParams()
  const [searchParams] = useSearchParams()
  const page = parseInt(searchParams.get('page') || '1')

  const { data, isLoading } = useQuery({
    queryKey: ['articles', { category, page }],
    queryFn: () => api.get('/articles', { params: { category, page, per_page: 20 } }),
  })

  // 加载分类列表
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get('/categories'),
  })

  // 图标映射
  const iconMap: any = {
    government: TrendingUp,
    energy: Zap,
    power: Zap,
    coal: Flame,
    renewable: Wind,
    carbon: Wind,
    steel: BarChart3,
    metal: BarChart3,
    default: Folder
  }

  // 颜色映射
  const colorMap: any = {
    government: 'from-blue-500 to-cyan-500',
    energy: 'from-yellow-500 to-orange-500',
    power: 'from-yellow-500 to-orange-500',
    coal: 'from-orange-500 to-red-500',
    renewable: 'from-green-500 to-emerald-500',
    carbon: 'from-green-500 to-teal-500',
    steel: 'from-gray-500 to-slate-600',
    metal: 'from-purple-500 to-indigo-500',
    default: 'from-gray-500 to-gray-600'
  }

  // 动态生成分类列表
  const categories = categoriesData?.items?.map((cat: any) => ({
    name: cat.name,
    code: cat.code,
    icon: iconMap[cat.icon] || iconMap.default,
    path: `/category/${cat.code}`,
    color: colorMap[cat.icon] || colorMap.default,
    count: cat.article_count
  })) || []

  if (isLoading) {
    return <div className="max-w-7xl mx-auto px-4 py-8">加载中...</div>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 分类导航 */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">分类导航</h2>
        <div className="flex flex-wrap gap-3">
          <Link
            to="/articles"
            className={`px-4 py-2 rounded-lg transition-all ${
              !category
                ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/50'
                : 'glass-card hover:bg-primary-500/10'
            }`}
          >
            全部
          </Link>
          {categories.map((cat) => (
            <Link
              key={cat.code}
              to={cat.path}
              className={`px-4 py-2 rounded-lg transition-all ${
                category === cat.code
                  ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/50'
                  : 'glass-card hover:bg-primary-500/10'
              }`}
            >
              {cat.name}
              {cat.count > 0 && (
                <span className="ml-2 text-sm opacity-75">({cat.count})</span>
              )}
            </Link>
          ))}
        </div>
      </div>

      {/* 文章列表标题 */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">
          {category ? getCategoryName(category) : '全部文章'}
        </h1>
        <div className="text-gray-400">
          共 {data?.total || 0} 篇文章
        </div>
      </div>

      {/* 文章列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.items?.map((article: any) => (
          <Link
            key={article.id}
            to={`/articles/${article.id}`}
            className="glass-card-hover p-6 group"
          >
            <div className="flex items-start justify-between mb-3">
              <span className="px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm">
                {article.category_name || getCategoryName(article.category)}
              </span>
              <span className="text-gray-400 text-sm">{formatDate(article.published_at, 'MM-dd')}</span>
            </div>
            <h3 className="text-lg font-semibold mb-2 group-hover:text-primary-400 transition-colors line-clamp-2">
              {article.title}
            </h3>
            <p className="text-gray-400 text-sm line-clamp-3">{article.summary}</p>
            <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
              <span>{article.source}</span>
              <span>{article.view_count} 阅读</span>
            </div>
          </Link>
        ))}
      </div>

      {/* 分页 */}
      {data && data.pages > 1 && (
        <div className="mt-8 flex justify-center gap-2">
          {Array.from({ length: data.pages }, (_, i) => i + 1).map((p) => (
            <Link
              key={p}
              to={category ? `/category/${category}?page=${p}` : `/articles?page=${p}`}
              className={`px-4 py-2 rounded-lg transition-all ${
                p === page
                  ? 'bg-primary-500 text-white'
                  : 'glass-card hover:bg-primary-500/10'
              }`}
            >
              {p}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
