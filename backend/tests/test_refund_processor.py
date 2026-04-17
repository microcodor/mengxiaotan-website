"""
退款处理器单元测试
"""

import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, Order, RefundApplication, Subscription, SubscriptionPlan
from app.services.refund_processor import RefundProcessor


@pytest.fixture
def refund_processor(app):
    """创建退款处理器实例"""
    with app.app_context():
        yield RefundProcessor()


@pytest.fixture
def test_user(app):
    """创建测试用户"""
    import time
    with app.app_context():
        # Use timestamp to ensure unique phone number
        phone = f'138{int(time.time() * 1000) % 100000000:08d}'
        user = User(
            phone=phone,
            nickname='测试用户',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Refresh to get the ID
        db.session.refresh(user)
        user_id = user.id
        
        yield user
        
        # Clean up - fetch fresh instance
        user_to_delete = db.session.get(User, user_id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()


@pytest.fixture
def admin_user(app):
    """创建管理员用户"""
    import time
    with app.app_context():
        # Use timestamp to ensure unique phone number
        phone = f'139{int(time.time() * 1000) % 100000000:08d}'
        admin = User(
            phone=phone,
            nickname='管理员',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        # Refresh to get the ID
        db.session.refresh(admin)
        admin_id = admin.id
        
        yield admin
        
        # Clean up - fetch fresh instance
        admin_to_delete = db.session.get(User, admin_id)
        if admin_to_delete:
            db.session.delete(admin_to_delete)
            db.session.commit()


@pytest.fixture
def subscription_plan(app):
    """创建订阅套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='标准版',
            price=99.00,
            duration_days=30,
            features={'push': True, 'ai_brief': True}
        )
        db.session.add(plan)
        db.session.commit()
        
        # Refresh to get the ID
        db.session.refresh(plan)
        plan_id = plan.id
        
        yield plan
        
        # Clean up - fetch fresh instance
        plan_to_delete = db.session.get(SubscriptionPlan, plan_id)
        if plan_to_delete:
            db.session.delete(plan_to_delete)
            db.session.commit()


@pytest.fixture
def paid_order(app, test_user, subscription_plan):
    """创建已支付订单"""
    with app.app_context():
        order = Order(
            order_no=f'TEST{datetime.now().strftime("%Y%m%d%H%M%S%f")}',
            user_id=test_user.id,
            plan_id=subscription_plan.id,
            amount=99.00,
            payment_method='offline',
            payment_status='paid',
            payment_time=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()
        
        # Refresh to get the ID
        db.session.refresh(order)
        order_id = order.id
        
        yield order
        
        # Clean up - fetch fresh instance
        order_to_delete = db.session.get(Order, order_id)
        if order_to_delete:
            db.session.delete(order_to_delete)
            db.session.commit()


@pytest.fixture
def active_subscription(app, test_user, subscription_plan):
    """创建活跃订阅"""
    with app.app_context():
        subscription = Subscription(
            user_id=test_user.id,
            plan_id=subscription_plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            status='active'
        )
        db.session.add(subscription)
        db.session.commit()
        
        # Refresh to get the ID
        db.session.refresh(subscription)
        subscription_id = subscription.id
        
        yield subscription
        
        # Clean up - fetch fresh instance
        subscription_to_delete = db.session.get(Subscription, subscription_id)
        if subscription_to_delete:
            db.session.delete(subscription_to_delete)
            db.session.commit()


class TestCreateRefundApplication:
    """测试创建退款申请"""
    
    def test_create_refund_application_success(self, app, refund_processor, paid_order, test_user):
        """测试成功创建退款申请"""
        with app.app_context():
            reason = "服务不满意，申请退款"
            
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason=reason
            )
            
            # 验证返回结果
            assert 'application_id' in result
            assert result['status'] == 'pending'
            assert 'created_at' in result
            
            # 验证退款申请记录
            application = RefundApplication.query.get(result['application_id'])
            assert application is not None
            assert application.order_id == paid_order.id
            assert application.user_id == test_user.id
            assert application.reason == reason
            assert application.status == 'pending'
            
            # 验证订单状态更新
            order = Order.query.get(paid_order.id)
            assert order.payment_status == 'refund_pending'
            assert order.refund_status == 'pending'
            assert order.refund_reason == reason
            assert order.refund_applied_at is not None
            
            # 清理
            db.session.delete(application)
            db.session.commit()
    
    def test_create_refund_application_order_not_found(self, app, refund_processor, test_user):
        """测试订单不存在"""
        with app.app_context():
            with pytest.raises(ValueError, match="订单不存在"):
                refund_processor.create_refund_application(
                    order_id=99999,
                    user_id=test_user.id,
                    reason="测试"
                )
    
    def test_create_refund_application_order_not_belong_to_user(self, app, refund_processor, paid_order):
        """测试订单不属于该用户"""
        import time
        with app.app_context():
            # 创建另一个用户
            phone = f'137{int(time.time() * 1000) % 100000000:08d}'
            other_user = User(
                phone=phone,
                nickname='其他用户',
                role='user'
            )
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()
            
            try:
                with pytest.raises(ValueError, match="订单不属于该用户"):
                    refund_processor.create_refund_application(
                        order_id=paid_order.id,
                        user_id=other_user.id,
                        reason="测试"
                    )
            finally:
                db.session.delete(other_user)
                db.session.commit()
    
    def test_create_refund_application_order_not_paid(self, app, refund_processor, test_user, subscription_plan):
        """测试订单状态不是已支付"""
        with app.app_context():
            # 创建待支付订单
            pending_order = Order(
                order_no=f'PENDING{datetime.now().strftime("%Y%m%d%H%M%S%f")}',
                user_id=test_user.id,
                plan_id=subscription_plan.id,
                amount=99.00,
                payment_method='offline',
                payment_status='pending'
            )
            db.session.add(pending_order)
            db.session.commit()
            
            try:
                with pytest.raises(ValueError, match="订单状态必须为已支付才能申请退款"):
                    refund_processor.create_refund_application(
                        order_id=pending_order.id,
                        user_id=test_user.id,
                        reason="测试"
                    )
            finally:
                db.session.delete(pending_order)
                db.session.commit()
    
    def test_create_refund_application_duplicate_pending(self, app, refund_processor, paid_order, test_user):
        """测试已有待处理的退款申请"""
        with app.app_context():
            # 创建第一个退款申请
            result1 = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="第一次申请"
            )
            
            try:
                # 尝试创建第二个退款申请
                with pytest.raises(ValueError, match="该订单已有待处理的退款申请"):
                    refund_processor.create_refund_application(
                        order_id=paid_order.id,
                        user_id=test_user.id,
                        reason="第二次申请"
                    )
            finally:
                # 清理
                application = RefundApplication.query.get(result1['application_id'])
                if application:
                    db.session.delete(application)
                    db.session.commit()


class TestApproveRefund:
    """测试批准退款"""
    
    def test_approve_refund_success(self, app, refund_processor, paid_order, test_user, admin_user, active_subscription):
        """测试成功批准退款"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # 批准退款
                success = refund_processor.approve_refund(
                    application_id=application_id,
                    admin_id=admin_user.id
                )
                
                assert success is True
                
                # 验证退款申请状态
                application = RefundApplication.query.get(application_id)
                assert application.status == 'approved'
                assert application.processed_by == admin_user.id
                assert application.processed_at is not None
                
                # 验证订单状态
                order = Order.query.get(paid_order.id)
                assert order.payment_status == 'refunded'
                assert order.refund_status == 'approved'
                assert order.refund_processed_by == admin_user.id
                assert order.refund_processed_at is not None
                
                # 验证订阅状态
                subscription = Subscription.query.get(active_subscription.id)
                assert subscription.status == 'cancelled'
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_approve_refund_application_not_found(self, app, refund_processor, admin_user):
        """测试退款申请不存在"""
        with app.app_context():
            with pytest.raises(ValueError, match="退款申请不存在"):
                refund_processor.approve_refund(
                    application_id=99999,
                    admin_id=admin_user.id
                )
    
    def test_approve_refund_application_not_pending(self, app, refund_processor, paid_order, test_user, admin_user):
        """测试退款申请状态不是待处理"""
        with app.app_context():
            # 创建并批准退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                refund_processor.approve_refund(
                    application_id=application_id,
                    admin_id=admin_user.id
                )
                
                # 尝试再次批准
                with pytest.raises(ValueError, match="退款申请状态必须为待处理"):
                    refund_processor.approve_refund(
                        application_id=application_id,
                        admin_id=admin_user.id
                    )
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()


class TestRejectRefund:
    """测试拒绝退款"""
    
    def test_reject_refund_success(self, app, refund_processor, paid_order, test_user, admin_user):
        """测试成功拒绝退款"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # 拒绝退款
                reject_reason = "不符合退款条件"
                success = refund_processor.reject_refund(
                    application_id=application_id,
                    admin_id=admin_user.id,
                    reason=reject_reason
                )
                
                assert success is True
                
                # 验证退款申请状态
                application = RefundApplication.query.get(application_id)
                assert application.status == 'rejected'
                assert application.processed_by == admin_user.id
                assert application.processed_at is not None
                assert application.reject_reason == reject_reason
                
                # 验证订单状态恢复为 paid
                order = Order.query.get(paid_order.id)
                assert order.payment_status == 'paid'
                assert order.refund_status == 'rejected'
                assert order.refund_processed_by == admin_user.id
                assert order.refund_processed_at is not None
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_reject_refund_application_not_found(self, app, refund_processor, admin_user):
        """测试退款申请不存在"""
        with app.app_context():
            with pytest.raises(ValueError, match="退款申请不存在"):
                refund_processor.reject_refund(
                    application_id=99999,
                    admin_id=admin_user.id,
                    reason="测试"
                )


class TestGetPendingApplications:
    """测试获取待处理退款申请"""
    
    def test_get_pending_applications_empty(self, app, refund_processor):
        """测试没有待处理申请"""
        with app.app_context():
            result = refund_processor.get_pending_applications()
            
            assert result['applications'] == []
            assert result['total'] == 0
            assert result['page'] == 1
    
    def test_get_pending_applications_with_data(self, app, refund_processor, test_user, subscription_plan):
        """测试有待处理申请"""
        with app.app_context():
            # 创建多个订单和退款申请
            applications = []
            orders = []
            
            for i in range(3):
                order = Order(
                    order_no=f'TEST{datetime.now().strftime("%Y%m%d%H%M%S%f")}{i}',
                    user_id=test_user.id,
                    plan_id=subscription_plan.id,
                    amount=99.00,
                    payment_method='offline',
                    payment_status='paid',
                    payment_time=datetime.utcnow()
                )
                db.session.add(order)
                db.session.commit()
                orders.append(order)
                
                result = refund_processor.create_refund_application(
                    order_id=order.id,
                    user_id=test_user.id,
                    reason=f"退款原因 {i+1}"
                )
                applications.append(result['application_id'])
            
            try:
                # 查询待处理申请
                result = refund_processor.get_pending_applications()
                
                assert len(result['applications']) >= 3
                assert result['total'] >= 3
                assert result['page'] == 1
                
                # 验证返回的数据结构
                app_data = result['applications'][0]
                assert 'id' in app_data
                assert 'order_id' in app_data
                assert 'order_no' in app_data
                assert 'user_id' in app_data
                assert 'user_phone' in app_data
                assert 'amount' in app_data
                assert 'reason' in app_data
                assert 'status' in app_data
                assert 'applied_at' in app_data
                assert 'plan_name' in app_data
                
            finally:
                # 清理
                for app_id in applications:
                    application = RefundApplication.query.get(app_id)
                    if application:
                        db.session.delete(application)
                
                for order in orders:
                    db.session.delete(order)
                
                db.session.commit()
    
    def test_get_pending_applications_pagination(self, app, refund_processor, test_user, subscription_plan):
        """测试分页功能"""
        with app.app_context():
            # 创建5个退款申请
            applications = []
            orders = []
            
            for i in range(5):
                order = Order(
                    order_no=f'PAGE{datetime.now().strftime("%Y%m%d%H%M%S%f")}{i}',
                    user_id=test_user.id,
                    plan_id=subscription_plan.id,
                    amount=99.00,
                    payment_method='offline',
                    payment_status='paid',
                    payment_time=datetime.utcnow()
                )
                db.session.add(order)
                db.session.commit()
                orders.append(order)
                
                result = refund_processor.create_refund_application(
                    order_id=order.id,
                    user_id=test_user.id,
                    reason=f"退款原因 {i+1}"
                )
                applications.append(result['application_id'])
            
            try:
                # 第一页，每页2条
                result_page1 = refund_processor.get_pending_applications(page=1, per_page=2)
                assert len(result_page1['applications']) == 2
                assert result_page1['total'] >= 5
                
                # 第二页
                result_page2 = refund_processor.get_pending_applications(page=2, per_page=2)
                assert len(result_page2['applications']) == 2
                
                # 第三页
                result_page3 = refund_processor.get_pending_applications(page=3, per_page=2)
                assert len(result_page3['applications']) >= 1
                
            finally:
                # 清理
                for app_id in applications:
                    application = RefundApplication.query.get(app_id)
                    if application:
                        db.session.delete(application)
                
                for order in orders:
                    db.session.delete(order)
                
                db.session.commit()



class TestNotifyUser:
    """测试退款通知功能"""
    
    def test_notify_user_pending_status(self, app, refund_processor, paid_order, test_user, mocker):
        """测试发送待处理状态通知"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # Mock MultiChannelPusher
                mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
                mock_pusher_instance = mock_pusher.return_value
                mock_pusher_instance.push.return_value = {
                    'email': {'success': True, 'message': '邮件发送成功'}
                }
                
                # 调用通知方法
                success = refund_processor.notify_user(application_id, 'pending')
                
                assert success is True
                
                # 验证 push 方法被调用
                mock_pusher_instance.push.assert_called_once()
                call_args = mock_pusher_instance.push.call_args
                
                # 验证调用参数
                assert call_args[1]['user_id'] == test_user.id
                assert '退款申请已提交' in call_args[1]['subject']
                assert paid_order.order_no in call_args[1]['content']
                assert '申请退款' in call_args[1]['content']
                assert call_args[1]['html'] is True
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_notify_user_approved_status(self, app, refund_processor, paid_order, test_user, admin_user, active_subscription, mocker):
        """测试发送批准状态通知"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # Mock MultiChannelPusher
                mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
                mock_pusher_instance = mock_pusher.return_value
                mock_pusher_instance.push.return_value = {
                    'email': {'success': True, 'message': '邮件发送成功'}
                }
                
                # 批准退款（会自动调用 notify_user）
                refund_processor.approve_refund(application_id, admin_user.id)
                
                # 验证 push 方法被调用（创建时一次，批准时一次）
                assert mock_pusher_instance.push.call_count == 2
                
                # 获取最后一次调用（批准通知）
                last_call_args = mock_pusher_instance.push.call_args
                
                # 验证调用参数
                assert last_call_args[1]['user_id'] == test_user.id
                assert '退款申请已批准' in last_call_args[1]['subject']
                assert paid_order.order_no in last_call_args[1]['content']
                assert '订阅已取消' in last_call_args[1]['content']
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_notify_user_rejected_status(self, app, refund_processor, paid_order, test_user, admin_user, mocker):
        """测试发送拒绝状态通知"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # Mock MultiChannelPusher
                mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
                mock_pusher_instance = mock_pusher.return_value
                mock_pusher_instance.push.return_value = {
                    'email': {'success': True, 'message': '邮件发送成功'}
                }
                
                # 拒绝退款（会自动调用 notify_user）
                reject_reason = "不符合退款条件"
                refund_processor.reject_refund(application_id, admin_user.id, reject_reason)
                
                # 验证 push 方法被调用（创建时一次，拒绝时一次）
                assert mock_pusher_instance.push.call_count == 2
                
                # 获取最后一次调用（拒绝通知）
                last_call_args = mock_pusher_instance.push.call_args
                
                # 验证调用参数
                assert last_call_args[1]['user_id'] == test_user.id
                assert '退款申请已拒绝' in last_call_args[1]['subject']
                assert paid_order.order_no in last_call_args[1]['content']
                assert reject_reason in last_call_args[1]['content']
                assert '订阅仍然有效' in last_call_args[1]['content']
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_notify_user_application_not_found(self, app, refund_processor, mocker):
        """测试退款申请不存在时的通知"""
        with app.app_context():
            # Mock MultiChannelPusher
            mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
            
            # 调用通知方法（申请不存在）
            success = refund_processor.notify_user(99999, 'pending')
            
            # 应该返回 False（但不抛出异常）
            assert success is False
            
            # 验证 push 方法未被调用
            mock_pusher.return_value.push.assert_not_called()
    
    def test_notify_user_push_failure_does_not_affect_refund(self, app, refund_processor, paid_order, test_user, mocker):
        """测试推送失败不影响退款操作"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # Mock MultiChannelPusher 使其失败
                mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
                mock_pusher_instance = mock_pusher.return_value
                mock_pusher_instance.push.return_value = {
                    'email': {'success': False, 'message': '邮件发送失败'},
                    'wechat': {'success': False, 'message': '企业微信发送失败'}
                }
                
                # 调用通知方法
                success = refund_processor.notify_user(application_id, 'pending')
                
                # 即使推送失败，也应该返回 True（不影响退款操作）
                assert success is True
                
                # 验证退款申请仍然存在且状态正确
                application = RefundApplication.query.get(application_id)
                assert application is not None
                assert application.status == 'pending'
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_notify_user_exception_handling(self, app, refund_processor, paid_order, test_user, mocker):
        """测试通知异常处理"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="申请退款"
            )
            application_id = result['application_id']
            
            try:
                # Mock MultiChannelPusher 使其抛出异常
                mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
                mock_pusher_instance = mock_pusher.return_value
                mock_pusher_instance.push.side_effect = Exception("推送服务异常")
                
                # 调用通知方法
                success = refund_processor.notify_user(application_id, 'pending')
                
                # 即使抛出异常，也应该返回 True（不影响退款操作）
                assert success is True
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
    
    def test_notification_content_includes_all_required_info(self, app, refund_processor, paid_order, test_user, mocker):
        """测试通知内容包含所有必需信息"""
        with app.app_context():
            # 创建退款申请
            result = refund_processor.create_refund_application(
                order_id=paid_order.id,
                user_id=test_user.id,
                reason="服务不满意"
            )
            application_id = result['application_id']
            
            try:
                # Mock MultiChannelPusher
                mock_pusher = mocker.patch('app.services.refund_processor.MultiChannelPusher')
                mock_pusher_instance = mock_pusher.return_value
                mock_pusher_instance.push.return_value = {
                    'email': {'success': True, 'message': '邮件发送成功'}
                }
                
                # 调用通知方法
                refund_processor.notify_user(application_id, 'pending')
                
                # 获取调用参数
                call_args = mock_pusher_instance.push.call_args
                content = call_args[1]['content']
                
                # 验证通知内容包含所有必需信息
                assert paid_order.order_no in content  # 订单号
                assert str(paid_order.amount) in content  # 订单金额
                assert '服务不满意' in content  # 退款原因
                
                # 验证HTML格式
                assert '<h3>' in content
                assert '<ul>' in content
                assert '<li>' in content
                
            finally:
                # 清理
                application = RefundApplication.query.get(application_id)
                if application:
                    db.session.delete(application)
                    db.session.commit()
