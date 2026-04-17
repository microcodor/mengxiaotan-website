"""
SMSPushService 单元测试
测试短信推送服务的核心功能
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.sms_push_service import SMSPushService


class TestSMSPushService:
    """SMSPushService 单元测试类"""
    
    @pytest.fixture
    def sms_service_aliyun(self, app):
        """创建阿里云短信推送服务实例"""
        with app.app_context():
            service = SMSPushService(
                provider='aliyun',
                api_key='test_key',
                api_secret='test_secret'
            )
            # 禁用重试以加快测试速度
            service.max_retries = 0
            service.retry_interval = 0
            return service
    
    @pytest.fixture
    def sms_service_tencent(self, app):
        """创建腾讯云短信推送服务实例"""
        with app.app_context():
            service = SMSPushService(
                provider='tencent',
                api_key='test_key',
                api_secret='test_secret'
            )
            service.max_retries = 0
            service.retry_interval = 0
            return service
    
    def test_validate_config_success(self, sms_service_aliyun):
        """测试配置验证 - 成功场景"""
        assert sms_service_aliyun._validate_config() is True
    
    def test_validate_config_missing_provider(self, app):
        """测试配置验证 - 缺少服务商"""
        with app.app_context():
            service = SMSPushService(
                provider='',
                api_key='test_key',
                api_secret='test_secret'
            )
            assert service._validate_config() is False
    
    def test_validate_config_invalid_provider(self, app):
        """测试配置验证 - 无效服务商"""
        with app.app_context():
            service = SMSPushService(
                provider='invalid',
                api_key='test_key',
                api_secret='test_secret'
            )
            assert service._validate_config() is False
    
    def test_validate_config_missing_api_key(self, app):
        """测试配置验证 - 缺少API密钥"""
        with app.app_context():
            service = SMSPushService(
                provider='aliyun',
                api_key='',
                api_secret='test_secret'
            )
            assert service._validate_config() is False
    
    def test_validate_phone_valid(self, sms_service_aliyun):
        """测试手机号验证 - 有效手机号"""
        assert sms_service_aliyun._validate_phone('13800138000') is True
        assert sms_service_aliyun._validate_phone('15912345678') is True
        assert sms_service_aliyun._validate_phone('18888888888') is True
    
    def test_validate_phone_invalid(self, sms_service_aliyun):
        """测试手机号验证 - 无效手机号"""
        assert sms_service_aliyun._validate_phone('12345678901') is False  # 第二位不是3-9
        assert sms_service_aliyun._validate_phone('1380013800') is False   # 少于11位
        assert sms_service_aliyun._validate_phone('138001380000') is False # 多于11位
        assert sms_service_aliyun._validate_phone('') is False
        assert sms_service_aliyun._validate_phone(None) is False
    
    def test_validate_phone_with_spaces(self, sms_service_aliyun):
        """测试手机号验证 - 包含空格"""
        assert sms_service_aliyun._validate_phone('138 0013 8000') is True
        assert sms_service_aliyun._validate_phone('138-0013-8000') is True
    
    def test_truncate_content_short(self, sms_service_aliyun):
        """测试内容截断 - 短内容（不需要截断）"""
        content = "这是一条短消息"
        result, is_truncated = sms_service_aliyun._truncate_content(content)
        
        assert result == content
        assert is_truncated is False
    
    def test_truncate_content_long_without_link(self, sms_service_aliyun):
        """测试内容截断 - 长内容（无链接）"""
        content = "这是一条很长的消息" * 10  # 超过70字
        result, is_truncated = sms_service_aliyun._truncate_content(content)
        
        assert len(result) <= 70
        assert result.endswith("...")
        assert is_truncated is True
    
    def test_truncate_content_long_with_link(self, sms_service_aliyun):
        """测试内容截断 - 长内容（带链接）"""
        content = "这是一条很长的消息" * 10
        link = "https://example.com/article/123"
        result, is_truncated = sms_service_aliyun._truncate_content(content, link)
        
        assert "..." in result
        assert link in result
        assert is_truncated is True
    
    def test_truncate_content_exactly_70_chars(self, sms_service_aliyun):
        """测试内容截断 - 恰好70字"""
        content = "A" * 70
        result, is_truncated = sms_service_aliyun._truncate_content(content)
        
        assert result == content
        assert is_truncated is False
    
    def test_truncate_content_71_chars(self, sms_service_aliyun):
        """测试内容截断 - 71字（需要截断）"""
        content = "A" * 71
        result, is_truncated = sms_service_aliyun._truncate_content(content)
        
        assert len(result) == 70  # 67 + "..."
        assert result.endswith("...")
        assert is_truncated is True
    
    def test_send_invalid_phone(self, sms_service_aliyun):
        """测试发送短信 - 无效手机号"""
        result = sms_service_aliyun.send('invalid_phone', 'Test content')
        assert result is False
    
    def test_send_empty_phone(self, sms_service_aliyun):
        """测试发送短信 - 空手机号"""
        result = sms_service_aliyun.send('', 'Test content')
        assert result is False
    
    @patch('requests.get')
    def test_send_aliyun_success(self, mock_get, sms_service_aliyun):
        """测试阿里云短信发送 - 成功"""
        # Mock阿里云API响应
        mock_response = Mock()
        mock_response.json.return_value = {'Code': 'OK'}
        mock_get.return_value = mock_response
        
        result = sms_service_aliyun.send('13800138000', 'Test content')
        
        assert result is True
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_send_aliyun_failure(self, mock_get, sms_service_aliyun):
        """测试阿里云短信发送 - 失败"""
        # Mock阿里云API失败响应
        mock_response = Mock()
        mock_response.json.return_value = {'Code': 'isv.BUSINESS_LIMIT_CONTROL', 'Message': 'Business limit'}
        mock_get.return_value = mock_response
        
        result = sms_service_aliyun.send('13800138000', 'Test content')
        
        assert result is False
    
    @patch('requests.get')
    def test_send_aliyun_exception(self, mock_get, sms_service_aliyun):
        """测试阿里云短信发送 - 异常"""
        # Mock异常
        mock_get.side_effect = Exception('Network error')
        
        result = sms_service_aliyun.send('13800138000', 'Test content')
        
        assert result is False
    
    @patch('requests.post')
    def test_send_tencent_success(self, mock_post, sms_service_tencent):
        """测试腾讯云短信发送 - 成功"""
        # Mock腾讯云API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'Response': {
                'SendStatusSet': [{'Code': 'Ok'}]
            }
        }
        mock_post.return_value = mock_response
        
        result = sms_service_tencent.send('13800138000', 'Test content')
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_tencent_failure(self, mock_post, sms_service_tencent):
        """测试腾讯云短信发送 - 失败"""
        # Mock腾讯云API失败响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'Response': {
                'SendStatusSet': [{'Code': 'FailedOperation', 'Message': 'Send failed'}]
            }
        }
        mock_post.return_value = mock_response
        
        result = sms_service_tencent.send('13800138000', 'Test content')
        
        assert result is False
    
    @patch('requests.post')
    def test_send_tencent_exception(self, mock_post, sms_service_tencent):
        """测试腾讯云短信发送 - 异常"""
        # Mock异常
        mock_post.side_effect = Exception('Network error')
        
        result = sms_service_tencent.send('13800138000', 'Test content')
        
        assert result is False
    
    @patch('requests.get')
    def test_send_with_long_content(self, mock_get, sms_service_aliyun):
        """测试发送短信 - 长内容自动截断"""
        # Mock阿里云API响应
        mock_response = Mock()
        mock_response.json.return_value = {'Code': 'OK'}
        mock_get.return_value = mock_response
        
        long_content = "这是一条很长的消息" * 10
        link = "https://example.com/article/123"
        
        result = sms_service_aliyun.send('13800138000', long_content, link)
        
        assert result is True
    
    @patch('requests.get')
    @patch('time.sleep')
    def test_send_with_retry(self, mock_sleep, mock_get, app):
        """测试发送短信 - 重试机制"""
        with app.app_context():
            service = SMSPushService(
                provider='aliyun',
                api_key='test_key',
                api_secret='test_secret'
            )
            service.max_retries = 1
            service.retry_interval = 1
            
            # Mock第一次失败，第二次成功
            call_count = [0]
            
            def side_effect(*args, **kwargs):
                call_count[0] += 1
                mock_response = Mock()
                if call_count[0] == 1:
                    mock_response.json.return_value = {'Code': 'ERROR', 'Message': 'Temporary error'}
                else:
                    mock_response.json.return_value = {'Code': 'OK'}
                return mock_response
            
            mock_get.side_effect = side_effect
            
            result = service.send('13800138000', 'Test content')
            
            assert result is True
            assert mock_get.call_count == 2
            mock_sleep.assert_called_once()
    
    @patch('requests.get')
    def test_send_batch_success(self, mock_get, sms_service_aliyun):
        """测试批量发送短信 - 成功"""
        # Mock阿里云API响应
        mock_response = Mock()
        mock_response.json.return_value = {'Code': 'OK'}
        mock_get.return_value = mock_response
        
        phones = ['13800138000', '13900139000', '13700137000']
        result = sms_service_aliyun.send_batch(phones, 'Test content')
        
        assert result['success_count'] == 3
        assert result['failed_count'] == 0
        assert len(result['failed_phones']) == 0
    
    @patch('requests.get')
    def test_send_batch_partial_failure(self, mock_get, sms_service_aliyun):
        """测试批量发送短信 - 部分失败"""
        # Mock第二个手机号失败
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            mock_response = Mock()
            if call_count[0] == 2:
                mock_response.json.return_value = {'Code': 'ERROR', 'Message': 'Failed'}
            else:
                mock_response.json.return_value = {'Code': 'OK'}
            return mock_response
        
        mock_get.side_effect = side_effect
        
        phones = ['13800138000', '13900139000', '13700137000']
        result = sms_service_aliyun.send_batch(phones, 'Test content')
        
        assert result['success_count'] == 2
        assert result['failed_count'] == 1
        assert '13900139000' in result['failed_phones']
    
    def test_send_with_special_characters(self, sms_service_aliyun):
        """测试发送短信 - 包含特殊字符"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'Code': 'OK'}
            mock_get.return_value = mock_response
            
            content = "测试内容 - Special chars: @#$%^&*()"
            result = sms_service_aliyun.send('13800138000', content)
            
            assert result is True
    
    @patch('requests.get')
    def test_send_timeout(self, mock_get, sms_service_aliyun):
        """测试发送短信 - 超时"""
        # Mock超时
        mock_get.side_effect = TimeoutError('Connection timeout')
        
        result = sms_service_aliyun.send('13800138000', 'Test content')
        
        assert result is False
    
    def test_percent_encode(self, sms_service_aliyun):
        """测试URL编码"""
        # 测试特殊字符编码
        assert sms_service_aliyun._percent_encode('test value') == 'test%20value'
        assert sms_service_aliyun._percent_encode('test*value') == 'test%2Avalue'
        assert sms_service_aliyun._percent_encode('test~value') == 'test~value'
    
    def test_calculate_aliyun_signature(self, sms_service_aliyun):
        """测试阿里云签名计算"""
        params = {
            'Action': 'SendSms',
            'Version': '2017-05-25',
            'AccessKeyId': 'test_key'
        }
        
        signature = sms_service_aliyun._calculate_aliyun_signature(params)
        
        # 签名应该是非空字符串
        assert isinstance(signature, str)
        assert len(signature) > 0
    
    def test_calculate_tencent_signature(self, sms_service_tencent):
        """测试腾讯云签名计算"""
        payload = {
            'PhoneNumberSet': ['+8613800138000'],
            'SmsSdkAppId': 'test_app_id'
        }
        timestamp = 1234567890
        
        signature = sms_service_tencent._calculate_tencent_signature(payload, timestamp)
        
        # 签名应该是非空字符串，且包含TC3-HMAC-SHA256
        assert isinstance(signature, str)
        assert 'TC3-HMAC-SHA256' in signature
        assert len(signature) > 0
