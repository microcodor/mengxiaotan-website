import React, { useState } from 'react';
import { 
  Bell, 
  Mail, 
  MessageSquare, 
  Smartphone, 
  Search,
  Send,
  Check,
  AlertCircle,
  Edit,
  Save,
  XCircle
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001';

interface PushChannels {
  enterprise_wechat?: string;
  dingtalk?: string;
  feishu?: string;
  email?: string;
  sms?: string;
}

interface UserPushSettings {
  user_id: number;
  username: string;
  company_name: string | null;
  subscription_level: string;
  allowed_channels: string[];
  configured_channels: PushChannels;
}

const PushManagement: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<UserPushSettings | null>(null);
  const [editingUser, setEditingUser] = useState<number | null>(null);
  const [editFormData, setEditFormData] = useState<PushChannels>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const channelConfig = {
    enterprise_wechat: { 
      name: '企业微信', 
      icon: MessageSquare, 
      color: 'text-green-600',
      placeholder: '请输入企业微信UserID（如：zhangsan）',
      description: '企业微信成员账号，可在企业微信管理后台 → 通讯录 → 成员详情中查看',
      example: '示例：zhangsan 或 ZhangSan',
      helpLink: 'https://developer.work.weixin.qq.com/document/path/90196'
    },
    dingtalk: { 
      name: '钉钉', 
      icon: MessageSquare, 
      color: 'text-blue-600',
      placeholder: '请输入钉钉UserID',
      description: '钉钉用户的唯一标识，可在钉钉管理后台 → 通讯录 → 成员详情中查看',
      example: '示例：manager1234 或 userId123',
      helpLink: 'https://open.dingtalk.com/document/orgapp/userid'
    },
    feishu: { 
      name: '飞书', 
      icon: MessageSquare, 
      color: 'text-purple-600',
      placeholder: '请输入飞书Open ID（如：ou_xxx）',
      description: '飞书用户的Open ID，可通过飞书开放平台API获取，或在管理后台查看',
      example: '示例：ou_c245b0a7dff2725cfa2fb104f8b48b9d',
      helpLink: 'https://open.feishu.cn/document/home/user-identity-introduction/open-id'
    },
    email: { 
      name: '邮件', 
      icon: Mail, 
      color: 'text-orange-600',
      placeholder: '请输入邮箱地址（如：user@example.com）',
      description: '接收推送消息的邮箱地址，需确保邮箱有效且可以正常接收邮件',
      example: '示例：zhangsan@company.com',
      helpLink: null
    },
    sms: { 
      name: '短信', 
      icon: Smartphone, 
      color: 'text-red-600',
      placeholder: '请输入手机号（如：13800138000）',
      description: '接收短信的手机号码，仅支持中国大陆手机号（11位数字）',
      example: '示例：13800138000',
      helpLink: null
    }
  };

  const handleSearchUser = async () => {
    if (!searchTerm.trim()) {
      showMessage('error', '请输入用户ID');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const userId = parseInt(searchTerm);
      
      if (isNaN(userId)) {
        showMessage('error', '请输入有效的用户ID');
        return;
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/push-settings/admin/user/${userId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSelectedUser(response.data);
      setEditFormData(response.data.configured_channels || {});
      setMessage(null);
    } catch (error: any) {
      console.error('查询用户失败:', error);
      showMessage('error', error.response?.data?.message || '查询用户失败');
      setSelectedUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!selectedUser) return;

    setSaving(true);
    setMessage(null);

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/api/push-settings/admin/user/${selectedUser.user_id}`,
        editFormData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      showMessage('success', '推送设置已保存');
      setEditingUser(null);
      
      const response = await axios.get(
        `${API_BASE_URL}/api/push-settings/admin/user/${selectedUser.user_id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSelectedUser(response.data);
    } catch (error: any) {
      console.error('保存推送设置失败:', error);
      showMessage('error', error.response?.data?.message || '保存推送设置失败');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async (channel: string) => {
    if (!selectedUser) return;

    setTesting(channel);
    setMessage(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/api/push-settings/admin/user/${selectedUser.user_id}/test`,
        {
          channel,
          message: '这是一条管理员测试消息'
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        showMessage('success', `${channelConfig[channel as keyof typeof channelConfig].name}测试推送已发送`);
      } else {
        showMessage('error', response.data.message || '测试推送失败');
      }
    } catch (error: any) {
      console.error('测试推送失败:', error);
      showMessage('error', error.response?.data?.message || '测试推送失败');
    } finally {
      setTesting(null);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const subscriptionLevelNames: Record<string, string> = {
    free: '免费订阅',
    standard: '基础版',
    premium: '高级版'
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 页面标题 */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg">
            <Bell className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">推送配置管理</h1>
            <p className="text-sm text-gray-400 mt-1">为用户配置推送渠道接收人信息</p>
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className={`mb-6 p-4 rounded-xl flex items-start gap-3 border ${
          message.type === 'success' 
            ? 'bg-primary-500/10 text-primary-300 border-primary-500/30' 
            : 'bg-red-500/10 text-red-300 border-red-500/30'
        }`}>
          {message.type === 'success' ? <Check className="w-5 h-5 flex-shrink-0 mt-0.5" /> : <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />}
          <span className="flex-1">{message.text}</span>
        </div>
      )}

      {/* 使用说明 */}
      <div className="mb-6 glass-card p-5">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-gray-200 mb-3">配置说明</h3>
            <div className="space-y-3 text-sm text-gray-300">
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <div className="font-medium text-gray-200 mb-1.5 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center text-xs font-bold">1</span>
                  推送渠道配置
                </div>
                <p className="text-gray-400 ml-8">
                  为用户填写各IM平台的接收人ID。不同平台的ID格式不同，请参考每个渠道下方的说明和示例。
                </p>
              </div>
              
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <div className="font-medium text-gray-200 mb-1.5 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center text-xs font-bold">2</span>
                  IM应用配置（用户侧）
                </div>
                <p className="text-gray-400 ml-8">
                  用户需要在"个人设置 → IM应用配置"中配置自己的IM应用信息（Corp ID、Secret等）。这是推送服务的认证凭证。
                </p>
              </div>
              
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <div className="font-medium text-gray-200 mb-1.5 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center text-xs font-bold">3</span>
                  测试推送
                </div>
                <p className="text-gray-400 ml-8">
                  配置完成后，点击"测试"按钮验证推送是否正常。如果测试失败，请确认用户已配置IM应用信息，且接收人ID填写正确。
                </p>
              </div>
              
              <div className="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/30">
                <div className="font-medium text-yellow-300 mb-1.5 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  订阅等级限制
                </div>
                <p className="text-yellow-200/80 text-xs">
                  不同订阅等级支持的推送渠道不同：<br/>
                  • <strong>免费订阅</strong>：仅支持企业微信<br/>
                  • <strong>基础版</strong>：支持企业微信、钉钉、飞书、邮件<br/>
                  • <strong>高级版</strong>：支持所有渠道（含短信）
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 查询用户 */}
      <div className="mb-6 glass-card p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Search className="w-5 h-5 text-primary-400" />
          查询用户
        </h2>
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearchUser()}
              placeholder="输入用户ID（例如：1）"
              className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors text-gray-200 placeholder-gray-500"
            />
          </div>
          <button
            onClick={handleSearchUser}
            disabled={loading}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-sm transition-all"
          >
            {loading ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : <Search className="w-4 h-4" />}
            查询
          </button>
        </div>
      </div>

      {selectedUser && (
        <div className="glass-card p-6">
          {/* 用户信息 */}
          <div className="mb-6 pb-6 border-b border-white/10">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-sm font-bold">
                {selectedUser.username.charAt(0).toUpperCase()}
              </div>
              用户信息
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <span className="text-xs text-gray-400 block mb-1">用户ID</span>
                <span className="font-semibold text-gray-200">{selectedUser.user_id}</span>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <span className="text-xs text-gray-400 block mb-1">用户名</span>
                <span className="font-semibold text-gray-200">{selectedUser.username}</span>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <span className="text-xs text-gray-400 block mb-1">企业名称</span>
                <span className="font-semibold text-gray-200">{selectedUser.company_name || '-'}</span>
              </div>
              <div className="bg-white/5 rounded-lg p-3 border border-white/10">
                <span className="text-xs text-gray-400 block mb-1">订阅等级</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  selectedUser.subscription_level === 'premium' ? 'bg-purple-500/20 text-purple-300' :
                  selectedUser.subscription_level === 'standard' ? 'bg-blue-500/20 text-blue-300' :
                  'bg-gray-500/20 text-gray-300'
                }`}>
                  {subscriptionLevelNames[selectedUser.subscription_level]}
                </span>
              </div>
            </div>
          </div>

          {/* 推送渠道配置 */}
          <div>
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-primary-400" />
                推送渠道配置
              </h2>
              {editingUser !== selectedUser.user_id ? (
                <button 
                  onClick={() => { setEditingUser(selectedUser.user_id); setEditFormData(selectedUser.configured_channels); }} 
                  className="px-4 py-2 text-primary-400 hover:bg-white/5 rounded-lg flex items-center gap-2 font-medium transition-colors border border-white/10"
                >
                  <Edit className="w-4 h-4" />编辑
                </button>
              ) : (
                <div className="flex gap-2">
                  <button 
                    onClick={() => setEditingUser(null)} 
                    className="px-4 py-2 text-gray-400 hover:bg-white/5 rounded-lg flex items-center gap-2 font-medium transition-colors border border-white/10"
                  >
                    <XCircle className="w-4 h-4" />取消
                  </button>
                  <button 
                    onClick={handleSave} 
                    disabled={saving} 
                    className="px-4 py-2 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-sm transition-all"
                  >
                    {saving ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : <Save className="w-4 h-4" />}
                    保存
                  </button>
                </div>
              )}
            </div>

            <div className="space-y-4">
              {Object.entries(channelConfig).map(([key, config]) => {
                const Icon = config.icon;
                const isEditing = editingUser === selectedUser.user_id;
                const value = isEditing ? editFormData[key as keyof PushChannels] || '' : selectedUser.configured_channels[key as keyof PushChannels] || '';
                const isConfigured = !!selectedUser.configured_channels[key as keyof PushChannels];
                const isAllowed = selectedUser.allowed_channels.includes(key);

                return (
                  <div key={key} className={`border rounded-xl p-5 transition-all ${
                    isAllowed 
                      ? 'border-white/10 hover:border-primary-500/30 bg-white/5' 
                      : 'border-white/5 bg-white/[0.02] opacity-60'
                  }`}>
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3 flex-1">
                        <div className={`p-2 rounded-lg bg-gradient-to-br flex-shrink-0 ${
                          key === 'enterprise_wechat' ? 'from-green-500 to-green-600' :
                          key === 'dingtalk' ? 'from-blue-500 to-blue-600' :
                          key === 'feishu' ? 'from-purple-500 to-purple-600' :
                          key === 'email' ? 'from-orange-500 to-orange-600' :
                          'from-red-500 to-red-600'
                        }`}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-gray-200">{config.name}</span>
                            {isConfigured && !isEditing && (
                              <span className="px-2 py-0.5 rounded-full text-xs bg-primary-500/20 text-primary-300 font-medium inline-flex items-center gap-1">
                                <Check className="w-3 h-3" />已配置
                              </span>
                            )}
                            {!isAllowed && (
                              <span className="px-2 py-0.5 rounded-full text-xs bg-gray-500/20 text-gray-400 font-medium">
                                需升级订阅
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-400 leading-relaxed mb-1">
                            {config.description}
                          </p>
                          {config.example && (
                            <p className="text-xs text-gray-500 italic">
                              {config.example}
                            </p>
                          )}
                          {config.helpLink && (
                            <a 
                              href={config.helpLink} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-xs text-primary-400 hover:text-primary-300 inline-flex items-center gap-1 mt-1"
                            >
                              查看官方文档 →
                            </a>
                          )}
                        </div>
                      </div>
                      {!isEditing && isConfigured && isAllowed && (
                        <button 
                          onClick={() => handleTest(key)} 
                          disabled={testing === key} 
                          className="px-3 py-1.5 text-sm bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:from-primary-600 hover:to-primary-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed flex items-center gap-1.5 font-medium shadow-sm transition-all flex-shrink-0"
                        >
                          {testing === key ? (
                            <>
                              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                              测试中
                            </>
                          ) : (
                            <>
                              <Send className="w-3 h-3" />测试
                            </>
                          )}
                        </button>
                      )}
                    </div>
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => isEditing && setEditFormData({ ...editFormData, [key]: e.target.value })}
                      placeholder={config.placeholder}
                      disabled={!isEditing || !isAllowed}
                      className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                        !isEditing || !isAllowed 
                          ? 'bg-white/5 border-white/10 text-gray-300 cursor-not-allowed' 
                          : 'bg-white/10 border-white/20 text-gray-200'
                      } placeholder-gray-500`}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {!selectedUser && !loading && (
        <div className="glass-card p-16 text-center">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center mx-auto mb-4">
            <Bell className="w-10 h-10 text-gray-400" />
          </div>
          <p className="text-gray-300 text-lg font-medium mb-2">请输入用户ID查询</p>
          <p className="text-gray-500 text-sm">在上方搜索框输入用户ID，即可查看和配置该用户的推送设置</p>
        </div>
      )}
    </div>
  );
};

export default PushManagement;
