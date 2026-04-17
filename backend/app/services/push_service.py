"""
推送服务
支持企业微信、个人微信（待实现）
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
from app import db
from app.models import BroadcastTask, BroadcastLog, User, Subscription
import logging

logger = logging.getLogger(__name__)


class PushService:
    """推送服务基类"""
    
    def __init__(self):
        self.name = "PushService"
    
    def send(self, user_id: int, content: str, **kwargs) -> bool:
        """发送推送"""
        raise NotImplementedError


class WeChatWorkPushService(PushService):
    """企业微信推送服务"""
    
    def __init__(self, corpid: str, corpsecret: str, agentid: str):
        super().__init__()
        self.name = "WeChatWork"
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> Optional[str]:
        """获取企业微信 access_token"""
        # 检查 token 是否过期
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # 获取新 token
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            'corpid': self.corpid,
            'corpsecret': self.corpsecret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode') == 0:
                self.access_token = data['access_token']
                # token 有效期 7200 秒，提前 5 分钟刷新
                from datetime import timedelta
                self.token_expires_at = datetime.now() + timedelta(seconds=7200 - 300)
                return self.access_token
            else:
                logger.error(f"获取企业微信 token 失败: {data}")
                return None
        except Exception as e:
            logger.error(f"获取企业微信 token 异常: {e}")
            return None
    
    def send(self, user_id: int, content: str, **kwargs) -> bool:
        """发送企业微信消息"""
        token = self.get_access_token()
        if not token:
            return False
        
        # 获取用户的企业微信 ID
        user = User.query.get(user_id)
        if not user:
            return False
        
        subscription = Subscription.query.filter_by(
            user_id=user_id, 
            status='active'
        ).first()
        
        if not subscription or not subscription.push_channels:
            logger.warning(f"用户 {user_id} 未配置企业微信推送")
            return False
        
        wechat_userid = subscription.push_channels.get('enterprise_wechat')
        if not wechat_userid:
            logger.warning(f"用户 {user_id} 未绑定企业微信")
            return False
        
        # 构造消息
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
        
        message_type = kwargs.get('message_type', 'text')
        
        if message_type == 'text':
            data = {
                'touser': wechat_userid,
                'msgtype': 'text',
                'agentid': self.agentid,
                'text': {
                    'content': content
                }
            }
        elif message_type == 'markdown':
            data = {
                'touser': wechat_userid,
                'msgtype': 'markdown',
                'agentid': self.agentid,
                'markdown': {
                    'content': content
                }
            }
        elif message_type == 'textcard':
            data = {
                'touser': wechat_userid,
                'msgtype': 'textcard',
                'agentid': self.agentid,
                'textcard': {
                    'title': kwargs.get('title', '蒙小碳·能源站'),
                    'description': content,
                    'url': kwargs.get('url', ''),
                    'btntxt': kwargs.get('btntxt', '查看详情')
                }
            }
        else:
            data = {
                'touser': wechat_userid,
                'msgtype': 'text',
                'agentid': self.agentid,
                'text': {
                    'content': content
                }
            }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"企业微信推送成功: user_id={user_id}")
                return True
            else:
                logger.error(f"企业微信推送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"企业微信推送异常: {e}")
            return False
    
    def send_batch(self, user_ids: List[int], content: str, **kwargs) -> Dict[str, int]:
        """批量发送"""
        success_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            if self.send(user_id, content, **kwargs):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            'success': success_count,
            'failed': failed_count
        }


class PushManager:
    """推送管理器"""
    
    def __init__(self):
        self.services = {}
    
    def register_service(self, name: str, service: PushService):
        """注册推送服务"""
        self.services[name] = service
    
    def get_service(self, name: str) -> Optional[PushService]:
        """获取推送服务"""
        return self.services.get(name)
    
    def send_to_user(self, user_id: int, content: str, channels: List[str] = None, **kwargs) -> Dict[str, bool]:
        """发送给单个用户"""
        if channels is None:
            channels = ['wechat_work']
        
        results = {}
        for channel in channels:
            service = self.get_service(channel)
            if service:
                results[channel] = service.send(user_id, content, **kwargs)
            else:
                results[channel] = False
        
        return results
    
    def send_to_users(self, user_ids: List[int], content: str, channels: List[str] = None, **kwargs) -> Dict[str, Dict]:
        """发送给多个用户"""
        if channels is None:
            channels = ['wechat_work']
        
        results = {}
        for channel in channels:
            service = self.get_service(channel)
            if service:
                results[channel] = service.send_batch(user_ids, content, **kwargs)
            else:
                results[channel] = {'success': 0, 'failed': len(user_ids)}
        
        return results
    
    def send_daily_brief(self, brief_content: Dict) -> Dict:
        """发送每日简报"""
        # 获取所有活跃订阅用户
        from datetime import datetime
        active_subscriptions = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.end_date > datetime.utcnow()
        ).all()
        
        user_ids = [sub.user_id for sub in active_subscriptions]
        
        if not user_ids:
            return {'message': '没有活跃订阅用户', 'sent': 0}
        
        # 构造简报内容
        content = self._format_daily_brief(brief_content)
        
        # 发送推送
        results = self.send_to_users(
            user_ids, 
            content, 
            channels=['wechat_work'],
            message_type='markdown',
            title='蒙小碳·每日简报'
        )
        
        return {
            'message': '简报推送完成',
            'total_users': len(user_ids),
            'results': results
        }
    
    def _format_daily_brief(self, brief_content: Dict) -> str:
        """格式化每日简报为 Markdown"""
        content = brief_content.get('content', {})
        ai_suggestion = brief_content.get('ai_suggestion', '')
        
        markdown = f"""# 蒙小碳·每日简报
        
