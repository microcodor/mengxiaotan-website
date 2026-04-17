# -*- coding: utf-8 -*-
"""
订阅套餐迁移脚本
将旧的3个套餐（免费版、标准版、高级版）迁移到新的2个套餐（免费订阅、基础版）
"""
from app import create_app, db
from app.models import SubscriptionPlan, Subscription, User
from datetime import datetime

app = create_app()

with app.app_context():
    print("=" * 60)
    print("开始迁移订阅套餐...")
    print("=" * 60)
    
    # 1. 查询现有套餐
    old_plans = SubscriptionPlan.query.all()
    print(f"\n当前套餐数量: {len(old_plans)}")
    for plan in old_plans:
        print(f"  - {plan.name}: ¥{plan.price}/{plan.duration_days}天")
    
    # 2. 禁用旧套餐（不删除，保留历史数据）
    print("\n禁用旧套餐...")
    for plan in old_plans:
        plan.is_active = False
        print(f"  ✓ 已禁用: {plan.name}")
    db.session.commit()
    
    # 3. 创建新套餐
    print("\n创建新套餐...")
    
    new_plans = [
        SubscriptionPlan(
            name='免费订阅',
            price=0,
            duration_days=7,  # 限时7天试用
            features={
                '政策速览': '发改委最新通知、能源行业解读、双碳政策动向',
                '市场行情': '煤炭价格指数、油气期货走势、新能源装机数据',
                '热点聚焦': 'AI算力需求下的能源转型、储能技术突破、国际能源博弈',
                '蒙小碳简评': '3分钟提炼核心，关键数据标注，快速抓住重点',
                '推送时间': '每日9:00',
                '推送渠道': '企业微信/微信',
                '试用期限': '7天免费体验'
            },
            sort_order=1,
            is_active=True
        ),
        SubscriptionPlan(
            name='基础版',
            price=39,
            duration_days=30,  # 按月订阅
            features={
                '免费版全部功能': '包含所有免费订阅内容',
                '企业画像构建': '基于官网、财报、招投标信息，自动生成企业核心竞争力分析',
                '风险与机会识别': '环保处罚、产能过剩风险预警；政策适配性机会分析',
                '战略级内参': '定制报告2份/月（技术路线优化、区域市场布局建议）',
                '动态监测': '实时推送企业相关政策、价格波动预警',
                '数字分身沙盘': '模拟政策、价格波动对企业利润的影响，生成可视化报告',
                '订阅优惠': '按年订阅赠1个月（468元/年，相当于36元/月）',
                '推送渠道': '企业微信/微信'
            },
            sort_order=2,
            is_active=True
        ),
    ]
    
    for plan in new_plans:
        db.session.add(plan)
        print(f"  ✓ 已创建: {plan.name} (¥{plan.price}/{plan.duration_days}天)")
    
    db.session.commit()
    
    # 4. 查询新套餐ID
    free_plan = SubscriptionPlan.query.filter_by(name='免费订阅', is_active=True).first()
    basic_plan = SubscriptionPlan.query.filter_by(name='基础版', is_active=True).first()
    
    print(f"\n新套餐ID:")
    print(f"  - 免费订阅: {free_plan.id}")
    print(f"  - 基础版: {basic_plan.id}")
    
    # 5. 迁移现有用户订阅（可选）
    print("\n检查现有用户订阅...")
    active_subscriptions = Subscription.query.filter_by(status='active').all()
    print(f"活跃订阅数量: {len(active_subscriptions)}")
    
    if active_subscriptions:
        print("\n建议手动处理现有订阅，或运行以下迁移逻辑：")
        print("  - 旧免费版 → 新免费订阅（7天试用）")
        print("  - 旧标准版/高级版 → 新基础版（保留剩余天数）")
        
        # 如果需要自动迁移，取消下面的注释
        # for sub in active_subscriptions:
        #     old_plan_name = sub.plan.name
        #     if old_plan_name == '免费版':
        #         sub.plan_id = free_plan.id
        #         print(f"  ✓ 用户 {sub.user_id}: 免费版 → 免费订阅")
        #     elif old_plan_name in ['标准版', '高级版']:
        #         sub.plan_id = basic_plan.id
        #         print(f"  ✓ 用户 {sub.user_id}: {old_plan_name} → 基础版")
        # db.session.commit()
    
    # 6. 统计信息
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)
    
    all_plans = SubscriptionPlan.query.all()
    active_plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    
    print(f"\n套餐统计:")
    print(f"  - 总套餐数: {len(all_plans)}")
    print(f"  - 活跃套餐数: {len(active_plans)}")
    print(f"  - 已禁用套餐数: {len(all_plans) - len(active_plans)}")
    
    print(f"\n当前活跃套餐:")
    for plan in active_plans:
        print(f"  - {plan.name}: ¥{plan.price}/{plan.duration_days}天")
    
    print("\n" + "=" * 60)
    print("注意事项:")
    print("  1. 旧套餐已禁用但未删除，保留历史数据")
    print("  2. 现有用户订阅未自动迁移，请根据业务需求手动处理")
    print("  3. 新用户将使用新的套餐体系")
    print("=" * 60)
