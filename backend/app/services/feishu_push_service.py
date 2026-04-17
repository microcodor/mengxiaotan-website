"""
飞书推送服务
支持发送文本、富文本、卡片消息
"""
import requests
import logging
import time
from typing import Optional, Dict
from flask import current_app

logger = logging.getLogger(__name__)


class FeishuPushService:
    """
    飞书推送服务
    
    文档: https://open.feishu.cn/document/server-docs/im-v1/message/create
    """
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        """
        初始化飞书推送服务
        
        Args:
            app_id: 应用AppId
            app_secret: 应用AppSecret
        """
        self.app_id = app_id or current_app.config.get('FEISHU_APP_ID')
        self.app_secret = app_secret or current_app.config.get('FEISHU_APP_SECRET')
        
        self.tenant_access_token = None
        self.token_expires_at = 0
        
        if not all([self.app_id, self.app_secret]):
            logger.warning("飞书配置不完整，推送功能将不可用")
    
    def get_tenant_access_token(self) -> Optional[str]:
        """
        获取tenant_access_token
        
        Returns:
            tenant_access_token或None
        """
        # 检查token是否过期
        if self.tenant_access_token and time.time() < self.token_expires_at:
            return self.tenant_access_token
        
        # 获取新token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        data = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                self.tenant_access_token = result.get('tenant_access_token')
                # token有效期7200秒，提前5分钟刷新
                self.token_expires_at = time.time() + result.get('expire', 7200) - 300
                logger.info("飞书tenant_access_token获取成功")
                return self.tenant_access_token
            else:
                logger.error(f"获取飞书tenant_access_token失败: {result}")
                return None
        except Exception as e:
            logger.error(f"获取飞书tenant_access_token异常: {e}")
            return None
    
    def send_text(self, user_id: str, content: str) -> bool:
        """
        发送文本消息
        
        Args:
            user_id: 飞书用户open_id
            content: 消息内容
            
        Returns:
            是否发送成功
        """
        tenant_access_token = self.get_tenant_access_token()
        if not tenant_access_token:
            logger.error("无法获取tenant_access_token")
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "receive_id_type": "open_id"
        }
        
        data = {
            "receive_id": user_id,
            "msg_type": "text",
            "content": f'{{"text":"{content}"}}'
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                logger.info(f"飞书文本消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"飞书文本消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"飞书文本消息发送异常: {e}")
            return False
    
    def send_post(self, user_id: str, title: str, content: str) -> bool:
        """
        发送富文本消息
        
        Args:
            user_id: 飞书用户open_id
            title: 消息标题
            content: 富文本内容
            
        Returns:
            是否发送成功
        """
        tenant_access_token = self.get_tenant_access_token()
        if not tenant_access_token:
            logger.error("无法获取tenant_access_token")
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "receive_id_type": "open_id"
        }
        
        # 构造富文本内容
        post_content = {
            "zh_cn": {
                "title": title,
                "content": [
                    [
                        {
                            "tag": "text",
                            "text": content
                        }
                    ]
                ]
            }
        }
        
        data = {
            "receive_id": user_id,
            "msg_type": "post",
            "content": str(post_content).replace("'", '"')
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                logger.info(f"飞书富文本消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"飞书富文本消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"飞书富文本消息发送异常: {e}")
            return False
    
    def send_interactive(self, user_id: str, card_content: dict) -> bool:
        """
        发送交互式卡片消息
        
        Args:
            user_id: 飞书用户open_id
            card_content: 卡片内容
            
        Returns:
            是否发送成功
        """
        tenant_access_token = self.get_tenant_access_token()
        if not tenant_access_token:
            logger.error("无法获取tenant_access_token")
            return False
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "receive_id_type": "open_id"
        }
        
        data = {
            "receive_id": user_id,
            "msg_type": "interactive",
            "content": str(card_content).replace("'", '"')
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                logger.info(f"飞书卡片消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"飞书卡片消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"飞书卡片消息发送异常: {e}")
            return False
    
    def send(self, user_id: str, subject: str, content: str, 
             message_type: str = 'text') -> bool:
        """
        统一发送接口
        
        Args:
            user_id: 飞书用户open_id
            subject: 消息主题
            content: 消息内容
            message_type: 消息类型 (text/post)
            
        Returns:
            是否发送成功
        """
        if not all([self.app_id, self.app_secret]):
            logger.error("飞书配置不完整")
            return False
        
        if message_type == 'post':
            return self.send_post(user_id, subject, content)
        else:
            # 组合主题和内容
            full_content = f"{subject}\\n\\n{content}"
            return self.send_text(user_id, full_content)


# 全局实例
_feishu_service = None


def get_feishu_service() -> FeishuPushService:
    """获取飞书推送服务实例"""
    global _feishu_service
    if _feishu_service is None:
        _feishu_service = FeishuPushService()
    return _feishu_service
