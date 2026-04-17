"""
权限控制器 (Permission Controller)

根据用户的订阅套餐等级控制数据看板和功能的访问权限。
"""

from typing import Optional
from datetime import datetime
from flask import request
from app.models import User, Subscription, SubscriptionPlan, PermissionAccessLog
from app import db


class PermissionController:
    """权限控制器，基于订阅等级控制功能访问权限"""
    
    # 权限矩阵：定义每个订阅等级可访问的功能
    PERMISSION_MATRIX = {
        'free': [
            'dashboard_basic',      # 基础数据看板
            'push_enterprise_wechat'  # 企业微信推送
        ],
        'standard': [
            'dashboard_basic',      # 基础数据看板
            'dashboard_full',       # 完整数据看板
            'push_enterprise_wechat',  # 企业微信推送
            'push_email',           # 邮件推送
            'ai_brief'              # AI简报
        ],
        'premium': [
            'dashboard_basic',      # 基础数据看板
            'dashboard_full',       # 完整数据看板
            'dashboard_trend',      # 趋势分析
            'push_enterprise_wechat',  # 企业微信推送
            'push_email',           # 邮件推送
            'push_sms',             # 短信推送
            'keyword_custom',       # 关键词定制
            'ai_brief',             # AI简报
            'ai_decision'           # AI决策建议
        ]
    }
    
    def get_user_subscription_level(self, user_id: int) -> str:
        """
        获取用户订阅等级
        
        Args:
            user_id: 用户ID
            
        Returns:
            订阅等级: 'free', 'standard', 'premium'
            如果用户没有订阅或订阅已过期，返回 'free'
        """
        # 查询用户的活跃订阅
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # 如果没有活跃订阅，返回免费版
        if not subscription:
            return 'free'
        
        # 检查订阅是否过期
        if subscription.end_date < datetime.utcnow():
            return 'free'
        
        # 获取订阅套餐信息
        plan = subscription.plan
        if not plan:
            return 'free'
        
        # 根据套餐名称判断等级
        plan_name_lower = plan.name.lower()
        
        if '高级' in plan.name or 'premium' in plan_name_lower:
            return 'premium'
        elif '标准' in plan.name or 'standard' in plan_name_lower:
            return 'standard'
        else:
            return 'free'
    
    def get_available_features(self, subscription_level: str) -> list[str]:
        """
        获取订阅等级可用的功能列表
        
        Args:
            subscription_level: 订阅等级 ('free', 'standard', 'premium')
            
        Returns:
            功能标识列表
        """
        return self.PERMISSION_MATRIX.get(subscription_level, [])
    
    def check_permission(self, user_id: int, feature: str, log_access: bool = True) -> dict:
        """
        检查用户是否有权限访问指定功能
        
        Args:
            user_id: 用户ID
            feature: 功能标识 (如 'dashboard_full', 'keyword_custom')
            log_access: 是否记录访问日志，默认为True
            
        Returns:
            dict: {
                'allowed': bool,  # 是否允许访问
                'subscription_level': str,  # 用户订阅等级
                'is_expired': bool,  # 订阅是否过期
                'message': str,  # 提示信息
                'required_level': str  # 功能所需的最低订阅等级 (如果权限不足)
            }
        
        Validates: Requirements 5.8
        """
        # 查询用户的活跃订阅
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # 检查订阅是否存在
        if not subscription:
            result = {
                'allowed': False,
                'subscription_level': 'free',
                'is_expired': False,
                'message': '您当前没有订阅，仅可访问免费版功能',
                'required_level': self._get_required_level(feature)
            }
            # 记录访问日志
            if log_access:
                self._log_access(user_id, feature, 'free', False)
            return result
        
        # 检查订阅是否过期
        is_expired = subscription.end_date < datetime.utcnow()
        if is_expired:
            result = {
                'allowed': False,
                'subscription_level': 'free',
                'is_expired': True,
                'message': '您的订阅已过期，请续费以继续使用高级功能',
                'required_level': self._get_required_level(feature)
            }
            # 记录访问日志
            if log_access:
                self._log_access(user_id, feature, 'free', False)
            return result
        
        # 获取订阅套餐信息
        plan = subscription.plan
        if not plan:
            result = {
                'allowed': False,
                'subscription_level': 'free',
                'is_expired': False,
                'message': '订阅套餐信息异常',
                'required_level': self._get_required_level(feature)
            }
            # 记录访问日志
            if log_access:
                self._log_access(user_id, feature, 'free', False)
            return result
        
        # 确定用户订阅等级
        plan_name_lower = plan.name.lower()
        if '高级' in plan.name or 'premium' in plan_name_lower:
            user_level = 'premium'
        elif '标准' in plan.name or 'standard' in plan_name_lower:
            user_level = 'standard'
        else:
            user_level = 'free'
        
        # 获取该等级可用的功能列表
        available_features = self.get_available_features(user_level)
        
        # 检查功能是否在可用列表中
        allowed = feature in available_features
        
        # 记录访问日志
        if log_access:
            self._log_access(user_id, feature, user_level, allowed)
        
        if allowed:
            return {
                'allowed': True,
                'subscription_level': user_level,
                'is_expired': False,
                'message': '权限验证通过'
            }
        else:
            required_level = self._get_required_level(feature)
            return {
                'allowed': False,
                'subscription_level': user_level,
                'is_expired': False,
                'message': f'此功能需要{required_level}版本订阅，请升级您的订阅',
                'required_level': required_level
            }
    
    def _get_required_level(self, feature: str) -> str:
        """
        获取功能所需的最低订阅等级
        
        Args:
            feature: 功能标识
            
        Returns:
            最低订阅等级: 'free', 'standard', 'premium'
        """
        # 遍历权限矩阵，找到包含该功能的最低等级
        level_hierarchy = ['free', 'standard', 'premium']
        
        for level in level_hierarchy:
            if feature in self.PERMISSION_MATRIX.get(level, []):
                return level
        
        # 如果功能不在任何等级中，默认返回 premium
        return 'premium'
    
    def _log_access(self, user_id: int, feature: str, subscription_level: str, allowed: bool) -> None:
        """
        记录权限访问日志
        
        Args:
            user_id: 用户ID
            feature: 访问的功能/模块
            subscription_level: 用户订阅等级
            allowed: 是否允许访问
        
        Validates: Requirements 5.8
        """
        try:
            # 获取用户IP地址
            ip_address = None
            if request:
                ip_address = request.remote_addr
            
            # 创建访问日志记录
            log = PermissionAccessLog(
                user_id=user_id,
                feature=feature,
                subscription_level=subscription_level,
                allowed=allowed,
                ip_address=ip_address,
                accessed_at=datetime.utcnow()
            )
            
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            # 日志记录失败不应影响主流程，静默失败
            db.session.rollback()
            # 可以在这里添加错误日志记录
            pass
