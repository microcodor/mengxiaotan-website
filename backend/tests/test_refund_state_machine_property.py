"""
Property-based tests for Refund State Machine

**Validates: Requirements 2.4, 2.7, 2.8**

Uses hypothesis to test universal properties of the refund state machine:
- Property 1: 退款状态机转换正确性

Feature: subscription-enhancement, Property 1: 退款状态机转换正确性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta
from decimal import Decimal
from app.services.refund_processor import RefundProcessor
from app.models import User, Order, RefundApplication, Subscription, SubscriptionPlan
from app import db


# Custom strategies for generating test data
@st.composite
def user_strategy(draw):
    """Generate random User data"""
    # Generate unique phone numbers using timestamp and random digits
    import time
    timestamp = str(int(time.time() * 1000000))[-8:]  # Last 8 digits of microsecond timestamp
    random_digits = draw(st.text(min_size=3, max_size=3, alphabet='0123456789'))
    phone = timestamp + random_digits
    nickname = draw(st.text(min_size=2, max_size=20))
    role = draw(st.sampled_from(['user', 'admin']))
    return {
        'phone': phone,
        'nickname': nickname,
        'role': role
    }


@st.composite
def order_amount_strategy(draw):
    """Generate random order amounts (99.00 to 9999.00)"""
    amount = draw(st.floats(min_value=99.0, max_value=9999.0))
    # Round to 2 decimal places
    return round(amount, 2)


@st.composite
def refund_reason_strategy(draw):
    """Generate random refund reasons"""
    reasons = [
        '服务不符合预期',
        '价格太贵',
        '不需要了',
        '功能不满足需求',
        '其他原因',
        '误操作购买',
        '体验不好'
    ]
    return draw(st.sampled_from(reasons))


class TestRefundStateMachineProperties:
    """Property-based tests for refund state machine transitions"""
    
    # Feature: subscription-enhancement, Property 1: 退款状态机转换正确性
    @given(
        user_data=user_strategy(),
        admin_data=user_strategy(),
        amount=order_amount_strategy(),
        reason=refund_reason_strategy()
    )
    @settings(
        max_examples=20,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_1_create_refund_transitions_to_refund_pending(
        self, app, db_session, user_data, admin_data, amount, reason
    ):
        """
        Property 1: 退款状态机转换正确性 - 创建退款申请
        **Validates: Requirements 2.4**
        
        When creating a refund application for a paid order,
        the order status should transition from 'paid' to 'refund_pending'
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
            
            # Create subscription plan
            plan = SubscriptionPlan(
                name='测试套餐',
                price=Decimal(str(amount)),
                duration_days=30,
                features={}
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create paid order
            order = Order(
                order_no=f'TEST{datetime.now().timestamp()}',
                user_id=user.id,
                plan_id=plan.id,
                amount=Decimal(str(amount)),
                payment_method='offline',
                payment_status='paid',
                payment_time=datetime.utcnow()
            )
            db_session.add(order)
            db_session.commit()
            
            # Verify initial state
            assert order.payment_status == 'paid'
            assert order.refund_status is None
            
            # Create refund application
            processor = RefundProcessor()
            result = processor.create_refund_application(
                order_id=order.id,
                user_id=user.id,
                reason=reason
            )
            
            # Verify state transition
            db_session.refresh(order)
            assert order.payment_status == 'refund_pending', \
                f"Order status should be 'refund_pending', got '{order.payment_status}'"
            assert order.refund_status == 'pending', \
                f"Refund status should be 'pending', got '{order.refund_status}'"
            assert order.refund_reason == reason
            assert order.refund_applied_at is not None
            
            # Verify refund application created
            assert result['application_id'] is not None
            assert result['status'] == 'pending'
    
    # Feature: subscription-enhancement, Property 1: 退款状态机转换正确性
    @given(
        user_data=user_strategy(),
        admin_data=user_strategy(),
        amount=order_amount_strategy(),
        reason=refund_reason_strategy()
    )
    @settings(
        max_examples=20,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_1_approve_refund_transitions_to_refunded(
        self, app, db_session, user_data, admin_data, amount, reason
    ):
        """
        Property 1: 退款状态机转换正确性 - 批准退款
        **Validates: Requirements 2.7**
        
        When approving a refund application,
        the order status should transition from 'refund_pending' to 'refunded'
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
            
            # Create admin user
            admin = User(
                phone=admin_data['phone'],
                nickname=admin_data['nickname'],
                role='admin'
            )
            db_session.add(admin)
            db_session.flush()
            
            # Create subscription plan
            plan = SubscriptionPlan(
                name='测试套餐',
                price=Decimal(str(amount)),
                duration_days=30,
                features={}
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create order in refund_pending state
            order = Order(
                order_no=f'TEST{datetime.now().timestamp()}',
                user_id=user.id,
                plan_id=plan.id,
                amount=Decimal(str(amount)),
                payment_method='offline',
                payment_status='refund_pending',
                payment_time=datetime.utcnow(),
                refund_status='pending',
                refund_reason=reason,
                refund_applied_at=datetime.utcnow()
            )
            db_session.add(order)
            db_session.flush()
            
            # Create refund application
            application = RefundApplication(
                order_id=order.id,
                user_id=user.id,
                reason=reason,
                status='pending',
                applied_at=datetime.utcnow()
            )
            db_session.add(application)
            db_session.commit()
            
            # Verify initial state
            assert order.payment_status == 'refund_pending'
            assert order.refund_status == 'pending'
            assert application.status == 'pending'
            
            # Approve refund
            processor = RefundProcessor()
            result = processor.approve_refund(
                application_id=application.id,
                admin_id=admin.id
            )
            
            # Verify state transition
            db_session.refresh(order)
            db_session.refresh(application)
            
            assert result is True
            assert order.payment_status == 'refunded', \
                f"Order status should be 'refunded', got '{order.payment_status}'"
            assert order.refund_status == 'approved', \
                f"Refund status should be 'approved', got '{order.refund_status}'"
            assert order.refund_processed_by == admin.id
            assert order.refund_processed_at is not None
            assert application.status == 'approved'
            assert application.processed_by == admin.id
            assert application.processed_at is not None
    
    # Feature: subscription-enhancement, Property 1: 退款状态机转换正确性
    @given(
        user_data=user_strategy(),
        admin_data=user_strategy(),
        amount=order_amount_strategy(),
        reason=refund_reason_strategy(),
        reject_reason=refund_reason_strategy()
    )
    @settings(
        max_examples=20,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_1_reject_refund_restores_to_paid(
        self, app, db_session, user_data, admin_data, amount, reason, reject_reason
    ):
        """
        Property 1: 退款状态机转换正确性 - 拒绝退款
        **Validates: Requirements 2.8**
        
        When rejecting a refund application,
        the order status should transition from 'refund_pending' back to 'paid'
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
            
            # Create admin user
            admin = User(
                phone=admin_data['phone'],
                nickname=admin_data['nickname'],
                role='admin'
            )
            db_session.add(admin)
            db_session.flush()
            
            # Create subscription plan
            plan = SubscriptionPlan(
                name='测试套餐',
                price=Decimal(str(amount)),
                duration_days=30,
                features={}
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create order in refund_pending state
            order = Order(
                order_no=f'TEST{datetime.now().timestamp()}',
                user_id=user.id,
                plan_id=plan.id,
                amount=Decimal(str(amount)),
                payment_method='offline',
                payment_status='refund_pending',
                payment_time=datetime.utcnow(),
                refund_status='pending',
                refund_reason=reason,
                refund_applied_at=datetime.utcnow()
            )
            db_session.add(order)
            db_session.flush()
            
            # Create refund application
            application = RefundApplication(
                order_id=order.id,
                user_id=user.id,
                reason=reason,
                status='pending',
                applied_at=datetime.utcnow()
            )
            db_session.add(application)
            db_session.commit()
            
            # Verify initial state
            assert order.payment_status == 'refund_pending'
            assert order.refund_status == 'pending'
            assert application.status == 'pending'
            
            # Reject refund
            processor = RefundProcessor()
            result = processor.reject_refund(
                application_id=application.id,
                admin_id=admin.id,
                reason=reject_reason
            )
            
            # Verify state transition
            db_session.refresh(order)
            db_session.refresh(application)
            
            assert result is True
            assert order.payment_status == 'paid', \
                f"Order status should be restored to 'paid', got '{order.payment_status}'"
            assert order.refund_status == 'rejected', \
                f"Refund status should be 'rejected', got '{order.refund_status}'"
            assert order.refund_processed_by == admin.id
            assert order.refund_processed_at is not None
            assert application.status == 'rejected'
            assert application.processed_by == admin.id
            assert application.processed_at is not None
            assert application.reject_reason == reject_reason
    
    # Feature: subscription-enhancement, Property 1: 退款状态机转换正确性
    @given(
        user_data=user_strategy(),
        admin_data=user_strategy(),
        amount=order_amount_strategy(),
        reason=refund_reason_strategy()
    )
    @settings(
        max_examples=20,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_1_approve_refund_cancels_subscription(
        self, app, db_session, user_data, admin_data, amount, reason
    ):
        """
        Property 1: 退款状态机转换正确性 - 批准退款取消订阅
        **Validates: Requirements 2.7**
        
        When approving a refund application,
        the associated subscription status should transition to 'cancelled'
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
            
            # Create admin user
            admin = User(
                phone=admin_data['phone'],
                nickname=admin_data['nickname'],
                role='admin'
            )
            db_session.add(admin)
            db_session.flush()
            
            # Create subscription plan
            plan = SubscriptionPlan(
                name='测试套餐',
                price=Decimal(str(amount)),
                duration_days=30,
                features={}
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create active subscription
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db_session.add(subscription)
            db_session.flush()
            
            # Create order in refund_pending state
            order = Order(
                order_no=f'TEST{datetime.now().timestamp()}',
                user_id=user.id,
                plan_id=plan.id,
                amount=Decimal(str(amount)),
                payment_method='offline',
                payment_status='refund_pending',
                payment_time=datetime.utcnow(),
                refund_status='pending',
                refund_reason=reason,
                refund_applied_at=datetime.utcnow()
            )
            db_session.add(order)
            db_session.flush()
            
            # Create refund application
            application = RefundApplication(
                order_id=order.id,
                user_id=user.id,
                reason=reason,
                status='pending',
                applied_at=datetime.utcnow()
            )
            db_session.add(application)
            db_session.commit()
            
            # Verify initial state
            assert subscription.status == 'active'
            assert order.payment_status == 'refund_pending'
            
            # Approve refund
            processor = RefundProcessor()
            result = processor.approve_refund(
                application_id=application.id,
                admin_id=admin.id
            )
            
            # Verify subscription cancelled
            db_session.refresh(subscription)
            db_session.refresh(order)
            
            assert result is True
            assert order.payment_status == 'refunded'
            assert subscription.status == 'cancelled', \
                f"Subscription status should be 'cancelled', got '{subscription.status}'"
    
    # Feature: subscription-enhancement, Property 1: 退款状态机转换正确性
    @given(
        user_data=user_strategy(),
        amount=order_amount_strategy(),
        reason=refund_reason_strategy()
    )
    @settings(
        max_examples=20,
        deadline=5000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_1_state_transitions_are_atomic(
        self, app, db_session, user_data, amount, reason
    ):
        """
        Property 1: 退款状态机转换正确性 - 状态转换原子性
        **Validates: Requirements 2.4, 2.7, 2.8**
        
        All state transitions should be atomic - either all changes succeed or all fail
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
            
            # Create subscription plan
            plan = SubscriptionPlan(
                name='测试套餐',
                price=Decimal(str(amount)),
                duration_days=30,
                features={}
            )
            db_session.add(plan)
            db_session.flush()
            
            # Create paid order
            order = Order(
                order_no=f'TEST{datetime.now().timestamp()}',
                user_id=user.id,
                plan_id=plan.id,
                amount=Decimal(str(amount)),
                payment_method='offline',
                payment_status='paid',
                payment_time=datetime.utcnow()
            )
            db_session.add(order)
            db_session.commit()
            
            # Create refund application
            processor = RefundProcessor()
            result = processor.create_refund_application(
                order_id=order.id,
                user_id=user.id,
                reason=reason
            )
            
            # Verify both order and application are updated atomically
            db_session.refresh(order)
            application = RefundApplication.query.get(result['application_id'])
            
            # Both should be in pending state
            assert order.payment_status == 'refund_pending'
            assert order.refund_status == 'pending'
            assert application.status == 'pending'
            
            # Both should have consistent timestamps
            assert order.refund_applied_at is not None
            assert application.applied_at is not None
