"""
推送设置API
用户端和管理端的推送渠道配置
"""
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from app import db
from app.models import User, Subscription
from app.services.multi_channel_pusher import MultiChannelPusher
from app.utils.crypto import encrypt_im_app_config, decrypt_im_app_config, mask_im_app_config
import logging

logger = logging.getLogger(__name__)

blp = Blueprint('push_settings', __name__, url_prefix='/api/push-settings', description='推送设置')

pusher = MultiChannelPusher()


# ==================== IM应用配置API ====================

@blp.route('/im-apps', methods=['GET'])
@jwt_required()
def get_im_apps():
    """
    获取当前用户的IM应用配置
    
    Returns:
        IM应用配置(Secret脱敏)
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        abort(404, message='用户不存在')
    
    # 获取配置并脱敏
    config = user.im_app_config or {}
    masked_config = mask_im_app_config(config)
    
    return {
        'enterprise_wechat': masked_config.get('enterprise_wechat', {'enabled': False}),
        'dingtalk': masked_config.get('dingtalk', {'enabled': False}),
        'feishu': masked_config.get('feishu', {'enabled': False})
    }, 200


@blp.route('/im-apps', methods=['POST'])
@jwt_required()
def update_im_apps():
    """
    更新当前用户的IM应用配置
    
    Request Body:
        {
            "enterprise_wechat": {
                "enabled": true,
                "corp_id": "ww1234567890abcdef",
                "agent_id": "1000002",
                "secret": "your-secret-here"
            },
            "dingtalk": {
                "enabled": true,
                "app_key": "dingxxxxxxxx",
                "app_secret": "your-secret-here",
                "agent_id": "123456789"
            },
            "feishu": {
                "enabled": true,
                "app_id": "cli_xxxxxxxx",
                "app_secret": "your-secret-here"
            }
        }
    
    Returns:
        更新后的配置(Secret脱敏)
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        abort(404, message='用户不存在')
    
    data = request.get_json() or {}
    
    # 获取当前配置
    current_config = user.im_app_config or {}
    
    # 更新企业微信配置
    if 'enterprise_wechat' in data:
        wechat = data['enterprise_wechat']
        if wechat.get('enabled'):
            # 验证必填字段
            if not wechat.get('corp_id') or not wechat.get('agent_id') or not wechat.get('secret'):
                abort(400, message='企业微信配置不完整,需要corp_id、agent_id和secret')
            
            current_config['enterprise_wechat'] = {
                'enabled': True,
                'corp_id': wechat['corp_id'],
                'agent_id': wechat['agent_id'],
                'secret': wechat['secret']  # 稍后加密
            }
        else:
            current_config['enterprise_wechat'] = {'enabled': False}
    
    # 更新钉钉配置
    if 'dingtalk' in data:
        dingtalk = data['dingtalk']
        if dingtalk.get('enabled'):
            if not dingtalk.get('app_key') or not dingtalk.get('app_secret') or not dingtalk.get('agent_id'):
                abort(400, message='钉钉配置不完整,需要app_key、app_secret和agent_id')
            
            current_config['dingtalk'] = {
                'enabled': True,
                'app_key': dingtalk['app_key'],
                'app_secret': dingtalk['app_secret'],
                'agent_id': dingtalk['agent_id']
            }
        else:
            current_config['dingtalk'] = {'enabled': False}
    
    # 更新飞书配置
    if 'feishu' in data:
        feishu = data['feishu']
        if feishu.get('enabled'):
            if not feishu.get('app_id') or not feishu.get('app_secret'):
                abort(400, message='飞书配置不完整,需要app_id和app_secret')
            
            current_config['feishu'] = {
                'enabled': True,
                'app_id': feishu['app_id'],
                'app_secret': feishu['app_secret']
            }
        else:
            current_config['feishu'] = {'enabled': False}
    
    # 加密敏感信息
    encrypted_config = encrypt_im_app_config(current_config)
    
    # 保存到数据库
    user.im_app_config = encrypted_config
    db.session.commit()
    
    logger.info(f"用户 {user_id} 更新IM应用配置")
    
    # 返回脱敏后的配置
    masked_config = mask_im_app_config(current_config)
    
    return {
        'message': 'IM应用配置已更新',
        'config': masked_config
    }, 200


