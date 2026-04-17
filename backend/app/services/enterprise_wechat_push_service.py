"""
企业微信推送服务
支持发送文本、Markdown、图文消息
"""
import requests
import logging
import time
from typing import Optional, Dict
from flask import current_app

logger = logging.getLogger(__name__)


class EnterpriseWechatPushService:
    """
    企业微信推送服务
    
    文档: https://developer.work.weixin.qq.com/document/path/90236
    """
    
    def __init__(self, corp_id: str = None, corp_secret: str = None, agent_id: str = None):
        """
        初始化企业微信推送服务
        
        Args:
            corp_id: 企业ID
            corp_secret: 应用Secret
            agent_id: 应用AgentId
        """
        self.corp_id = corp_id or current_app.config.get('WECHAT_CORP_ID')
        self.corp_secret = corp_secret or current_app.config.get('WECHAT_CORP_SECRET')
        self.agent_id = agent_id or current_app.config.get('WECHAT_AGENT_ID')
        
        self.access_token = None
        self.token_expires_at = 0
        
        if not all([self.corp_id, self.corp_secret, self.agent_id]):
            logger.warning("企业微信配置不完整，推送功能将不可用")
    
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
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            'corpid': self.corp_id,
            'corpsecret': self.corp_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode') == 0:
                self.access_token = data.get('access_token')
                # token有效期7200秒，提前5分钟刷新
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 300
                logger.info("企业微信access_token获取成功")
                return self.access_token
            else:
                logger.error(f"获取企业微信access_token失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取企业微信access_token异常: {e}")
            return None
    
    def send_text(self, user_id: str, content: str) -> bool:
        """
        发送文本消息
        
        Args:
            user_id: 企业微信用户ID
            content: 消息内容
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content
            },
            "safe": 0
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"企业微信文本消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"企业微信文本消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"企业微信文本消息发送异常: {e}")
            return False
    
    def send_markdown(self, user_id: str, content: str) -> bool:
        """
        发送Markdown消息
        
        Args:
            user_id: 企业微信用户ID
            content: Markdown内容
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {
                "content": content
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"企业微信Markdown消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"企业微信Markdown消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"企业微信Markdown消息发送异常: {e}")
            return False
    
    def send_news(self, user_id: str, articles: list) -> bool:
        """
        发送图文消息
        
        Args:
            user_id: 企业微信用户ID
            articles: 图文列表，每个元素包含title, description, url, picurl
            
        Returns:
            是否发送成功
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("无法获取access_token")
            return False
        
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "news",
            "agentid": self.agent_id,
            "news": {
                "articles": articles
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"企业微信图文消息发送成功: {user_id}")
                return True
            else:
                logger.error(f"企业微信图文消息发送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"企业微信图文消息发送异常: {e}")
            return False
    
    def send(self, user_id: str, subject: str, content: str, 
             message_type: str = 'text') -> bool:
        """
        统一发送接口
        
        Args:
            user_id: 企业微信用户ID
            subject: 消息主题
            content: 消息内容
            message_type: 消息类型 (text/markdown)
            
        Returns:
            是否发送成功
        """
        if not all([self.corp_id, self.corp_secret, self.agent_id]):
            logger.error("企业微信配置不完整")
            return False
        
        # 组合主题和内容
        full_content = f"**{subject}**\n\n{content}" if message_type == 'markdown' else f"{subject}\n\n{content}"
        
        if message_type == 'markdown':
            return self.send_markdown(user_id, full_content)
        else:
            return self.send_text(user_id, full_content)


# 全局实例
_enterprise_wechat_service = None


def get_enterprise_wechat_service() -> EnterpriseWechatPushService:
    """获取企业微信推送服务实例"""
    global _enterprise_wechat_service
    if _enterprise_wechat_service is None:
        _enterprise_wechat_service = EnterpriseWechatPushService()
    return _enterprise_wechat_service
