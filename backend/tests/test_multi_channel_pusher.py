"""
测试多渠道推送器 (MultiChannelPusher)
"""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Subscription, SubscriptionPlan
from app.services.multi_channel_pusher import MultiChannelPusher


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        # Skip drop_all to avoid circular dependency issues in tests


@pytest.fixture
def pusher():
    """创建推送器实例"""
    return MultiChannelPusher()


@pytest.fixture
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(
            phone='13800138000',
            nickname='testuser'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def free_plan(app):
    """创建免费版套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='免费版',
            price=0,
            duration_days=365,
            features={'level': 'free'}
        )
        db.session.add(plan)
        db.session.commit()
        return plan.id


@pytest.fixture
def standard_plan(app):
    """创建标准版套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='标准版',
            price=99,
            duration_days=30,
            features={'level': 'standard'}
        )
        db.session.add(plan)
        db.session.commit()
        return plan.id


@pytest.fixture
def premium_plan(app):
    """创建高级版套餐"""
    with app.app_context():
        plan = SubscriptionPlan(
            name='高级版',
            price=299,
            duration_days=30,
            features={'level': 'premium'}
        )
        db.session.add(plan)
        db.session.commit()
        return plan.id


class TestGetUserChannels:
    """测试 get_user_channels 方法"""
    
    def test_no_active_subscription(self, app, pusher, test_user):
        """测试用户没有活跃订阅"""
        with app.app_context():
            result = pusher.get_user_channels(test_user)
            
            assert result['enterprise_wechat'] is None
            assert result['email'] is None
            assert result['sms'] is None
            assert result['subscription_level'] is None
            assert result['allowed_channels'] == []
    
    def test_free_subscription(self, app, pusher, test_user, free_plan):
        """测试免费版订阅"""
        with app.app_context():
            # 创建免费版订阅
            subscription = Subscription(
                user_id=test_user,
                plan_id=free_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active',
                push_channels={
                    'enterprise_wechat': 'wx_free_user'
                }
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            
            assert result['enterprise_wechat'] == 'wx_free_user'
            assert result['email'] is None
            assert result['sms'] is None
            assert result['subscription_level'] == 'free'
            assert result['allowed_channels'] == ['enterprise_wechat']
    
    def test_standard_subscription(self, app, pusher, test_user, standard_plan):
        """测试标准版订阅"""
        with app.app_context():
            # 创建标准版订阅
            subscription = Subscription(
                user_id=test_user,
                plan_id=standard_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active',
                push_channels={
                    'enterprise_wechat': 'wx_standard_user',
                    'email': 'standard@example.com'
                }
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            
            assert result['enterprise_wechat'] == 'wx_standard_user'
            assert result['email'] == 'standard@example.com'
            assert result['sms'] is None
            assert result['subscription_level'] == 'standard'
            assert set(result['allowed_channels']) == {'enterprise_wechat', 'email'}
    
    def test_premium_subscription(self, app, pusher, test_user, premium_plan):
        """测试高级版订阅"""
        with app.app_context():
            # 创建高级版订阅
            subscription = Subscription(
                user_id=test_user,
                plan_id=premium_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active',
                push_channels={
                    'enterprise_wechat': 'wx_premium_user',
                    'email': 'premium@example.com',
                    'sms': '13900139000'
                }
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            
            assert result['enterprise_wechat'] == 'wx_premium_user'
            assert result['email'] == 'premium@example.com'
            assert result['sms'] == '13900139000'
            assert result['subscription_level'] == 'premium'
            assert set(result['allowed_channels']) == {'enterprise_wechat', 'email', 'sms'}
    
    def test_empty_push_channels(self, app, pusher, test_user, free_plan):
        """测试空的推送渠道配置"""
        with app.app_context():
            # 创建订阅但不配置推送渠道
            subscription = Subscription(
                user_id=test_user,
                plan_id=free_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active',
                push_channels=None
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            
            assert result['enterprise_wechat'] is None
            assert result['email'] is None
            assert result['sms'] is None
            assert result['subscription_level'] == 'free'
            assert result['allowed_channels'] == ['enterprise_wechat']


class TestValidateChannelConfig:
    """测试 validate_channel_config 方法"""
    
    def test_valid_enterprise_wechat(self, pusher):
        """测试有效的企业微信ID"""
        is_valid, error = pusher.validate_channel_config('enterprise_wechat', 'wx_user_123')
        assert is_valid is True
        assert error == ""
    
    def test_empty_enterprise_wechat(self, pusher):
        """测试空的企业微信ID"""
        is_valid, error = pusher.validate_channel_config('enterprise_wechat', '')
        assert is_valid is False
        assert "不能为空" in error
    
    def test_whitespace_enterprise_wechat(self, pusher):
        """测试只有空格的企业微信ID"""
        is_valid, error = pusher.validate_channel_config('enterprise_wechat', '   ')
        assert is_valid is False
        assert "不能为空" in error
    
    def test_valid_email(self, pusher):
        """测试有效的邮箱地址"""
        valid_emails = [
            'user@example.com',
            'test.user@example.com',
            'user+tag@example.co.uk',
            'user_name@example-domain.com'
        ]
        
        for email in valid_emails:
            is_valid, error = pusher.validate_channel_config('email', email)
            assert is_valid is True, f"邮箱 {email} 应该是有效的"
            assert error == ""
    
    def test_invalid_email(self, pusher):
        """测试无效的邮箱地址"""
        invalid_emails = [
            '',
            'invalid',
            'invalid@',
            '@example.com',
            'user@',
            'user @example.com',
            'user@example',
            'user@.com'
        ]
        
        for email in invalid_emails:
            is_valid, error = pusher.validate_channel_config('email', email)
            assert is_valid is False, f"邮箱 {email} 应该是无效的"
            assert "格式不正确" in error or "不能为空" in error
    
    def test_valid_phone(self, pusher):
        """测试有效的手机号"""
        valid_phones = [
            '13800138000',
            '13900139000',
            '15012345678',
            '18612345678',
            '19912345678'
        ]
        
        for phone in valid_phones:
            is_valid, error = pusher.validate_channel_config('sms', phone)
            assert is_valid is True, f"手机号 {phone} 应该是有效的"
            assert error == ""
    
    def test_phone_with_spaces_and_dashes(self, pusher):
        """测试带空格和连字符的手机号"""
        phones_with_formatting = [
            '138 0013 8000',
            '138-0013-8000',
            '138 0013-8000'
        ]
        
        for phone in phones_with_formatting:
            is_valid, error = pusher.validate_channel_config('sms', phone)
            assert is_valid is True, f"手机号 {phone} 应该是有效的（自动移除格式）"
            assert error == ""
    
    def test_invalid_phone(self, pusher):
        """测试无效的手机号"""
        invalid_phones = [
            '',
            '12345678901',  # 不是1开头
            '1380013800',   # 少于11位
            '138001380000', # 多于11位
            '10012345678',  # 第二位不是3-9
            'abcdefghijk',  # 非数字
            '138-0013-800'  # 格式化后少于11位
        ]
        
        for phone in invalid_phones:
            is_valid, error = pusher.validate_channel_config('sms', phone)
            assert is_valid is False, f"手机号 {phone} 应该是无效的"
            assert "格式不正确" in error or "不能为空" in error
    
    def test_unsupported_channel(self, pusher):
        """测试不支持的渠道"""
        is_valid, error = pusher.validate_channel_config('unknown_channel', 'value')
        assert is_valid is False
        assert "不支持的推送渠道" in error


class TestCheckChannelPermission:
    """测试 check_channel_permission 方法"""
    
    def test_no_subscription(self, app, pusher, test_user):
        """测试没有订阅的用户"""
        with app.app_context():
            has_permission, error = pusher.check_channel_permission(test_user, 'enterprise_wechat')
            assert has_permission is False
            assert "没有活跃订阅" in error
    
    def test_free_user_enterprise_wechat(self, app, pusher, test_user, free_plan):
        """测试免费版用户访问企业微信渠道"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user,
                plan_id=free_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            has_permission, error = pusher.check_channel_permission(test_user, 'enterprise_wechat')
            assert has_permission is True
            assert error == ""
    
    def test_free_user_email(self, app, pusher, test_user, free_plan):
        """测试免费版用户访问邮件渠道"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user,
                plan_id=free_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            has_permission, error = pusher.check_channel_permission(test_user, 'email')
            assert has_permission is False
            assert "标准版或高级版" in error
    
    def test_free_user_sms(self, app, pusher, test_user, free_plan):
        """测试免费版用户访问短信渠道"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user,
                plan_id=free_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            has_permission, error = pusher.check_channel_permission(test_user, 'sms')
            assert has_permission is False
            assert "高级版" in error
    
    def test_standard_user_email(self, app, pusher, test_user, standard_plan):
        """测试标准版用户访问邮件渠道"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user,
                plan_id=standard_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            has_permission, error = pusher.check_channel_permission(test_user, 'email')
            assert has_permission is True
            assert error == ""
    
    def test_standard_user_sms(self, app, pusher, test_user, standard_plan):
        """测试标准版用户访问短信渠道"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user,
                plan_id=standard_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            has_permission, error = pusher.check_channel_permission(test_user, 'sms')
            assert has_permission is False
            assert "高级版" in error
    
    def test_premium_user_all_channels(self, app, pusher, test_user, premium_plan):
        """测试高级版用户访问所有渠道"""
        with app.app_context():
            subscription = Subscription(
                user_id=test_user,
                plan_id=premium_plan,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            # 测试企业微信
            has_permission, error = pusher.check_channel_permission(test_user, 'enterprise_wechat')
            assert has_permission is True
            assert error == ""
            
            # 测试邮件
            has_permission, error = pusher.check_channel_permission(test_user, 'email')
            assert has_permission is True
            assert error == ""
            
            # 测试短信
            has_permission, error = pusher.check_channel_permission(test_user, 'sms')
            assert has_permission is True
            assert error == ""


class TestSubscriptionLevelDetection:
    """测试订阅等级检测"""
    
    def test_detect_free_level(self, app, pusher, test_user):
        """测试检测免费版"""
        with app.app_context():
            plan = SubscriptionPlan(
                name='免费版',
                price=0,
                duration_days=365
            )
            db.session.add(plan)
            db.session.commit()
            
            subscription = Subscription(
                user_id=test_user,
                plan_id=plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            assert result['subscription_level'] == 'free'
    
    def test_detect_standard_level(self, app, pusher, test_user):
        """测试检测标准版"""
        with app.app_context():
            plan = SubscriptionPlan(
                name='Standard Plan',
                price=99,
                duration_days=30
            )
            db.session.add(plan)
            db.session.commit()
            
            subscription = Subscription(
                user_id=test_user,
                plan_id=plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            assert result['subscription_level'] == 'standard'
    
    def test_detect_premium_level(self, app, pusher, test_user):
        """测试检测高级版"""
        with app.app_context():
            plan = SubscriptionPlan(
                name='Premium Plan',
                price=299,
                duration_days=30
            )
            db.session.add(plan)
            db.session.commit()
            
            subscription = Subscription(
                user_id=test_user,
                plan_id=plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                status='active'
            )
            db.session.add(subscription)
            db.session.commit()
            
            result = pusher.get_user_channels(test_user)
            assert result['subscription_level'] == 'premium'