@blp.route('/im-apps/test', methods=['POST'])
@jwt_required()
def test_im_app():
    """
    测试IM应用配置连接
    
    Request Body:
        {
            "platform": "enterprise_wechat"  // enterprise_wechat, dingtalk, feishu
        }
    
    Returns:
        测试结果
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        abort(404, message='用户不存在')
    
    data = request.get_json() or {}
    platform = data.get('platform')
    
    if not platform:
        abort(400, message='请指定要测试的平台')
    
    if platform not in ['enterprise_wechat', 'dingtalk', 'feishu']:
        abort(400, message='不支持的平台')
    
    # 获取并解密配置
    encrypted_config = user.im_app_config or {}
    config = decrypt_im_app_config(encrypted_config)
    
    platform_config = config.get(platform, {})
    
    if not platform_config.get('enabled'):
        abort(400, message=f'{platform}未启用')
    
    # 测试连接(尝试获取access_token)
    try:
        if platform == 'enterprise_wechat':
            from app.services.enterprise_wechat_push_service import EnterpriseWechatPushService
            service = EnterpriseWechatPushService(
                corp_id=platform_config['corp_id'],
                agent_id=platform_config['agent_id'],
                secret=platform_config['secret']
            )
            token = service._get_access_token()
            if token:
                return {'success': True, 'message': '企业微信连接测试成功'}, 200
            else:
                return {'success': False, 'message': '企业微信连接测试失败,无法获取access_token'}, 200
        
        elif platform == 'dingtalk':
            from app.services.dingtalk_push_service import DingtalkPushService
            service = DingtalkPushService(
                app_key=platform_config['app_key'],
                app_secret=platform_config['app_secret'],
                agent_id=platform_config['agent_id']
            )
            token = service._get_access_token()
            if token:
                return {'success': True, 'message': '钉钉连接测试成功'}, 200
            else:
                return {'success': False, 'message': '钉钉连接测试失败,无法获取access_token'}, 200
        
        elif platform == 'feishu':
            from app.services.feishu_push_service import FeishuPushService
            service = FeishuPushService(
                app_id=platform_config['app_id'],
                app_secret=platform_config['app_secret']
            )
            token = service._get_access_token()
            if token:
                return {'success': True, 'message': '飞书连接测试成功'}, 200
            else:
                return {'success': False, 'message': '飞书连接测试失败,无法获取access_token'}, 200
    
    except Exception as e:
        logger.error(f"测试IM应用连接失败: {e}")
        return {'success': False, 'message': f'连接测试失败: {str(e)}'}, 200


# ==================== 推送渠道配置API (接收人) ====================

# ==================== 推送渠道配置API (接收人) ====================

@blp.route('/channels', methods=['GET'])
@jwt_required()
def get_push_channels():
    """
    获取当前用户的推送渠道配置(接收人)
    
    Returns:
        推送渠道配置
    """
    user_id = int(get_jwt_identity())
    
    # 获取用户渠道配置
    user_channels = pusher.get_user_channels(user_id)
    
    response = {
        'subscription_level': user_channels.get('subscription_level'),
        'allowed_channels': user_channels.get('allowed_channels', []),
        'channels': {
            'enterprise_wechat': user_channels.get('enterprise_wechat'),
            'dingtalk': user_channels.get('dingtalk'),
            'feishu': user_channels.get('feishu'),
            'email': user_channels.get('email'),
            'sms': user_channels.get('sms')
        }
    }
    
    return response, 200


@blp.route('/channels', methods=['POST'])
@jwt_required()
def update_push_channels():
    """
    更新当前用户的推送渠道配置(接收人)
    
    Request Body:
        {
            "enterprise_wechat": "zhangsan",
            "dingtalk": "manager123",
            "feishu": "ou_xxx",
            "email": "user@example.com",
            "sms": "13800138000"
        }
    
    Returns:
        更新后的推送设置
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    # 查询用户的活跃订阅
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()
    
    if not subscription:
        abort(400, message='没有活跃订阅，无法配置推送渠道')
    
    # 获取当前推送渠道配置
    push_channels = subscription.push_channels or {}
    
    # 验证并更新各个渠道
    errors = []
    
    for channel in ['enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms']:
        if channel in data:
            value = data[channel]
            
            # 如果值为None或空字符串，删除该渠道配置
            if not value:
                push_channels.pop(channel, None)
                continue
            
            # 验证渠道配置
            is_valid, error_msg = pusher.validate_channel_config(channel, value)
            if not is_valid:
                errors.append(f"{channel}: {error_msg}")
                continue
            
            # 检查权限
            has_permission, error_msg = pusher.check_channel_permission(user_id, channel)
            if not has_permission:
                errors.append(f"{channel}: {error_msg}")
                continue
            
            # 更新配置
            push_channels[channel] = value
    
    if errors:
        abort(400, message='配置验证失败: ' + '; '.join(errors))
    
    # 保存到数据库
    subscription.push_channels = push_channels
    db.session.commit()
    
    logger.info(f"用户 {user_id} 更新推送设置: {list(push_channels.keys())}")
    
    return {
        'message': '推送设置已更新',
        'configured_channels': push_channels
    }, 200


