"""
Unit tests for Permission API endpoints

Tests the /api/permissions/features and /api/permissions/check/{feature} endpoints.
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Subscription, SubscriptionPlan
from app import db


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


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post('/api/auth/login', json={
        'phone': '13800000001',
        'password': 'password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


class TestPermissionFeaturesEndpoint:
    """Test GET /api/permissions/features endpoint"""
    
    def test_get_features_without_auth_returns_401(self, client):
        """Test that accessing features without authentication returns 401"""
        response = client.get('/api/permissions/features')
        assert response.status_code == 401
    
    def test_get_features_for_free_user(self, client, app, test_user, auth_headers):
        """Test getting features for user without subscription (free level)"""
        with app.app_context():
            response = client.get('/api/permissions/features', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert 'data' in data
            assert data['data']['subscription_level'] == 'free'
            assert 'features' in data['data']
            
            features = data['data']['features']
            assert 'dashboard_basic' in features
            assert 'push_enterprise_wechat' in features
            assert 'dashboard_full' not in features
            assert 'keyword_custom' not in features
    
    def test_get_features_for_standard_user(self, client, app, test_user, subscription_plans, auth_headers):
        """Test getting features for standard subscription user"""
        with app.app_context():
            # Create standard subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/features', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert data['data']['subscription_level'] == 'standard'
            
            features = data['data']['features']
            assert 'dashboard_basic' in features
            assert 'dashboard_full' in features
            assert 'ai_brief' in features
            assert 'push_email' in features
            assert 'keyword_custom' not in features
            assert 'dashboard_trend' not in features
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_get_features_for_premium_user(self, client, app, test_user, subscription_plans, auth_headers):
        """Test getting features for premium subscription user"""
        with app.app_context():
            # Create premium subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/features', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert data['data']['subscription_level'] == 'premium'
            
            features = data['data']['features']
            assert 'dashboard_basic' in features
            assert 'dashboard_full' in features
            assert 'dashboard_trend' in features
            assert 'keyword_custom' in features
            assert 'ai_brief' in features
            assert 'ai_decision' in features
            assert 'push_sms' in features
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_get_features_for_expired_subscription(self, client, app, test_user, subscription_plans, auth_headers):
        """Test that expired subscription returns free level features"""
        with app.app_context():
            # Create expired subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow() - timedelta(days=400),
                end_date=datetime.utcnow() - timedelta(days=35),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/features', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert data['data']['subscription_level'] == 'free'
            
            features = data['data']['features']
            assert 'dashboard_basic' in features
            assert 'dashboard_full' not in features
            
            db.session.delete(subscription)
            db.session.commit()


class TestPermissionCheckEndpoint:
    """Test GET /api/permissions/check/{feature} endpoint"""
    
    def test_check_permission_without_auth_returns_401(self, client):
        """Test that checking permission without authentication returns 401"""
        response = client.get('/api/permissions/check/dashboard_full')
        assert response.status_code == 401
    
    def test_check_basic_dashboard_for_free_user(self, client, app, test_user, auth_headers):
        """Test checking basic dashboard permission for free user"""
        with app.app_context():
            response = client.get('/api/permissions/check/dashboard_basic', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            assert 'data' in data
            
            result = data['data']
            # Free user without subscription cannot access even free features
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['is_expired'] is False
    
    def test_check_full_dashboard_for_free_user(self, client, app, test_user, auth_headers):
        """Test checking full dashboard permission for free user"""
        with app.app_context():
            response = client.get('/api/permissions/check/dashboard_full', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            
            result = data['data']
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['required_level'] == 'standard'
            assert '标准' in result['message'] or 'standard' in result['message']
    
    def test_check_keyword_custom_for_free_user(self, client, app, test_user, auth_headers):
        """Test checking keyword customization for free user"""
        with app.app_context():
            response = client.get('/api/permissions/check/keyword_custom', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            
            result = data['data']
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['required_level'] == 'premium'
    
    def test_check_full_dashboard_for_standard_user(self, client, app, test_user, subscription_plans, auth_headers):
        """Test checking full dashboard permission for standard user"""
        with app.app_context():
            # Create standard subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/check/dashboard_full', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            
            result = data['data']
            assert result['allowed'] is True
            assert result['subscription_level'] == 'standard'
            assert result['is_expired'] is False
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_check_trend_analysis_for_standard_user(self, client, app, test_user, subscription_plans, auth_headers):
        """Test that standard user cannot access trend analysis"""
        with app.app_context():
            # Create standard subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/check/dashboard_trend', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            
            result = data['data']
            assert result['allowed'] is False
            assert result['subscription_level'] == 'standard'
            assert result['required_level'] == 'premium'
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_check_all_features_for_premium_user(self, client, app, test_user, subscription_plans, auth_headers):
        """Test that premium user can access all features"""
        with app.app_context():
            # Create premium subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            # Test multiple premium features
            features_to_test = [
                'dashboard_basic',
                'dashboard_full',
                'dashboard_trend',
                'keyword_custom',
                'ai_decision',
                'push_sms'
            ]
            
            for feature in features_to_test:
                response = client.get(f'/api/permissions/check/{feature}', headers=auth_headers)
                
                assert response.status_code == 200
                data = response.json
                assert data['success'] is True
                
                result = data['data']
                assert result['allowed'] is True, f"Premium user should have access to {feature}"
                assert result['subscription_level'] == 'premium'
                assert result['is_expired'] is False
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_check_permission_with_expired_subscription(self, client, app, test_user, subscription_plans, auth_headers):
        """Test that expired subscription denies access"""
        with app.app_context():
            # Create expired subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow() - timedelta(days=400),
                end_date=datetime.utcnow() - timedelta(days=35),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/check/dashboard_trend', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            
            result = data['data']
            assert result['allowed'] is False
            assert result['subscription_level'] == 'free'
            assert result['is_expired'] is True
            assert '过期' in result['message']
            
            db.session.delete(subscription)
            db.session.commit()
    
    def test_check_permission_for_unknown_feature(self, client, app, test_user, subscription_plans, auth_headers):
        """Test checking permission for unknown feature"""
        with app.app_context():
            # Create premium subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['premium'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            response = client.get('/api/permissions/check/unknown_feature', headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json
            assert data['success'] is True
            
            result = data['data']
            # Unknown feature should not be allowed even for premium users
            assert result['allowed'] is False
            assert result['subscription_level'] == 'premium'
            
            db.session.delete(subscription)
            db.session.commit()


class TestPermissionAPIIntegration:
    """Integration tests for permission API"""
    
    def test_features_and_check_consistency(self, client, app, test_user, subscription_plans, auth_headers):
        """Test that features endpoint and check endpoint are consistent"""
        with app.app_context():
            # Create standard subscription
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=subscription_plans['standard'].id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            # Get features list
            features_response = client.get('/api/permissions/features', headers=auth_headers)
            features_data = features_response.json
            available_features = features_data['data']['features']
            
            # Check each feature
            for feature in available_features:
                check_response = client.get(f'/api/permissions/check/{feature}', headers=auth_headers)
                check_data = check_response.json
                
                # Feature in the list should be allowed
                assert check_data['data']['allowed'] is True, \
                    f"Feature {feature} is in features list but check returns not allowed"
            
            # Check a feature not in the list
            unavailable_feature = 'dashboard_trend'  # Not available for standard
            if unavailable_feature not in available_features:
                check_response = client.get(f'/api/permissions/check/{unavailable_feature}', headers=auth_headers)
                check_data = check_response.json
                
                # Feature not in the list should not be allowed
                assert check_data['data']['allowed'] is False, \
                    f"Feature {unavailable_feature} is not in features list but check returns allowed"
            
            db.session.delete(subscription)
            db.session.commit()
