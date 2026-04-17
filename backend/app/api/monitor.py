# -*- coding: utf-8 -*-
"""
监控告警 API
"""
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from flask import request
from app.api import monitor_bp
from app.models import User
from app.services.monitor_service import monitor_service
import logging

logger = logging.getLogger(__name__)


def admin_required():
    """管理员权限装饰器"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user


@monitor_bp.route('/statistics')
class MonitorStatistics(MethodView):
    @jwt_required()
    def get(self):
        """获取爬虫统计信息"""
        admin_required()
        
        days = request.args.get('days', 7, type=int)
        
        if days < 1 or days > 90:
            abort(400, message='统计天数必须在1-90之间')
        
        stats = monitor_service.get_crawl_statistics(days=days)
        
        return stats


@monitor_bp.route('/failures')
class MonitorFailures(MethodView):
    @jwt_required()
    def get(self):
        """获取最近的失败记录"""
        admin_required()
        
        limit = request.args.get('limit', 10, type=int)
        
        if limit < 1 or limit > 100:
            abort(400, message='返回数量必须在1-100之间')
        
        failures = monitor_service.get_recent_failures(limit=limit)
        
        return {
            'failures': failures,
            'total': len(failures)
        }


@monitor_bp.route('/health')
class MonitorHealth(MethodView):
    @jwt_required()
    def get(self):
        """获取系统健康状态"""
        admin_required()
        
        health = monitor_service.check_system_health()
        
        return health


@monitor_bp.route('/test-alert')
class TestAlert(MethodView):
    @jwt_required()
    def post(self):
        """测试告警功能"""
        admin_required()
        
        try:
            monitor_service.send_alert(
                spider_name='test_spider',
                error_msg='这是一条测试告警消息'
            )
            return {'message': '测试告警已发送，请检查企业微信和邮箱'}
        except Exception as e:
            logger.error(f"发送测试告警失败: {str(e)}")
            abort(500, message=f'发送失败: {str(e)}')
