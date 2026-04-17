# -*- coding: utf-8 -*-
"""
订阅服务
处理订阅创建、试用期管理、年付优惠等业务逻辑
"""
from datetime import datetime, timedelta
from app.models import Subscription, SubscriptionPlan, Order, User
from app import db
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """订阅服务类"""
    
    # 试用期配置
    TRIAL_DURATION_DAYS = 7
    TRIAL_PLAN_NAME = '免费订阅'
    
    # 基础版配置
    BASIC_PLAN_NAME = '基础版'
    MONTHLY_PRICE = 39
    YEARLY_PRICE = 468
    YEARLY_DURATION_DAYS = 365  # 12个月 + 赠送1个月
    
    @staticmethod
    def can_start_trial(user_id: int) -> tuple[bool, str]:
        """
        检查用户是否可以开始试用
        
        Args:
            user_id: 用户ID
            
        Returns:
            (can_trial, message)
        """
        # 检查用户是否已经试用过
        trial_plan = SubscriptionPlan.query.filter_by(
            name=SubscriptionService.TRIAL_PLAN_NAME,
            is_active=True
        ).first()
        
        if not trial_plan:
            return False, '试用套餐不存在'
        
        # 查询用户是否有过该套餐的订阅记录（包括已过期的）
        existing_trial = Subscription.query.filter_by(
            user_id=user_id,
            plan_id=trial_plan.id
        ).first()
        
        if existing_trial:
            return False, '您已经使用过免费试用'
        
        return True, '可以开始试用'
    
    @staticmethod
    def create_trial_subscription(user_id: int) -> Dict:
        """
        创建试用订阅
        
        Args:
            user_id: 用户ID
            
        Returns:
            订阅信息字典
            
        Raises:
            ValueError: 如果用户不能试用
        """
        # 检查是否可以试用
        can_trial, message = SubscriptionService.can_start_trial(user_id)
        if not can_trial:
            raise ValueError(message)
        
        # 获取试用套餐
        trial_plan = SubscriptionPlan.query.filter_by(
            name=SubscriptionService.TRIAL_PLAN_NAME,
            is_active=True
        ).first()
        
        if not trial_plan:
            raise ValueError('试用套餐不存在')
        
        # 创建订阅
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=SubscriptionService.TRIAL_DURATION_DAYS)
        
        subscription = Subscription(
            user_id=user_id,
            plan_id=trial_plan.id,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        logger.info(f"用户 {user_id} 开始试用，有效期至 {end_date}")
        
        return {
            'subscription_id': subscription.id,
            'plan_name': trial_plan.name,
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': SubscriptionService.TRIAL_DURATION_DAYS,
            'status': 'active'
        }
    
    @staticmethod
    def create_paid_subscription(
        user_id: int,
        plan_id: int,
        payment_cycle: str = 'monthly',
        order_id: Optional[int] = None
    ) -> Dict:
        """
        创建付费订阅
        
        Args:
            user_id: 用户ID
            plan_id: 套餐ID
            payment_cycle: 支付周期 ('monthly' 或 'yearly')
            order_id: 关联的订单ID（可选）
            
        Returns:
            订阅信息字典
            
        Raises:
            ValueError: 如果参数无效
        """
        # 获取套餐
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            raise ValueError('套餐不存在')
        
        # 检查支付周期
        if payment_cycle not in ['monthly', 'yearly']:
            raise ValueError('无效的支付周期')
        
        # 计算订阅时长
        if plan.name == SubscriptionService.BASIC_PLAN_NAME:
            if payment_cycle == 'yearly':
                duration_days = SubscriptionService.YEARLY_DURATION_DAYS
            else:
                duration_days = 30  # 月付
        else:
            duration_days = plan.duration_days
        
        # 检查是否已有活跃订阅
        existing = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).first()
        
        if existing:
            # 从现有订阅结束时间开始
            start_date = existing.end_date
        else:
            start_date = datetime.utcnow()
        
        end_date = start_date + timedelta(days=duration_days)
        
        # 创建订阅
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        logger.info(
            f"用户 {user_id} 创建付费订阅，套餐: {plan.name}, "
            f"周期: {payment_cycle}, 有效期至 {end_date}"
        )
        
        return {
            'subscription_id': subscription.id,
            'plan_name': plan.name,
            'payment_cycle': payment_cycle,
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': duration_days,
            'status': 'active',
            'order_id': order_id
        }
    
    @staticmethod
    def calculate_order_amount(plan_id: int, payment_cycle: str = 'monthly') -> float:
        """
        计算订单金额
        
        Args:
            plan_id: 套餐ID
            payment_cycle: 支付周期 ('monthly' 或 'yearly')
            
        Returns:
            订单金额
            
        Raises:
            ValueError: 如果参数无效
        """
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            raise ValueError('套餐不存在')
        
        # 免费套餐
        if plan.price == 0:
            return 0
        
        # 基础版套餐
        if plan.name == SubscriptionService.BASIC_PLAN_NAME:
            if payment_cycle == 'yearly':
                return SubscriptionService.YEARLY_PRICE
            else:
                return SubscriptionService.MONTHLY_PRICE
        
        # 其他套餐
        return float(plan.price)
    
    @staticmethod
    def calculate_duration_days(plan_id: int, payment_cycle: str = 'monthly') -> int:
        """
        计算订阅时长（天数）
        
        Args:
            plan_id: 套餐ID
            payment_cycle: 支付周期 ('monthly' 或 'yearly')
            
        Returns:
            订阅时长（天数）
            
        Raises:
            ValueError: 如果参数无效
        """
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            raise ValueError('套餐不存在')
        
        # 基础版套餐
        if plan.name == SubscriptionService.BASIC_PLAN_NAME:
            if payment_cycle == 'yearly':
                return SubscriptionService.YEARLY_DURATION_DAYS  # 365天（赠1个月）
            else:
                return 30  # 月付
        
        # 其他套餐
        return plan.duration_days
    
    @staticmethod
    def check_trial_expiry() -> list:
        """
        检查即将到期的试用订阅
        
        Returns:
            即将到期的订阅列表
        """
        # 获取试用套餐
        trial_plan = SubscriptionPlan.query.filter_by(
            name=SubscriptionService.TRIAL_PLAN_NAME,
            is_active=True
        ).first()
        
        if not trial_plan:
            return []
        
        # 查询即将到期的试用订阅（1天内到期）
        tomorrow = datetime.utcnow() + timedelta(days=1)
        today = datetime.utcnow()
        
        expiring_subscriptions = Subscription.query.filter(
            Subscription.plan_id == trial_plan.id,
            Subscription.status == 'active',
            Subscription.end_date > today,
            Subscription.end_date <= tomorrow
        ).all()
        
        return expiring_subscriptions
    
    @staticmethod
    def expire_trial_subscriptions() -> int:
        """
        将已过期的试用订阅标记为过期
        
        Returns:
            过期的订阅数量
        """
        # 获取试用套餐
        trial_plan = SubscriptionPlan.query.filter_by(
            name=SubscriptionService.TRIAL_PLAN_NAME,
            is_active=True
        ).first()
        
        if not trial_plan:
            return 0
        
        # 查询已过期但状态仍为active的试用订阅
        now = datetime.utcnow()
        expired_subscriptions = Subscription.query.filter(
            Subscription.plan_id == trial_plan.id,
            Subscription.status == 'active',
            Subscription.end_date <= now
        ).all()
        
        count = 0
        for subscription in expired_subscriptions:
            subscription.status = 'expired'
            count += 1
            logger.info(f"试用订阅 {subscription.id} 已过期")
        
        if count > 0:
            db.session.commit()
        
        return count
    
    @staticmethod
    def get_user_subscription_status(user_id: int) -> Dict:
        """
        获取用户订阅状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            订阅状态信息
        """
        # 查询活跃订阅
        active_subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).first()
        
        if active_subscription:
            plan = active_subscription.plan
            days_remaining = (active_subscription.end_date - datetime.utcnow()).days
            
            return {
                'has_subscription': True,
                'subscription_id': active_subscription.id,
                'plan_name': plan.name,
                'plan_id': plan.id,
                'is_trial': plan.name == SubscriptionService.TRIAL_PLAN_NAME,
                'start_date': active_subscription.start_date,
                'end_date': active_subscription.end_date,
                'days_remaining': days_remaining,
                'status': 'active'
            }
        
        # 检查是否可以试用
        can_trial, message = SubscriptionService.can_start_trial(user_id)
        
        return {
            'has_subscription': False,
            'can_trial': can_trial,
            'trial_message': message,
            'status': 'none'
        }
