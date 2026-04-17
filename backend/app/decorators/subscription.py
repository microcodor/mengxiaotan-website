"""
订阅等级装饰器 (Subscription Decorator)

提供基于订阅等级的访问控制装饰器，用于保护需要特定订阅等级的API端点。
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.services.permission_controller import PermissionController
from app.models import PermissionAccessLog
from app import db
from datetime import datetime


def require_subscription(min_level: str, feature: str = None):
    """
    订阅等级装饰器
    
    用于保护需要特定订阅等级的API端点。装饰器会检查当前用户的订阅等级，
    如果用户的订阅等级低于所需等级，则返回403错误。
    
    注意：此装饰器会自动验证JWT，因此不需要额外添加 @jwt_required() 装饰器。
    
    Args:
        min_level: 最低订阅等级 ('free', 'standard', 'premium')
        feature: 功能标识，用于日志记录（可选）
    
    Returns:
        装饰器函数
    
    Example:
        @app.route('/api/dashboard/advanced')
        @require_subscription('standard', 'dashboard_full')
        def get_advanced_dashboard():
            # 只有标准版及以上用户可访问
            pass
    
    Validates: Requirements 5.5, 5.8
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 验证JWT token
            verify_jwt_in_request()
            
            # 获取当前用户ID
            user_id = get_jwt_identity()
            
            # 创建权限控制器实例
            controller = PermissionController()
            
            # 获取用户订阅等级
            user_level = controller.get_user_subscription_level(user_id)
            
            # 定义等级层次结构
            level_hierarchy = {'free': 0, 'standard': 1, 'premium': 2}
            
            # 比较用户等级和所需等级
            user_level_value = level_hierarchy.get(user_level, -1)
            required_level_value = level_hierarchy.get(min_level, 999)
            
            # 确定是否允许访问
            allowed = user_level_value >= required_level_value
            
            # 记录访问日志
            try:
                feature_name = feature or f.__name__
                ip_address = request.remote_addr if request else None
                
                log = PermissionAccessLog(
                    user_id=user_id,
                    feature=feature_name,
                    subscription_level=user_level,
                    allowed=allowed,
                    ip_address=ip_address,
                    accessed_at=datetime.utcnow()
                )
                
                db.session.add(log)
                db.session.commit()
            except Exception:
                # 日志记录失败不应影响主流程
                db.session.rollback()
            
            if not allowed:
                # 权限不足，返回403错误
                return jsonify({
                    'error': '权限不足',
                    'message': f'此功能需要{min_level}版本订阅',
                    'current_level': user_level,
                    'required_level': min_level
                }), 403
            
            # 权限验证通过，执行原函数
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