@blp.route('/test', methods=['POST'])
@jwt_required()
def test_push_channel():
    """
    测试推送渠道
    
    Request Body:
        {
            "channel": "enterprise_wechat"
        }
    
    Returns:
        测试结果
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    channel = data.get('channel')
    message = data.get('message', '这是一条测试消息')
    
    if not channel:
        abort(400, message='请指定推送渠道')
    
    # 检查渠道是否有效
    valid_channels = ['enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms']
    if channel not in valid_channels:
        abort(400, message=f'无效的推送渠道，支持的渠道: {", ".join(valid_channels)}')
    
    # 检查权限
    has_permission, error_msg = pusher.check_channel_permission(user_id, channel)
    if not has_permission:
        abort(403, message=error_msg)
    
    # 获取用户渠道配置
    user_channels = pusher.get_user_channels(user_id)
    if not user_channels.get(channel):
        abort(400, message=f'未配置{channel}渠道')
    
    # 发送测试推送
    try:
        result = pusher.push(
            user_id=user_id,
            subject='蒙小碳测试推送',
            content=message,
            channels=[channel]
        )
        
        channel_result = result.get(channel, {})
        
        if channel_result.get('success'):
            return {
                'success': True,
                'message': '测试推送发送成功',
                'channel': channel
            }, 200
        else:
            return {
                'success': False,
                'message': channel_result.get('message', '测试推送发送失败'),
                'channel': channel
            }, 200
    except Exception as e:
        logger.error(f"测试推送失败: {e}")
        abort(500, message=f'测试推送失败: {str(e)}')


# ==================== 管理员API ====================

@blp.route('/admin/user/<int:user_id>', methods=['GET'])
@jwt_required()
def admin_get_user_push_settings(user_id):
    """
    管理员获取指定用户的推送设置
    
    Args:
        user_id: 用户ID
    
    Returns:
        用户的推送设置
    """
    # TODO: 添加管理员权限验证
    current_user_id = int(get_jwt_identity())
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用户不存在')
    
    # 获取用户渠道配置
    user_channels = pusher.get_user_channels(user_id)
    
    response = {
        'user_id': user_id,
        'username': user.username,
        'company_name': user.company.name if user.company else None,
        'subscription_level': user_channels.get('subscription_level'),
        'allowed_channels': user_channels.get('allowed_channels', []),
        'configured_channels': {
            'enterprise_wechat': user_channels.get('enterprise_wechat'),
            'dingtalk': user_channels.get('dingtalk'),
            'feishu': user_channels.get('feishu'),
            'email': user_channels.get('email'),
            'sms': user_channels.get('sms')
        }
    }
    
    return response, 200


@blp.route('/admin/user/<int:user_id>', methods=['PUT'])
@jwt_required()
def admin_update_user_push_settings(user_id):
    """
    管理员为指定用户配置推送设置
    
    Args:
        user_id: 用户ID
    
    Request Body:
        {
            "enterprise_wechat": "user123",
            "dingtalk": "user456",
            "feishu": "ou_xxx",
            "email": "user@example.com",
            "sms": "13800138000"
        }
    
    Returns:
        更新后的推送设置
    """
    # TODO: 添加管理员权限验证
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用户不存在')
    
    # 查询用户的活跃订阅
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()
    
    if not subscription:
        abort(400, message='用户没有活跃订阅，无法配置推送渠道')
    
    # 获取当前推送渠道配置
    push_channels = subscription.push_channels or {}
    
    # 验证并更新各个渠道
    errors = []
    
    for channel in ['enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms']:
        if channel in data:
            value = data[channel]
            
            # 如果值为None或空字符串，删除该渠道配置
            if not value:
                push_channels.pop(channel, None)
                continue
            
            # 验证渠道配置
            is_valid, error_msg = pusher.validate_channel_config(channel, value)
            if not is_valid:
                errors.append(f"{channel}: {error_msg}")
                continue
            
            # 管理员可以为用户配置任何渠道，不检查权限
            # 但仍然需要验证格式
            
            # 更新配置
            push_channels[channel] = value
    
    if errors:
        abort(400, message='配置验证失败: ' + '; '.join(errors))
    
    # 保存到数据库
    subscription.push_channels = push_channels
    db.session.commit()
    
    logger.info(f"管理员 {current_user_id} 为用户 {user_id} 更新推送设置: {list(push_channels.keys())}")
    
    return {
        'message': '推送设置已更新',
        'user_id': user_id,
        'configured_channels': push_channels
    }, 200


@blp.route('/admin/user/<int:user_id>/test', methods=['POST'])
@jwt_required()
def admin_test_user_push(user_id):
    """
    管理员为指定用户测试推送
    
    Args:
        user_id: 用户ID
    
    Request Body:
        {
            "channel": "enterprise_wechat",
            "message": "这是一条测试消息"
        }
    
    Returns:
        测试结果
    """
    # TODO: 添加管理员权限验证
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        abort(404, message='用户不存在')
    
    channel = data.get('channel')
    message = data.get('message', '这是一条管理员测试消息')
    
    if not channel:
        abort(400, message='请指定推送渠道')
    
    # 检查渠道是否有效
    valid_channels = ['enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms']
    if channel not in valid_channels:
        abort(400, message=f'无效的推送渠道，支持的渠道: {", ".join(valid_channels)}')
    
    # 获取用户渠道配置
    user_channels = pusher.get_user_channels(user_id)
    if not user_channels.get(channel):
        abort(400, message=f'用户未配置{channel}渠道')
    
    # 发送测试推送
    try:
        result = pusher.push(
            user_id=user_id,
            subject='蒙小碳管理员测试推送',
            content=message,
            channels=[channel]
        )
        
        channel_result = result.get(channel, {})
        
        logger.info(f"管理员 {current_user_id} 为用户 {user_id} 测试推送 {channel}: {channel_result}")
        
        if channel_result.get('success'):
            return {
                'success': True,
                'message': '测试推送发送成功',
                'channel': channel,
                'user_id': user_id
            }, 200
        else:
            return {
                'success': False,
                'message': channel_result.get('message', '测试推送发送失败'),
                'channel': channel,
                'user_id': user_id
            }, 200
    except Exception as e:
        logger.error(f"管理员测试推送失败: {e}")
        abort(500, message=f'测试推送失败: {str(e)}')
