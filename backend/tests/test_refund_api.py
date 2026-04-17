"""
退款API端点集成测试

测试退款申请创建、审批和拒绝的API端点功能。
"""

import pytest
from datetime import datetime, timedelta
from app.models import User, Order, SubscriptionPlan, Subscription, RefundApplication
from app import db


@pytest.fixture
def test_user(client):
    """创建测试用户"""
    user = User(
        phone='13800138000',
        nickname='测试用户',
        role='user',
        status='active'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(client):
    """创建管理员用户"""
    admin = User(
        phone='13900139000',
        nickname='管理员',
        role='admin',
        status='active'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def test_plan(client):
    """创建测试订阅套餐"""
    plan = SubscriptionPlan(
        name='标准版',
        price=99.00,
        duration_days=30,
        features={'feature1': True},
        is_active=True
    )
    db.session.add(plan)
    db.session.commit()
    return plan


@pytest.fixture
def paid_order(client, test_user, test_plan):
    """创建已支付订单"""
    order = Order(
        order_no='ORD20240101000001',
        user_id=test_user.id,
        plan_id=test_plan.id,
        amount=test_plan.price,
        payment_method='alipay',
        payment_status='paid',
        payment_time=datetime.utcnow()
    )
    db.session.add(order)
    db.session.commit()
    return order


@pytest.fixture
def user_token(client, test_user):
    """获取用户JWT token"""
    response = client.post('/api/auth/login', json={
        'phone': '13800138000',
        'password': 'password123'
    })
    return response.json['access_token']


@pytest.fixture
def admin_token(client, admin_user):
    """获取管理员JWT token"""
    response = client.post('/api/auth/login', json={
        'phone': '13900139000',
        'password': 'admin123'
    })
    return response.json['access_token']


class TestRefundApplicationAPI:
    """测试用户退款申请API"""
    
    def test_create_refund_application_success(self, client, paid_order, user_token):
        """测试成功创建退款申请"""
        response = client.post(
            '/api/subscriptions/refunds',
            json={
                'order_id': paid_order.id,
                'reason': '服务不满意，申请退款'
            },
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['success'] is True
        assert 'application_id' in data['data']
        assert data['data']['status'] == 'pending'
        
        # 验证数据库记录
        application = RefundApplication.query.get(data['data']['application_id'])
        assert application is not None
        assert application.order_id == paid_order.id
        assert application.reason == '服务不满意，申请退款'
        assert application.status == 'pending'
        
        # 验证订单状态已更新
        order = Order.query.get(paid_order.id)
        assert order.payment_status == 'refund_pending'
        assert order.refund_status == 'pending'
    
    def test_create_refund_application_missing_order_id(self, client, user_token):
        """测试缺少order_id字段"""
        response = client.post(
            '/api/subscriptions/refunds',
            json={
                'reason': '申请退款'
            },
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 400
        assert response.json['success'] is False
        assert '缺少 order_id' in response.json['error']
    
    def test_create_refund_application_missing_reason(self, client, paid_order, user_token):
        """测试缺少退款原因"""
        response = client.post(
            '/api/subscriptions/refunds',
            json={
                'order_id': paid_order.id
            },
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 400
        assert response.json['success'] is False
        assert '退款原因不能为空' in response.json['error']
    
    def test_create_refund_application_order_not_paid(self, client, test_user, test_plan, user_token):
        """测试订单状态不是paid时无法申请退款"""
        # 创建pending状态的订单
        order = Order(
            order_no='ORD20240101000002',
            user_id=test_user.id,
            plan_id=test_plan.id,
            amount=test_plan.price,
            payment_method='alipay',
            payment_status='pending'
        )
        db.session.add(order)
        db.session.commit()
        
        response = client.post(
            '/api/subscriptions/refunds',
            json={
                'order_id': order.id,
                'reason': '申请退款'
            },
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 400
        assert response.json['success'] is False
        assert '订单状态必须为已支付' in response.json['error']
    
    def test_create_refund_application_duplicate(self, client, paid_order, user_token):
        """测试重复申请退款"""
        # 第一次申请
        client.post(
            '/api/subscriptions/refunds',
            json={
                'order_id': paid_order.id,
                'reason': '第一次申请'
            },
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        # 第二次申请
        response = client.post(
            '/api/subscriptions/refunds',
            json={
                'order_id': paid_order.id,
                'reason': '第二次申请'
            },
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 400
        assert response.json['success'] is False
        assert '已有待处理的退款申请' in response.json['error']
    
    def test_get_refund_applications_list(self, client, paid_order, user_token):
        """测试获取退款申请列表"""
        # 创建退款申请
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='测试退款',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.get(
            '/api/subscriptions/refunds',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert len(data['data']) > 0
        assert data['data'][0]['id'] == application.id
        assert data['data'][0]['status'] == 'pending'
    
    def test_get_refund_application_detail(self, client, paid_order, user_token):
        """测试获取退款申请详情"""
        # 创建退款申请
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='测试退款详情',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.get(
            f'/api/subscriptions/refunds/{application.id}',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert data['data']['id'] == application.id
        assert data['data']['reason'] == '测试退款详情'
        assert data['data']['status'] == 'pending'
    
    def test_get_refund_application_not_found(self, client, user_token):
        """测试获取不存在的退款申请"""
        response = client.get(
            '/api/subscriptions/refunds/99999',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 404
        assert response.json['success'] is False


class TestAdminRefundAPI:
    """测试管理员退款审批API"""
    
    def test_get_pending_refunds_list(self, client, paid_order, admin_token):
        """测试获取待处理退款列表"""
        # 创建待处理退款申请
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='待审批退款',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.get(
            '/api/admin/refunds',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'items' in data
        assert len(data['items']) > 0
        assert data['items'][0]['status'] == 'pending'
    
    def test_get_refunds_list_with_status_filter(self, client, paid_order, admin_token):
        """测试按状态过滤退款列表"""
        # 创建不同状态的退款申请
        app1 = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='待审批',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(app1)
        db.session.commit()
        
        response = client.get(
            '/api/admin/refunds?status=pending',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert all(item['status'] == 'pending' for item in data['items'])
    
    def test_get_refund_detail_as_admin(self, client, paid_order, admin_token):
        """测试管理员获取退款详情"""
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='管理员查看详情',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.get(
            f'/api/admin/refunds/{application.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == application.id
        assert 'order' in data
        assert 'user' in data
        assert 'plan' in data
    
    def test_approve_refund_success(self, client, paid_order, test_plan, admin_token, admin_user):
        """测试成功批准退款"""
        # 创建订阅
        subscription = Subscription(
            user_id=paid_order.user_id,
            plan_id=test_plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            status='active'
        )
        db.session.add(subscription)
        
        # 创建退款申请
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='批准测试',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.post(
            f'/api/admin/refunds/{application.id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert '已批准' in data['message']
        
        # 验证退款申请状态
        app = RefundApplication.query.get(application.id)
        assert app.status == 'approved'
        assert app.processed_by == admin_user.id
        assert app.processed_at is not None
        
        # 验证订单状态
        order = Order.query.get(paid_order.id)
        assert order.payment_status == 'refunded'
        assert order.refund_status == 'approved'
        
        # 验证订阅状态
        sub = Subscription.query.get(subscription.id)
        assert sub.status == 'cancelled'
    
    def test_approve_refund_not_pending(self, client, paid_order, admin_token):
        """测试批准非待处理状态的退款"""
        # 创建已批准的退款申请
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='已批准',
            status='approved',
            applied_at=datetime.utcnow(),
            processed_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.post(
            f'/api/admin/refunds/{application.id}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 400
        assert '状态必须为待处理' in response.json['message']
    
    def test_reject_refund_success(self, client, paid_order, admin_token, admin_user):
        """测试成功拒绝退款"""
        # 创建退款申请
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='拒绝测试',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.post(
            f'/api/admin/refunds/{application.id}/reject',
            json={'reason': '不符合退款条件'},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert '已拒绝' in data['message']
        
        # 验证退款申请状态
        app = RefundApplication.query.get(application.id)
        assert app.status == 'rejected'
        assert app.processed_by == admin_user.id
        assert app.processed_at is not None
        assert app.reject_reason == '不符合退款条件'
        
        # 验证订单状态恢复为paid
        order = Order.query.get(paid_order.id)
        assert order.payment_status == 'paid'
        assert order.refund_status == 'rejected'
    
    def test_reject_refund_missing_reason(self, client, paid_order, admin_token):
        """测试拒绝退款时缺少原因"""
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='测试',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.post(
            f'/api/admin/refunds/{application.id}/reject',
            json={},
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 400
        assert '拒绝原因不能为空' in response.json['message']
    
    def test_approve_refund_without_admin_permission(self, client, paid_order, user_token):
        """测试非管理员无法批准退款"""
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='权限测试',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.post(
            f'/api/admin/refunds/{application.id}/approve',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 403
        assert '需要管理员权限' in response.json['message']
    
    def test_reject_refund_without_admin_permission(self, client, paid_order, user_token):
        """测试非管理员无法拒绝退款"""
        application = RefundApplication(
            order_id=paid_order.id,
            user_id=paid_order.user_id,
            reason='权限测试',
            status='pending',
            applied_at=datetime.utcnow()
        )
        db.session.add(application)
        db.session.commit()
        
        response = client.post(
            f'/api/admin/refunds/{application.id}/reject',
            json={'reason': '测试'},
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 403
        assert '需要管理员权限' in response.json['message']


class TestRefundAPIPermissions:
    """测试退款API权限控制"""
    
    def test_create_refund_without_auth(self, client, paid_order):
        """测试未认证用户无法创建退款申请"""
        response = client.post(
            '/api/subscriptions/refunds',
            json={
                'order_id': paid_order.id,
                'reason': '测试'
            }
        )
        
        assert response.status_code == 401
    
    def test_get_refunds_without_auth(self, client):
        """测试未认证用户无法获取退款列表"""
        response = client.get('/api/subscriptions/refunds')
        
        assert response.status_code == 401
    
    def test_admin_get_refunds_without_auth(self, client):
        """测试未认证用户无法访问管理员退款接口"""
        response = client.get('/api/admin/refunds')
        
        assert response.status_code == 401
