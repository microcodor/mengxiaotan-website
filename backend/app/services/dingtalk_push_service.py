"""
钉钉推送服务
支持发送文本、Markdown、链接消息
"""
import requests
import logging
import time
from typing import Optional, Dict
from flask import current_app

logger = logging.getLogger(__name__)


class DingTalkPushService:
    """
    钉钉推送服务
    
    文档: https://open.dingtalk.com/document/orgapp/message-types-and-data-format
    """
    
    def __init__(self, app_key: str = None, app_secret: str = None, agent_id: str = None):
        """
        初始化钉钉推送服务
        
        Args:
            app_key: 应用AppKey
            app_secret: 应用AppSecret
            agent_id: 应用AgentId
        """
        self.app_key = app_key or current_app.config.get('DINGTALK_APP_KEY')
        self.app_secret = app_secret or current_app.config.get('DINGTALK_APP_SECRET')
        self.agent_id = agent_id or current_app.config.get('DINGTALK_AGENT_ID')
        
        self.access_token = None
        self.token_expires_at = 0
        
        if not all([self.app_key, self.app_secret, self.agent_id]):
            logger.warning("钉钉配置不完整，推送功能将不可用")
    
    def get_access_token(self) -> Optional[str]:
        """
        获取access_token
        
        Returns:
            access_token或None
        """
        # 检查token是否过期
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        # 获取新token
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            'appkey': self.app_key,
            'appsecret': self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode') == 0:
                self.access_token = data.get('access_token')
                # token有效期7200秒，提前5分钟刷新
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 300
                logger.info("钉钉access_token获取成功")
                return self.access_token
            else:
                logger.error(f"获取钉钉access_token失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取钉钉access_token异常: {e}")
            return None
    
    def send_text(self, user_id: str, content: str) -> bool:
        """
        发送文本消息
        
        Args:
            user_id: 钉钉用户ID
            content: 消息内容
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return False
        
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"钉钉文本消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"钉钉文本消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"钉钉文本消息发送异常: {e}")
            return False
    
    def send_markdown(self, user_id: str, title: str, content: str) -> bool:
        """
        发送Markdown消息
        
        Args:
            user_id: 钉钉用户ID
            title: 消息标题
            content: Markdown内容
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return False
        
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                }
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"钉钉Markdown消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"钉钉Markdown消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"钉钉Markdown消息发送异常: {e}")
            return False
    
    def send_link(self, user_id: str, title: str, text: str, 
                  message_url: str, pic_url: str = None) -> bool:
        """
        发送链接消息
        
        Args:
            user_id: 钉钉用户ID
            title: 消息标题
            text: 消息内容
            message_url: 点击消息跳转的URL
            pic_url: 图片URL
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return False
        
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"
        
        link_data = {
            "messageUrl": message_url,
            "title": title,
            "text": text
        }
        
        if pic_url:
            link_data["picUrl"] = pic_url
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "link",
                "link": link_data
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"钉钉链接消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"钉钉链接消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"钉钉链接消息发送异常: {e}")
            return False
    
    def send(self, user_id: str, subject: str, content: str, 
             message_type: str = 'text') -> bool:
        """
        统一发送接口
        
        Args:
            user_id: 钉钉用户ID
            subject: 消息主题
            content: 消息内容
            message_type: 消息类型 (text/markdown)
            
        Returns:
            是否发送成功
        """
        if not all([self.app_key, self.app_secret, self.agent_id]):
            logger.error("钉钉配置不完整")
            return False
        
        if message_type == 'markdown':
            return self.send_markdown(user_id, subject, content)
        else:
            # 组合主题和内容
            full_content = f"{subject}\n\n{content}"
            return self.send_text(user_id, full_content)


# 全局实例
_dingtalk_service = None


def get_dingtalk_service() -> DingTalkPushService:
    """获取钉钉推送服务实例"""
    global _dingtalk_service
    if _dingtalk_service is None:
        _dingtalk_service = DingTalkPushService()
    return _dingtalk_service
