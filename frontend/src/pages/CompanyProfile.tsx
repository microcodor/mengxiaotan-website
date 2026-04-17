import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, AlertTriangle, Lightbulb, Award, 
  Building2, Users, MapPin, Calendar, Download,
  Shield, Target, Zap, BarChart3, PieChart, Activity
} from 'lucide-react'
import api from '@/lib/api'
import { useNavigate } from 'react-router-dom'

export default function CompanyProfile() {
  const navigate = useNavigate()
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null)

  // 获取用户的企业信息
  const { data: userInfo } = useQuery({
    queryKey: ['userInfo'],
    queryFn: () => api.get('/users/me'),
  })

  // 自动选择用户的企业
  useEffect(() => {
    if (userInfo?.company_id) {
      setSelectedCompanyId(userInfo.company_id)
    }
  }, [userInfo])

  // 获取企业画像
  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['companyProfile', selectedCompanyId],
    queryFn: () => api.get(`/company-profile/${selectedCompanyId}`),
    enabled: !!selectedCompanyId,
  })

  // 获取评级颜色
  const getRatingColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-blue-400'
    if (score >= 40) return 'text-yellow-400'
    return 'text-red-400'
  }

  // 获取评级文本
  const getRatingText = (score: number) => {
    if (score >= 80) return '优秀'
    if (score >= 60) return '良好'
    if (score >= 40) return '一般'
    return '较差'
  }

  // 获取风险等级颜色
  const getRiskColor = (level: string) => {
    if (level === 'low') return 'text-green-400 bg-green-500/10 border-green-500/30'
    if (level === 'medium') return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
    return 'text-red-400 bg-red-500/10 border-red-500/30'
  }

  // 获取机会等级颜色
  const getOpportunityColor = (level: string) => {
    if (level === 'high') return 'text-green-400 bg-green-500/10 border-green-500/30'
    if (level === 'medium') return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
    return 'text-gray-400 bg-gray-500/10 border-gray-500/30'
  }

  // 导出报告
  const handleExport = async (format: string) => {
    try {
      const response = await api.get(`/company-profile/${selectedCompanyId}/export?format=${format}`)
      
      if (format === 'json') {
        // 下载JSON文件
        const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `company_profile_${selectedCompanyId}.json`
        a.click()
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('导出失败:', error)
      alert('导出失败，请稍后重试')
    }
  }

  if (!userInfo?.company_id) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-8 text-center">
          <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">未绑定企业</h2>
          <p className="text-gray-400 mb-6">请先在个人中心绑定企业信息</p>
          <button
            onClick={() => navigate('/dashboard/profile')}
            className="btn-primary"
          >
            前往个人中心
          </button>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-8 text-center">
          <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">加载失败</h2>
          <p className="text-gray-400 mb-6">{(error as any)?.message || '获取企业画像失败'}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            重新加载
          </button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-8 text-center">
          <Activity className="w-16 h-16 text-primary-400 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold mb-2">正在生成企业画像...</h2>
          <p className="text-gray-400">这可能需要几秒钟时间</p>
        </div>
      </div>
    )
  }

  const profileData = profile?.data

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">企业画像</h1>
          <p className="text-gray-400">基于公开信息的智能分析</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => handleExport('json')}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>导出JSON</span>
          </button>
        </div>
      </div>

      {/* 综合评分卡片 */}
      <div className="glass-card p-8 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">{profileData?.company_name}</h2>
            <p className="text-gray-400">
              生成时间: {new Date(profileData?.generated_at).toLocaleString('zh-CN')}
            </p>
          </div>
          <div className="text-center">
            <div className={`text-6xl font-bold mb-2 ${getRatingColor(profileData?.overall_score)}`}>
              {profileData?.overall_score}
            </div>
            <div className="text-lg text-gray-400">
              综合评分 · {getRatingText(profileData?.overall_score)}
            </div>
          </div>
        </div>
      </div>

      {/* 关键指标 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* 竞争力 */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <TrendingUp className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <div className="text-sm text-gray-400">竞争力得分</div>
              <div className="text-2xl font-bold text-primary-400">
                {profileData?.competitiveness?.score}分
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            {profileData?.competitiveness?.strengths?.length || 0} 个核心优势
          </div>
        </div>

        {/* 风险等级 */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-yellow-500/10 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-400" />
            </div>
            <div>
              <div className="text-sm text-gray-400">风险等级</div>
              <div className="text-2xl font-bold">
                <span className={`inline-block px-3 py-1 rounded-full text-sm ${getRiskColor(profileData?.risks?.overall_risk_level)}`}>
                  {profileData?.risks?.overall_risk_level?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            {(
              (profileData?.risks?.environmental_risks?.length || 0) +
              (profileData?.risks?.capacity_risks?.length || 0) +
              (profileData?.risks?.policy_risks?.length || 0) +
              (profileData?.risks?.market_risks?.length || 0)
            )} 个风险点
          </div>
        </div>

        {/* 机会等级 */}
        <div className="glass-card p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-green-500/10 rounded-lg">
              <Lightbulb className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <div className="text-sm text-gray-400">机会等级</div>
              <div className="text-2xl font-bold">
                <span className={`inline-block px-3 py-1 rounded-full text-sm ${getOpportunityColor(profileData?.opportunities?.overall_opportunity_level)}`}>
                  {profileData?.opportunities?.overall_opportunity_level?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            {(
              (profileData?.opportunities?.policy_opportunities?.length || 0) +
              (profileData?.opportunities?.market_opportunities?.length || 0) +
              (profileData?.opportunities?.technology_opportunities?.length || 0)
            )} 个机会点
          </div>
        </div>
      </div>

      {/* 企业画像摘要 */}
      {profileData?.summary && (
        <div className="glass-card p-6 mb-8">
          <h3 className="text-xl font-bold mb-4 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-primary-400" />
            <span>企业画像摘要</span>
          </h3>
          <pre className="text-gray-300 whitespace-pre-wrap font-sans">
            {profileData.summary}
          </pre>
        </div>
      )}

      {/* 核心竞争力 */}
      <div className="glass-card p-6 mb-8">
        <h3 className="text-xl font-bold mb-6 flex items-center space-x-2">
          <Award className="w-5 h-5 text-primary-400" />
          <span>核心竞争力分析</span>
        </h3>

        {/* 核心优势 */}
        {profileData?.competitiveness?.strengths?.length > 0 && (
          <div className="mb-6">
            <h4 className="text-lg font-semibold mb-4 text-gray-300">核心优势</h4>
            <div className="space-y-4">
              {profileData.competitiveness.strengths.map((strength: any, index: number) => (
                <div key={index} className="bg-primary-500/5 border border-primary-500/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-primary-400">{strength.type}</span>
                    <span className="text-sm text-gray-400">得分: {strength.score}</span>
                  </div>
                  <p className="text-gray-300 text-sm">{strength.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 核心能力 */}
        {profileData?.competitiveness?.core_capabilities?.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold mb-4 text-gray-300">核心能力</h4>
            <div className="flex flex-wrap gap-2">
              {profileData.competitiveness.core_capabilities.map((capability: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-500/10 text-primary-400 rounded-full text-sm"
                >
                  {capability}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 风险识别 */}
      <div className="glass-card p-6 mb-8">
        <h3 className="text-xl font-bold mb-6 flex items-center space-x-2">
          <Shield className="w-5 h-5 text-yellow-400" />
          <span>风险识别</span>
        </h3>

        <div className="space-y-6">
          {/* 环保风险 */}
          {profileData?.risks?.environmental_risks?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">环保风险</h4>
              <div className="space-y-3">
                {profileData.risks.environmental_risks.map((risk: any, index: number) => (
                  <div key={index} className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-yellow-400">{risk.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getRiskColor(risk.level)}`}>
                        {risk.level.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{risk.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">缓解措施:</span> {risk.mitigation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 产能风险 */}
          {profileData?.risks?.capacity_risks?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">产能风险</h4>
              <div className="space-y-3">
                {profileData.risks.capacity_risks.map((risk: any, index: number) => (
                  <div key={index} className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-yellow-400">{risk.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getRiskColor(risk.level)}`}>
                        {risk.level.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{risk.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">缓解措施:</span> {risk.mitigation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 政策风险 */}
          {profileData?.risks?.policy_risks?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">政策风险</h4>
              <div className="space-y-3">
                {profileData.risks.policy_risks.map((risk: any, index: number) => (
                  <div key={index} className="bg-red-500/5 border border-red-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-red-400">{risk.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getRiskColor(risk.level)}`}>
                        {risk.level.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{risk.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">缓解措施:</span> {risk.mitigation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 市场风险 */}
          {profileData?.risks?.market_risks?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">市场风险</h4>
              <div className="space-y-3">
                {profileData.risks.market_risks.map((risk: any, index: number) => (
                  <div key={index} className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-yellow-400">{risk.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getRiskColor(risk.level)}`}>
                        {risk.level.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{risk.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">缓解措施:</span> {risk.mitigation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 发展机会 */}
      <div className="glass-card p-6 mb-8">
        <h3 className="text-xl font-bold mb-6 flex items-center space-x-2">
          <Target className="w-5 h-5 text-green-400" />
          <span>发展机会</span>
        </h3>

        <div className="space-y-6">
          {/* 政策机会 */}
          {profileData?.opportunities?.policy_opportunities?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">政策机会</h4>
              <div className="space-y-3">
                {profileData.opportunities.policy_opportunities.map((opp: any, index: number) => (
                  <div key={index} className="bg-green-500/5 border border-green-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-green-400">{opp.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getOpportunityColor(opp.potential)}`}>
                        {opp.potential.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{opp.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">行动建议:</span> {opp.action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 市场机会 */}
          {profileData?.opportunities?.market_opportunities?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">市场机会</h4>
              <div className="space-y-3">
                {profileData.opportunities.market_opportunities.map((opp: any, index: number) => (
                  <div key={index} className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-blue-400">{opp.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getOpportunityColor(opp.potential)}`}>
                        {opp.potential.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{opp.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">行动建议:</span> {opp.action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 技术机会 */}
          {profileData?.opportunities?.technology_opportunities?.length > 0 && (
            <div>
              <h4 className="text-lg font-semibold mb-4 text-gray-300">技术机会</h4>
              <div className="space-y-3">
                {profileData.opportunities.technology_opportunities.map((opp: any, index: number) => (
                  <div key={index} className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-purple-400">{opp.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getOpportunityColor(opp.potential)}`}>
                        {opp.potential.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-2">{opp.description}</p>
                    <p className="text-gray-400 text-xs">
                      <span className="font-semibold">行动建议:</span> {opp.action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 数据来源 */}
      {profileData?.data_sources && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">数据来源</h3>
          <div className="flex flex-wrap gap-2">
            {profileData.data_sources.map((source: string, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-500/10 text-gray-400 rounded-full text-sm"
              >
                {source}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
