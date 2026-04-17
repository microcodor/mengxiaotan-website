import { useState, useEffect } from 'react';
import { Clock, Play, Pause, RefreshCw, Zap } from 'lucide-react';
import api from '../../lib/api';

interface Job {
  id: string;
  name: string;
  next_run_time: string | null;
  trigger: string;
}

interface SchedulerStatus {
  enabled: boolean;
  running: boolean;
  jobs_count: number;
  message: string;
}

export default function Scheduler() {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<SchedulerStatus | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [running, setRunning] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadData();
    // 每30秒刷新一次
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statusRes, jobsRes] = await Promise.all([
        api.get('/scheduler/status'),
        api.get('/scheduler/jobs')
      ]);
      setStatus(statusRes);
      setJobs(jobsRes.jobs || []);
    } catch (error: any) {
      alert(error.response?.data?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handlePauseJob = async (jobId: string) => {
    if (!confirm('确定要暂停这个任务吗？')) return;
    
    try {
      setRunning({ ...running, [jobId]: true });
      await api.post(`/scheduler/jobs/${jobId}/pause`);
      alert('任务已暂停');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    } finally {
      setRunning({ ...running, [jobId]: false });
    }
  };

  const handleResumeJob = async (jobId: string) => {
    try {
      setRunning({ ...running, [jobId]: true });
      await api.post(`/scheduler/jobs/${jobId}/resume`);
      alert('任务已恢复');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    } finally {
      setRunning({ ...running, [jobId]: false });
    }
  };

  const handleTriggerJob = async (jobId: string) => {
    if (!confirm('确定要立即运行这个任务吗？')) return;
    
    try {
      setRunning({ ...running, [jobId]: true });
      await api.post(`/scheduler/jobs/${jobId}/trigger`);
      alert('任务已触发，请查看爬虫管理页面的日志');
      loadData();
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    } finally {
      setRunning({ ...running, [jobId]: false });
    }
  };

  const handleRunAll = async () => {
    if (!confirm('确定要立即运行所有爬虫吗？这可能需要几分钟时间。')) return;
    
    try {
      setRunning({ ...running, 'run-all': true });
      await api.post('/scheduler/run-all');
      alert('已开始运行所有爬虫，请查看爬虫管理页面的日志');
    } catch (error: any) {
      alert(error.response?.data?.message || '操作失败');
    } finally {
      setRunning({ ...running, 'run-all': false });
    }
  };

  if (loading && !status) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">定时任务管理</h1>
        <div className="flex space-x-4">
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-white/5 text-white rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            <span>刷新</span>
          </button>
          <button
            onClick={handleRunAll}
            disabled={running['run-all']}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50"
          >
            <Zap className="w-5 h-5" />
            <span>{running['run-all'] ? '运行中...' : '立即运行所有爬虫'}</span>
          </button>
        </div>
      </div>

      {/* 状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">调度器状态</p>
              <p className="text-2xl font-bold mt-2">
                {status?.enabled ? (
                  <span className="text-green-400">已启用</span>
                ) : (
                  <span className="text-red-400">未启用</span>
                )}
              </p>
            </div>
            <Clock className="w-12 h-12 text-primary-400 opacity-50" />
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">运行状态</p>
              <p className="text-2xl font-bold mt-2">
                {status?.running ? (
                  <span className="text-green-400">运行中</span>
                ) : (
                  <span className="text-gray-400">已停止</span>
                )}
              </p>
            </div>
            <Play className="w-12 h-12 text-green-400 opacity-50" />
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">任务数量</p>
              <p className="text-2xl font-bold mt-2">{status?.jobs_count || 0}</p>
            </div>
            <RefreshCw className="w-12 h-12 text-primary-400 opacity-50" />
          </div>
        </div>
      </div>

      {/* 任务列表 */}
      <div className="glass-card">
        <div className="p-6 border-b border-white/10">
          <h2 className="text-xl font-semibold">定时任务列表</h2>
          <p className="text-sm text-gray-400 mt-1">
            系统会在每天 08:00、12:00、18:00 自动运行所有爬虫
          </p>
        </div>

        {!status?.enabled ? (
          <div className="p-8 text-center text-gray-400">
            <p>定时任务调度器未启用</p>
            <p className="text-sm mt-2">请在配置文件中设置 ENABLE_SCHEDULER=true</p>
          </div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            暂无定时任务
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    任务名称
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    任务ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    触发器
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    下次运行时间
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium">{job.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {job.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {job.trigger}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {job.next_run_time
                        ? new Date(job.next_run_time).toLocaleString('zh-CN')
                        : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleTriggerJob(job.id)}
                          disabled={running[job.id]}
                          className="text-green-400 hover:text-green-300 disabled:opacity-50"
                          title="立即运行"
                        >
                          <Play className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handlePauseJob(job.id)}
                          disabled={running[job.id]}
                          className="text-yellow-400 hover:text-yellow-300 disabled:opacity-50"
                          title="暂停任务"
                        >
                          <Pause className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 说明 */}
      <div className="mt-6 glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">使用说明</h3>
        <div className="space-y-2 text-sm text-gray-300">
          <p>• <strong>自动运行</strong>：系统会在每天 08:00、12:00、18:00 自动运行所有爬虫</p>
          <p>• <strong>立即运行</strong>：点击"立即运行"按钮可以手动触发任务</p>
          <p>• <strong>暂停任务</strong>：暂停后任务将不会自动运行，需要手动恢复</p>
          <p>• <strong>查看日志</strong>：运行结果请在"爬虫管理"页面查看日志</p>
          <p>• <strong>禁用调度器</strong>：在 .env 文件中设置 ENABLE_SCHEDULER=false 可以禁用定时任务</p>
        </div>
      </div>
    </div>
  );
}
