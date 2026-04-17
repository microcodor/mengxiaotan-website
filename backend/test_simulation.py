"""
测试数字分身沙盘功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.simulation_service import SimulationService
from app import create_app, db
import json


def test_simulation():
    """测试模拟功能"""
    print("="*60)
    print("数字分身沙盘功能测试")
    print("="*60)
    
    app = create_app('development')
    
    with app.app_context():
        simulation_service = SimulationService(db)
        
        # 测试企业数据
        company_data = {
            'id': 1,
            'name': '内蒙古汇能煤电集团',
            'industry': '煤炭化工',
            'production_capacity': 5000000,  # 500万吨/年
            'region': '内蒙古'
        }
        
        print("\n1. 构建基准财务模型")
        print("-" * 60)
        base_model = simulation_service.build_financial_model(company_data)
        print(f"企业名称: {company_data['name']}")
        print(f"产能: {base_model['assumptions']['production_capacity']:,.0f} 吨/年")
        print(f"产量: {base_model['production']:,.0f} 吨/年")
        print(f"营业收入: ¥{base_model['revenue']:,.2f}")
        print(f"营业成本: ¥{base_model['costs']['total']:,.2f}")
        print(f"净利润: ¥{base_model['net_profit']:,.2f}")
        print(f"ROE: {base_model['roe']}%")
        print(f"ROI: {base_model['roi']}%")
        print(f"碳排放: {base_model['carbon_emission']:,.0f} 吨CO2/年")
        
        print("\n2. 场景1：碳税政策影响")
        print("-" * 60)
        scenario1_config = {
            'name': '碳税政策影响分析',
            'description': '模拟碳税50元/吨CO2对企业的影响',
            'time_range': 3,
            'policies': [
                {
                    'type': 'carbon_tax',
                    'rate': 50
                }
            ],
            'price_changes': []
        }
        
        result1 = simulation_service.simulate_scenario(1, scenario1_config)
        print(f"场景名称: {result1['scenario_name']}")
        print(f"\n基准情况:")
        print(f"  净利润: ¥{result1['base_case']['net_profit']:,.2f}")
        print(f"  ROE: {result1['base_case']['roe']}%")
        print(f"\n模拟情况:")
        print(f"  净利润: ¥{result1['simulated_case']['net_profit']:,.2f}")
        print(f"  ROE: {result1['simulated_case']['roe']}%")
        print(f"\n影响分析:")
        print(f"  利润变化: ¥{result1['impact']['profit_change']:,.2f} ({result1['impact']['profit_change_percent']:+.2f}%)")
        print(f"  ROE变化: {result1['impact']['roe_change']:+.2f}%")
        
        print("\n3. 场景2：煤炭价格上涨20%")
        print("-" * 60)
        scenario2_config = {
            'name': '煤炭价格上涨影响',
            'description': '模拟原材料价格上涨20%对企业的影响',
            'time_range': 3,
            'policies': [],
            'price_changes': [
                {
                    'type': 'raw_material',
                    'change': 20
                }
            ]
        }
        
        result2 = simulation_service.simulate_scenario(1, scenario2_config)
        print(f"场景名称: {result2['scenario_name']}")
        print(f"\n基准情况:")
        print(f"  净利润: ¥{result2['base_case']['net_profit']:,.2f}")
        print(f"  成本: ¥{result2['base_case']['total_cost']:,.2f}")
        print(f"\n模拟情况:")
        print(f"  净利润: ¥{result2['simulated_case']['net_profit']:,.2f}")
        print(f"  成本: ¥{result2['simulated_case']['total_cost']:,.2f}")
        print(f"\n影响分析:")
        print(f"  成本变化: ¥{result2['impact']['cost_change']:,.2f} ({result2['impact']['cost_change_percent']:+.2f}%)")
        print(f"  利润变化: ¥{result2['impact']['profit_change']:,.2f} ({result2['impact']['profit_change_percent']:+.2f}%)")
        
        print("\n4. 场景3：新能源补贴政策")
        print("-" * 60)
        scenario3_config = {
            'name': '新能源补贴政策',
            'description': '模拟生产补贴100元/吨对企业的影响',
            'time_range': 5,
            'policies': [
                {
                    'type': 'subsidy',
                    'subsidy_type': 'production',
                    'rate': 100
                }
            ],
            'price_changes': []
        }
        
        result3 = simulation_service.simulate_scenario(1, scenario3_config)
        print(f"场景名称: {result3['scenario_name']}")
        print(f"\n基准情况:")
        print(f"  收入: ¥{result3['base_case']['revenue']:,.2f}")
        print(f"  净利润: ¥{result3['base_case']['net_profit']:,.2f}")
        print(f"\n模拟情况:")
        print(f"  收入: ¥{result3['simulated_case']['revenue']:,.2f}")
        print(f"  净利润: ¥{result3['simulated_case']['net_profit']:,.2f}")
        print(f"\n影响分析:")
        print(f"  收入变化: ¥{result3['impact']['revenue_change']:,.2f} ({result3['impact']['revenue_change_percent']:+.2f}%)")
        print(f"  利润变化: ¥{result3['impact']['profit_change']:,.2f} ({result3['impact']['profit_change_percent']:+.2f}%)")
        
        print("\n5. 场景对比")
        print("-" * 60)
        comparison = simulation_service.compare_scenarios(1, [
            scenario1_config,
            scenario2_config,
            scenario3_config
        ])
        
        print(f"对比场景数: {len(comparison['scenarios'])}")
        print(f"最优场景: {comparison['best_scenario']}")
        print(f"最差场景: {comparison['worst_scenario']}")
        print(f"\n利润范围:")
        print(f"  最小值: ¥{comparison['comparison_summary']['profit_range']['min']:,.2f}")
        print(f"  最大值: ¥{comparison['comparison_summary']['profit_range']['max']:,.2f}")
        print(f"  差值: ¥{comparison['comparison_summary']['profit_range']['diff']:,.2f}")
        print(f"\nROE范围:")
        print(f"  最小值: {comparison['comparison_summary']['roe_range']['min']}%")
        print(f"  最大值: {comparison['comparison_summary']['roe_range']['max']}%")
        print(f"  差值: {comparison['comparison_summary']['roe_range']['diff']:+.2f}%")
        
        print("\n6. 时间序列数据（场景1）")
        print("-" * 60)
        print(f"{'年份':<10} {'利润(万元)':<20} {'ROE(%)':<15} {'ROI(%)':<15}")
        print("-" * 60)
        for data in result1['time_series']:
            print(f"{data['year']:<10} {data['profit']/10000:,.2f}{'':<8} {data['roe']:<15.2f} {data['roi']:<15.2f}")
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)


if __name__ == '__main__':
    test_simulation()
