from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import permissions_bp
from app.services.permission_controller import PermissionController


@permissions_bp.route('/features')
class PermissionFeatures(MethodView):
    @jwt_required()
    def get(self):
        """获取用户可用功能列表"""
        user_id = int(get_jwt_identity())
        controller = PermissionController()
        
        # 获取用户订阅等级
        subscription_level = controller.get_user_subscription_level(user_id)
        
        # 获取该等级可用的功能列表
        available_features = controller.get_available_features(subscription_level)
        
        return jsonify({
            'success': True,
            'data': {
                'subscription_level': subscription_level,
                'features': available_features
            }
        }), 200


@permissions_bp.route('/check/<string:feature>')
class PermissionCheck(MethodView):
    @jwt_required()
    def get(self, feature):
        """检查用户是否有权限访问指定功能"""
        user_id = int(get_jwt_identity())
        controller = PermissionController()
        
        # 检查权限
        result = controller.check_permission(user_id, feature)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
