"""
多渠道推送器 (MultiChannelPusher)
支持企业微信、钉钉、飞书、邮件、短信等多种推送渠道
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from app import db
from app.models import Subscription, SubscriptionPlan, User
from app.services.email_push_service import get_email_push_service
from app.services.sms_push_service import get_sms_push_service
from app.services.enterprise_wechat_push_service import get_enterprise_wechat_service
from app.services.dingtalk_push_service import get_dingtalk_service
from app.services.feishu_push_service import get_feishu_service

logger = logging.getLogger(__name__)


class MultiChannelPusher:
    """
    多渠道推送器
    
    职责:
    - 获取用户配置的推送渠道
    - 验证渠道配置（邮箱格式、手机号格式、IM ID格式）
    - 根据订阅等级控制可用渠道
    """
    
    # 订阅等级与可用渠道的映射
    SUBSCRIPTION_LEVEL_CHANNELS = {
        'free': ['enterprise_wechat', 'dingtalk', 'feishu'],
        'standard': ['enterprise_wechat', 'dingtalk', 'feishu', 'email'],
        'premium': ['enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms']
    }
    
    # 邮箱格式正则表达式
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # 手机号格式正则表达式（中国大陆手机号）
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
    
    def __init__(self):
        """初始化多渠道推送器"""
        self.name = "MultiChannelPusher"
        self.email_service = None  # 延迟初始化
        self.sms_service = None  # 延迟初始化
        self.wechat_service = None  # 延迟初始化
        self.dingtalk_service = None  # 延迟初始化
        self.feishu_service = None  # 延迟初始化
    
    def get_user_channels(self, user_id: int) -> Dict[str, Optional[str]]:
        """
        获取用户配置的推送渠道
        
        Args:
            user_id: 用户ID
            
        Returns:
            {
                'enterprise_wechat': 'user_wechat_id' or None,
                'dingtalk': 'user_dingtalk_id' or None,
                'feishu': 'user_feishu_id' or None,
                'email': 'user@example.com' or None,
                'sms': '13800138000' or None,
                'subscription_level': 'free' | 'standard' | 'premium',
                'allowed_channels': ['enterprise_wechat', 'dingtalk', 'feishu', ...]
            }
        """
        # 查询用户的活跃订阅
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            logger.warning(f"用户 {user_id} 没有活跃订阅")
            return {
                'enterprise_wechat': None,
                'dingtalk': None,
                'feishu': None,
                'email': None,
                'sms': None,
                'subscription_level': None,
                'allowed_channels': []
            }
        
        # 获取订阅等级
        subscription_level = self._get_subscription_level(subscription)
        
        # 获取该等级允许的渠道
        allowed_channels = self.SUBSCRIPTION_LEVEL_CHANNELS.get(subscription_level, [])
        
        # 获取用户配置的推送渠道
        push_channels = subscription.push_channels or {}
        
        # 构造返回结果
        result = {
            'enterprise_wechat': push_channels.get('enterprise_wechat'),
            'dingtalk': push_channels.get('dingtalk'),
            'feishu': push_channels.get('feishu'),
            'email': push_channels.get('email'),
            'sms': push_channels.get('sms'),
            'subscription_level': subscription_level,
            'allowed_channels': allowed_channels
        }
        
        return result
    
    def validate_channel_config(self, channel: str, value: str) -> Tuple[bool, str]:
        """
        验证渠道配置
        
        Args:
            channel: 渠道名称 ('enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms')
            value: 渠道配置值
            
        Returns:
            (is_valid, error_message)
        """
        if channel == 'enterprise_wechat':
            # 企业微信ID验证：非空字符串
            if not value or not isinstance(value, str) or not value.strip():
                return False, "企业微信ID不能为空"
            return True, ""
        
        elif channel == 'dingtalk':
            # 钉钉ID验证：非空字符串
            if not value or not isinstance(value, str) or not value.strip():
                return False, "钉钉ID不能为空"
            return True, ""
        
        elif channel == 'feishu':
            # 飞书ID验证：非空字符串
            if not value or not isinstance(value, str) or not value.strip():
                return False, "飞书ID不能为空"
            return True, ""
        
        elif channel == 'email':
            # 邮箱格式验证
            if not value or not isinstance(value, str):
                return False, "邮箱地址不能为空"
            
            if not self.EMAIL_PATTERN.match(value):
                return False, "邮箱地址格式不正确"
            
            return True, ""
        
        elif channel == 'sms':
            # 手机号格式验证
            if not value or not isinstance(value, str):
                return False, "手机号码不能为空"
            
            # 移除可能的空格和连字符
            phone = value.replace(' ', '').replace('-', '')
            
            if not self.PHONE_PATTERN.match(phone):
                return False, "手机号码格式不正确（请输入11位中国大陆手机号）"
            
            return True, ""
        
        else:
            return False, f"不支持的推送渠道: {channel}"
    
    def check_channel_permission(self, user_id: int, channel: str) -> Tuple[bool, str]:
        """
        检查用户是否有权限使用指定渠道
        
        Args:
            user_id: 用户ID
            channel: 渠道名称
            
        Returns:
            (has_permission, error_message)
        """
        # 获取用户渠道信息
        user_channels = self.get_user_channels(user_id)
        
        subscription_level = user_channels.get('subscription_level')
        if not subscription_level:
            return False, "用户没有活跃订阅"
        
        allowed_channels = user_channels.get('allowed_channels', [])
        
        if channel not in allowed_channels:
            # 根据渠道给出具体的升级提示
            if channel in ['enterprise_wechat', 'dingtalk', 'feishu']:
                return False, "IM推送需要有效订阅"
            elif channel == 'email':
                return False, "邮件推送需要基础版或高级版订阅"
            elif channel == 'sms':
                return False, "短信推送需要高级版订阅"
            else:
                return False, f"当前订阅等级不支持 {channel} 渠道"
        
        return True, ""
    
    def _get_subscription_level(self, subscription: Subscription) -> str:
        """
        获取订阅等级
        
        Args:
            subscription: 订阅对象
            
        Returns:
            'free' | 'standard' | 'premium'
        """
        if not subscription.plan:
            return 'free'
        
        plan_name = subscription.plan.name.lower()
        
        # 根据套餐名称判断等级
        if 'premium' in plan_name or '高级' in plan_name:
            return 'premium'
        elif 'standard' in plan_name or '标准' in plan_name or '基础' in plan_name:
            return 'standard'
        elif 'free' in plan_name or '免费' in plan_name or '试用' in plan_name:
            return 'free'
        else:
            return 'free'
    
    def push(self, user_id: int, subject: str, content: str, 
             channels: Optional[List[str]] = None, html: bool = True) -> Dict[str, Dict[str, any]]:
        """
        推送消息到多个渠道
        
        Args:
            user_id: 用户ID
            subject: 消息主题
            content: 推送内容
            channels: 推送渠道列表，None表示使用用户配置的所有渠道
            html: 邮件内容是否为HTML格式（仅对邮件渠道有效）
            
        Returns:
            {
                'wechat': {'success': bool, 'message': str},
                'email': {'success': bool, 'message': str},
                'sms': {'success': bool, 'message': str}
            }
        """
        result = {}
        
        # 获取用户渠道配置
        user_channels = self.get_user_channels(user_id)
        
        if not user_channels.get('subscription_level'):
            logger.warning(f"用户 {user_id} 没有活跃订阅，无法推送")
            return {
                'enterprise_wechat': {'success': False, 'message': '用户没有活跃订阅'},
                'dingtalk': {'success': False, 'message': '用户没有活跃订阅'},
                'feishu': {'success': False, 'message': '用户没有活跃订阅'},
                'email': {'success': False, 'message': '用户没有活跃订阅'},
                'sms': {'success': False, 'message': '用户没有活跃订阅'}
            }
        
        # 确定要推送的渠道
        if channels is None:
            # 使用用户配置的所有渠道
            channels_to_push = []
            if user_channels.get('enterprise_wechat'):
                channels_to_push.append('enterprise_wechat')
            if user_channels.get('dingtalk'):
                channels_to_push.append('dingtalk')
            if user_channels.get('feishu'):
                channels_to_push.append('feishu')
            if user_channels.get('email'):
                channels_to_push.append('email')
            if user_channels.get('sms'):
                channels_to_push.append('sms')
        else:
            channels_to_push = channels
        
        # 并行推送到各个渠道
        for channel in channels_to_push:
            if channel == 'enterprise_wechat':
                result['enterprise_wechat'] = self._push_enterprise_wechat(user_id, user_channels, subject, content)
            elif channel == 'dingtalk':
                result['dingtalk'] = self._push_dingtalk(user_id, user_channels, subject, content)
            elif channel == 'feishu':
                result['feishu'] = self._push_feishu(user_id, user_channels, subject, content)
            elif channel == 'email':
                result['email'] = self._push_email(user_id, user_channels, subject, content, html)
            elif channel == 'sms':
                result['sms'] = self._push_sms(user_id, user_channels, subject, content)
        
        return result
    
    def _push_email(self, user_id: int, user_channels: Dict, subject: str, 
                    content: str, html: bool) -> Dict[str, any]:
        """
        推送邮件
        
        Args:
            user_id: 用户ID
            user_channels: 用户渠道配置
            subject: 邮件主题
            content: 邮件内容
            html: 是否为HTML格式
            
        Returns:
            {'success': bool, 'message': str}
        """
        # 检查权限
        has_permission, error_msg = self.check_channel_permission(user_id, 'email')
        if not has_permission:
            logger.warning(f"用户 {user_id} 无权限使用邮件推送: {error_msg}")
            return {'success': False, 'message': error_msg}
        
        # 获取邮箱地址
        email = user_channels.get('email')
        if not email:
            logger.warning(f"用户 {user_id} 未配置邮箱地址")
            return {'success': False, 'message': '未配置邮箱地址'}
        
        # 初始化邮件服务（延迟初始化）
        if self.email_service is None:
            self.email_service = get_email_push_service()
        
        # 发送邮件
        try:
            success = self.email_service.send(email, subject, content, html)
            if success:
                logger.info(f"邮件推送成功: 用户 {user_id}, 邮箱 {email}")
                return {'success': True, 'message': '邮件发送成功'}
            else:
                logger.error(f"邮件推送失败: 用户 {user_id}, 邮箱 {email}")
                return {'success': False, 'message': '邮件发送失败'}
        except Exception as e:
            logger.error(f"邮件推送异常: 用户 {user_id}, 错误: {e}")
            return {'success': False, 'message': f'邮件发送异常: {str(e)}'}
    
    def _push_enterprise_wechat(self, user_id: int, user_channels: Dict, subject: str, 
                                content: str) -> Dict[str, any]:
        """
        推送企业微信
        
        Args:
            user_id: 用户ID
            user_channels: 用户渠道配置
            subject: 消息主题
            content: 消息内容
            
        Returns:
            {'success': bool, 'message': str}
        """
        # 检查权限
        has_permission, error_msg = self.check_channel_permission(user_id, 'enterprise_wechat')
        if not has_permission:
            logger.warning(f"用户 {user_id} 无权限使用企业微信推送: {error_msg}")
            return {'success': False, 'message': error_msg}
        
        # 获取企业微信ID
        wechat_id = user_channels.get('enterprise_wechat')
        if not wechat_id:
            logger.warning(f"用户 {user_id} 未配置企业微信ID")
            return {'success': False, 'message': '未配置企业微信ID'}
        
        # 初始化企业微信服务（延迟初始化）
        if self.wechat_service is None:
            self.wechat_service = get_enterprise_wechat_service()
        
        # 发送消息
        try:
            success = self.wechat_service.send(wechat_id, subject, content, message_type='markdown')
            if success:
                logger.info(f"企业微信推送成功: 用户 {user_id}, 微信ID {wechat_id}")
                return {'success': True, 'message': '企业微信消息发送成功'}
            else:
                logger.error(f"企业微信推送失败: 用户 {user_id}, 微信ID {wechat_id}")
                return {'success': False, 'message': '企业微信消息发送失败'}
        except Exception as e:
            logger.error(f"企业微信推送异常: 用户 {user_id}, 错误: {e}")
            return {'success': False, 'message': f'企业微信消息发送异常: {str(e)}'}
    
    def _push_dingtalk(self, user_id: int, user_channels: Dict, subject: str, 
                       content: str) -> Dict[str, any]:
        """
        推送钉钉
        
        Args:
            user_id: 用户ID
            user_channels: 用户渠道配置
            subject: 消息主题
            content: 消息内容
            
        Returns:
            {'success': bool, 'message': str}
        """
        # 检查权限
        has_permission, error_msg = self.check_channel_permission(user_id, 'dingtalk')
        if not has_permission:
            logger.warning(f"用户 {user_id} 无权限使用钉钉推送: {error_msg}")
            return {'success': False, 'message': error_msg}
        
        # 获取钉钉ID
        dingtalk_id = user_channels.get('dingtalk')
        if not dingtalk_id:
            logger.warning(f"用户 {user_id} 未配置钉钉ID")
            return {'success': False, 'message': '未配置钉钉ID'}
        
        # 初始化钉钉服务（延迟初始化）
        if self.dingtalk_service is None:
            self.dingtalk_service = get_dingtalk_service()
        
        # 发送消息
        try:
            success = self.dingtalk_service.send(dingtalk_id, subject, content, message_type='markdown')
            if success:
                logger.info(f"钉钉推送成功: 用户 {user_id}, 钉钉ID {dingtalk_id}")
                return {'success': True, 'message': '钉钉消息发送成功'}
            else:
                logger.error(f"钉钉推送失败: 用户 {user_id}, 钉钉ID {dingtalk_id}")
                return {'success': False, 'message': '钉钉消息发送失败'}
        except Exception as e:
            logger.error(f"钉钉推送异常: 用户 {user_id}, 错误: {e}")
            return {'success': False, 'message': f'钉钉消息发送异常: {str(e)}'}
    
    def _push_feishu(self, user_id: int, user_channels: Dict, subject: str, 
                     content: str) -> Dict[str, any]:
        """
        推送飞书
        
        Args:
            user_id: 用户ID
            user_channels: 用户渠道配置
            subject: 消息主题
            content: 消息内容
            
        Returns:
            {'success': bool, 'message': str}
        """
        # 检查权限
        has_permission, error_msg = self.check_channel_permission(user_id, 'feishu')
        if not has_permission:
            logger.warning(f"用户 {user_id} 无权限使用飞书推送: {error_msg}")
            return {'success': False, 'message': error_msg}
        
        # 获取飞书ID
        feishu_id = user_channels.get('feishu')
        if not feishu_id:
            logger.warning(f"用户 {user_id} 未配置飞书ID")
            return {'success': False, 'message': '未配置飞书ID'}
        
        # 初始化飞书服务（延迟初始化）
        if self.feishu_service is None:
            self.feishu_service = get_feishu_service()
        
        # 发送消息
        try:
            success = self.feishu_service.send(feishu_id, subject, content, message_type='post')
            if success:
                logger.info(f"飞书推送成功: 用户 {user_id}, 飞书ID {feishu_id}")
                return {'success': True, 'message': '飞书消息发送成功'}
            else:
                logger.error(f"飞书推送失败: 用户 {user_id}, 飞书ID {feishu_id}")
                return {'success': False, 'message': '飞书消息发送失败'}
        except Exception as e:
            logger.error(f"飞书推送异常: 用户 {user_id}, 错误: {e}")
            return {'success': False, 'message': f'飞书消息发送异常: {str(e)}'}
    
    def _push_sms(self, user_id: int, user_channels: Dict, subject: str, 
                  content: str) -> Dict[str, any]:
        """
        推送短信（实现）
        
        Args:
            user_id: 用户ID
            user_channels: 用户渠道配置
            subject: 消息主题
            content: 消息内容
            
        Returns:
            {'success': bool, 'message': str}
        """
        # 检查权限
        has_permission, error_msg = self.check_channel_permission(user_id, 'sms')
        if not has_permission:
            logger.warning(f"用户 {user_id} 无权限使用短信推送: {error_msg}")
            return {'success': False, 'message': error_msg}
        
        # 获取手机号
        phone = user_channels.get('sms')
        if not phone:
            logger.warning(f"用户 {user_id} 未配置手机号")
            return {'success': False, 'message': '未配置手机号'}
        
        # 初始化短信服务（延迟初始化）
        if self.sms_service is None:
            self.sms_service = get_sms_push_service()
        
        # 准备短信内容（需求6.13：内容截断和链接）
        # 将主题和内容合并
        sms_content = f"{subject}: {content}"
        
        # 生成完整内容链接（如果需要）
        link = None
        if len(sms_content) > 70:
            # TODO: 生成实际的文章链接
            # 这里使用占位链接，实际应该根据推送内容生成对应的文章链接
            link = "https://mengxiaotan.com/articles"
        
        # 发送短信
        try:
            success = self.sms_service.send(phone, sms_content, link)
            if success:
                logger.info(f"短信推送成功: 用户 {user_id}, 手机号 {phone}")
                return {'success': True, 'message': '短信发送成功'}
            else:
                logger.error(f"短信推送失败: 用户 {user_id}, 手机号 {phone}")
                return {'success': False, 'message': '短信发送失败'}
        except Exception as e:
            logger.error(f"短信推送异常: 用户 {user_id}, 错误: {e}")
            return {'success': False, 'message': f'短信发送异常: {str(e)}'}
    
    def push_batch(self, user_ids: List[int], subject: str, content: str, 
                   html: bool = True) -> Dict[str, any]:
        """
        批量推送
        
        Args:
            user_ids: 用户ID列表
            subject: 消息主题
            content: 推送内容
            html: 邮件内容是否为HTML格式
            
        Returns:
            {
                'total': int,
                'success': int,
                'failed': int,
                'results': [{'user_id': int, 'channels': {...}}]
            }
        """
        total = len(user_ids)
        success = 0
        failed = 0
        results = []
        
        for user_id in user_ids:
            try:
                push_result = self.push(user_id, subject, content, html=html)
                
                # 检查是否至少有一个渠道成功
                has_success = any(
                    channel_result.get('success', False) 
                    for channel_result in push_result.values()
                )
                
                if has_success:
                    success += 1
                else:
                    failed += 1
                
                results.append({
                    'user_id': user_id,
                    'channels': push_result
                })
            except Exception as e:
                logger.error(f"批量推送失败: 用户 {user_id}, 错误: {e}")
                failed += 1
                results.append({
                    'user_id': user_id,
                    'error': str(e)
                })
        
        logger.info(f"批量推送完成: 总数 {total}, 成功 {success}, 失败 {failed}")
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'results': results
        }
