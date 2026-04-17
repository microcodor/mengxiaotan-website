"""
EmailPushService 单元测试
测试邮件推送服务的核心功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib
from app.services.email_push_service import EmailPushService


class TestEmailPushService:
    """EmailPushService 单元测试类"""
    
    @pytest.fixture
    def email_service(self, app):
        """创建邮件推送服务实例"""
        with app.app_context():
            # 使用测试配置
            service = EmailPushService(
                smtp_server='smtp.test.com',
                smtp_port=587,
                username='test@test.com',
                password='test_password'
            )
            # 禁用重试以加快测试速度
            service.max_retries = 1
            service.retry_interval = 0
            return service
    
    def test_validate_config_success(self, email_service):
        """测试配置验证 - 成功场景"""
        assert email_service._validate_config() is True
    
    def test_validate_config_missing_server(self, app):
        """测试配置验证 - 缺少服务器"""
        with app.app_context():
            service = EmailPushService(
                smtp_server='',
                smtp_port=587,
                username='test@test.com',
                password='test_password'
            )
            assert service._validate_config() is False
    
    def test_validate_config_missing_username(self, app):
        """测试配置验证 - 缺少用户名"""
        with app.app_context():
            service = EmailPushService(
                smtp_server='smtp.test.com',
                smtp_port=587,
                username='',
                password='test_password'
            )
            assert service._validate_config() is False
    
    def test_send_invalid_email(self, email_service):
        """测试发送邮件 - 无效邮箱地址"""
        result = email_service.send('invalid_email', 'Test', 'Content')
        assert result is False
    
    def test_send_empty_email(self, email_service):
        """测试发送邮件 - 空邮箱地址"""
        result = email_service.send('', 'Test', 'Content')
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_html_email_success(self, mock_smtp, email_service):
        """测试发送HTML邮件 - 成功"""
        # Mock SMTP服务器
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = email_service.send(
            'recipient@test.com',
            'Test Subject',
            '<h1>Test Content</h1>',
            html=True
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_plain_text_email_success(self, mock_smtp, email_service):
        """测试发送纯文本邮件 - 成功"""
        # Mock SMTP服务器
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = email_service.send(
            'recipient@test.com',
            'Test Subject',
            'Plain text content',
            html=False
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_smtp_auth_error(self, mock_smtp, email_service):
        """测试发送邮件 - SMTP认证失败"""
        # Mock SMTP认证失败
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, 'Authentication failed')
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = email_service.send('recipient@test.com', 'Test', 'Content')
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_email_smtp_connect_error(self, mock_smtp, email_service):
        """测试发送邮件 - SMTP连接失败"""
        # Mock SMTP连接失败
        mock_smtp.side_effect = smtplib.SMTPConnectError(421, 'Cannot connect')
        
        result = email_service.send('recipient@test.com', 'Test', 'Content')
        
        assert result is False
    
    @patch('smtplib.SMTP')
    def test_send_email_generic_exception(self, mock_smtp, email_service):
        """测试发送邮件 - 通用异常"""
        # Mock通用异常
        mock_smtp.side_effect = Exception('Unexpected error')
        
        result = email_service.send('recipient@test.com', 'Test', 'Content')
        
        assert result is False
    
    @patch('smtplib.SMTP')
    @patch('time.sleep')  # Mock sleep以加快测试
    def test_send_email_retry_mechanism(self, mock_sleep, mock_smtp, app):
        """测试发送邮件 - 重试机制"""
        with app.app_context():
            # 创建服务实例，设置重试次数
            service = EmailPushService(
                smtp_server='smtp.test.com',
                smtp_port=587,
                username='test@test.com',
                password='test_password'
            )
            service.max_retries = 3
            service.retry_interval = 1  # 1秒重试间隔
            
            # Mock第一次和第二次失败，第三次成功
            mock_server = MagicMock()
            call_count = [0]
            
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] < 3:
                    raise smtplib.SMTPException('Temporary error')
                return mock_server
            
            mock_smtp.side_effect = side_effect
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = service.send('recipient@test.com', 'Test', 'Content')
            
            # 应该成功（第三次尝试）
            assert result is True
            # 应该调用了2次sleep（前两次失败后）
            assert mock_sleep.call_count == 2
    
    @patch('smtplib.SMTP')
    def test_send_batch_success(self, mock_smtp, email_service):
        """测试批量发送邮件 - 成功"""
        # Mock SMTP服务器
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        emails = ['user1@test.com', 'user2@test.com', 'user3@test.com']
        result = email_service.send_batch(emails, 'Test Subject', 'Test Content')
        
        assert result['success_count'] == 3
        assert result['failed_count'] == 0
        assert len(result['failed_emails']) == 0
    
    @patch('smtplib.SMTP')
    def test_send_batch_partial_failure(self, mock_smtp, email_service):
        """测试批量发送邮件 - 部分失败"""
        # Mock SMTP服务器，第二个邮件失败
        mock_server = MagicMock()
        call_count = [0]
        
        def send_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise smtplib.SMTPException('Failed')
        
        mock_server.send_message.side_effect = send_side_effect
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        emails = ['user1@test.com', 'user2@test.com', 'user3@test.com']
        result = email_service.send_batch(emails, 'Test Subject', 'Test Content')
        
        assert result['success_count'] == 2
        assert result['failed_count'] == 1
        assert 'user2@test.com' in result['failed_emails']
    
    @patch('smtplib.SMTP')
    def test_send_email_timeout(self, mock_smtp, email_service):
        """测试发送邮件 - 超时"""
        # Mock超时
        mock_smtp.side_effect = TimeoutError('Connection timeout')
        
        result = email_service.send('recipient@test.com', 'Test', 'Content')
        
        assert result is False
    
    def test_send_email_with_special_characters(self, email_service):
        """测试发送邮件 - 包含特殊字符"""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # 包含中文和特殊字符的内容
            result = email_service.send(
                'recipient@test.com',
                '测试主题 - Test Subject',
                '<h1>测试内容</h1><p>Special chars: @#$%^&*()</p>',
                html=True
            )
            
            assert result is True
            mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_with_long_content(self, mock_smtp, email_service):
        """测试发送邮件 - 长内容"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # 生成长内容（超过1000字）
        long_content = 'A' * 2000
        
        result = email_service.send(
            'recipient@test.com',
            'Long Content Test',
            long_content,
            html=False
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
