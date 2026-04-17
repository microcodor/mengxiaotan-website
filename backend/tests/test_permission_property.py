"""
Property-based tests for Permission Control

**Validates: Requirements 5.1, 5.5, 5.7**

Uses hypothesis to test universal properties of the permission control system:
- Property 4: 权限控制正确性

Feature: subscription-enhancement, Property 4: 权限控制正确性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta
from decimal import Decimal
from app.services.permission_controller import PermissionController
from app.models import User, Subscription, SubscriptionPlan
from app import db


# Custom strategies for generating test data
@st.composite
def user_strategy(draw):
    """Generate random User data"""
    import time
    timestamp = str(int(time.time() * 1000000))[-8:]
    random_digits = draw(st.text(min_size=3, max_size=3, alphabet='0123456789'))
    phone = timestamp + random_digits
    nickname = draw(st.text(min_size=2, max_size=20))
    return {
        'phone': phone,
        'nickname': nickname
    }


@st.composite
def subscription_level_strategy(draw):
    """Generate random subscription level"""
    return draw(st.sampled_from(['free', 'standard', 'premium']))


@st.composite
def feature_strategy(draw):
    """Generate random feature identifier"""
    all_features = [
        'dashboard_basic',
        'dashboard_full',
        'dashboard_trend',
        'push_enterprise_wechat',
        'push_email',
        'push_sms',
        'keyword_custom',
        'ai_brief',
        'ai_decision'
    ]
    return draw(st.sampled_from(all_features))


@st.composite
def plan_price_strategy(draw):
    """Generate random plan price"""
    prices = {
        'free': 0,
        'standard': draw(st.floats(min_value=99.0, max_value=500.0)),
        'premium': draw(st.floats(min_value=500.0, max_value=2000.0))
    }
    level = draw(st.sampled_from(['free', 'standard', 'premium']))
    return level, round(prices[level], 2)


class TestPermissionControlProperties:
    """Property-based tests for permission control"""
    
    # Feature: subscription-enhancement, Property 4: 权限控制正确性
    @given(
        user_data=user_strategy(),
        subscription_level=subscription_level_strategy(),
        feature=feature_strategy()
    )
    @settings(
        max_examples=100,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_4_permission_matrix_correctness(
        self, app, db_session, user_data, subscription_level, feature
    ):
        """
        Property 4: 权限控制正确性 - 权限矩阵正确性
        **Validates: Requirements 5.1**
        
        For any user and feature, permission control should follow the permission matrix:
        - Free users can only access free features
        - Standard users can access free + standard features
        - Premium users can access all features
        """
        with app.app_context():
            # Define permission matrix (same as in PermissionController)
            permission_matrix = {
                'free': [
                    'dashboard_basic',
                    'push_enterprise_wechat'
                ],
                'standard': [
                    'dashboard_basic',
                    'dashboard_full',
                    'push_enterprise_wechat',
                    'push_email',
                    'ai_brief'
                ],
                'premium': [
                    'dashboard_basic',
                    'dashboard_full',
                    'dashboard_trend',
                    'push_enterprise_wechat',
                    'push_email',
                    'push_sms',
                    'keyword_custom',
                    'ai_brief',
                    'ai_decision'
                ]
            }
            
            # Create test user
            user = User(
                phone=user_data['phone'],
                nickname=user_data['nickname'],
                role='user'
            )
            db_session.add(user)
            db_session.flush()
            
            # Create subscription plan based on level
            plan_names = {
                'free': '免费版',
                'standard': '标准版',
                'premium': '高级版'
            }
            plan_prices = {
                'free': 0,
                'standard': 299,
                'premium': 999
            }
            
            plan = SubscriptionPlan(
                name=plan_names[subscription_level],
                price=Decimal(str(plan_prices[subscription_level])),
                duration_days=365,
                features={'level': subscription_level},
                is_active=True
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create active subscription (skip for free level)
            if subscription_level != 'free':
                subscription = Subscription(
                    user_id=user.id,
                    plan_id=plan.id,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=365),
                    status='active'
                )
                db_session.add(subscription)
                db_session.commit()
            
            # Check permission
            controller = PermissionController()
            
            if subscription_level == 'free':
                # Free users without subscription
                result = controller.check_permission(user.id, feature)
                # Free users should not have access to any features without subscription
                assert result['allowed'] is False
                assert result['subscription_level'] == 'free'
            else:
                result = controller.check_permission(user.id, feature)
                
                # Verify permission matches matrix
                expected_allowed = feature in permission_matrix[subscription_level]
                assert result['allowed'] == expected_allowed, \
                    f"User with {subscription_level} subscription should {'have' if expected_allowed else 'not have'} access to {feature}"
                assert result['subscription_level'] == subscription_level
    
    # Feature: subscription-enhancement, Property 4: 权限控制正确性
    @given(
        user_data=user_strategy(),
        feature=feature_strategy()
    )
    @settings(
        max_examples=100,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_4_subscription_upgrade_expands_permissions(
        self, app, db_session, user_data, feature
    ):
        """
        Property 4: 权限控制正确性 - 订阅升级扩展权限
        **Validates: Requirements 5.7**
        
        When user subscription level upgrades, permissions should immediately expand
        """
        with app.app_context():
            # Create test user
            user = User(
                phone=user_data['phone'],
                nickname=user_data['nickname'],
                role='user'
            )
            db_session.add(user)
            db_session.flush()
            
            # Create standard plan
            standard_plan = SubscriptionPlan(
                name='标准版',
                price=Decimal('299.00'),
                duration_days=365,
                features={'level': 'standard'},
                is_active=True
            )
            db_session.add(standard_plan)
            db_session.flush()
            
            # Create standard subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db_session.add(subscription)
            db_session.commit()
            
            # Check permission with standard subscription
            controller = PermissionController()
            result_before = controller.check_permission(user.id, feature)
            level_before = result_before['subscription_level']
            allowed_before = result_before['allowed']
            
            # Upgrade to premium
            premium_plan = SubscriptionPlan(
                name='高级版',
                price=Decimal('999.00'),
                duration_days=365,
                features={'level': 'premium'},
                is_active=True
            )
            db_session.add(premium_plan)
            db_session.flush()
            
            # Cancel old subscription and create new premium subscription
            subscription.status = 'cancelled'
            premium_subscription = Subscription(
                user_id=user.id,
                plan_id=premium_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db_session.add(premium_subscription)
            db_session.commit()
            
            # Check permission after upgrade
            result_after = controller.check_permission(user.id, feature)
            level_after = result_after['subscription_level']
            allowed_after = result_after['allowed']
            
            # Verify upgrade
            assert level_before == 'standard'
            assert level_after == 'premium'
            
            # Verify permissions expanded (if feature was not allowed before, it might be allowed now)
            # Premium should have access to all features
            if feature in ['dashboard_trend', 'push_sms', 'keyword_custom', 'ai_decision']:
                # These are premium-only features
                assert allowed_before is False, f"Standard user should not have access to {feature}"
                assert allowed_after is True, f"Premium user should have access to {feature}"
            elif feature in ['dashboard_full', 'push_email', 'ai_brief']:
                # These are standard+ features
                assert allowed_before is True, f"Standard user should have access to {feature}"
                assert allowed_after is True, f"Premium user should have access to {feature}"
    
    # Feature: subscription-enhancement, Property 4: 权限控制正确性
    @given(
        user_data=user_strategy(),
        feature=feature_strategy()
    )
    @settings(
        max_examples=100,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_4_subscription_downgrade_restricts_permissions(
        self, app, db_session, user_data, feature
    ):
        """
        Property 4: 权限控制正确性 - 订阅降级收缩权限
        **Validates: Requirements 5.7**
        
        When user subscription level downgrades, permissions should immediately restrict
        """
        with app.app_context():
            # Create test user
            user = User(
                phone=user_data['phone'],
                nickname=user_data['nickname'],
                role='user'
            )
            db_session.add(user)
            db_session.flush()
            
            # Create premium plan
            premium_plan = SubscriptionPlan(
                name='高级版',
                price=Decimal('999.00'),
                duration_days=365,
                features={'level': 'premium'},
                is_active=True
            )
            db_session.add(premium_plan)
            db_session.flush()
            
            # Create premium subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=premium_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db_session.add(subscription)
            db_session.commit()
            
            # Check permission with premium subscription
            controller = PermissionController()
            result_before = controller.check_permission(user.id, feature)
            level_before = result_before['subscription_level']
            allowed_before = result_before['allowed']
            
            # Downgrade to standard
            standard_plan = SubscriptionPlan(
                name='标准版',
                price=Decimal('299.00'),
                duration_days=365,
                features={'level': 'standard'},
                is_active=True
            )
            db_session.add(standard_plan)
            db_session.flush()
            
            # Cancel old subscription and create new standard subscription
            subscription.status = 'cancelled'
            standard_subscription = Subscription(
                user_id=user.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db_session.add(standard_subscription)
            db_session.commit()
            
            # Check permission after downgrade
            result_after = controller.check_permission(user.id, feature)
            level_after = result_after['subscription_level']
            allowed_after = result_after['allowed']
            
            # Verify downgrade
            assert level_before == 'premium'
            assert level_after == 'standard'
            
            # Verify permissions restricted (if feature was allowed before, it might not be allowed now)
            if feature in ['dashboard_trend', 'push_sms', 'keyword_custom', 'ai_decision']:
                # These are premium-only features
                assert allowed_before is True, f"Premium user should have access to {feature}"
                assert allowed_after is False, f"Standard user should not have access to {feature}"
            elif feature in ['dashboard_full', 'push_email', 'ai_brief']:
                # These are standard+ features
                assert allowed_before is True, f"Premium user should have access to {feature}"
                assert allowed_after is True, f"Standard user should still have access to {feature}"
    
    # Feature: subscription-enhancement, Property 4: 权限控制正确性
    @given(
        user_data=user_strategy(),
        subscription_level=subscription_level_strategy(),
        feature=feature_strategy()
    )
    @settings(
        max_examples=100,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_4_expired_subscription_denies_access(
        self, app, db_session, user_data, subscription_level, feature
    ):
        """
        Property 4: 权限控制正确性 - 过期订阅拒绝访问
        **Validates: Requirements 5.7**
        
        When subscription expires, user should be treated as free level
        """
        with app.app_context():
            # Skip free level (no subscription to expire)
            assume(subscription_level != 'free')
            
            # Create test user
            user = User(
                phone=user_data['phone'],
                nickname=user_data['nickname'],
                role='user'
            )
            db_session.add(user)
            db_session.flush()
            
            # Create subscription plan
            plan_names = {
                'standard': '标准版',
                'premium': '高级版'
            }
            plan_prices = {
                'standard': 299,
                'premium': 999
            }
            
            plan = SubscriptionPlan(
                name=plan_names[subscription_level],
                price=Decimal(str(plan_prices[subscription_level])),
                duration_days=365,
                features={'level': subscription_level},
                is_active=True
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create expired subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                start_date=datetime.utcnow() - timedelta(days=400),
                end_date=datetime.utcnow() - timedelta(days=35),  # Expired 35 days ago
                status='active'
            )
            db_session.add(subscription)
            db_session.commit()
            
            # Check permission
            controller = PermissionController()
            result = controller.check_permission(user.id, feature)
            
            # Verify expired subscription is treated as free
            assert result['subscription_level'] == 'free', \
                "Expired subscription should be treated as free level"
            assert result['is_expired'] is True, \
                "Result should indicate subscription is expired"
            
            # Free level features should still be denied (no active subscription)
            assert result['allowed'] is False
    
    # Feature: subscription-enhancement, Property 4: 权限控制正确性
    @given(
        user_data=user_strategy(),
        feature=feature_strategy()
    )
    @settings(
        max_examples=100,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_4_permission_denied_returns_error(
        self, app, db_session, user_data, feature
    ):
        """
        Property 4: 权限控制正确性 - 权限不足返回错误
        **Validates: Requirements 5.5**
        
        When user tries to access a feature beyond their subscription level,
        should return permission denied error with required level
        """
        with app.app_context():
            # Create test user
            user = User(
                phone=user_data['phone'],
                nickname=user_data['nickname'],
                role='user'
            )
            db_session.add(user)
            db_session.flush()
            
            # Create standard plan
            standard_plan = SubscriptionPlan(
                name='标准版',
                price=Decimal('299.00'),
                duration_days=365,
                features={'level': 'standard'},
                is_active=True
            )
            db_session.add(standard_plan)
            db_session.flush()
            
            # Create standard subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db_session.add(subscription)
            db_session.commit()
            
            # Check permission
            controller = PermissionController()
            result = controller.check_permission(user.id, feature)
            
            # If permission denied, should have required_level
            if not result['allowed']:
                assert 'required_level' in result, \
                    "Permission denied result should include required_level"
                assert result['required_level'] in ['free', 'standard', 'premium'], \
                    "Required level should be a valid subscription level"
                assert 'message' in result, \
                    "Permission denied result should include error message"
                
                # For premium-only features, required level should be premium
                if feature in ['dashboard_trend', 'push_sms', 'keyword_custom', 'ai_decision']:
                    assert result['required_level'] == 'premium', \
                        f"Feature {feature} should require premium level"
    
    # Feature: subscription-enhancement, Property 4: 权限控制正确性
    @given(
        user_data=user_strategy()
    )
    @settings(
        max_examples=100,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_4_permission_hierarchy_consistency(
        self, app, db_session, user_data
    ):
        """
        Property 4: 权限控制正确性 - 权限层级一致性
        **Validates: Requirements 5.1**
        
        Permission hierarchy should be consistent:
        - Standard includes all free features
        - Premium includes all standard features
        """
        with app.app_context():
            controller = PermissionController()
            
            # Get features for each level
            free_features = set(controller.get_available_features('free'))
            standard_features = set(controller.get_available_features('standard'))
            premium_features = set(controller.get_available_features('premium'))
            
            # Verify hierarchy
            assert free_features.issubset(standard_features), \
                "Standard level should include all free features"
            assert standard_features.issubset(premium_features), \
                "Premium level should include all standard features"
            
            # Verify no empty sets
            assert len(free_features) > 0, "Free level should have at least one feature"
            assert len(standard_features) > len(free_features), \
                "Standard level should have more features than free"
            assert len(premium_features) > len(standard_features), \
                "Premium level should have more features than standard"
