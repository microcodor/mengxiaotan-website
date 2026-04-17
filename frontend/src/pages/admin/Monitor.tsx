import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, TrendingUp, RefreshCw, Bell } from 'lucide-react';
import api from '../../lib/api';

interface Statistics {
  period_days: number;
  total_runs: number;
  success_runs: number;
  failed_runs: number;
  success_rate: number;
  total_articles: number;
  spiders: SpiderStat[];
}

interface SpiderStat {
  name: string;
  total_runs: number;
  success_runs: number;
  success_rate: number;
  total_articles: number;
}

interface Failure {
  spider_name: string;
  error_msg: string;
  failed_at: string;
}

interface Health {
  is_healthy: boolean;
  db_healthy: boolean;
  recent_runs: number;
  error_sources: number;
  checked_at: string;
}

export default function Monitor() {
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [failures, setFailures] = useState<Failure[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [days, setDays] = useState(7);
  const [testingAlert, setTestingAlert] = useState(false);

  useEffect(() => {
    loadData();
    // 每分钟刷新一次
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, [days]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsRes, failuresRes, healthRes] = await Promise.all([
        api.get(`/monitor/statistics?days=${days}`),
        api.get('/monitor/failures?limit=10'),
        api.get('/monitor/health')
      ]);
      setStatistics(statsRes);
      setFailures(failuresRes.failures || []);
      setHealth(healthRes);
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTestAlert = async () => {
    if (!confirm('确定要发送测试告警吗？')) return;
    
    try {
      setTestingAlert(true);
      await api.post('/monitor/test-alert');
      alert('测试告警已发送，请检查企业微信和邮箱');
    } catch (error: any) {
      alert(error.response?.data?.message || '发送失败');
    } finally {
      setTestingAlert(false);
    }
  };

  if (loading && !statistics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">监控告警</h1>
        <div className="flex space-x-4">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-primary-500"
          >
            <option value={1}>最近1天</option>
            <option value={7}>最近7天</option>
            <option value={30}>最近30天</option>
            <option value={90}>最近90天</option>
          </select>
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-white/5 text-white rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            <span>刷新</span>
          </button>
          <button
            onClick={handleTestAlert}
            disabled={testingAlert}
            className="flex items-center space-x-2 px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30 transition-colors disabled:opacity-50"
          >
            <Bell className="w-5 h-5" />
            <span>{testingAlert ? '发送中...' : '测试告警'}</span>
          </button>
        </div>
      </div>

      {/* 系统健康状态 */}
      <div className="glass-card p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">系统健康状态</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="flex items-center space-x-4">
            {health?.is_healthy ? (
              <CheckCircle className="w-12 h-12 text-green-400" />
            ) : (
              <AlertTriangle className="w-12 h-12 text-red-400" />
            )}
            <div>
              <p className="text-gray-400 text-sm">总体状态</p>
              <p className="text-xl font-bold">
                {health?.is_healthy ? (
                  <span className="text-green-400">健康</span>
                ) : (
                  <span className="text-red-400">异常</span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {health?.db_healthy ? (
              <CheckCircle className="w-12 h-12 text-green-400" />
            ) : (
              <AlertTriangle className="w-12 h-12 text-red-400" />
            )}
            <div>
              <p className="text-gray-400 text-sm">数据库</p>
              <p className="text-xl font-bold">
                {health?.db_healthy ? (
                  <span className="text-green-400">正常</span>
                ) : (
                  <span className="text-red-400">异常</span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Activity className="w-12 h-12 text-primary-400 opacity-50" />
            <div>
              <p className="text-gray-400 text-sm">最近1小时运行</p>
              <p className="text-xl font-bold">{health?.recent_runs || 0} 次</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <AlertTriangle className={`w-12 h-12 ${health?.error_sources ? 'text-red-400' : 'text-gray-400 opacity-50'}`} />
            <div>
              <p className="text-gray-400 text-sm">错误爬虫</p>
              <p className="text-xl font-bold">
                {health?.error_sources ? (
                  <span className="text-red-400">{health.error_sources} 个</span>
                ) : (
                  <span className="text-gray-400">0 个</span>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">总运行次数</p>
              <p className="text-2xl font-bold mt-2">{statistics?.total_runs || 0}</p>
            </div>
            <Activity className="w-12 h-12 text-primary-400 opacity-50" />
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">成功次数</p>
              <p className="text-2xl font-bold mt-2 text-green-400">{statistics?.success_runs || 0}</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-400 opacity-50" />
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">失败次数</p>
              <p className="text-2xl font-bold mt-2 text-red-400">{statistics?.failed_runs || 0}</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-400 opacity-50" />
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">成功率</p>
              <p className="text-2xl font-bold mt-2">{statistics?.success_rate || 0}%</p>
            </div>
            <TrendingUp className="w-12 h-12 text-primary-400 opacity-50" />
          </div>
        </div>
      </div>

      {/* 业务指标 */}
      {statistics?.business_metrics && (
        <>
          {/* 用户指标 */}
          <div className="glass-card p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">用户指标</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">总用户数</p>
                <p className="text-2xl font-bold">{statistics.business_metrics.users?.total || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">新增用户</p>
                <p className="text-2xl font-bold text-green-400">{statistics.business_metrics.users?.new || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">活跃用户</p>
                <p className="text-2xl font-bold text-blue-400">{statistics.business_metrics.users?.active || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">活跃率</p>
                <p className="text-2xl font-bold text-primary-400">{statistics.business_metrics.users?.active_rate || 0}%</p>
              </div>
            </div>
          </div>

          {/* 文章指标 */}
          <div className="glass-card p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">文章指标</h2>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">文章总数</p>
                <p className="text-2xl font-bold">{statistics.business_metrics.articles?.total || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">新增文章</p>
                <p className="text-2xl font-bold text-green-400">{statistics.business_metrics.articles?.new || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">已审核</p>
                <p className="text-2xl font-bold text-blue-400">{statistics.business_metrics.articles?.reviewed || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">待审核</p>
                <p className="text-2xl font-bold text-yellow-400">{statistics.business_metrics.articles?.pending || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">审核率</p>
                <p className="text-2xl font-bold text-primary-400">{statistics.business_metrics.articles?.review_rate || 0}%</p>
              </div>
            </div>
          </div>

          {/* 订阅和订单指标 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* 订阅指标 */}
            <div className="glass-card p-6">
              <h2 className="text-xl font-semibold mb-4">订阅指标</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">活跃订阅</span>
                  <span className="text-2xl font-bold text-green-400">{statistics.business_metrics.subscriptions?.active || 0}</span>
                </div>
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">新增订阅</span>
                  <span className="text-2xl font-bold text-blue-400">{statistics.business_metrics.subscriptions?.new || 0}</span>
                </div>
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">即将到期</span>
                  <span className="text-2xl font-bold text-yellow-400">{statistics.business_metrics.subscriptions?.expiring_soon || 0}</span>
                </div>
              </div>
            </div>

            {/* 订单指标 */}
            <div className="glass-card p-6">
              <h2 className="text-xl font-semibold mb-4">订单指标</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">订单总数</span>
                  <span className="text-2xl font-bold">{statistics.business_metrics.orders?.total || 0}</span>
                </div>
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">待处理</span>
                  <span className="text-2xl font-bold text-yellow-400">{statistics.business_metrics.orders?.pending || 0}</span>
                </div>
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">已支付</span>
                  <span className="text-2xl font-bold text-green-400">{statistics.business_metrics.orders?.paid || 0}</span>
                </div>
                <div className="flex items-center justify-between bg-white/5 rounded-lg p-4">
                  <span className="text-gray-400">总收入</span>
                  <span className="text-2xl font-bold text-primary-400">¥{(statistics.business_metrics.orders?.revenue || 0).toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* AI简报指标 */}
          <div className="glass-card p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">AI简报指标</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">简报总数</p>
                <p className="text-2xl font-bold">{statistics.business_metrics.briefs?.total || 0}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">最近生成</p>
                <p className="text-2xl font-bold text-green-400">{statistics.business_metrics.briefs?.recent || 0}</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 爬虫统计 */}
      <div className="glass-card mb-8">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-semibold">爬虫运行统计</h2>
          <p className="text-sm text-gray-400 mt-1">
            最近 {statistics?.period_days} 天，共抓取 {statistics?.total_articles || 0} 篇文章
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  爬虫名称
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  总运行次数
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  成功次数
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  成功率
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  抓取文章数
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {statistics?.spiders?.map((spider) => (
                <tr key={spider.name} className="hover:bg-white/5">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium">{spider.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {spider.total_runs}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-green-400">
                    {spider.success_runs}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={spider.success_rate >= 80 ? 'text-green-400' : spider.success_rate >= 50 ? 'text-yellow-400' : 'text-red-400'}>
                      {spider.success_rate.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {spider.total_articles}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 最近失败记录 */}
      <div className="glass-card">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-semibold">最近失败记录</h2>
          <p className="text-sm text-gray-400 mt-1">
            显示最近 10 条失败记录
          </p>
        </div>

        {failures.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400 opacity-50" />
            <p>太棒了！最近没有失败记录</p>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {failures.map((failure, index) => (
              <div key={index} className="p-6 hover:bg-white/5">
                <div className="flex items-start space-x-4">
                  <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-medium">{failure.spider_name}</h3>
                      <span className="text-xs text-gray-400">
                        {new Date(failure.failed_at).toLocaleString('zh-CN')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 break-words">
                      {failure.error_msg || '未知错误'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 说明 */}
      <div className="mt-6 glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">告警说明</h3>
        <div className="space-y-2 text-sm text-gray-300">
          <p>• <strong>自动告警</strong>：当爬虫连续失败3次时，系统会自动发送告警</p>
          <p>• <strong>告警渠道</strong>：企业微信、邮件（需要配置）</p>
          <p>• <strong>测试告警</strong>：点击"测试告警"按钮可以测试告警功能是否正常</p>
          <p>• <strong>配置邮件</strong>：在 .env 文件中配置 SMTP_SERVER、SMTP_USER、SMTP_PASSWORD、ALERT_EMAILS</p>
          <p>• <strong>健康检查</strong>：系统会定期检查数据库连接和爬虫状态</p>
        </div>
      </div>
    </div>
  );
}
