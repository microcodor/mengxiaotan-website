"""
权限访问日志测试

测试权限访问日志的记录功能，验证日志是否正确记录用户访问数据看板的信息。

Validates: Requirements 5.8
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Subscription, SubscriptionPlan, PermissionAccessLog
from app.services.permission_controller import PermissionController
from app import db


@pytest.fixture
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(
            phone='13800000000',
            nickname='测试用户',
            role='user',
            status='active'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # 清理
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def another_user(app):
    """创建另一个测试用户"""
    with app.app_context():
        user = User(
            phone='13900000001',
            nickname='另一个测试用户',
            role='user',
            status='active'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # 清理
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def free_plan(app):
    """创建免费版套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='免费版',
            price=0,
            duration_days=365,
            features={'level': 'free'},
            is_active=True
        )
        db.session.add(plan)
        db.session.commit()
        
        yield plan
        
        # 清理
        db.session.delete(plan)
        db.session.commit()


@pytest.fixture
def standard_plan(app):
    """创建标准版套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='标准版',
            price=299,
            duration_days=365,
            features={'level': 'standard'},
            is_active=True
        )
        db.session.add(plan)
        db.session.commit()
        
        yield plan
        
        # 清理
        db.session.delete(plan)
        db.session.commit()


@pytest.fixture
def premium_plan(app):
    """创建高级版套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='高级版',
            price=999,
            duration_days=365,
            features={'level': 'premium'},
            is_active=True
        )
        db.session.add(plan)
        db.session.commit()
        
        yield plan
        
        # 清理
        db.session.delete(plan)
        db.session.commit()


