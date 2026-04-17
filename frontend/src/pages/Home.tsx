import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { TrendingUp, Zap, Flame, Wind, ArrowRight, BarChart3, Folder } from 'lucide-react'
import api from '@/lib/api'
import { formatDate, getCategoryName } from '@/lib/utils'

export default function Home() {
  const { data: carouselArticles } = useQuery({
    queryKey: ['carousel'],
    queryFn: () => api.get('/articles/carousel'),
  })

  const { data: topArticles } = useQuery({
    queryKey: ['top'],
    queryFn: () => api.get('/articles/top'),
  })

  const { data: articlesData } = useQuery({
    queryKey: ['articles', { page: 1 }],
    queryFn: () => api.get('/articles', { params: { page: 1, per_page: 12 } }),
  })

  const { data: dailyBrief } = useQuery({
    queryKey: ['daily-brief'],
    queryFn: () => api.get('/articles/daily-brief'),
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

  // 动态生成分类列表（取前8个）
  const categories = categoriesData?.items?.slice(0, 8).map((cat: any) => ({
    name: cat.name,
    code: cat.code,
    icon: iconMap[cat.icon] || iconMap.default,
    path: `/category/${cat.code}`,
    color: colorMap[cat.icon] || colorMap.default,
    count: cat.article_count
  })) || []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 焦点轮播区 */}
      {carouselArticles && carouselArticles.length > 0 && (
        <section className="mb-12">
          <div className="glass-card p-8 neon-border">
            <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-tech-cyan bg-clip-text text-transparent">
              焦点资讯
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {carouselArticles.slice(0, 4).map((article: any) => (
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
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-primary-400 transition-colors line-clamp-2">
                    {article.title}
                  </h3>
                  <p className="text-gray-400 text-sm line-clamp-2">{article.summary}</p>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* 蒙小碳今日建议 */}
      <section className="mb-12">
        <div className="glass-card p-6 border-2 border-tech-green/50 animate-glow">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-tech-cyan rounded-full flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-primary-400">蒙小碳·今日一句话建议</h3>
              <p className="text-gray-400 text-sm">AI 智能分析 · 每日更新</p>
            </div>
          </div>
          <p className="text-lg text-gray-200 leading-relaxed">
            {dailyBrief?.ai_suggestion || '根据最新政策和市场动态，建议关注发改委近期发布的煤炭保供政策，预计短期内煤价将保持稳定。新能源领域，光伏装机量持续增长，建议关注相关产业链投资机会。'}
          </p>
        </div>
      </section>

      {/* 快捷入口 */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">快捷入口</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-4">
          {/* 资讯入口 */}
          <Link
            to="/articles"
            className="glass-card-hover p-6 text-center group"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform">
              <Folder className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold group-hover:text-primary-400 transition-colors">
              资讯中心
            </h3>
            <p className="text-sm text-gray-400 mt-1">查看全部资讯</p>
          </Link>

          {/* 数据看板入口 */}
          <Link
            to="/dashboard"
            className="glass-card-hover p-6 text-center group"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-indigo-500 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold group-hover:text-primary-400 transition-colors">
              数据看板
            </h3>
            <p className="text-sm text-gray-400 mt-1">查看数据分析</p>
          </Link>

          {/* 订阅服务入口 */}
          <Link
            to="/subscription"
            className="glass-card-hover p-6 text-center group"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold group-hover:text-primary-400 transition-colors">
              订阅服务
            </h3>
            <p className="text-sm text-gray-400 mt-1">开通会员服务</p>
          </Link>

          {/* 企业信息入口 */}
          <Link
            to="/dashboard/company"
            className="glass-card-hover p-6 text-center group"
          >
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center transform group-hover:scale-110 transition-transform">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-semibold group-hover:text-primary-400 transition-colors">
              企业信息
            </h3>
            <p className="text-sm text-gray-400 mt-1">管理企业资料</p>
          </Link>
        </div>
      </section>

      {/* 最新资讯 */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">最新资讯</h2>
          <Link to="/articles" className="flex items-center space-x-2 text-primary-400 hover:text-primary-300">
            <span>查看更多</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articlesData?.items?.map((article: any) => (
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
      </section>
    </div>
  )
}
