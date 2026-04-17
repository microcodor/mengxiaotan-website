"""
测试订阅装饰器 (Subscription Decorator Tests)

测试 @require_subscription 装饰器的功能，包括：
- 允许具有足够订阅等级的用户访问
- 拒绝订阅等级不足的用户访问
- 返回正确的错误响应格式
- 支持不同的订阅等级 (free, standard, premium)

Validates: Requirements 5.5
"""

import pytest
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from app.decorators.subscription import require_subscription
from app.models import User, Subscription, SubscriptionPlan
from app import db
from datetime import datetime, timedelta


@pytest.fixture
def test_app(app):
    """创建测试应用并配置JWT"""
    # JWT已在app fixture中配置
    return app


@pytest.fixture
def create_user_with_subscription(db_session):
    """创建具有指定订阅等级的用户"""
    def _create_user(phone: str, subscription_level: str):
        # 创建用户
        user = User(
            phone=phone,
            nickname=f"test_user_{phone}",
            password_hash="test_hash"
        )
        db_session.add(user)
        db_session.flush()
        
        # 创建订阅套餐
        plan_name_map = {
            'free': '免费版',
            'standard': '标准版',
            'premium': '高级版'
        }
        plan = SubscriptionPlan(
            name=plan_name_map[subscription_level],
            price=0.0 if subscription_level == 'free' else 99.0,
            duration_days=30,
            features={}
        )
        db_session.add(plan)
        db_session.flush()
        
        # 创建订阅记录
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status='active',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        db_session.commit()
        
        return user
    
    return _create_user


def test_decorator_allows_sufficient_subscription_level(test_app, create_user_with_subscription):
    """测试装饰器允许具有足够订阅等级的用户访问"""
    with test_app.app_context():
        # 创建标准版用户
        user = create_user_with_subscription('13800000001', 'standard')
        
        # 创建测试路由
        @test_app.route('/test/standard')
        @require_subscription('standard')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/standard',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'success'


def test_decorator_denies_insufficient_subscription_level(test_app, create_user_with_subscription):
    """测试装饰器拒绝订阅等级不足的用户访问"""
    with test_app.app_context():
        # 创建免费版用户
        user = create_user_with_subscription('13800000002', 'free')
        
        # 创建测试路由
        @test_app.route('/test/premium')
        @require_subscription('premium')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/premium',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == '权限不足'
        assert data['message'] == '此功能需要premium版本订阅'
        assert data['current_level'] == 'free'
        assert data['required_level'] == 'premium'


def test_decorator_returns_proper_error_response(test_app, create_user_with_subscription):
    """测试装饰器返回正确的错误响应格式"""
    with test_app.app_context():
        # 创建标准版用户
        user = create_user_with_subscription('13800000003', 'standard')
        
        # 创建测试路由
        @test_app.route('/test/premium_feature')
        @require_subscription('premium')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/premium_feature',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应格式
        assert response.status_code == 403
        data = response.get_json()
        
        # 验证所有必需字段存在
        assert 'error' in data
        assert 'message' in data
        assert 'current_level' in data
        assert 'required_level' in data
        
        # 验证字段值正确
        assert data['current_level'] == 'standard'
        assert data['required_level'] == 'premium'


def test_decorator_works_with_free_level(test_app, create_user_with_subscription):
    """测试装饰器支持免费版等级"""
    with test_app.app_context():
        # 创建免费版用户
        user = create_user_with_subscription('13800000004', 'free')
        
        # 创建测试路由（要求免费版）
        @test_app.route('/test/free')
        @require_subscription('free')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/free',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'success'


def test_decorator_works_with_standard_level(test_app, create_user_with_subscription):
    """测试装饰器支持标准版等级"""
    with test_app.app_context():
        # 创建标准版用户
        user = create_user_with_subscription('13800000005', 'standard')
        
        # 创建测试路由（要求标准版）
        @test_app.route('/test/standard_feature')
        @require_subscription('standard')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/standard_feature',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'success'


def test_decorator_works_with_premium_level(test_app, create_user_with_subscription):
    """测试装饰器支持高级版等级"""
    with test_app.app_context():
        # 创建高级版用户
        user = create_user_with_subscription('13800000006', 'premium')
        
        # 创建测试路由（要求高级版）
        @test_app.route('/test/premium_feature')
        @require_subscription('premium')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/premium_feature',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'success'


def test_premium_user_can_access_standard_features(test_app, create_user_with_subscription):
    """测试高级版用户可以访问标准版功能"""
    with test_app.app_context():
        # 创建高级版用户
        user = create_user_with_subscription('13800000007', 'premium')
        
        # 创建测试路由（要求标准版）
        @test_app.route('/test/standard_for_premium')
        @require_subscription('standard')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/standard_for_premium',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'success'


def test_standard_user_cannot_access_premium_features(test_app, create_user_with_subscription):
    """测试标准版用户不能访问高级版功能"""
    with test_app.app_context():
        # 创建标准版用户
        user = create_user_with_subscription('13800000008', 'standard')
        
        # 创建测试路由（要求高级版）
        @test_app.route('/test/premium_for_standard')
        @require_subscription('premium')
        def test_route():
            return jsonify({'message': 'success'})
        
        # 生成JWT token
        access_token = create_access_token(identity=user.id)
        
        # 创建测试客户端
        client = test_app.test_client()
        
        # 发送请求
        response = client.get(
            '/test/premium_for_standard',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # 验证响应
        assert response.status_code == 403
        data = response.get_json()
        assert data['error'] == '权限不足'
        assert data['current_level'] == 'standard'
        assert data['required_level'] == 'premium'