class TestPermissionAccessLog:
    """权限访问日志测试类"""
    
    def test_log_created_on_permission_check(self, app, test_user, free_plan):
        """测试权限检查时创建日志"""
        with app.app_context():
            controller = PermissionController()
            
            # 检查权限
            result = controller.check_permission(test_user.id, 'dashboard_full')
            
            # 验证日志已创建
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='dashboard_full'
            ).first()
            
            assert log is not None
            assert log.subscription_level == 'free'
            assert log.allowed == False
            assert log.accessed_at is not None
    
    def test_log_contains_correct_subscription_level(self, app, test_user, standard_plan):
        """测试日志包含正确的订阅等级"""
        with app.app_context():
            # 创建标准版订阅
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            controller = PermissionController()
            
            # 检查权限
            result = controller.check_permission(test_user.id, 'dashboard_full')
            
            # 验证日志包含正确的订阅等级
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='dashboard_full'
            ).first()
            
            assert log is not None
            assert log.subscription_level == 'standard'
            assert log.allowed == True
    
    def test_log_records_allowed_access(self, app, test_user, premium_plan):
        """测试日志记录允许的访问"""
        with app.app_context():
            # 创建高级版订阅
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=premium_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            controller = PermissionController()
            
            # 检查权限（高级版功能）
            result = controller.check_permission(test_user.id, 'keyword_custom')
            
            # 验证日志记录允许访问
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='keyword_custom'
            ).first()
            
            assert log is not None
            assert log.allowed == True
            assert log.subscription_level == 'premium'
    
    def test_log_records_denied_access(self, app, test_user, free_plan):
        """测试日志记录拒绝的访问"""
        with app.app_context():
            controller = PermissionController()
            
            # 检查权限（高级版功能，但用户是免费版）
            result = controller.check_permission(test_user.id, 'keyword_custom')
            
            # 验证日志记录拒绝访问
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='keyword_custom'
            ).first()
            
            assert log is not None
            assert log.allowed == False
            assert log.subscription_level == 'free'
    
    def test_log_records_multiple_accesses(self, app, test_user, standard_plan):
        """测试日志记录多次访问"""
        with app.app_context():
            # 创建标准版订阅
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            controller = PermissionController()
            
            # 多次检查权限
            controller.check_permission(test_user.id, 'dashboard_basic')
            controller.check_permission(test_user.id, 'dashboard_full')
            controller.check_permission(test_user.id, 'ai_brief')
            
            # 验证所有访问都被记录
            logs = PermissionAccessLog.query.filter_by(user_id=test_user.id).all()
            
            assert len(logs) == 3
            features = [log.feature for log in logs]
            assert 'dashboard_basic' in features
            assert 'dashboard_full' in features
            assert 'ai_brief' in features
    
    def test_log_can_be_disabled(self, app, test_user, free_plan):
        """测试可以禁用日志记录"""
        with app.app_context():
            controller = PermissionController()
            
            # 检查权限，禁用日志记录
            result = controller.check_permission(test_user.id, 'dashboard_full', log_access=False)
            
            # 验证日志未创建
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='dashboard_full'
            ).first()
            
            assert log is None
    
    def test_log_includes_access_time(self, app, test_user, free_plan):
        """测试日志包含访问时间"""
        with app.app_context():
            controller = PermissionController()
            
            before_time = datetime.utcnow()
            result = controller.check_permission(test_user.id, 'dashboard_basic')
            after_time = datetime.utcnow()
            
            # 验证日志包含访问时间
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='dashboard_basic'
            ).first()
            
            assert log is not None
            assert log.accessed_at is not None
            assert before_time <= log.accessed_at <= after_time
    
    def test_log_records_expired_subscription(self, app, test_user, standard_plan):
        """测试日志记录过期订阅的访问"""
        with app.app_context():
            # 创建已过期的订阅
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow() - timedelta(days=60),
                end_date=datetime.utcnow() - timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            controller = PermissionController()
            
            # 检查权限
            result = controller.check_permission(test_user.id, 'dashboard_full')
            
            # 验证日志记录为免费版（因为订阅已过期）
            log = PermissionAccessLog.query.filter_by(
                user_id=test_user.id,
                feature='dashboard_full'
            ).first()
            
            assert log is not None
            assert log.subscription_level == 'free'
            assert log.allowed == False
    
    def test_log_failure_does_not_affect_permission_check(self, app, test_user, free_plan, monkeypatch):
        """测试日志记录失败不影响权限检查"""
        with app.app_context():
            controller = PermissionController()
            
            # 模拟数据库提交失败
            def mock_commit():
                raise Exception("Database error")
            
            monkeypatch.setattr(db.session, 'commit', mock_commit)
            
            # 检查权限应该仍然成功
            result = controller.check_permission(test_user.id, 'dashboard_basic')
            
            # 验证权限检查结果正确
            assert result['allowed'] == True
            assert result['subscription_level'] == 'free'
    
    def test_query_logs_by_user(self, app, test_user, another_user, free_plan):
        """测试按用户查询日志"""
        with app.app_context():
            controller = PermissionController()
            
            # 两个用户分别访问
            controller.check_permission(test_user.id, 'dashboard_basic')
            controller.check_permission(test_user.id, 'dashboard_full')
            controller.check_permission(another_user.id, 'dashboard_basic')
            
            # 查询特定用户的日志
            user_logs = PermissionAccessLog.query.filter_by(user_id=test_user.id).all()
            
            assert len(user_logs) == 2
            assert all(log.user_id == test_user.id for log in user_logs)
    
    def test_query_logs_by_feature(self, app, test_user, another_user, free_plan):
        """测试按功能查询日志"""
        with app.app_context():
            controller = PermissionController()
            
            # 多个用户访问同一功能
            controller.check_permission(test_user.id, 'dashboard_full')
            controller.check_permission(another_user.id, 'dashboard_full')
            controller.check_permission(test_user.id, 'dashboard_basic')
            
            # 查询特定功能的日志
            feature_logs = PermissionAccessLog.query.filter_by(feature='dashboard_full').all()
            
            assert len(feature_logs) == 2
            assert all(log.feature == 'dashboard_full' for log in feature_logs)
    
    def test_query_logs_by_time_range(self, app, test_user, free_plan):
        """测试按时间范围查询日志"""
        with app.app_context():
            controller = PermissionController()
            
            # 记录访问
            controller.check_permission(test_user.id, 'dashboard_basic')
            
            # 查询最近1小时的日志
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_logs = PermissionAccessLog.query.filter(
                PermissionAccessLog.accessed_at >= one_hour_ago
            ).all()
            
            assert len(recent_logs) >= 1
            assert all(log.accessed_at >= one_hour_ago for log in recent_logs)