**日期**: {datetime.now().strftime('%Y年%m月%d日')}

---

"""
        
        # 添加各分类摘要
        categories = {
            'ndrc': '📋 发改委动态',
            'coal': '⚫ 煤炭行业',
            'power': '⚡ 电力行业',
            'new_energy': '🌱 新能源'
        }
        
        for key, title in categories.items():
            if key in content and content[key]:
                markdown += f"## {title}\n\n"
                for item in content[key][:3]:  # 只显示前3条
                    markdown += f"- {item}\n"
                markdown += "\n"
        
        # 添加 AI 建议
        if ai_suggestion:
            markdown += f"## 💡 今日建议\n\n{ai_suggestion}\n\n"
        
        markdown += "---\n\n"
        markdown += "*查看更多详情，请访问 [蒙小碳·能源站](http://localhost:5173)*"
        
        return markdown
    
    def send_article_notification(self, article_id: int, user_ids: List[int] = None) -> Dict:
        """发送文章通知"""
        from app.models import Article
        
        article = Article.query.get(article_id)
        if not article:
            return {'error': '文章不存在'}
        
        # 如果没有指定用户，发送给所有订阅用户
        if user_ids is None:
            from datetime import datetime
            active_subscriptions = Subscription.query.filter(
                Subscription.status == 'active',
                Subscription.end_date > datetime.utcnow()
            ).all()
            user_ids = [sub.user_id for sub in active_subscriptions]
        
        # 构造消息
        content = f"""📰 新文章推送

**{article.title}**

{article.summary or ''}

分类: {article.category}
来源: {article.source}
"""
        
        # 发送推送
        results = self.send_to_users(
            user_ids,
            content,
            channels=['wechat_work'],
            message_type='textcard',
            title=article.title,
            url=f"http://localhost:5173/articles/{article.id}"
        )
        
        return {
            'message': '文章推送完成',
            'article_id': article_id,
            'total_users': len(user_ids),
            'results': results
        }


# 全局推送管理器实例
push_manager = PushManager()


def init_push_services(app):
    """初始化推送服务"""
    # 从配置读取企业微信配置
    corpid = app.config.get('WECHAT_WORK_CORPID', '')
    corpsecret = app.config.get('WECHAT_WORK_CORPSECRET', '')
    agentid = app.config.get('WECHAT_WORK_AGENTID', '')
    
    if corpid and corpsecret and agentid:
        wechat_work_service = WeChatWorkPushService(corpid, corpsecret, agentid)
        push_manager.register_service('wechat_work', wechat_work_service)
        logger.info("企业微信推送服务已注册")
    else:
        logger.warning("企业微信配置不完整，推送服务未启用")
