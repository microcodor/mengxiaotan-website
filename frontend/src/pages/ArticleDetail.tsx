import { useQuery } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { Calendar, Eye, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import api from '@/lib/api'
import { formatDate, getCategoryName } from '@/lib/utils'

export default function ArticleDetail() {
  const { id } = useParams()

  const { data: article, isLoading } = useQuery({
    queryKey: ['article', id],
    queryFn: () => api.get(`/articles/${id}`),
  })

  if (isLoading) {
    return <div className="max-w-4xl mx-auto px-4 py-8">加载中...</div>
  }

  if (!article) {
    return <div className="max-w-4xl mx-auto px-4 py-8">文章不存在</div>
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <article className="glass-card p-8">
        {/* 文章头部 */}
        <div className="mb-6">
          <span className="px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm">
            {article.category_name || getCategoryName(article.category)}
          </span>
        </div>

        <h1 className="text-4xl font-bold mb-6">{article.title}</h1>

        {/* 元信息 */}
        <div className="flex flex-wrap items-center gap-6 text-gray-400 text-sm mb-8 pb-8 border-b border-white/10">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(article.published_at)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Eye className="w-4 h-4" />
            <span>{article.view_count} 阅读</span>
          </div>
          <div>来源: {article.source}</div>
          {article.source_url && (
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-primary-400 hover:text-primary-300"
            >
              <span>原文链接</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>

        {/* 摘要 */}
        {article.summary && (
          <div className="bg-primary-500/10 border-l-4 border-primary-500 p-6 mb-8">
            <p className="text-lg text-gray-200">{article.summary}</p>
          </div>
        )}

        {/* 正文 */}
        <div className="prose prose-invert prose-lg max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // 自定义段落样式
              p: ({ children }) => (
                <p className="mb-6 leading-relaxed text-gray-200">{children}</p>
              ),
              // 自定义标题样式
              h1: ({ children }) => (
                <h1 className="text-3xl font-bold mt-8 mb-4 text-white">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-2xl font-bold mt-8 mb-4 text-white">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-xl font-bold mt-6 mb-3 text-white">{children}</h3>
              ),
              h4: ({ children }) => (
                <h4 className="text-lg font-bold mt-6 mb-3 text-white">{children}</h4>
              ),
              // 自定义列表样式
              ul: ({ children }) => (
                <ul className="list-disc list-inside mb-6 space-y-2 text-gray-200">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside mb-6 space-y-2 text-gray-200">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="ml-4">{children}</li>
              ),
              // 自定义引用样式
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-primary-500 pl-6 py-2 my-6 bg-primary-500/10 text-gray-200 italic">
                  {children}
                </blockquote>
              ),
              // 自定义代码块样式
              code: ({ inline, children, ...props }: any) => {
                return inline ? (
                  <code className="px-2 py-1 bg-white/10 text-primary-400 rounded text-sm font-mono" {...props}>
                    {children}
                  </code>
                ) : (
                  <code className="block p-4 bg-black/30 text-gray-200 rounded-lg overflow-x-auto text-sm font-mono my-4" {...props}>
                    {children}
                  </code>
                )
              },
              // 自定义表格样式
              table: ({ children }) => (
                <div className="overflow-x-auto my-6">
                  <table className="min-w-full divide-y divide-white/10">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-white/5">{children}</thead>
              ),
              tbody: ({ children }) => (
                <tbody className="divide-y divide-white/10">{children}</tbody>
              ),
              tr: ({ children }) => (
                <tr className="hover:bg-white/5 transition-colors">{children}</tr>
              ),
              th: ({ children }) => (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-6 py-4 text-sm text-gray-200">{children}</td>
              ),
              // 自定义链接样式 - 移除链接功能,只显示文本
              a: ({ children }) => (
                <span className="text-gray-200">{children}</span>
              ),
              // 自定义图片样式 - 移除图片
              img: () => null,
              // 自定义水平线样式
              hr: () => (
                <hr className="my-8 border-white/10" />
              ),
              // 自定义强调样式
              strong: ({ children }) => (
                <strong className="font-bold text-white">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-gray-200">{children}</em>
              ),
            }}
          >
            {article.content}
          </ReactMarkdown>
        </div>

        {/* 标签 */}
        {article.tags && article.tags.length > 0 && (
          <div className="mt-8 pt-8 border-t border-white/10">
            <div className="flex flex-wrap gap-2">
              {article.tags.map((tag: string) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-white/5 text-gray-300 rounded-full text-sm"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </article>
    </div>
  )
}
