"""
短信推送服务 (SMSPushService)
支持阿里云和腾讯云短信API
实现内容截断（70字限制）和重试机制（1次）
"""
import logging
import time
import hashlib
import hmac
import json
import requests
from typing import Optional, Tuple
from flask import current_app
from datetime import datetime

logger = logging.getLogger(__name__)


class SMSPushService:
    """
    短信推送服务
    
    职责:
    - 支持阿里云和腾讯云短信API
    - 实现内容截断（70字限制）
    - 超长内容附带链接
    - 实现重试机制（1次）
    """
    
    def __init__(self, provider: Optional[str] = None, 
                 api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None):
        """
        初始化短信推送服务
        
        Args:
            provider: 短信服务商 ('aliyun' or 'tencent')，可选，默认从配置读取
            api_key: API密钥，可选，默认从配置读取
            api_secret: API密钥，可选，默认从配置读取
        """
        self.provider = provider or current_app.config.get('SMS_PROVIDER', '')
        self.api_key = api_key or current_app.config.get('SMS_API_KEY', '')
        self.api_secret = api_secret or current_app.config.get('SMS_API_SECRET', '')
        
        # 重试配置（需求6.13：实现重试机制1次）
        self.max_retries = 1
        self.retry_interval = 60  # 1分钟
        
        # 短信内容长度限制（需求6.13）
        self.max_content_length = 70
        self.truncate_length = 67  # 留3个字符给"..."
    
    def send(self, phone: str, content: str, link: Optional[str] = None) -> bool:
        """
        发送短信（带重试机制和内容截断）
        
        Args:
            phone: 手机号码
            content: 短信内容
            link: 完整内容链接（当内容超过70字时使用）
            
        Returns:
            是否发送成功
        """
        # 验证配置
        if not self._validate_config():
            logger.error("短信配置不完整，无法发送短信")
            return False
        
        # 验证手机号
        if not self._validate_phone(phone):
            logger.error(f"无效的手机号码: {phone}")
            return False
        
        # 处理内容截断（需求6.13）
        sms_content, is_truncated = self._truncate_content(content, link)
        
        if is_truncated:
            logger.info(f"短信内容超过{self.max_content_length}字，已截断并附带链接")
        
        # 实现重试机制（1次重试）
        for attempt in range(1, self.max_retries + 2):  # 原始尝试 + 1次重试 = 2次
            try:
                success = self._send_sms(phone, sms_content)
                if success:
                    logger.info(f"短信发送成功: {phone}, 内容长度: {len(sms_content)}")
                    return True
                else:
                    logger.warning(f"短信发送失败 (尝试 {attempt}/{self.max_retries + 1}): {phone}")
            except Exception as e:
                logger.error(f"短信发送异常 (尝试 {attempt}/{self.max_retries + 1}): {e}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt <= self.max_retries:
                logger.info(f"等待 {self.retry_interval} 秒后重试...")
                time.sleep(self.retry_interval)
        
        logger.error(f"短信发送失败，已达到最大重试次数 ({self.max_retries}): {phone}")
        return False
    
    def _truncate_content(self, content: str, link: Optional[str] = None) -> Tuple[str, bool]:
        """
        截断短信内容（需求6.13）
        
        Args:
            content: 原始内容
            link: 完整内容链接
            
        Returns:
            (处理后的内容, 是否被截断)
        """
        # 如果内容长度在限制内，直接返回
        if len(content) <= self.max_content_length:
            return content, False
        
        # 内容超长，需要截断
        truncated = content[:self.truncate_length] + "..."
        
        # 如果提供了链接，附加到截断内容后
        if link:
            truncated += f" 查看完整内容: {link}"
        
        return truncated, True
    
    def _send_sms(self, phone: str, content: str) -> bool:
        """
        实际发送短信的内部方法
        
        Args:
            phone: 手机号码
            content: 短信内容
            
        Returns:
            是否发送成功
        """
        if self.provider == 'aliyun':
            return self._send_aliyun(phone, content)
        elif self.provider == 'tencent':
            return self._send_tencent(phone, content)
        else:
            logger.error(f"不支持的短信服务商: {self.provider}")
            return False
    
    def _send_aliyun(self, phone: str, content: str) -> bool:
        """
        阿里云短信发送
        
        使用阿里云短信API发送短信
        文档: https://help.aliyun.com/document_detail/101414.html
        
        Args:
            phone: 手机号码
            content: 短信内容
            
        Returns:
            是否发送成功
        """
        try:
            # 阿里云短信API端点
            endpoint = "https://dysmsapi.aliyuncs.com/"
            
            # 构造请求参数
            params = {
                'Action': 'SendSms',
                'Version': '2017-05-25',
                'RegionId': 'cn-hangzhou',
                'PhoneNumbers': phone,
                'SignName': current_app.config.get('SMS_SIGN_NAME', '蒙小碳能源站'),
                'TemplateCode': current_app.config.get('SMS_TEMPLATE_CODE', ''),
                'TemplateParam': json.dumps({'content': content}),
                'AccessKeyId': self.api_key,
                'Format': 'JSON',
                'SignatureMethod': 'HMAC-SHA1',
                'SignatureVersion': '1.0',
                'SignatureNonce': str(int(time.time() * 1000)),
                'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            # 计算签名
            signature = self._calculate_aliyun_signature(params)
            params['Signature'] = signature
            
            # 发送请求
            response = requests.get(endpoint, params=params, timeout=10)
            result = response.json()
            
            # 检查响应
            if result.get('Code') == 'OK':
                logger.info(f"阿里云短信发送成功: {phone}")
                return True
            else:
                logger.error(f"阿里云短信发送失败: {result.get('Message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"阿里云短信发送异常: {e}")
            return False
    
    def _calculate_aliyun_signature(self, params: dict) -> str:
        """
        计算阿里云API签名
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 构造待签名字符串
        canonicalized_query_string = '&'.join([f"{k}={self._percent_encode(str(v))}" 
                                                for k, v in sorted_params if k != 'Signature'])
        
        string_to_sign = f"GET&%2F&{self._percent_encode(canonicalized_query_string)}"
        
        # 计算HMAC-SHA1签名
        h = hmac.new((self.api_secret + '&').encode('utf-8'), 
                     string_to_sign.encode('utf-8'), 
                     hashlib.sha1)
        
        import base64
        signature = base64.b64encode(h.digest()).decode('utf-8')
        
        return signature
    
    def _percent_encode(self, s: str) -> str:
        """
        URL编码（阿里云特殊编码规则）
        
        Args:
            s: 待编码字符串
            
        Returns:
            编码后的字符串
        """
        import urllib.parse
        return urllib.parse.quote(s, safe='').replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
    
    def _send_tencent(self, phone: str, content: str) -> bool:
        """
        腾讯云短信发送
        
        使用腾讯云短信API发送短信
        文档: https://cloud.tencent.com/document/product/382/52077
        
        Args:
            phone: 手机号码
            content: 短信内容
            
        Returns:
            是否发送成功
        """
        try:
            # 腾讯云短信API端点
            endpoint = "https://sms.tencentcloudapi.com/"
            
            # SDK App ID
            sdk_app_id = current_app.config.get('SMS_SDK_APP_ID', '')
            
            # 构造请求体
            payload = {
                'PhoneNumberSet': [f"+86{phone}"],
                'SmsSdkAppId': sdk_app_id,
                'SignName': current_app.config.get('SMS_SIGN_NAME', '蒙小碳能源站'),
                'TemplateId': current_app.config.get('SMS_TEMPLATE_ID', ''),
                'TemplateParamSet': [content]
            }
            
            # 构造请求头
            timestamp = int(time.time())
            headers = {
                'Content-Type': 'application/json',
                'X-TC-Action': 'SendSms',
                'X-TC-Version': '2021-01-11',
                'X-TC-Timestamp': str(timestamp),
                'X-TC-Region': 'ap-guangzhou'
            }
            
            # 计算签名
            signature = self._calculate_tencent_signature(payload, timestamp)
            headers['Authorization'] = signature
            
            # 发送请求
            response = requests.post(endpoint, 
                                    json=payload, 
                                    headers=headers, 
                                    timeout=10)
            result = response.json()
            
            # 检查响应
            if 'Response' in result and 'SendStatusSet' in result['Response']:
                status_set = result['Response']['SendStatusSet']
                if status_set and status_set[0].get('Code') == 'Ok':
                    logger.info(f"腾讯云短信发送成功: {phone}")
                    return True
                else:
                    error_msg = status_set[0].get('Message', 'Unknown error') if status_set else 'Unknown error'
                    logger.error(f"腾讯云短信发送失败: {error_msg}")
                    return False
            else:
                logger.error(f"腾讯云短信发送失败: {result.get('Response', {}).get('Error', {}).get('Message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"腾讯云短信发送异常: {e}")
            return False
    
    def _calculate_tencent_signature(self, payload: dict, timestamp: int) -> str:
        """
        计算腾讯云API签名（TC3-HMAC-SHA256）
        
        Args:
            payload: 请求体
            timestamp: 时间戳
            
        Returns:
            签名字符串
        """
        # 简化实现：实际生产环境应使用腾讯云SDK
        # 这里返回基本的认证格式
        date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
        
        # 构造规范请求串
        canonical_request = f"POST\n/\n\ncontent-type:application/json\nhost:sms.tencentcloudapi.com\n\ncontent-type;host\n{hashlib.sha256(json.dumps(payload).encode('utf-8')).hexdigest()}"
        
        # 构造待签名字符串
        credential_scope = f"{date}/sms/tc3_request"
        string_to_sign = f"TC3-HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        
        # 计算签名
        secret_date = hmac.new(f"TC3{self.api_secret}".encode('utf-8'), 
                               date.encode('utf-8'), 
                               hashlib.sha256).digest()
        secret_service = hmac.new(secret_date, 
                                  b"sms", 
                                  hashlib.sha256).digest()
        secret_signing = hmac.new(secret_service, 
                                  b"tc3_request", 
                                  hashlib.sha256).digest()
        signature = hmac.new(secret_signing, 
                            string_to_sign.encode('utf-8'), 
                            hashlib.sha256).hexdigest()
        
        # 构造Authorization
        authorization = f"TC3-HMAC-SHA256 Credential={self.api_key}/{credential_scope}, SignedHeaders=content-type;host, Signature={signature}"
        
        return authorization
    
    def _validate_phone(self, phone: str) -> bool:
        """
        验证手机号格式（中国大陆手机号）
        
        Args:
            phone: 手机号码
            
        Returns:
            是否有效
        """
        if not phone or not isinstance(phone, str):
            return False
        
        # 移除可能的空格和连字符
        phone = phone.replace(' ', '').replace('-', '')
        
        # 验证格式：1开头，第二位是3-9，总共11位
        import re
        pattern = re.compile(r'^1[3-9]\d{9}$')
        
        return bool(pattern.match(phone))
    
    def _validate_config(self) -> bool:
        """
        验证短信配置是否完整
        
        Returns:
            配置是否有效
        """
        if not self.provider:
            logger.error("SMS_PROVIDER 未配置")
            return False
        
        if self.provider not in ['aliyun', 'tencent']:
            logger.error(f"不支持的短信服务商: {self.provider}")
            return False
        
        if not self.api_key:
            logger.error("SMS_API_KEY 未配置")
            return False
        
        if not self.api_secret:
            logger.error("SMS_API_SECRET 未配置")
            return False
        
        return True
    
    def send_batch(self, phones: list, content: str, link: Optional[str] = None) -> dict:
        """
        批量发送短信
        
        Args:
            phones: 手机号码列表
            content: 短信内容
            link: 完整内容链接
            
        Returns:
            {
                'success_count': int,  # 成功数量
                'failed_count': int,   # 失败数量
                'failed_phones': list  # 失败的手机号列表
            }
        """
        success_count = 0
        failed_count = 0
        failed_phones = []
        
        for phone in phones:
            if self.send(phone, content, link):
                success_count += 1
            else:
                failed_count += 1
                failed_phones.append(phone)
        
        logger.info(f"批量短信发送完成: 成功 {success_count}, 失败 {failed_count}")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_phones': failed_phones
        }


# 创建全局实例（延迟初始化，在应用上下文中使用）
def get_sms_push_service() -> SMSPushService:
    """
    获取短信推送服务实例
    
    Returns:
        SMSPushService 实例
    """
    return SMSPushService()
