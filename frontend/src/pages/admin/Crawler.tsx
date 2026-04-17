import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Square, RefreshCw, Activity, Clock, CheckCircle, XCircle, AlertCircle, Zap, TrendingUp } from 'lucide-react'
import api from '@/lib/api'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function AdminCrawler() {
  const [selectedTab, setSelectedTab] = useState<'spiders' | 'logs' | 'stats' | 'progress' | 'schedule'>('spiders')
  const [showProgress, setShowProgress] = useState(false)
  const queryClient = useQueryClient()

  const { data: spidersData, isLoading: spidersLoading } = useQuery({
    queryKey: ['spiders'],
    queryFn: () => api.get('/crawler/spiders'),
    refetchInterval: (data) => {
      // 如果有爬虫正在运行，2秒刷新一次；否则10秒
      const hasRunning = data?.items?.some((s: any) => s.status === 'running')
      return hasRunning ? 2000 : 10000
    },
  })

  const { data: logsData, isLoading: logsLoading } = useQuery({
    queryKey: ['crawler-logs'],
    queryFn: () => api.get('/crawler/logs'),
    enabled: selectedTab === 'logs',
  })

  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['crawler-stats'],
    queryFn: () => api.get('/crawler/stats'),
    enabled: selectedTab === 'stats',
  })

  // 定时任务查询
  const { data: scheduleData, isLoading: scheduleLoading } = useQuery({
    queryKey: ['crawler-schedule'],
    queryFn: () => api.get('/crawler/schedule'),
    enabled: selectedTab === 'schedule',
    refetchInterval: 5000, // 每5秒刷新一次
  })

  // 实时进度查询
  const { data: progressData, isLoading: progressLoading } = useQuery({
    queryKey: ['crawler-progress'],
    queryFn: () => api.get('/crawler/progress'),
    refetchInterval: 2000, // 每2秒刷新一次
    enabled: showProgress || selectedTab === 'progress',
  })

  // 自动显示/隐藏进度面板
  useEffect(() => {
    const hasRunning = spidersData?.items?.some((s: any) => s.status === 'running')
    if (hasRunning && !showProgress && selectedTab === 'spiders') {
      setShowProgress(true)
    } else if (!hasRunning && showProgress) {
      // 延迟5秒后隐藏
      const timer = setTimeout(() => setShowProgress(false), 5000)
      return () => clearTimeout(timer)
    }
  }, [spidersData, showProgress, selectedTab])

  const runMutation = useMutation({
    mutationFn: (spiderName: string) => api.post(`/crawler/spiders/${spiderName}/run`),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['spiders'] })
      queryClient.invalidateQueries({ queryKey: ['crawler-logs'] })
      setShowProgress(true) // 显示进度面板
      // 使用简单的toast提示
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-green-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = '✅ 爬虫已启动'
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 2000)
    },
    onError: (error: any) => {
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-red-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = `❌ ${error.response?.data?.message || '启动失败'}`
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 3000)
    },
  })

  const stopMutation = useMutation({
    mutationFn: (spiderName: string) => api.post(`/crawler/spiders/${spiderName}/stop`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spiders'] })
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-blue-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = '⏹️ 爬虫已停止'
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 2000)
    },
    onError: (error: any) => {
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-red-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = `❌ ${error.response?.data?.message || '停止失败'}`
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 3000)
    },
  })

  // 一键运行所有爬虫
  const runAllMutation = useMutation({
    mutationFn: () => api.post('/crawler/spiders/run-all'),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['spiders'] })
      queryClient.invalidateQueries({ queryKey: ['crawler-logs'] })
      setShowProgress(true) // 显示进度面板
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-green-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.innerHTML = `
        <div class="font-semibold mb-1">🚀 批量启动成功</div>
        <div class="text-sm">
          ✅ 已启动: ${data.started_count} 个<br/>
          ${data.running_count > 0 ? `⏳ 运行中: ${data.running_count} 个<br/>` : ''}
          ${data.failed_count > 0 ? `❌ 失败: ${data.failed_count} 个` : ''}
        </div>
      `
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 4000)
    },
    onError: (error: any) => {
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-red-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = `❌ ${error.response?.data?.message || '批量启动失败'}`
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 3000)
    },
  })

  // 暂停定时任务
  const pauseJobMutation = useMutation({
    mutationFn: (jobId: string) => api.post(`/crawler/schedule/${jobId}/pause`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['crawler-schedule'] })
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-blue-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = '⏸️ 任务已暂停'
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 2000)
    },
  })

  // 恢复定时任务
  const resumeJobMutation = useMutation({
    mutationFn: (jobId: string) => api.post(`/crawler/schedule/${jobId}/resume`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['crawler-schedule'] })
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-green-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = '▶️ 任务已恢复'
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 2000)
    },
  })

  // 立即触发定时任务
  const triggerJobMutation = useMutation({
    mutationFn: (jobId: string) => api.post(`/crawler/schedule/${jobId}/trigger`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['crawler-schedule'] })
      const toast = document.createElement('div')
      toast.className = 'fixed top-4 right-4 bg-green-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in'
      toast.textContent = '⚡ 任务已触发'
      document.body.appendChild(toast)
      setTimeout(() => {
        toast.classList.add('animate-fade-out')
        setTimeout(() => document.body.removeChild(toast), 300)
      }, 2000)
    },
  })

  const spiders = spidersData?.items || []
  const logs = logsData?.items || []
  const stats = statsData || {}
  const progressItems = progressData?.items || []
  const scheduleJobs = scheduleData?.items || []

  const getStatusBadge = (status: string) => {
    const badges = {
      active: { text: '正常', class: 'bg-green-500/20 text-green-400', icon: CheckCircle },
      running: { text: '运行中', class: 'bg-blue-500/20 text-blue-400', icon: Activity },
      error: { text: '错误', class: 'bg-red-500/20 text-red-400', icon: XCircle },
      disabled: { text: '已禁用', class: 'bg-gray-500/20 text-gray-400', icon: Square },
    }
    const badge = badges[status as keyof typeof badges] || badges.active
    const Icon = badge.icon
    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm ${badge.class}`}>
        <Icon className="w-4 h-4" />
        <span>{badge.text}</span>
      </span>
    )
  }

  const getLogStatusBadge = (status: string) => {
    const badges = {
      success: { text: '成功', class: 'bg-green-500/20 text-green-400', icon: CheckCircle },
      running: { text: '运行中', class: 'bg-blue-500/20 text-blue-400', icon: Activity },
      failed: { text: '失败', class: 'bg-red-500/20 text-red-400', icon: XCircle },
    }
    const badge = badges[status as keyof typeof badges] || badges.running
    const Icon = badge.icon
    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded text-xs ${badge.class}`}>
        <Icon className="w-3 h-3" />
        <span>{badge.text}</span>
      </span>
    )
  }

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(0)}秒`
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}分钟`
    return `${(seconds / 3600).toFixed(1)}小时`
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold">爬虫管理</h1>
          
          {/* 一键爬取按钮 */}
          <button
            onClick={() => runAllMutation.mutate()}
            disabled={runAllMutation.isPending}
            className="btn-primary flex items-center space-x-2 px-6 py-3 text-lg"
          >
            <Zap className="w-5 h-5" />
            <span>{runAllMutation.isPending ? '启动中...' : '🚀 一键爬取所有平台'}</span>
          </button>
        </div>

        {/* 标签页 */}
        <div className="flex space-x-2">
          {[
            { value: 'spiders', label: '爬虫列表' },
            { value: 'schedule', label: '定时任务' },
            { value: 'logs', label: '爬取日志' },
            { value: 'stats', label: '统计信息' },
            { value: 'progress', label: `实时进度 ${progressItems.length > 0 ? `(${progressItems.length})` : ''}` },
          ].map((tab) => (
            <button
              key={tab.value}
              onClick={() => setSelectedTab(tab.value as any)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedTab === tab.value
                  ? 'bg-primary-500 text-white'
                  : 'glass-card hover:bg-white/10'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 实时进度浮动面板 */}
      {showProgress && progressItems.length > 0 && selectedTab === 'spiders' && (
        <div className="fixed bottom-4 right-4 w-96 glass-card p-4 shadow-2xl z-40 animate-slide-up">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-primary-400 animate-pulse" />
              <h3 className="font-semibold">实时进度</h3>
              <span className="text-xs text-gray-400">({progressItems.length} 个运行中)</span>
            </div>
            <button
              onClick={() => setShowProgress(false)}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {progressItems.map((item: any) => (
              <div key={item.spider_name} className="bg-white/5 rounded p-3 text-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-primary-400">{item.display_name}</span>
                  <span className="text-xs text-gray-400">{formatDuration(item.duration)}</span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>📄 {item.items_scraped} 篇</span>
                  <span>🔗 {item.requests_count} 请求</span>
                </div>
                {item.last_log_line && (
                  <div className="mt-1 text-xs text-gray-500 truncate">
                    {item.last_log_line}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 爬虫列表 */}
      {selectedTab === 'spiders' && (
        <div className="space-y-4">
          {spidersLoading ? (
            <div className="text-center py-8">加载中...</div>
          ) : (
            spiders.map((spider: any) => (
              <div key={spider.name} className="glass-card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-semibold">{spider.display_name}</h3>
                      {getStatusBadge(spider.status)}
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{spider.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{spider.schedule}</span>
                      </span>
                      {spider.last_crawl_at && (
                        <span>
                          最后运行: {format(new Date(spider.last_crawl_at), 'yyyy-MM-dd HH:mm', { locale: zhCN })}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => runMutation.mutate(spider.name)}
                      disabled={runMutation.isPending || spider.status === 'running'}
                      className="btn-primary flex items-center space-x-2 px-4 py-2"
                    >
                      <Play className="w-4 h-4" />
                      <span>运行</span>
                    </button>
                    {spider.status === 'running' && (
                      <button
                        onClick={() => stopMutation.mutate(spider.name)}
                        disabled={stopMutation.isPending}
                        className="btn-secondary flex items-center space-x-2 px-4 py-2"
                      >
                        <Square className="w-4 h-4" />
                        <span>停止</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* 最后执行记录 */}
                {spider.last_log && (
                  <div className="border-t border-white/10 pt-4 mt-4">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        {getLogStatusBadge(spider.last_log.status)}
                        <span className="text-gray-400">
                          抓取文章: <span className="text-primary-400">{spider.last_log.articles_count || 0}</span> 篇
                        </span>
                        {spider.last_log.started_at && (
                          <span className="text-gray-400">
                            开始: {format(new Date(spider.last_log.started_at), 'HH:mm:ss', { locale: zhCN })}
                          </span>
                        )}
                        {spider.last_log.finished_at && (
                          <span className="text-gray-400">
                            结束: {format(new Date(spider.last_log.finished_at), 'HH:mm:ss', { locale: zhCN })}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* 错误信息 */}
                {spider.error_msg && (
                  <div className="border-t border-white/10 pt-4 mt-4">
                    <div className="flex items-start space-x-2 text-sm text-red-400">
                      <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{spider.error_msg}</span>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* 爬取日志 */}
      {selectedTab === 'logs' && (
        <div className="glass-card">
          {logsLoading ? (
            <div className="text-center py-8">加载中...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-4">数据源</th>
                    <th className="text-left p-4">状态</th>
                    <th className="text-left p-4">文章数</th>
                    <th className="text-left p-4">开始时间</th>
                    <th className="text-left p-4">结束时间</th>
                    <th className="text-left p-4">耗时</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log: any) => (
                    <tr key={log.id} className="border-b border-white/10 hover:bg-white/5">
                      <td className="p-4">{log.source_name}</td>
                      <td className="p-4">{getLogStatusBadge(log.status)}</td>
                      <td className="p-4">{log.articles_count || 0}</td>
                      <td className="p-4">
                        {log.started_at ? format(new Date(log.started_at), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN }) : '-'}
                      </td>
                      <td className="p-4">
                        {log.finished_at ? format(new Date(log.finished_at), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN }) : '-'}
                      </td>
                      <td className="p-4">
                        {log.duration ? `${log.duration.toFixed(1)}s` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* 统计信息 */}
      {selectedTab === 'stats' && (
        <div className="space-y-6">
          {statsLoading ? (
            <div className="text-center py-8">加载中...</div>
          ) : (
            <>
              {/* 概览卡片 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="glass-card p-6">
                  <div className="text-sm text-gray-400 mb-1">总文章数</div>
                  <div className="text-3xl font-bold text-primary-400">{stats.total_articles || 0}</div>
                </div>
                <div className="glass-card p-6">
                  <div className="text-sm text-gray-400 mb-1">今日抓取</div>
                  <div className="text-3xl font-bold text-green-400">{stats.today_articles || 0}</div>
                </div>
                <div className="glass-card p-6">
                  <div className="text-sm text-gray-400 mb-1">活跃爬虫</div>
                  <div className="text-3xl font-bold text-blue-400">{stats.spider_stats?.active || 0}</div>
                </div>
                <div className="glass-card p-6">
                  <div className="text-sm text-gray-400 mb-1">错误爬虫</div>
                  <div className="text-3xl font-bold text-red-400">{stats.spider_stats?.error || 0}</div>
                </div>
              </div>

              {/* 分类统计 */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4">分类统计</h3>
                <div className="space-y-3">
                  {stats.category_stats?.map((item: any) => (
                    <div key={item.category} className="flex items-center justify-between">
                      <span className="text-gray-300">{item.category}</span>
                      <span className="text-primary-400 font-semibold">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* 来源统计 */}
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-4">来源统计</h3>
                <div className="space-y-3">
                  {stats.source_stats?.map((item: any) => (
                    <div key={item.source} className="flex items-center justify-between">
                      <span className="text-gray-300">{item.source}</span>
                      <span className="text-primary-400 font-semibold">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* 定时任务 */}
      {selectedTab === 'schedule' && (
        <div className="space-y-4">
          {scheduleLoading ? (
            <div className="text-center py-8">加载中...</div>
          ) : scheduleJobs.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <Clock className="w-16 h-16 mx-auto mb-4 text-gray-500" />
              <p className="text-gray-400 text-lg">没有定时任务</p>
            </div>
          ) : (
            <>
              <div className="glass-card p-4 bg-blue-500/10 border border-blue-500/20">
                <div className="flex items-center space-x-2 text-blue-400">
                  <Clock className="w-5 h-5" />
                  <span className="font-semibold">
                    共 {scheduleJobs.length} 个定时任务
                  </span>
                </div>
              </div>

              {scheduleJobs.map((job: any) => (
                <div key={job.id} className="glass-card p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-semibold">{job.name}</h3>
                        {job.is_paused ? (
                          <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm bg-gray-500/20 text-gray-400">
                            <Square className="w-4 h-4" />
                            <span>已暂停</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400">
                            <CheckCircle className="w-4 h-4" />
                            <span>运行中</span>
                          </span>
                        )}
                        
                        {/* 任务类型标签 */}
                        {job.type === 'crawler' && (
                          <span className="px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-400">
                            爬虫任务
                          </span>
                        )}
                        {job.type === 'ai_brief' && (
                          <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-400">
                            AI简报
                          </span>
                        )}
                        {job.type === 'subscription' && (
                          <span className="px-2 py-1 rounded text-xs bg-yellow-500/20 text-yellow-400">
                            订阅管理
                          </span>
                        )}
                      </div>
                      
                      <div className="space-y-2 text-sm text-gray-400">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">任务ID:</span>
                          <span className="font-mono text-gray-300">{job.id}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">触发器:</span>
                          <span className="text-gray-300">{job.trigger}</span>
                        </div>
                        {job.next_run_time && (
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">下次运行:</span>
                            <span className="text-primary-400 font-semibold">
                              {format(new Date(job.next_run_time), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN })}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      {job.is_paused ? (
                        <button
                          onClick={() => resumeJobMutation.mutate(job.id)}
                          disabled={resumeJobMutation.isPending}
                          className="btn-primary flex items-center space-x-2 px-4 py-2"
                          title="恢复任务"
                        >
                          <Play className="w-4 h-4" />
                          <span>恢复</span>
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => triggerJobMutation.mutate(job.id)}
                            disabled={triggerJobMutation.isPending}
                            className="btn-secondary flex items-center space-x-2 px-4 py-2"
                            title="立即执行一次"
                          >
                            <Zap className="w-4 h-4" />
                            <span>立即执行</span>
                          </button>
                          <button
                            onClick={() => pauseJobMutation.mutate(job.id)}
                            disabled={pauseJobMutation.isPending}
                            className="btn-secondary flex items-center space-x-2 px-4 py-2"
                            title="暂停任务"
                          >
                            <Square className="w-4 h-4" />
                            <span>暂停</span>
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}

      {/* 实时进度标签页 */}
      {selectedTab === 'progress' && (
        <div className="space-y-4">
          {progressLoading ? (
            <div className="text-center py-8">加载中...</div>
          ) : progressItems.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <Activity className="w-16 h-16 mx-auto mb-4 text-gray-500" />
              <p className="text-gray-400 text-lg">当前没有运行中的爬虫</p>
              <p className="text-gray-500 text-sm mt-2">点击"一键爬取所有平台"或单独启动爬虫</p>
            </div>
          ) : (
            <>
              <div className="glass-card p-4 bg-blue-500/10 border border-blue-500/20">
                <div className="flex items-center space-x-2 text-blue-400">
                  <TrendingUp className="w-5 h-5" />
                  <span className="font-semibold">
                    正在运行 {progressItems.length} 个爬虫，实时更新中...
                  </span>
                </div>
              </div>

              {progressItems.map((item: any) => (
                <div key={item.spider_name} className="glass-card p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-semibold">{item.display_name}</h3>
                        <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm bg-blue-500/20 text-blue-400">
                          <Activity className="w-4 h-4 animate-pulse" />
                          <span>运行中</span>
                        </span>
                      </div>
                      
                      {/* 进度指标 */}
                      <div className="grid grid-cols-4 gap-4 mt-4">
                        <div className="bg-white/5 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">已抓取文章</div>
                          <div className="text-2xl font-bold text-primary-400">{item.items_scraped}</div>
                        </div>
                        <div className="bg-white/5 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">请求数</div>
                          <div className="text-2xl font-bold text-green-400">{item.requests_count}</div>
                        </div>
                        <div className="bg-white/5 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">运行时长</div>
                          <div className="text-2xl font-bold text-blue-400">{formatDuration(item.duration)}</div>
                        </div>
                        <div className="bg-white/5 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">开始时间</div>
                          <div className="text-sm font-semibold text-gray-300">
                            {item.started_at ? format(new Date(item.started_at), 'HH:mm:ss', { locale: zhCN }) : '-'}
                          </div>
                        </div>
                      </div>

                      {/* 最新日志 */}
                      {item.last_log_line && (
                        <div className="mt-4 bg-black/30 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">最新日志:</div>
                          <div className="text-sm text-gray-300 font-mono">
                            {item.last_log_line}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}
