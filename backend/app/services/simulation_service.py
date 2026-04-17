"""
数字分身沙盘模拟服务
Digital Twin Sandbox Simulation Service
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class SimulationService:
    """数字分身沙盘模拟服务"""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== 财务模型 ====================
    
    def build_financial_model(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建企业财务模型
        
        Args:
            company_data: 企业数据
            
        Returns:
            财务模型数据
        """
        # 基础假设
        assumptions = {
            'production_capacity': company_data.get('production_capacity', 1000000),  # 产能（吨/年）
            'capacity_utilization': 0.85,  # 产能利用率
            'product_price': 5000,  # 产品价格（元/吨）
            'raw_material_cost_ratio': 0.45,  # 原材料成本占比
            'labor_cost_ratio': 0.15,  # 人工成本占比
            'energy_cost_ratio': 0.20,  # 能源成本占比
            'other_cost_ratio': 0.10,  # 其他成本占比
            'tax_rate': 0.25,  # 税率
            'carbon_emission_factor': 2.5,  # 碳排放系数（吨CO2/吨产品）
        }
        
        # 根据企业类型调整参数
        industry = company_data.get('industry', '')
        if '煤' in industry or '化工' in industry:
            assumptions['carbon_emission_factor'] = 3.0
            assumptions['energy_cost_ratio'] = 0.25
        elif '新能源' in industry or '光伏' in industry:
            assumptions['carbon_emission_factor'] = 0.5
            assumptions['energy_cost_ratio'] = 0.10
        
        # 计算基准财务指标
        production = assumptions['production_capacity'] * assumptions['capacity_utilization']
        revenue = production * assumptions['product_price']
        
        raw_material_cost = revenue * assumptions['raw_material_cost_ratio']
        labor_cost = revenue * assumptions['labor_cost_ratio']
        energy_cost = revenue * assumptions['energy_cost_ratio']
        other_cost = revenue * assumptions['other_cost_ratio']
        
        total_cost = raw_material_cost + labor_cost + energy_cost + other_cost
        gross_profit = revenue - total_cost
        tax = gross_profit * assumptions['tax_rate']
        net_profit = gross_profit - tax
        
        # 计算ROE和ROI（假设净资产为净利润的10倍）
        net_assets = net_profit * 10
        roe = (net_profit / net_assets * 100) if net_assets > 0 else 0
        roi = (net_profit / revenue * 100) if revenue > 0 else 0
        
        # 计算碳排放
        carbon_emission = production * assumptions['carbon_emission_factor']
        
        return {
            'assumptions': assumptions,
            'production': production,
            'revenue': revenue,
            'costs': {
                'raw_material': raw_material_cost,
                'labor': labor_cost,
                'energy': energy_cost,
                'other': other_cost,
                'total': total_cost
            },
            'gross_profit': gross_profit,
            'tax': tax,
            'net_profit': net_profit,
            'net_assets': net_assets,
            'roe': round(roe, 2),
            'roi': round(roi, 2),
            'carbon_emission': carbon_emission
        }
    
    # ==================== 政策影响模型 ====================
    
    def apply_policy_impact(self, base_model: Dict[str, Any], policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        应用政策影响
        
        Args:
            base_model: 基准财务模型
            policies: 政策列表
            
        Returns:
            应用政策后的财务模型
        """
        model = base_model.copy()
        policy_impacts = []
        
        for policy in policies:
            policy_type = policy.get('type')
            
            if policy_type == 'carbon_tax':
                # 碳税政策
                impact = self._apply_carbon_tax(model, policy)
                policy_impacts.append(impact)
                
            elif policy_type == 'subsidy':
                # 补贴政策
                impact = self._apply_subsidy(model, policy)
                policy_impacts.append(impact)
                
            elif policy_type == 'quota':
                # 配额政策
                impact = self._apply_quota(model, policy)
                policy_impacts.append(impact)
                
            elif policy_type == 'electricity_price':
                # 电价政策
                impact = self._apply_electricity_price(model, policy)
                policy_impacts.append(impact)
        
        # 重新计算财务指标
        model = self._recalculate_financials(model)
        model['policy_impacts'] = policy_impacts
        
        return model
    
    def _apply_carbon_tax(self, model: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """应用碳税政策"""
        tax_rate = policy.get('rate', 50)  # 元/吨CO2
        carbon_emission = model['carbon_emission']
        carbon_tax_cost = carbon_emission * tax_rate
        
        # 增加成本
        model['costs']['carbon_tax'] = carbon_tax_cost
        model['costs']['total'] += carbon_tax_cost
        
        return {
            'type': 'carbon_tax',
            'name': '碳税政策',
            'description': f'碳税税率: {tax_rate}元/吨CO2',
            'impact': -carbon_tax_cost,
            'impact_ratio': -(carbon_tax_cost / model['revenue'] * 100)
        }
    
    def _apply_subsidy(self, model: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """应用补贴政策"""
        subsidy_type = policy.get('subsidy_type', 'production')
        subsidy_rate = policy.get('rate', 100)  # 元/吨
        
        if subsidy_type == 'production':
            subsidy_amount = model['production'] * subsidy_rate
        else:
            subsidy_amount = model['revenue'] * (subsidy_rate / 100)
        
        # 增加收入
        model['revenue'] += subsidy_amount
        model['subsidy_income'] = subsidy_amount
        
        return {
            'type': 'subsidy',
            'name': '补贴政策',
            'description': f'补贴类型: {subsidy_type}, 补贴标准: {subsidy_rate}',
            'impact': subsidy_amount,
            'impact_ratio': (subsidy_amount / model['revenue'] * 100)
        }
    
    def _apply_quota(self, model: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """应用配额政策"""
        quota = policy.get('quota', model['carbon_emission'] * 0.9)  # 配额（吨CO2）
        penalty_rate = policy.get('penalty_rate', 100)  # 超额惩罚（元/吨CO2）
        
        excess_emission = max(0, model['carbon_emission'] - quota)
        penalty_cost = excess_emission * penalty_rate
        
        # 增加成本
        if penalty_cost > 0:
            model['costs']['quota_penalty'] = penalty_cost
            model['costs']['total'] += penalty_cost
        
        return {
            'type': 'quota',
            'name': '配额政策',
            'description': f'配额: {quota}吨CO2, 超额惩罚: {penalty_rate}元/吨',
            'impact': -penalty_cost,
            'impact_ratio': -(penalty_cost / model['revenue'] * 100) if penalty_cost > 0 else 0
        }
    
    def _apply_electricity_price(self, model: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
        """应用电价政策"""
        price_change = policy.get('change', 0)  # 电价变化百分比
        
        # 假设能源成本中50%是电力成本
        electricity_cost = model['costs']['energy'] * 0.5
        cost_change = electricity_cost * (price_change / 100)
        
        # 调整能源成本
        model['costs']['energy'] += cost_change
        model['costs']['total'] += cost_change
        
        return {
            'type': 'electricity_price',
            'name': '电价政策',
            'description': f'电价变化: {price_change:+.1f}%',
            'impact': -cost_change,
            'impact_ratio': -(cost_change / model['revenue'] * 100)
        }
    
    # ==================== 价格波动模型 ====================
    
    def apply_price_changes(self, base_model: Dict[str, Any], price_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        应用价格变化
        
        Args:
            base_model: 基准财务模型
            price_changes: 价格变化列表
            
        Returns:
            应用价格变化后的财务模型
        """
        model = base_model.copy()
        price_impacts = []
        
        for price_change in price_changes:
            price_type = price_change.get('type')
            change_percent = price_change.get('change', 0)
            
            if price_type == 'product':
                # 产品价格变化
                impact = self._apply_product_price_change(model, change_percent)
                price_impacts.append(impact)
                
            elif price_type == 'raw_material':
                # 原材料价格变化
                impact = self._apply_raw_material_price_change(model, change_percent)
                price_impacts.append(impact)
                
            elif price_type == 'energy':
                # 能源价格变化
                impact = self._apply_energy_price_change(model, change_percent)
                price_impacts.append(impact)
        
        # 重新计算财务指标
        model = self._recalculate_financials(model)
        model['price_impacts'] = price_impacts
        
        return model
    
    def _apply_product_price_change(self, model: Dict[str, Any], change_percent: float) -> Dict[str, Any]:
        """应用产品价格变化"""
        revenue_change = model['revenue'] * (change_percent / 100)
        model['revenue'] += revenue_change
        
        return {
            'type': 'product',
            'name': '产品价格变化',
            'description': f'价格变化: {change_percent:+.1f}%',
            'impact': revenue_change,
            'impact_ratio': change_percent
        }
    
    def _apply_raw_material_price_change(self, model: Dict[str, Any], change_percent: float) -> Dict[str, Any]:
        """应用原材料价格变化"""
        cost_change = model['costs']['raw_material'] * (change_percent / 100)
        model['costs']['raw_material'] += cost_change
        model['costs']['total'] += cost_change
        
        return {
            'type': 'raw_material',
            'name': '原材料价格变化',
            'description': f'价格变化: {change_percent:+.1f}%',
            'impact': -cost_change,
            'impact_ratio': -(cost_change / model['revenue'] * 100)
        }
    
    def _apply_energy_price_change(self, model: Dict[str, Any], change_percent: float) -> Dict[str, Any]:
        """应用能源价格变化"""
        cost_change = model['costs']['energy'] * (change_percent / 100)
        model['costs']['energy'] += cost_change
        model['costs']['total'] += cost_change
        
        return {
            'type': 'energy',
            'name': '能源价格变化',
            'description': f'价格变化: {change_percent:+.1f}%',
            'impact': -cost_change,
            'impact_ratio': -(cost_change / model['revenue'] * 100)
        }
    
    # ==================== 辅助方法 ====================
    
    def _recalculate_financials(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """重新计算财务指标"""
        model['gross_profit'] = model['revenue'] - model['costs']['total']
        model['tax'] = model['gross_profit'] * model['assumptions']['tax_rate']
        model['net_profit'] = model['gross_profit'] - model['tax']
        
        # 重新计算ROE和ROI
        if model['net_assets'] > 0:
            model['roe'] = round(model['net_profit'] / model['net_assets'] * 100, 2)
        else:
            model['roe'] = 0
            
        if model['revenue'] > 0:
            model['roi'] = round(model['net_profit'] / model['revenue'] * 100, 2)
        else:
            model['roi'] = 0
        
        return model
    
    # ==================== 场景模拟 ====================
    
    def simulate_scenario(self, company_id: int, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟场景
        
        Args:
            company_id: 企业ID
            scenario_config: 场景配置
            
        Returns:
            模拟结果
        """
        # 获取企业数据
        company = self.db.session.execute(
            'SELECT * FROM companies WHERE id = :id',
            {'id': company_id}
        ).fetchone()
        
        if not company:
            raise ValueError(f'企业不存在: {company_id}')
        
        company_data = dict(company)
        
        # 构建基准财务模型
        base_model = self.build_financial_model(company_data)
        
        # 应用政策影响
        policies = scenario_config.get('policies', [])
        if policies:
            simulated_model = self.apply_policy_impact(base_model.copy(), policies)
        else:
            simulated_model = base_model.copy()
        
        # 应用价格变化
        price_changes = scenario_config.get('price_changes', [])
        if price_changes:
            simulated_model = self.apply_price_changes(simulated_model, price_changes)
        
        # 生成时间序列数据
        time_range = scenario_config.get('time_range', 3)
        time_series = self._generate_time_series(base_model, simulated_model, time_range)
        
        # 计算影响
        impact = self._calculate_impact(base_model, simulated_model)
        
        return {
            'scenario_name': scenario_config.get('name', '未命名场景'),
            'scenario_description': scenario_config.get('description', ''),
            'company_name': company_data.get('name', ''),
            'base_case': self._format_model_output(base_model),
            'simulated_case': self._format_model_output(simulated_model),
            'impact': impact,
            'time_series': time_series,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_time_series(self, base_model: Dict[str, Any], simulated_model: Dict[str, Any], years: int) -> List[Dict[str, Any]]:
        """生成时间序列数据"""
        time_series = []
        
        base_profit = base_model['net_profit']
        simulated_profit = simulated_model['net_profit']
        
        for year in range(1, years + 1):
            # 假设影响逐年递增
            impact_factor = year / years
            
            year_profit = base_profit + (simulated_profit - base_profit) * impact_factor
            year_roe = (year_profit / base_model['net_assets'] * 100) if base_model['net_assets'] > 0 else 0
            year_roi = (year_profit / base_model['revenue'] * 100) if base_model['revenue'] > 0 else 0
            
            time_series.append({
                'year': year,
                'profit': round(year_profit, 2),
                'roe': round(year_roe, 2),
                'roi': round(year_roi, 2)
            })
        
        return time_series
    
    def _calculate_impact(self, base_model: Dict[str, Any], simulated_model: Dict[str, Any]) -> Dict[str, Any]:
        """计算影响"""
        return {
            'revenue_change': round(simulated_model['revenue'] - base_model['revenue'], 2),
            'revenue_change_percent': round((simulated_model['revenue'] - base_model['revenue']) / base_model['revenue'] * 100, 2) if base_model['revenue'] > 0 else 0,
            'cost_change': round(simulated_model['costs']['total'] - base_model['costs']['total'], 2),
            'cost_change_percent': round((simulated_model['costs']['total'] - base_model['costs']['total']) / base_model['costs']['total'] * 100, 2) if base_model['costs']['total'] > 0 else 0,
            'profit_change': round(simulated_model['net_profit'] - base_model['net_profit'], 2),
            'profit_change_percent': round((simulated_model['net_profit'] - base_model['net_profit']) / base_model['net_profit'] * 100, 2) if base_model['net_profit'] > 0 else 0,
            'roe_change': round(simulated_model['roe'] - base_model['roe'], 2),
            'roi_change': round(simulated_model['roi'] - base_model['roi'], 2)
        }
    
    def _format_model_output(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """格式化模型输出"""
        return {
            'revenue': round(model['revenue'], 2),
            'total_cost': round(model['costs']['total'], 2),
            'gross_profit': round(model['gross_profit'], 2),
            'net_profit': round(model['net_profit'], 2),
            'roe': model['roe'],
            'roi': model['roi'],
            'cost_breakdown': {
                'raw_material': round(model['costs']['raw_material'], 2),
                'labor': round(model['costs']['labor'], 2),
                'energy': round(model['costs']['energy'], 2),
                'other': round(model['costs']['other'], 2)
            }
        }
    
    # ==================== 场景对比 ====================
    
    def compare_scenarios(self, company_id: int, scenario_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对比多个场景
        
        Args:
            company_id: 企业ID
            scenario_configs: 场景配置列表
            
        Returns:
            对比结果
        """
        scenarios = []
        
        for config in scenario_configs:
            result = self.simulate_scenario(company_id, config)
            scenarios.append(result)
        
        # 找出最优和最差场景
        best_scenario = max(scenarios, key=lambda x: x['simulated_case']['net_profit'])
        worst_scenario = min(scenarios, key=lambda x: x['simulated_case']['net_profit'])
        
        return {
            'scenarios': scenarios,
            'best_scenario': best_scenario['scenario_name'],
            'worst_scenario': worst_scenario['scenario_name'],
            'comparison_summary': {
                'profit_range': {
                    'min': worst_scenario['simulated_case']['net_profit'],
                    'max': best_scenario['simulated_case']['net_profit'],
                    'diff': best_scenario['simulated_case']['net_profit'] - worst_scenario['simulated_case']['net_profit']
                },
                'roe_range': {
                    'min': worst_scenario['simulated_case']['roe'],
                    'max': best_scenario['simulated_case']['roe'],
                    'diff': best_scenario['simulated_case']['roe'] - worst_scenario['simulated_case']['roe']
                }
            }
        }
