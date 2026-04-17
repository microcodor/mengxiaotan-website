import { useState, useEffect } from 'react'
import { Bell, Settings, User, CheckCircle, XCircle, Loader } from 'lucide-react'
import axios from 'axios'

interface IMAppConfig {
  enterprise_wechat: {
    enabled: boolean
    corp_id?: string
    agent_id?: string
    secret?: string
  }
  dingtalk: {
    enabled: boolean
    app_key?: string
    app_secret?: string
    agent_id?: string
  }
  feishu: {
    enabled: boolean
    app_id?: string
    app_secret?: string
  }
}

interface ChannelConfig {
  enterprise_wechat?: string
  dingtalk?: string
  feishu?: string
  email?: string
  sms?: string
}

export default function PushSettings() {
  const [activeTab, setActiveTab] = useState<'apps' | 'channels'>('apps')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState<string | null>(null)
  
  // IM应用配置
  const [imApps, setImApps] = useState<IMAppConfig>({
    enterprise_wechat: { enabled: false },
    dingtalk: { enabled: false },
    feishu: { enabled: false }
  })
  
  // 推送渠道配置(接收人)
  const [channels, setChannels] = useState<ChannelConfig>({})
  const [subscriptionLevel, setSubscriptionLevel] = useState('')
  const [allowedChannels, setAllowedChannels] = useState<string[]>([])
  
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    loadIMApps()
    loadChannels()
  }, [])

  const loadIMApps = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('http://localhost:5001/api/push-settings/im-apps', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setImApps(response.data)
    } catch (error: any) {
      console.error('加载IM应用配置失败:', error)
      showMessage('error', '加载IM应用配置失败')
    }
  }

  const loadChannels = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('http://localhost:5001/api/push-settings/channels', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setChannels(response.data.channels || {})
      setSubscriptionLevel(response.data.subscription_level || '')
      setAllowedChannels(response.data.allowed_channels || [])
    } catch (error: any) {
      console.error('加载推送渠道配置失败:', error)
      showMessage('error', '加载推送渠道配置失败')
    }
  }

  const saveIMApps = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:5001/api/push-settings/im-apps', imApps, {
        headers: { Authorization: `Bearer ${token}` }
      })
      showMessage('success', 'IM应用配置已保存')
      loadIMApps() // 重新加载以获取脱敏后的数据
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const testIMApp = async (platform: string) => {
    setTesting(platform)
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.post(
        'http://localhost:5001/api/push-settings/im-apps/test',
        { platform },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      if (response.data.success) {
        showMessage('success', response.data.message)
      } else {
        showMessage('error', response.data.message)
      }
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || '测试失败')
    } finally {
      setTesting(null)
    }
  }

  const saveChannels = async () => {
    setSaving(true)
    try {
      const token = localStorage.getItem('access_token')
      await axios.post('http://localhost:5001/api/push-settings/channels', channels, {
        headers: { Authorization: `Bearer ${token}` }
      })
      showMessage('success', '推送渠道配置已保存')
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const testChannel = async (channel: string) => {
    setTesting(channel)
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.post(
        'http://localhost:5001/api/push-settings/test',
        { channel },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      if (response.data.success) {
        showMessage('success', '测试推送发送成功')
      } else {
        showMessage('error', response.data.message)
      }
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || '测试失败')
    } finally {
      setTesting(null)
    }
  }

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 3000)
  }

  const platformNames = {
    enterprise_wechat: '企业微信',
    dingtalk: '钉钉',
    feishu: '飞书',
    email: '邮件',
    sms: '短信'
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
          <Bell className="w-7 h-7 text-primary-400" />
          <span>推送设置</span>
        </h1>
        <p className="text-gray-400 mt-2">配置IM应用和推送接收人</p>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center space-x-2 ${
          message.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Tab切换 */}
      <div className="flex space-x-4 border-b border-white/10">
        <button
          onClick={() => setActiveTab('apps')}
          className={`px-4 py-2 font-medium transition-colors flex items-center space-x-2 ${
            activeTab === 'apps'
              ? 'text-primary-400 border-b-2 border-primary-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <Settings className="w-5 h-5" />
          <span>IM应用配置</span>
        </button>
        <button
          onClick={() => setActiveTab('channels')}
          className={`px-4 py-2 font-medium transition-colors flex items-center space-x-2 ${
            activeTab === 'channels'
              ? 'text-primary-400 border-b-2 border-primary-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <User className="w-5 h-5" />
          <span>接收人配置</span>
        </button>
      </div>

      {/* Tab内容 */}
      {activeTab === 'apps' && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <p className="text-gray-400 mb-6">
              配置您企业的IM应用信息,用于发送推送消息。每个平台需要单独配置。
            </p>

            {/* 企业微信配置 */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">企业微信应用配置</h3>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={imApps.enterprise_wechat.enabled}
                    onChange={(e) => setImApps({
                      ...imApps,
                      enterprise_wechat: { ...imApps.enterprise_wechat, enabled: e.target.checked }
                    })}
                    className="w-5 h-5"
                  />
                  <span className="text-gray-300">启用</span>
                </label>
              </div>

              {imApps.enterprise_wechat.enabled && (
                <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">企业ID (CorpID)</label>
                    <input
                      type="text"
                      value={imApps.enterprise_wechat.corp_id || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        enterprise_wechat: { ...imApps.enterprise_wechat, corp_id: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="ww1234567890abcdef"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">应用ID (AgentID)</label>
                    <input
                      type="text"
                      value={imApps.enterprise_wechat.agent_id || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        enterprise_wechat: { ...imApps.enterprise_wechat, agent_id: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="1000002"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">应用Secret</label>
                    <input
                      type="password"
                      value={imApps.enterprise_wechat.secret || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        enterprise_wechat: { ...imApps.enterprise_wechat, secret: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="输入应用Secret"
                    />
                  </div>
                  <button
                    onClick={() => testIMApp('enterprise_wechat')}
                    disabled={testing === 'enterprise_wechat'}
                    className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
                  >
                    {testing === 'enterprise_wechat' ? (
                      <><Loader className="w-4 h-4 animate-spin" /><span>测试中...</span></>
                    ) : (
                      <span>测试连接</span>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* 钉钉配置 */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">钉钉应用配置</h3>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={imApps.dingtalk.enabled}
                    onChange={(e) => setImApps({
                      ...imApps,
                      dingtalk: { ...imApps.dingtalk, enabled: e.target.checked }
                    })}
                    className="w-5 h-5"
                  />
                  <span className="text-gray-300">启用</span>
                </label>
              </div>

              {imApps.dingtalk.enabled && (
                <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">AppKey</label>
                    <input
                      type="text"
                      value={imApps.dingtalk.app_key || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        dingtalk: { ...imApps.dingtalk, app_key: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="dingxxxxxxxx"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">AppSecret</label>
                    <input
                      type="password"
                      value={imApps.dingtalk.app_secret || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        dingtalk: { ...imApps.dingtalk, app_secret: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="输入AppSecret"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">AgentID</label>
                    <input
                      type="text"
                      value={imApps.dingtalk.agent_id || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        dingtalk: { ...imApps.dingtalk, agent_id: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="123456789"
                    />
                  </div>
                  <button
                    onClick={() => testIMApp('dingtalk')}
                    disabled={testing === 'dingtalk'}
                    className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
                  >
                    {testing === 'dingtalk' ? (
                      <><Loader className="w-4 h-4 animate-spin" /><span>测试中...</span></>
                    ) : (
                      <span>测试连接</span>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* 飞书配置 */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">飞书应用配置</h3>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={imApps.feishu.enabled}
                    onChange={(e) => setImApps({
                      ...imApps,
                      feishu: { ...imApps.feishu, enabled: e.target.checked }
                    })}
                    className="w-5 h-5"
                  />
                  <span className="text-gray-300">启用</span>
                </label>
              </div>

              {imApps.feishu.enabled && (
                <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">App ID</label>
                    <input
                      type="text"
                      value={imApps.feishu.app_id || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        feishu: { ...imApps.feishu, app_id: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="cli_xxxxxxxx"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">App Secret</label>
                    <input
                      type="password"
                      value={imApps.feishu.app_secret || ''}
                      onChange={(e) => setImApps({
                        ...imApps,
                        feishu: { ...imApps.feishu, app_secret: e.target.value }
                      })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      placeholder="输入App Secret"
                    />
                  </div>
                  <button
                    onClick={() => testIMApp('feishu')}
                    disabled={testing === 'feishu'}
                    className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
                  >
                    {testing === 'feishu' ? (
                      <><Loader className="w-4 h-4 animate-spin" /><span>测试中...</span></>
                    ) : (
                      <span>测试连接</span>
                    )}
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={saveIMApps}
              disabled={saving}
              className="w-full py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 font-medium"
            >
              {saving ? '保存中...' : '保存配置'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'channels' && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <div className="mb-6">
              <p className="text-gray-400">
                当前订阅: <span className="text-primary-400 font-semibold">{subscriptionLevel || '未订阅'}</span>
              </p>
              <p className="text-gray-400 mt-2">
                可用渠道: {allowedChannels.map(c => platformNames[c as keyof typeof platformNames]).join('、') || '无'}
              </p>
            </div>

            <div className="space-y-6">
              {/* 企业微信接收人 */}
              {allowedChannels.includes('enterprise_wechat') && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">企业微信</h3>
                  <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">用户ID (UserID)</label>
                      <input
                        type="text"
                        value={channels.enterprise_wechat || ''}
                        onChange={(e) => setChannels({ ...channels, enterprise_wechat: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                        placeholder="zhangsan"
                      />
                      <p className="text-xs text-gray-500 mt-1">💡 在企业微信通讯录中查看成员账号</p>
                    </div>
                    {channels.enterprise_wechat && (
                      <button
                        onClick={() => testChannel('enterprise_wechat')}
                        disabled={testing === 'enterprise_wechat'}
                        className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50"
                      >
                        {testing === 'enterprise_wechat' ? '测试中...' : '测试推送'}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* 钉钉接收人 */}
              {allowedChannels.includes('dingtalk') && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">钉钉</h3>
                  <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">用户ID</label>
                      <input
                        type="text"
                        value={channels.dingtalk || ''}
                        onChange={(e) => setChannels({ ...channels, dingtalk: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                        placeholder="manager123"
                      />
                      <p className="text-xs text-gray-500 mt-1">💡 在钉钉通讯录中查看员工工号</p>
                    </div>
                    {channels.dingtalk && (
                      <button
                        onClick={() => testChannel('dingtalk')}
                        disabled={testing === 'dingtalk'}
                        className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50"
                      >
                        {testing === 'dingtalk' ? '测试中...' : '测试推送'}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* 飞书接收人 */}
              {allowedChannels.includes('feishu') && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">飞书</h3>
                  <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Open ID</label>
                      <input
                        type="text"
                        value={channels.feishu || ''}
                        onChange={(e) => setChannels({ ...channels, feishu: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                        placeholder="ou_xxx"
                      />
                      <p className="text-xs text-gray-500 mt-1">💡 在飞书通讯录中查看用户Open ID</p>
                    </div>
                    {channels.feishu && (
                      <button
                        onClick={() => testChannel('feishu')}
                        disabled={testing === 'feishu'}
                        className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50"
                      >
                        {testing === 'feishu' ? '测试中...' : '测试推送'}
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* 邮件 */}
              {allowedChannels.includes('email') && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">邮件</h3>
                  <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">邮箱地址</label>
                      <input
                        type="email"
                        value={channels.email || ''}
                        onChange={(e) => setChannels({ ...channels, email: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                        placeholder="user@example.com"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* 短信 */}
              {allowedChannels.includes('sms') && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">短信</h3>
                  <div className="space-y-4 pl-4 border-l-2 border-primary-400/30">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">手机号</label>
                      <input
                        type="tel"
                        value={channels.sms || ''}
                        onChange={(e) => setChannels({ ...channels, sms: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                        placeholder="13800138000"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={saveChannels}
              disabled={saving}
              className="w-full py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 font-medium mt-6"
            >
              {saving ? '保存中...' : '保存配置'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
