# -*- coding: utf-8 -*-
"""
验证订阅套餐数据
"""
from app import create_app, db
from app.models import SubscriptionPlan
from datetime import datetime
import json

app = create_app()

with app.app_context():
    print("=" * 80)
    print("订阅套餐数据验证")
    print("=" * 80)
    
    # 查询所有套餐
    all_plans = SubscriptionPlan.query.order_by(SubscriptionPlan.id).all()
    
    print(f"\n总套餐数: {len(all_plans)}")
    print("\n" + "=" * 80)
    
    for plan in all_plans:
        status = "✅ 活跃" if plan.is_active else "❌ 已禁用"
        print(f"\n【{status}】 {plan.name} (ID: {plan.id})")
        print("-" * 80)
        print(f"价格: ¥{plan.price}")
        print(f"周期: {plan.duration_days}天")
        print(f"排序: {plan.sort_order}")
        print(f"创建时间: {plan.created_at}")
        print(f"\n功能列表:")
        
        if plan.features:
            for key, value in plan.features.items():
                print(f"  • {key}: {value}")
        else:
            print("  （无功能配置）")
    
    print("\n" + "=" * 80)
    print("活跃套餐统计")
    print("=" * 80)
    
    active_plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.sort_order).all()
    
    print(f"\n活跃套餐数: {len(active_plans)}\n")
    
    for plan in active_plans:
        print(f"{plan.sort_order}. {plan.name}")
        print(f"   价格: ¥{plan.price}/{plan.duration_days}天")
        if plan.price == 0:
            print(f"   类型: 免费试用")
        elif plan.duration_days == 30:
            print(f"   类型: 月付")
            year_price = plan.price * 11  # 按年订阅赠1个月
            print(f"   年付: ¥{year_price}/年（赠1个月）")
        print()
    
    print("=" * 80)
    print("验证完成！")
    print("=" * 80)
