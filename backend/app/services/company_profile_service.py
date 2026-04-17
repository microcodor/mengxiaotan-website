# -*- coding: utf-8 -*-
"""
企业画像服务
基于公开信息构建企业画像，包括核心竞争力分析、风险识别和机会分析
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)


class CompanyProfileService:
    """企业画像服务类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def build_company_profile(self, company_id: int) -> Dict:
        """
        构建企业画像
        
        Args:
            company_id: 企业ID
            
        Returns:
            企业画像数据
        """
        from app.models import Company
        from app import db
        
        company = Company.query.get(company_id)
        if not company:
            raise ValueError('企业不存在')
        
        logger.info(f"开始构建企业画像: {company.name} (ID: {company_id})")
        
        # 1. 收集基础信息
        basic_info = self._collect_basic_info(company)
        
        # 2. 分析核心竞争力
        competitiveness = self._analyze_competitiveness(company, basic_info)
        
        # 3. 识别风险
        risks = self._identify_risks(company, basic_info)
        
        # 4. 识别机会
        opportunities = self._identify_opportunities(company, basic_info)
        
        # 5. 生成综合评分
        score = self._calculate_overall_score(competitiveness, risks, opportunities)
        
        profile = {
            'company_id': company_id,
            'company_name': company.name,
            'basic_info': basic_info,
            'competitiveness': competitiveness,
            'risks': risks,
            'opportunities': opportunities,
            'overall_score': score,
            'generated_at': datetime.utcnow().isoformat(),
            'data_sources': self._get_data_sources()
        }
        
        logger.info(f"企业画像构建完成: {company.name}, 综合评分: {score}")
        
        return profile
    
    def _collect_basic_info(self, company) -> Dict:
        """
        收集企业基础信息
        
        Args:
            company: 企业对象
            
        Returns:
            基础信息字典
        """
        logger.info(f"收集企业基础信息: {company.name}")
        
        basic_info = {
            'name': company.name,
            'short_name': company.short_name,
            'unified_social_credit_code': company.unified_social_credit_code,
            'legal_representative': company.legal_representative,
            'registered_capital': company.registered_capital,
            'establishment_date': company.establishment_date.isoformat() if company.establishment_date else None,
            'industry': company.industry,
            'industry_category': company.industry_category,
            'employee_count': company.employee_count,
            'annual_revenue': company.annual_revenue,
            'province': company.province,
            'city': company.city,
            'website': company.website,
            'description': company.description,
            'is_verified': company.is_verified
        }
        
        # 收集业务信息
        businesses = []
        for business in company.businesses:
            if business.is_active:
                businesses.append({
                    'type': business.business_type,
                    'name': business.business_name,
                    'scope': business.business_scope,
                    'annual_output': business.annual_output,
                    'market_share': business.market_share,
                    'is_primary': business.is_primary
                })
        
        basic_info['businesses'] = businesses
        
        return basic_info
    
    def _analyze_competitiveness(self, company, basic_info: Dict) -> Dict:
        """
        分析企业核心竞争力
        
        Args:
            company: 企业对象
            basic_info: 基础信息
            
        Returns:
            竞争力分析结果
        """
        logger.info(f"分析企业核心竞争力: {company.name}")
        
        competitiveness = {
            'strengths': [],
            'core_capabilities': [],
            'market_position': {},
            'technology_level': {},
            'score': 0
        }
        
        # 1. 分析企业规模优势
        if basic_info.get('employee_count'):
            employee_count = self._parse_count(basic_info['employee_count'])
            if employee_count >= 1000:
                competitiveness['strengths'].append({
                    'type': '规模优势',
                    'description': f"员工规模达{basic_info['employee_count']}，具有显著的规模优势",
                    'score': 8
                })
            elif employee_count >= 500:
                competitiveness['strengths'].append({
                    'type': '规模优势',
                    'description': f"员工规模{basic_info['employee_count']}，具有一定规模优势",
                    'score': 6
                })
        
        # 2. 分析业务多元化
        businesses = basic_info.get('businesses', [])
        if len(businesses) >= 3:
            competitiveness['strengths'].append({
                'type': '业务多元化',
                'description': f"拥有{len(businesses)}项业务，业务结构多元化",
                'score': 7
            })
            competitiveness['core_capabilities'].append('多元化经营能力')
        
        # 3. 分析主营业务
        primary_businesses = [b for b in businesses if b.get('is_primary')]
        if primary_businesses:
            for business in primary_businesses:
                if business.get('market_share'):
                    competitiveness['market_position'][business['name']] = {
                        'market_share': business['market_share'],
                        'annual_output': business.get('annual_output', '未知')
                    }
                    competitiveness['core_capabilities'].append(f"{business['name']}领域经验")
        
        # 4. 分析行业地位
        if basic_info.get('industry_category'):
            category = basic_info['industry_category']
            if '能源' in category or '电力' in category:
                competitiveness['strengths'].append({
                    'type': '行业定位',
                    'description': f"处于{category}行业，符合国家能源战略方向",
                    'score': 8
                })
        
        # 5. 分析地理位置优势
        if basic_info.get('province'):
            province = basic_info['province']
            # 能源资源丰富的省份
            energy_provinces = ['内蒙古', '山西', '陕西', '新疆', '宁夏', '青海']
            if any(p in province for p in energy_provinces):
                competitiveness['strengths'].append({
                    'type': '地理优势',
                    'description': f"位于{province}，能源资源丰富，具有地理位置优势",
                    'score': 7
                })
        
        # 6. 计算竞争力综合得分
        total_score = sum(s['score'] for s in competitiveness['strengths'])
        competitiveness['score'] = min(100, total_score * 10)  # 归一化到100分
        
        return competitiveness
    
    def _identify_risks(self, company, basic_info: Dict) -> Dict:
        """
        识别企业风险
        
        Args:
            company: 企业对象
            basic_info: 基础信息
            
        Returns:
            风险识别结果
        """
        logger.info(f"识别企业风险: {company.name}")
        
        risks = {
            'environmental_risks': [],
            'capacity_risks': [],
            'policy_risks': [],
            'market_risks': [],
            'overall_risk_level': 'low'  # low, medium, high
        }
        
        # 1. 环保风险（基于行业）
        industry = basic_info.get('industry', '')
        high_pollution_industries = ['煤炭', '钢铁', '化工', '水泥']
        if any(ind in industry for ind in high_pollution_industries):
            risks['environmental_risks'].append({
                'type': '环保合规风险',
                'description': f"{industry}行业面临严格的环保监管，需关注环保合规成本",
                'level': 'medium',
                'mitigation': '建议加强环保设施投入，关注最新环保政策'
            })
        
        # 2. 产能过剩风险
        businesses = basic_info.get('businesses', [])
        overcapacity_sectors = ['煤炭', '钢铁', '水泥', '电解铝']
        for business in businesses:
            business_type = business.get('type', '')
            if any(sector in business_type for sector in overcapacity_sectors):
                risks['capacity_risks'].append({
                    'type': '产能过剩风险',
                    'description': f"{business_type}领域存在产能过剩风险",
                    'level': 'medium',
                    'mitigation': '建议优化产能结构，提升产品附加值'
                })
        
        # 3. 政策风险（双碳目标）
        if '煤炭' in industry or '火电' in industry:
            risks['policy_risks'].append({
                'type': '双碳政策风险',
                'description': '双碳目标下，传统能源行业面临转型压力',
                'level': 'high',
                'mitigation': '建议加快清洁能源转型，布局新能源业务'
            })
        
        # 4. 市场风险（价格波动）
        if '煤炭' in industry or '石油' in industry or '天然气' in industry:
            risks['market_risks'].append({
                'type': '价格波动风险',
                'description': '能源价格波动可能影响企业盈利能力',
                'level': 'medium',
                'mitigation': '建议建立价格对冲机制，优化采购策略'
            })
        
        # 5. 计算整体风险等级
        all_risks = (
            risks['environmental_risks'] + 
            risks['capacity_risks'] + 
            risks['policy_risks'] + 
            risks['market_risks']
        )
        
        high_risk_count = sum(1 for r in all_risks if r['level'] == 'high')
        medium_risk_count = sum(1 for r in all_risks if r['level'] == 'medium')
        
        if high_risk_count >= 2:
            risks['overall_risk_level'] = 'high'
        elif high_risk_count >= 1 or medium_risk_count >= 3:
            risks['overall_risk_level'] = 'medium'
        else:
            risks['overall_risk_level'] = 'low'
        
        return risks
    
    def _identify_opportunities(self, company, basic_info: Dict) -> Dict:
        """
        识别企业机会
        
        Args:
            company: 企业对象
            basic_info: 基础信息
            
        Returns:
            机会识别结果
        """
        logger.info(f"识别企业机会: {company.name}")
        
        opportunities = {
            'policy_opportunities': [],
            'market_opportunities': [],
            'technology_opportunities': [],
            'overall_opportunity_level': 'medium'  # low, medium, high
        }
        
        industry = basic_info.get('industry', '')
        businesses = basic_info.get('businesses', [])
        
        # 1. 政策机会
        # 新能源政策支持
        new_energy_keywords = ['光伏', '风电', '储能', '氢能', '新能源']
        if any(keyword in industry for keyword in new_energy_keywords):
            opportunities['policy_opportunities'].append({
                'type': '新能源政策支持',
                'description': '国家大力支持新能源发展，行业前景广阔',
                'potential': 'high',
                'action': '建议加大新能源项目投资，抓住政策红利'
            })
        
        # 双碳目标机会
        if any(keyword in industry for keyword in ['节能', '环保', '清洁能源', 'CCUS']):
            opportunities['policy_opportunities'].append({
                'type': '双碳目标机会',
                'description': '双碳目标下，节能环保产业迎来发展机遇',
                'potential': 'high',
                'action': '建议布局碳减排、碳交易相关业务'
            })
        
        # 2. 市场机会
        # 能源转型机会
        if '煤炭' in industry or '火电' in industry:
            opportunities['market_opportunities'].append({
                'type': '能源转型机会',
                'description': '传统能源企业可向清洁能源转型',
                'potential': 'medium',
                'action': '建议探索煤电灵活性改造、煤制氢等转型路径'
            })
        
        # 区域市场机会
        province = basic_info.get('province', '')
        if province in ['内蒙古', '新疆', '青海', '甘肃']:
            opportunities['market_opportunities'].append({
                'type': '区域市场机会',
                'description': f"{province}是国家重要的能源基地，市场潜力大",
                'potential': 'high',
                'action': '建议深耕本地市场，拓展外送通道'
            })
        
        # 3. 技术机会
        # 数字化转型
        opportunities['technology_opportunities'].append({
            'type': '数字化转型',
            'description': '能源行业数字化、智能化转型加速',
            'potential': 'medium',
            'action': '建议投资智能化改造，提升运营效率'
        })
        
        # AI算力需求
        if '电力' in industry or '数据中心' in industry:
            opportunities['technology_opportunities'].append({
                'type': 'AI算力需求',
                'description': 'AI发展带动电力需求增长',
                'potential': 'high',
                'action': '建议关注数据中心、AI算力中心的电力供应需求'
            })
        
        # 4. 计算整体机会等级
        all_opportunities = (
            opportunities['policy_opportunities'] + 
            opportunities['market_opportunities'] + 
            opportunities['technology_opportunities']
        )
        
        high_potential_count = sum(1 for o in all_opportunities if o['potential'] == 'high')
        
        if high_potential_count >= 3:
            opportunities['overall_opportunity_level'] = 'high'
        elif high_potential_count >= 1:
            opportunities['overall_opportunity_level'] = 'medium'
        else:
            opportunities['overall_opportunity_level'] = 'low'
        
        return opportunities
    
    def _calculate_overall_score(
        self, 
        competitiveness: Dict, 
        risks: Dict, 
        opportunities: Dict
    ) -> int:
        """
        计算企业综合评分
        
        Args:
            competitiveness: 竞争力分析
            risks: 风险识别
            opportunities: 机会识别
            
        Returns:
            综合评分 (0-100)
        """
        # 竞争力得分 (40%)
        comp_score = competitiveness.get('score', 0) * 0.4
        
        # 风险得分 (30%)
        risk_level = risks.get('overall_risk_level', 'medium')
        risk_score_map = {'low': 30, 'medium': 20, 'high': 10}
        risk_score = risk_score_map.get(risk_level, 20)
        
        # 机会得分 (30%)
        opp_level = opportunities.get('overall_opportunity_level', 'medium')
        opp_score_map = {'low': 10, 'medium': 20, 'high': 30}
        opp_score = opp_score_map.get(opp_level, 20)
        
        overall_score = int(comp_score + risk_score + opp_score)
        
        return min(100, max(0, overall_score))
    
    def _get_data_sources(self) -> List[str]:
        """获取数据来源列表"""
        return [
            '企业工商信息',
            '企业官网',
            '公开财报',
            '招投标信息',
            '行业报告',
            '政策文件'
        ]
    
    def _parse_count(self, count_str: str) -> int:
        """
        解析数量字符串
        
        Args:
            count_str: 数量字符串，如 "1000-5000人"
            
        Returns:
            数量（取中间值）
        """
        if not count_str:
            return 0
        
        # 提取数字
        numbers = re.findall(r'\d+', count_str)
        if not numbers:
            return 0
        
        # 如果是范围，取中间值
        if len(numbers) >= 2:
            return (int(numbers[0]) + int(numbers[1])) // 2
        
        return int(numbers[0])
    
    def get_profile_summary(self, profile: Dict) -> str:
        """
        生成企业画像摘要
        
        Args:
            profile: 企业画像数据
            
        Returns:
            摘要文本
        """
        company_name = profile['company_name']
        score = profile['overall_score']
        
        # 评级
        if score >= 80:
            rating = '优秀'
        elif score >= 60:
            rating = '良好'
        elif score >= 40:
            rating = '一般'
        else:
            rating = '较差'
        
        # 核心优势
        strengths = profile['competitiveness']['strengths']
        strength_summary = '、'.join([s['type'] for s in strengths[:3]])
        
        # 主要风险
        risks = profile['risks']
        all_risks = (
            risks['environmental_risks'] + 
            risks['capacity_risks'] + 
            risks['policy_risks'] + 
            risks['market_risks']
        )
        risk_summary = '、'.join([r['type'] for r in all_risks[:3]])
        
        # 主要机会
        opportunities = profile['opportunities']
        all_opps = (
            opportunities['policy_opportunities'] + 
            opportunities['market_opportunities'] + 
            opportunities['technology_opportunities']
        )
        opp_summary = '、'.join([o['type'] for o in all_opps[:3]])
        
        summary = f"""
【企业画像摘要】

企业名称：{company_name}
综合评分：{score}分（{rating}）

核心优势：{strength_summary or '暂无'}
主要风险：{risk_summary or '暂无'}
发展机会：{opp_summary or '暂无'}

风险等级：{risks['overall_risk_level'].upper()}
机会等级：{opportunities['overall_opportunity_level'].upper()}
        """.strip()
        
        return summary
