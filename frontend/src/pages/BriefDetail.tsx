import { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { Calendar, Share2, Eye, TrendingUp, Zap, AlertCircle, ExternalLink } from 'lucide-react'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'

interface BriefContent {
  ai_summary: string
  content: {
    ndrc?: Array<{ title: string; summary: string; url: string; source: string; published_at: string }>
    coal?: Array<{ title: string; summary: string; url: string; source: string; published_at: string }>
    power?: Array<{ title: string; summary: string; url: string; source: string; published_at: string }>
    new_energy?: Array<{ title: string; summary: string; url: string; source: string; published_at: string }>
  }
  generated_at: string
  article_count: number
}

interface Brief {
  id: number
  brief_date: string
  content: BriefContent
  ai_suggestion?: string
  generated_at: string
  share_url: string
  view_count: number
  share_count: number
}

export default function BriefDetail() {
  const { shareToken } = useParams<{ shareToken: string }>()
  const [searchParams] = useSearchParams()
  const version = searchParams.get('v') || 'standard'
  
  const [brief, setBrief] = useState<Brief | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadBrief()
  }, [shareToken])

  const loadBrief = async () => {
    try {
      setLoading(true)
      const data = await api.get(`/briefs/${shareToken}?v=${version}`)
      setBrief(data)
    } catch (err: any) {
      setError(err.response?.data?.message || '加载简报失败')
    } finally {
      setLoading(false)
    }
  }

  const handleShare = async () => {
    try {
      await api.post(`/briefs/${shareToken}/share`)
      if (brief) {
        setBrief({ ...brief, share_count: brief.share_count + 1 })
      }
      
      // 复制链接到剪贴板
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(window.location.href)
        alert('链接已复制到剪贴板')
      }
    } catch (err) {
      console.error('分享失败:', err)
    }
  }

  const categoryNames: Record<string, { name: string; icon: string; color: string }> = {
    ndrc: { name: '发改委动态', icon: '📋', color: 'from-blue-500 to-cyan-500' },
    coal: { name: '煤炭行业', icon: '⚫', color: 'from-gray-600 to-gray-700' },
    power: { name: '电力行业', icon: '⚡', color: 'from-yellow-500 to-orange-500' },
    new_energy: { name: '新能源', icon: '🌱', color: 'from-green-500 to-emerald-500' }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-400">加载中...</p>
        </div>
      </div>
    )
  }

  if (error || !brief) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="glass-card p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">加载失败</h2>
          <p className="text-gray-400 mb-6">{error || '简报不存在'}</p>
          <a href="/" className="btn-primary inline-block">返回首页</a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* 头部 */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">蒙小碳·每日简报</h1>
                <p className="text-primary-100 text-sm">
                  {version === 'premium' ? '高级版' : '标准版'}
                </p>
              </div>
            </div>
            <button
              onClick={handleShare}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              <Share2 className="w-4 h-4" />
              分享
            </button>
          </div>
          
          <div className="flex items-center gap-6 text-sm text-primary-100">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              {formatDate(brief.brief_date, 'yyyy年MM月dd日')}
            </div>
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4" />
              {brief.view_count} 次浏览
            </div>
            <div className="flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              {brief.share_count} 次分享
            </div>
          </div>
        </div>
      </div>

      {/* 内容 */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* AI概览 */}
        {brief.content.ai_summary && (
          <div className="glass-card p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-primary-400" />
              <h2 className="text-xl font-bold">今日概览</h2>
            </div>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
              {brief.content.ai_summary}
            </p>
          </div>
        )}

        {/* AI决策建议（仅高级版） */}
        {brief.ai_suggestion && version === 'premium' && (
          <div className="glass-card p-6 mb-6 border-2 border-primary-500/30">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">💡 决策建议</h2>
                <p className="text-xs text-primary-400">高级版专享</p>
              </div>
            </div>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
              {brief.ai_suggestion}
            </p>
          </div>
        )}

        {/* 分类文章 */}
        {Object.entries(categoryNames).map(([key, config]) => {
          const articles = brief.content.content[key as keyof typeof brief.content.content]
          if (!articles || articles.length === 0) return null

          return (
            <div key={key} className="glass-card p-6 mb-6">
              <div className="flex items-center gap-2 mb-4">
                <div className={`w-10 h-10 bg-gradient-to-br ${config.color} rounded-lg flex items-center justify-center text-2xl`}>
                  {config.icon}
                </div>
                <h2 className="text-xl font-bold">{config.name}</h2>
                <span className="text-sm text-gray-400">({articles.length}篇)</span>
              </div>
              
              <div className="space-y-4">
                {articles.map((article, index) => (
                  <div key={index} className="border-l-2 border-primary-500/30 pl-4 hover:border-primary-500 transition-colors">
                    <h3 className="font-semibold text-gray-200 mb-1">{article.title}</h3>
                    {article.summary && (
                      <p className="text-sm text-gray-400 mb-2">{article.summary}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>{article.source}</span>
                      {article.published_at && (
                        <span>{formatDate(article.published_at, 'MM-dd HH:mm')}</span>
                      )}
                      {article.url && (
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-primary-400 hover:text-primary-300"
                        >
                          查看详情 <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}

        {/* 页脚 */}
        <div className="text-center text-sm text-gray-500 mt-8">
          <p>生成时间: {formatDate(brief.generated_at, 'yyyy-MM-dd HH:mm:ss')}</p>
          <p className="mt-2">共收录 {brief.content.article_count} 篇文章</p>
          <p className="mt-4">
            <a href="/" className="text-primary-400 hover:text-primary-300">
              访问蒙小碳·能源站
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
