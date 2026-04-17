"""
测试支付凭证查看和下载功能

测试需求:
- 需求1.4: 在订单列表中显示支付凭证的缩略图或下载链接
- 需求1.5: 管理员审核订单时，提供查看支付凭证的功能
- 需求1.6: 管理员能够下载支付凭证进行核对
"""

import os
import pytest
import tempfile
from io import BytesIO
from flask_jwt_extended import create_access_token
from app.models import User, Order, SubscriptionPlan
from app import db


@pytest.fixture
def test_users(app, db_session):
    """创建测试用户（普通用户和管理员）"""
    with app.app_context():
        # 创建普通用户
        user = User(
            phone='13800138000',
            nickname='测试用户',
            role='user'
        )
        user.set_password('password123')
        db_session.add(user)
        
        # 创建另一个普通用户
        other_user = User(
            phone='13800138001',
            nickname='其他用户',
            role='user'
        )
        other_user.set_password('password123')
        db_session.add(other_user)
        
        # 创建管理员
        admin = User(
            phone='13900139000',
            nickname='管理员',
            role='admin'
        )
        admin.set_password('admin123')
        db_session.add(admin)
        
        db_session.commit()
        
        return {
            'user': user,
            'other_user': other_user,
            'admin': admin
        }


@pytest.fixture
def test_plan(app, db_session):
    """创建测试订阅套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='标准版',
            price=99.00,
            duration_days=30,
            is_active=True
        )
        db_session.add(plan)
        db_session.commit()
        return plan


@pytest.fixture
def test_order_with_proof(app, db_session, test_users, test_plan):
    """创建带支付凭证的测试订单"""
    with app.app_context():
        # 创建临时支付凭证文件
        upload_folder = app.config['UPLOAD_FOLDER']
        proof_dir = os.path.join(upload_folder, 'payment_proofs', '2024', '01')
        os.makedirs(proof_dir, exist_ok=True)
        
        proof_filename = f"{1}_1234567890.jpg"
        proof_path = os.path.join(proof_dir, proof_filename)
        
        # 创建一个简单的测试图片文件
        with open(proof_path, 'wb') as f:
            f.write(b'fake image content')
        
        # 创建订单
        order = Order(
            order_no='TEST20240115001',
            user_id=test_users['user'].id,
            plan_id=test_plan.id,
            amount=99.00,
            payment_method='offline',
            payment_status='pending',
            payment_proof='/uploads/payment_proofs/2024/01/' + proof_filename,
            payment_info={
                'amount': 99.00,
                'transaction_id': 'TX123456789',
                'timestamp': '2024-01-15 10:30:00'
            }
        )
        db_session.add(order)
        db_session.commit()
        
        return order


@pytest.fixture
def test_order_without_proof(app, db_session, test_users, test_plan):
    """创建没有支付凭证的测试订单"""
    with app.app_context():
        order = Order(
            order_no='TEST20240115002',
            user_id=test_users['user'].id,
            plan_id=test_plan.id,
            amount=99.00,
            payment_method='offline',
            payment_status='pending'
        )
        db_session.add(order)
        db_session.commit()
        return order


class TestPaymentProofAccess:
    """测试支付凭证访问权限"""
    
    def test_owner_can_view_proof(self, app, client, test_users, test_order_with_proof):
        """测试订单所有者可以查看支付凭证"""
        with app.app_context():
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 请求查看支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'file_url' in data['data']
            assert 'payment_info' in data['data']
            assert data['data']['payment_info']['amount'] == 99.00
    
    def test_admin_can_view_proof(self, app, client, test_users, test_order_with_proof):
        """测试管理员可以查看任何订单的支付凭证 - 需求1.5"""
        with app.app_context():
            # 生成管理员token
            token = create_access_token(identity=str(test_users['admin'].id))
            
            # 请求查看支付凭证（不是管理员自己的订单）
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'file_url' in data['data']
    
    def test_other_user_cannot_view_proof(self, app, client, test_users, test_order_with_proof):
        """测试其他用户不能查看别人的支付凭证"""
        with app.app_context():
            # 生成其他用户token
            token = create_access_token(identity=str(test_users['other_user'].id))
            
            # 请求查看支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403
            data = response.get_json()
            assert data['success'] is False
            assert '无权访问' in data['error']
    
    def test_view_nonexistent_proof(self, app, client, test_users, test_order_without_proof):
        """测试查看不存在的支付凭证"""
        with app.app_context():
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 请求查看支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_without_proof.id}/payment-proof',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert '暂无支付凭证' in data['error']
    
    def test_view_nonexistent_order(self, app, client, test_users):
        """测试查看不存在的订单"""
        with app.app_context():
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 请求查看不存在的订单
            response = client.get(
                '/api/subscriptions/orders/99999/payment-proof',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404


class TestPaymentProofDownload:
    """测试支付凭证下载功能"""
    
    def test_owner_can_download_proof(self, app, client, test_users, test_order_with_proof):
        """测试订单所有者可以下载支付凭证 - 需求1.4"""
        with app.app_context():
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 请求下载支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            assert response.content_type.startswith('image/') or response.content_type == 'application/octet-stream'
            assert len(response.data) > 0
    
    def test_admin_can_download_proof(self, app, client, test_users, test_order_with_proof):
        """测试管理员可以下载任何订单的支付凭证 - 需求1.6"""
        with app.app_context():
            # 生成管理员token
            token = create_access_token(identity=str(test_users['admin'].id))
            
            # 请求下载支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            assert len(response.data) > 0
    
    def test_other_user_cannot_download_proof(self, app, client, test_users, test_order_with_proof):
        """测试其他用户不能下载别人的支付凭证"""
        with app.app_context():
            # 生成其他用户token
            token = create_access_token(identity=str(test_users['other_user'].id))
            
            # 请求下载支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403
            data = response.get_json()
            assert data['success'] is False
            assert '无权访问' in data['error']
    
    def test_download_nonexistent_proof(self, app, client, test_users, test_order_without_proof):
        """测试下载不存在的支付凭证"""
        with app.app_context():
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 请求下载支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_without_proof.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert '暂无支付凭证' in data['error']
    
    def test_download_with_missing_file(self, app, client, test_users, test_order_with_proof):
        """测试下载文件不存在的支付凭证"""
        with app.app_context():
            # 修改订单的支付凭证路径为不存在的文件
            test_order_with_proof.payment_proof = '/uploads/payment_proofs/2024/01/nonexistent.jpg'
            db.session.commit()
            
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 请求下载支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert '文件不存在' in data['error']


class TestPaymentProofIntegration:
    """测试支付凭证的集成场景"""
    
    def test_complete_workflow(self, app, client, test_users, test_plan):
        """测试完整的支付凭证工作流：上传 -> 查看 -> 下载"""
        with app.app_context():
            # 1. 创建订单
            order = Order(
                order_no='TEST20240115003',
                user_id=test_users['user'].id,
                plan_id=test_plan.id,
                amount=99.00,
                payment_method='offline',
                payment_status='pending'
            )
            db.session.add(order)
            db.session.commit()
            
            # 生成用户token
            token = create_access_token(identity=str(test_users['user'].id))
            
            # 2. 上传支付凭证
            data = {
                'file': (BytesIO(b'test image content'), 'test.jpg')
            }
            response = client.post(
                f'/api/subscriptions/orders/{order.id}/payment-proof',
                data=data,
                content_type='multipart/form-data',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            upload_data = response.get_json()
            assert upload_data['success'] is True
            
            # 3. 查看支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{order.id}/payment-proof',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            view_data = response.get_json()
            assert view_data['success'] is True
            assert 'file_url' in view_data['data']
            
            # 4. 下载支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{order.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            assert len(response.data) > 0
    
    def test_admin_review_workflow(self, app, client, test_users, test_order_with_proof):
        """测试管理员审核工作流 - 需求1.5, 1.6"""
        with app.app_context():
            # 生成管理员token
            admin_token = create_access_token(identity=str(test_users['admin'].id))
            
            # 1. 管理员查看支付凭证
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof',
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            
            # 验证OCR信息可见
            assert 'payment_info' in data['data']
            assert data['data']['payment_info']['amount'] == 99.00
            
            # 2. 管理员下载支付凭证进行核对
            response = client.get(
                f'/api/subscriptions/orders/{test_order_with_proof.id}/payment-proof/download',
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            assert response.status_code == 200
            assert len(response.data) > 0
