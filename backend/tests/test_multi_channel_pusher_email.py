"""
MultiChannelPusher 邮件推送集成测试
测试 MultiChannelPusher 与 EmailPushService 的集成
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.multi_channel_pusher import MultiChannelPusher
from app.models import User, Subscription, SubscriptionPlan


class TestMultiChannelPusherEmail:
    """MultiChannelPusher 邮件推送集成测试类"""
    
    @pytest.fixture
    def pusher(self, app):
        """创建多渠道推送器实例"""
        with app.app_context():
            return MultiChannelPusher()
    
    @pytest.fixture
    def test_user_with_email(self, app, db_session):
        """创建带邮箱配置的测试用户"""
        with app.app_context():
            # 创建标准版套餐
            plan = SubscriptionPlan(
                name='标准版',
                price=299.00,
                duration_days=365,
                features={'email': True}
            )
            db_session.add(plan)
            db_session.flush()
            
            # 创建用户
            user = User(
                phone='13800138000',
                password_hash='test_hash',
                nickname='测试用户'
            )
            db_session.add(user)
            db_session.flush()
            
            # 创建订阅
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                status='active',
                push_channels={
                    'email': 'test@example.com'
                }
            )
            db_session.add(subscription)
            db_session.commit()
            
            return user
    
    @patch('app.services.email_push_service.smtplib.SMTP')
    def test_push_email_success(self, mock_smtp, pusher, test_user_with_email, app):
        """测试邮件推送 - 成功"""
        with app.app_context():
            # Mock SMTP服务器
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # 推送邮件
            result = pusher.push(
                user_id=test_user_with_email.id,
                subject='测试主题',
                content='<h1>测试内容</h1>',
                channels=['email'],
                html=True
            )
            
            # 验证结果
            assert 'email' in result
            assert result['email']['success'] is True
            assert result['email']['message'] == '邮件发送成功'
            
            # 验证SMTP调用
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
    
    def test_push_email_no_permission(self, pusher, app, db_session):
        """测试邮件推送 - 无权限（免费版用户）"""
        with app.app_context():
            # 创建免费版套餐
            plan = SubscriptionPlan(
                name='免费版',
                price=0.00,
                duration_days=365,
                features={}
            )
            db_session.add(plan)
            db_session.flush()
            
            # 创建用户
            user = User(
                phone='13800138001',
                password_hash='test_hash',
                nickname='免费用户'
            )
            db_session.add(user)
            db_session.flush()
            
            # 创建订阅
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                status='active',
                push_channels={}
            )
            db_session.add(subscription)
            db_session.commit()
            
            # 推送邮件
            result = pusher.push(
                user_id=user.id,
                subject='测试主题',
                content='测试内容',
                channels=['email']
            )
            
            # 验证结果
            assert 'email' in result
            assert result['email']['success'] is False
            assert '邮件推送需要标准版或高级版订阅' in result['email']['message']
    
    def test_push_email_no_email_configured(self, pusher, app, db_session):
        """测试邮件推送 - 未配置邮箱"""
        with app.app_context():
            # 创建标准版套餐
            plan = SubscriptionPlan(
                name='标准版',
                price=299.00,
                duration_days=365,
                features={'email': True}
            )
            db_session.add(plan)
            db_session.flush()
            
            # 创建用户
            user = User(
                phone='13800138002',
                password_hash='test_hash',
                nickname='未配置邮箱用户'
            )
            db_session.add(user)
            db_session.flush()
            
            # 创建订阅（未配置邮箱）
            subscription = Subscription(
                user_id=user.id,
                plan_id=plan.id,
                status='active',
                push_channels={}
            )
            db_session.add(subscription)
            db_session.commit()
            
            # 推送邮件
            result = pusher.push(
                user_id=user.id,
                subject='测试主题',
                content='测试内容',
                channels=['email']
            )
            
            # 验证结果
            assert 'email' in result
            assert result['email']['success'] is False
            assert '未配置邮箱地址' in result['email']['message']
    
    @patch('app.services.email_push_service.smtplib.SMTP')
    def test_push_batch_with_email(self, mock_smtp, pusher, app, db_session):
        """测试批量推送 - 包含邮件渠道"""
        with app.app_context():
            # Mock SMTP服务器
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # 创建标准版套餐
            plan = SubscriptionPlan(
                name='标准版',
                price=299.00,
                duration_days=365,
                features={'email': True}
            )
            db_session.add(plan)
            db_session.flush()
            
            # 创建多个用户
            user_ids = []
            for i in range(3):
                user = User(
                    phone=f'1380013800{i}',
                    password_hash='test_hash',
                    nickname=f'用户{i}'
                )
                db_session.add(user)
                db_session.flush()
                
                subscription = Subscription(
                    user_id=user.id,
                    plan_id=plan.id,
                    status='active',
                    push_channels={
                        'email': f'user{i}@example.com'
                    }
                )
                db_session.add(subscription)
                user_ids.append(user.id)
            
            db_session.commit()
            
            # 批量推送
            result = pusher.push_batch(
                user_ids=user_ids,
                subject='批量测试',
                content='<p>批量测试内容</p>',
                html=True
            )
            
            # 验证结果
            assert result['total'] == 3
            assert result['success'] == 3
            assert result['failed'] == 0
            assert len(result['results']) == 3
            
            # 验证每个用户的推送结果
            for user_result in result['results']:
                assert 'user_id' in user_result
                assert 'channels' in user_result
                assert user_result['channels']['email']['success'] is True
