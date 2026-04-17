# -*- coding: utf-8 -*-
"""
订阅服务测试脚本
"""
from app import create_app, db
from app.models import User, SubscriptionPlan, Subscription
from app.services.subscription_service import SubscriptionService
from datetime import datetime

app = create_app()

with app.app_context():
    print("=" * 80)
    print("订阅服务测试")
    print("=" * 80)
    
    # 1. 测试套餐查询
    print("\n1. 查询活跃套餐")
    print("-" * 80)
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    for plan in plans:
        print(f"  • {plan.name} (ID: {plan.id})")
        print(f"    价格: ¥{plan.price}, 周期: {plan.duration_days}天")
    
    # 2. 测试金额计算
    print("\n2. 测试金额计算")
    print("-" * 80)
    basic_plan = SubscriptionPlan.query.filter_by(name='基础版', is_active=True).first()
    if basic_plan:
        monthly_amount = SubscriptionService.calculate_order_amount(basic_plan.id, 'monthly')
        yearly_amount = SubscriptionService.calculate_order_amount(basic_plan.id, 'yearly')
        print(f"  基础版月付: ¥{monthly_amount}")
        print(f"  基础版年付: ¥{yearly_amount}")
        
        monthly_days = SubscriptionService.calculate_duration_days(basic_plan.id, 'monthly')
        yearly_days = SubscriptionService.calculate_duration_days(basic_plan.id, 'yearly')
        print(f"  月付时长: {monthly_days}天")
        print(f"  年付时长: {yearly_days}天（赠1个月）")
    
    # 3. 测试用户订阅状态
    print("\n3. 测试用户订阅状态")
    print("-" * 80)
    test_user = User.query.filter_by(phone='13900139000').first()
    if test_user:
        status = SubscriptionService.get_user_subscription_status(test_user.id)
        print(f"  用户: {test_user.nickname} ({test_user.phone})")
        print(f"  有订阅: {status['has_subscription']}")
        if status['has_subscription']:
            print(f"  套餐: {status['plan_name']}")
            print(f"  是否试用: {status['is_trial']}")
            print(f"  剩余天数: {status['days_remaining']}天")
            print(f"  到期时间: {status['end_date']}")
        else:
            print(f"  可以试用: {status['can_trial']}")
            print(f"  提示: {status['trial_message']}")
    
    # 4. 测试试用订阅创建（如果可以）
    print("\n4. 测试试用订阅创建")
    print("-" * 80)
    if test_user:
        can_trial, message = SubscriptionService.can_start_trial(test_user.id)
        print(f"  可以试用: {can_trial}")
        print(f"  消息: {message}")
        
        if can_trial:
            try:
                result = SubscriptionService.create_trial_subscription(test_user.id)
                print(f"  ✓ 试用订阅创建成功")
                print(f"    订阅ID: {result['subscription_id']}")
                print(f"    开始时间: {result['start_date']}")
                print(f"    结束时间: {result['end_date']}")
                print(f"    时长: {result['duration_days']}天")
            except ValueError as e:
                print(f"  ✗ 创建失败: {e}")
    
    # 5. 测试即将到期的试用订阅
    print("\n5. 测试即将到期的试用订阅")
    print("-" * 80)
    expiring = SubscriptionService.check_trial_expiry()
    print(f"  即将到期数量: {len(expiring)}")
    for sub in expiring:
        print(f"  • 用户ID: {sub.user_id}, 到期时间: {sub.end_date}")
    
    # 6. 测试过期订阅处理
    print("\n6. 测试过期订阅处理")
    print("-" * 80)
    expired_count = SubscriptionService.expire_trial_subscriptions()
    print(f"  已过期数量: {expired_count}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
