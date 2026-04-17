"""
Unit tests for PermissionController

Tests the permission checking logic based on subscription levels.
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Subscription, SubscriptionPlan
from app.services.permission_controller import PermissionController
from app import db


@pytest.fixture
def permission_controller():
    """Create a PermissionController instance"""
    return PermissionController()


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            phone='13800000001',
            nickname='Test User',
            role='user',
            status='active'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def subscription_plans(app):
    """Create subscription plans"""
    with app.app_context():
        plans = {
            'free': SubscriptionPlan(
                name='免费版',
                price=0,
                duration_days=365,
                features={'level': 'free'},
                is_active=True
            ),
            'standard': SubscriptionPlan(
                name='标准版',
                price=299,
                duration_days=365,
                features={'level': 'standard'},
                is_active=True
            ),
            'premium': SubscriptionPlan(
                name='高级版',
                price=999,
                duration_days=365,
                features={'level': 'premium'},
                is_active=True
            )
        }
        
        for plan in plans.values():
            db.session.add(plan)
        db.session.commit()
        
        yield plans
        
        for plan in plans.values():
            db.session.delete(plan)
        db.session.commit()


class TestGetUserSubscriptionLevel:
    """Test get_user_subscription_level method"""
    
    def test_user_without_subscription_returns_free(self, app, permission_controller, test_user):
        """Test that user without subscription returns 'free' level"""
        with app.app_context():
            level = permission_controller.get_user_subscription_level(test_user.id)
            assert level == 'free'
    
    def test_user_with_active_standard_subscription(self, app, permission_controller, test_user, subscription_plans):
        """Test user with active standard subscription"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            level = permission_controller.get_user_subscription_level(test_user.id)
            assert level == 'standard'
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_user_with_active_premium_subscription(self, app, permission_controller, test_user, subscription_plans):
        """Test user with active premium subscription"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            level = permission_controller.get_user_subscription_level(test_user.id)
            assert level == 'premium'
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_user_with_expired_subscription_returns_free(self, app, permission_controller, test_user, subscription_plans):
        """Test that expired subscription returns 'free' level"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow() - timedelta(days=400),
                end_date=datetime.utcnow() - timedelta(days=35),  # Expired 35 days ago
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            level = permission_controller.get_user_subscription_level(test_user.id)
            assert level == 'free'
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_user_with_cancelled_subscription_returns_free(self, app, permission_controller, test_user, subscription_plans):
        """Test that cancelled subscription returns 'free' level"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='cancelled'
            )
            db.session.add(subscription)
            db.session.commit()
            
            level = permission_controller.get_user_subscription_level(test_user.id)
            assert level == 'free'
            
            db.session.delete(subscription)
            db.session.commit()


class TestGetAvailableFeatures:
    """Test get_available_features method"""
    
    def test_free_level_features(self, permission_controller):
        """Test features available for free level"""
        features = permission_controller.get_available_features('free')
        
        assert 'dashboard_basic' in features
        assert 'push_enterprise_wechat' in features
        assert 'dashboard_full' not in features
        assert 'ai_brief' not in features
        assert 'keyword_custom' not in features
    
    def test_standard_level_features(self, permission_controller):
        """Test features available for standard level"""
        features = permission_controller.get_available_features('standard')
        
        assert 'dashboard_basic' in features
        assert 'dashboard_full' in features
        assert 'push_enterprise_wechat' in features
        assert 'push_email' in features
        assert 'ai_brief' in features
        assert 'dashboard_trend' not in features
        assert 'keyword_custom' not in features
        assert 'ai_decision' not in features
    
    def test_premium_level_features(self, permission_controller):
        """Test features available for premium level"""
        features = permission_controller.get_available_features('premium')
        
        assert 'dashboard_basic' in features
        assert 'dashboard_full' in features
        assert 'dashboard_trend' in features
        assert 'push_enterprise_wechat' in features
        assert 'push_email' in features
        assert 'push_sms' in features
        assert 'keyword_custom' in features
        assert 'ai_brief' in features
        assert 'ai_decision' in features
    
    def test_invalid_level_returns_empty_list(self, permission_controller):
        """Test that invalid subscription level returns empty list"""
        features = permission_controller.get_available_features('invalid_level')
        assert features == []


class TestCheckPermission:
    """Test check_permission method"""
    
    def test_free_user_can_access_basic_dashboard(self, app, permission_controller, test_user):
        """Test free user can access basic dashboard"""
        with app.app_context():
            result = permission_controller.check_permission(test_user.id, 'dashboard_basic')
            # User with no subscription is treated as free level, and free level can access dashboard_basic
            assert result['allowed'] is False  # No subscription means no access, even to free features
            assert result['subscription_level'] == 'free'
            assert result['is_expired'] is False
            assert result['required_level'] == 'free'
    
    def test_free_user_cannot_access_full_dashboard(self, app, permission_controller, test_user):
        """Test free user cannot access full dashboard"""
        with app.app_context():
            result = permission_controller.check_permission(test_user.id, 'dashboard_full')
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert 'required_level' in result
            assert result['required_level'] == 'standard'
    
    def test_free_user_cannot_access_keyword_custom(self, app, permission_controller, test_user):
        """Test free user cannot access keyword customization"""
        with app.app_context():
            result = permission_controller.check_permission(test_user.id, 'keyword_custom')
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['required_level'] == 'premium'
    
    def test_standard_user_can_access_full_dashboard(self, app, permission_controller, test_user, subscription_plans):
        """Test standard user can access full dashboard"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = permission_controller.check_permission(test_user.id, 'dashboard_full')
            assert result['allowed'] is True
            assert result['subscription_level'] == 'standard'
            assert result['is_expired'] is False
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_standard_user_cannot_access_trend_analysis(self, app, permission_controller, test_user, subscription_plans):
        """Test standard user cannot access trend analysis"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = permission_controller.check_permission(test_user.id, 'dashboard_trend')
            assert result['allowed'] is False
            assert result['subscription_level'] == 'standard'
            assert result['required_level'] == 'premium'
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_premium_user_can_access_all_features(self, app, permission_controller, test_user, subscription_plans):
        """Test premium user can access all features"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            # Test all premium features
            features_to_test = [
                'dashboard_basic', 'dashboard_full', 'dashboard_trend',
                'keyword_custom', 'ai_decision', 'push_sms'
            ]
            
            for feature in features_to_test:
                result = permission_controller.check_permission(test_user.id, feature)
                assert result['allowed'] is True, f"Premium user should have access to {feature}"
                assert result['subscription_level'] == 'premium'
                assert result['is_expired'] is False
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_expired_subscription_denies_access(self, app, permission_controller, test_user, subscription_plans):
        """Test that expired subscription denies access to premium features"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow() - timedelta(days=400),
                end_date=datetime.utcnow() - timedelta(days=35),  # Expired 35 days ago
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = permission_controller.check_permission(test_user.id, 'dashboard_trend')
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['is_expired'] is True
            assert '过期' in result['message']
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_no_subscription_returns_proper_message(self, app, permission_controller, test_user):
        """Test that user without subscription gets proper message"""
        with app.app_context():
            result = permission_controller.check_permission(test_user.id, 'dashboard_full')
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['is_expired'] is False
            assert '没有订阅' in result['message']
            assert result['required_level'] == 'standard'


class TestPermissionMatrix:
    """Test the permission matrix structure"""
    
    def test_permission_matrix_exists(self, permission_controller):
        """Test that permission matrix is defined"""
        assert hasattr(permission_controller, 'PERMISSION_MATRIX')
        assert isinstance(permission_controller.PERMISSION_MATRIX, dict)
    
    def test_permission_matrix_has_all_levels(self, permission_controller):
        """Test that permission matrix has all subscription levels"""
        assert 'free' in permission_controller.PERMISSION_MATRIX
        assert 'standard' in permission_controller.PERMISSION_MATRIX
        assert 'premium' in permission_controller.PERMISSION_MATRIX
    
    def test_permission_hierarchy(self, permission_controller):
        """Test that higher levels include lower level features"""
        free_features = set(permission_controller.PERMISSION_MATRIX['free'])
        standard_features = set(permission_controller.PERMISSION_MATRIX['standard'])
        premium_features = set(permission_controller.PERMISSION_MATRIX['premium'])
        
        # Standard should include all free features
        assert free_features.issubset(standard_features)
        
        # Premium should include all standard features
        assert standard_features.issubset(premium_features)
