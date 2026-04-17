# -*- coding: utf-8 -*-
"""
企业画像功能测试脚本
"""
from app import create_app, db
from app.models import Company, CompanyBusiness, User
from app.services.company_profile_service import CompanyProfileService
from datetime import date
import json

app = create_app()

with app.app_context():
    print("=" * 80)
    print("企业画像功能测试")
    print("=" * 80)
    
    # 1. 创建测试企业
    print("\n1. 创建测试企业")
    print("-" * 80)
    
    # 检查是否已存在测试企业
    test_company = Company.query.filter_by(name='测试能源集团').first()
    
    if not test_company:
        test_company = Company(
            name='测试能源集团',
            short_name='测试能源',
            unified_social_credit_code='91150000MA0N1234XY',
            legal_representative='张三',
            registered_capital='50亿元',
            establishment_date=date(2010, 1, 1),
            contact_person='李四',
            contact_phone='0471-1234567',
            contact_email='contact@test-energy.com',
            province='内蒙古',
            city='呼和浩特市',
            district='新城区',
            address='新华大街123号',
            employee_count='1000-5000人',
            annual_revenue='100-500亿元',
            industry='能源',
            industry_category='煤炭开采和洗选业',
            description='测试能源集团是一家综合性能源企业，主营煤炭开采、火力发电等业务。',
            website='https://www.test-energy.com',
            is_verified=True,
            status='active'
        )
        db.session.add(test_company)
        db.session.flush()
        
        # 添加业务信息
        businesses = [
            CompanyBusiness(
                company_id=test_company.id,
                business_type='煤炭开采',
                business_name='煤炭开采业务',
                business_scope='煤炭开采、洗选、销售',
                annual_output='年产煤炭2000万吨',
                market_share='区域市场份额15%',
                is_primary=True,
                is_active=True,
                sort_order=1
            ),
            CompanyBusiness(
                company_id=test_company.id,
                business_type='火力发电',
                business_name='火力发电业务',
                business_scope='火力发电、电力销售',
                annual_output='装机容量300万千瓦',
                market_share='区域市场份额8%',
                is_primary=True,
                is_active=True,
                sort_order=2
            ),
            CompanyBusiness(
                company_id=test_company.id,
                business_type='新能源',
                business_name='新能源业务',
                business_scope='光伏发电、风力发电',
                annual_output='装机容量50万千瓦',
                market_share='新兴业务',
                is_primary=False,
                is_active=True,
                sort_order=3
            )
        ]
        db.session.add_all(businesses)
        db.session.commit()
        
        print(f"  ✓ 创建测试企业: {test_company.name} (ID: {test_company.id})")
    else:
        print(f"  ✓ 使用现有测试企业: {test_company.name} (ID: {test_company.id})")
    
    # 2. 生成企业画像
    print("\n2. 生成企业画像")
    print("-" * 80)
    
    service = CompanyProfileService()
    
    try:
        profile = service.build_company_profile(test_company.id)
        
        print(f"  ✓ 企业画像生成成功")
        print(f"\n  企业名称: {profile['company_name']}")
        print(f"  综合评分: {profile['overall_score']}分")
        
        # 3. 显示竞争力分析
        print("\n3. 竞争力分析")
        print("-" * 80)
        comp = profile['competitiveness']
        print(f"  竞争力得分: {comp['score']}分")
        print(f"  核心优势数量: {len(comp['strengths'])}")
        
        if comp['strengths']:
            print("\n  核心优势:")
            for strength in comp['strengths']:
                print(f"    • {strength['type']}: {strength['description']} (得分: {strength['score']})")
        
        if comp['core_capabilities']:
            print(f"\n  核心能力: {', '.join(comp['core_capabilities'])}")
        
        # 4. 显示风险识别
        print("\n4. 风险识别")
        print("-" * 80)
        risks = profile['risks']
        print(f"  整体风险等级: {risks['overall_risk_level'].upper()}")
        
        all_risks = (
            risks['environmental_risks'] + 
            risks['capacity_risks'] + 
            risks['policy_risks'] + 
            risks['market_risks']
        )
        print(f"  识别风险数量: {len(all_risks)}")
        
        if all_risks:
            print("\n  主要风险:")
            for risk in all_risks:
                print(f"    • {risk['type']} ({risk['level'].upper()})")
                print(f"      {risk['description']}")
                print(f"      缓解措施: {risk['mitigation']}")
        
        # 5. 显示机会识别
        print("\n5. 机会识别")
        print("-" * 80)
        opps = profile['opportunities']
        print(f"  整体机会等级: {opps['overall_opportunity_level'].upper()}")
        
        all_opps = (
            opps['policy_opportunities'] + 
            opps['market_opportunities'] + 
            opps['technology_opportunities']
        )
        print(f"  识别机会数量: {len(all_opps)}")
        
        if all_opps:
            print("\n  主要机会:")
            for opp in all_opps:
                print(f"    • {opp['type']} ({opp['potential'].upper()})")
                print(f"      {opp['description']}")
                print(f"      行动建议: {opp['action']}")
        
        # 6. 显示摘要
        print("\n6. 企业画像摘要")
        print("-" * 80)
        summary = service.get_profile_summary(profile)
        print(summary)
        
        # 7. 保存完整画像到文件
        print("\n7. 保存画像数据")
        print("-" * 80)
        output_file = f"company_profile_{test_company.id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2, default=str)
        print(f"  ✓ 画像数据已保存到: {output_file}")
        
    except Exception as e:
        print(f"  ✗ 生成企业画像失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
