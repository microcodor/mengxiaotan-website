"""
权限访问日志集成测试

测试权限访问日志在实际应用中的记录功能。

Validates: Requirements 5.8
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Subscription, SubscriptionPlan, PermissionAccessLog
from app.services.permission_controller import PermissionController
from app import db


def test_permission_controller_logs_access(app):
    """测试PermissionController记录访问日志"""
    with app.app_context():
        # 创建测试用户
        user = User.query.filter_by(phone='test_log_user').first()
        if not user:
            user = User(
                phone='test_log_user',
                nickname='测试日志用户',
                role='user',
                status='active'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # 清理之前的日志
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # 创建权限控制器
        controller = PermissionController()
        
        # 检查权限（应该记录日志）
        result = controller.check_permission(user.id, 'dashboard_full')
        
        # 验证日志已创建
        log = PermissionAccessLog.query.filter_by(
            user_id=user.id,
            feature='dashboard_full'
        ).first()
        
        assert log is not None, "日志应该被创建"
        assert log.subscription_level == 'free', "订阅等级应该是free"
        assert log.allowed == False, "访问应该被拒绝"
        assert log.accessed_at is not None, "访问时间应该被记录"
        
        # 清理
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()


def test_permission_controller_logs_with_subscription(app):
    """测试有订阅的用户访问日志"""
    with app.app_context():
        # 创建测试用户
        user = User.query.filter_by(phone='test_log_user2').first()
        if not user:
            user = User(
                phone='test_log_user2',
                nickname='测试日志用户2',
                role='user',
                status='active'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # 创建或获取标准版套餐
        plan = SubscriptionPlan.query.filter_by(name='标准版').first()
        if not plan:
            plan = SubscriptionPlan(
                name='标准版',
                price=299,
                duration_days=365,
                features={'level': 'standard'},
                is_active=True
            )
            db.session.add(plan)
            db.session.commit()
        
        # 创建订阅
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            status='active'
        )
        db.session.add(subscription)
        db.session.commit()
        
        # 清理之前的日志
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # 创建权限控制器
        controller = PermissionController()
        
        # 检查权限（应该记录日志）
        result = controller.check_permission(user.id, 'dashboard_full')
        
        # 验证日志已创建
        log = PermissionAccessLog.query.filter_by(
            user_id=user.id,
            feature='dashboard_full'
        ).first()
        
        assert log is not None, "日志应该被创建"
        assert log.subscription_level == 'standard', "订阅等级应该是standard"
        assert log.allowed == True, "访问应该被允许"
        
        # 清理
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.delete(subscription)
        db.session.delete(user)
        db.session.commit()


def test_permission_controller_can_disable_logging(app):
    """测试可以禁用日志记录"""
    with app.app_context():
        # 创建测试用户
        user = User.query.filter_by(phone='test_log_user3').first()
        if not user:
            user = User(
                phone='test_log_user3',
                nickname='测试日志用户3',
                role='user',
                status='active'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # 清理之前的日志
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # 创建权限控制器
        controller = PermissionController()
        
        # 检查权限，禁用日志记录
        result = controller.check_permission(user.id, 'dashboard_full', log_access=False)
        
        # 验证日志未创建
        log = PermissionAccessLog.query.filter_by(
            user_id=user.id,
            feature='dashboard_full'
        ).first()
        
        assert log is None, "日志不应该被创建"
        
        # 清理
        db.session.delete(user)
        db.session.commit()


def test_query_logs_by_user(app):
    """测试按用户查询日志"""
    with app.app_context():
        # 创建测试用户
        user = User.query.filter_by(phone='test_log_user4').first()
        if not user:
            user = User(
                phone='test_log_user4',
                nickname='测试日志用户4',
                role='user',
                status='active'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # 清理之前的日志
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # 创建权限控制器
        controller = PermissionController()
        
        # 多次检查权限
        controller.check_permission(user.id, 'dashboard_basic')
        controller.check_permission(user.id, 'dashboard_full')
        controller.check_permission(user.id, 'ai_brief')
        
        # 查询用户的所有日志
        logs = PermissionAccessLog.query.filter_by(user_id=user.id).all()
        
        assert len(logs) == 3, "应该有3条日志记录"
        features = [log.feature for log in logs]
        assert 'dashboard_basic' in features
        assert 'dashboard_full' in features
        assert 'ai_brief' in features
        
        # 清理
        PermissionAccessLog.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
