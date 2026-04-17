"""
动态监测预警API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.monitoring_service import MonitoringService
from app.models import User, Subscription
from datetime import datetime

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')


@monitoring_bp.route('/rules', methods=['GET'])
@jwt_required()
def get_rules():
    """获取用户的监测规则列表"""
    try:
        user_id = get_jwt_identity()
        
        # 检查订阅状态
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({'error': '需要有效订阅才能使用此功能'}), 403
        
        # 获取规则列表
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        rules = MonitoringService.get_user_rules(user_id, enabled_only)
        
        return jsonify({
            'rules': [rule.to_dict() for rule in rules],
            'total': len(rules)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/rules', methods=['POST'])
@jwt_required()
def create_rule():
    """创建监测规则"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 检查订阅状态
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            return jsonify({'error': '需要有效订阅才能使用此功能'}), 403
        
        # 验证必填字段
        required_fields = ['name', 'type', 'keywords']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 验证监测类型
        valid_types = ['policy', 'price', 'industry']
        if data['type'] not in valid_types:
            return jsonify({'error': f'无效的监测类型，必须是: {", ".join(valid_types)}'}), 400
        
        # 验证预警等级
        if 'level' in data:
            valid_levels = ['high', 'medium', 'low']
            if data['level'] not in valid_levels:
                return jsonify({'error': f'无效的预警等级，必须是: {", ".join(valid_levels)}'}), 400
        
        # 创建规则
        rule = MonitoringService.create_rule(
            user_id=user_id,
            company_id=user.company_id,
            rule_data=data
        )
        
        return jsonify({
            'message': '监测规则创建成功',
            'rule': rule.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/rules/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
    """获取指定监测规则"""
    try:
        user_id = get_jwt_identity()
        
        rule = MonitoringService.get_rule_by_id(rule_id, user_id)
        
        if not rule:
            return jsonify({'error': '规则不存在'}), 404
        
        return jsonify(rule.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/rules/<int:rule_id>', methods=['PUT'])
@jwt_required()
def update_rule(rule_id):
    """更新监测规则"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证监测类型
        if 'type' in data:
            valid_types = ['policy', 'price', 'industry']
            if data['type'] not in valid_types:
                return jsonify({'error': f'无效的监测类型，必须是: {", ".join(valid_types)}'}), 400
        
        # 验证预警等级
        if 'level' in data:
            valid_levels = ['high', 'medium', 'low']
            if data['level'] not in valid_levels:
                return jsonify({'error': f'无效的预警等级，必须是: {", ".join(valid_levels)}'}), 400
        
        rule = MonitoringService.update_rule(rule_id, user_id, data)
        
        if not rule:
            return jsonify({'error': '规则不存在'}), 404
        
        return jsonify({
            'message': '规则更新成功',
            'rule': rule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    """删除监测规则"""
    try:
        user_id = get_jwt_identity()
        
        success = MonitoringService.delete_rule(rule_id, user_id)
        
        if not success:
            return jsonify({'error': '规则不存在'}), 404
        
        return jsonify({'message': '规则删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
@jwt_required()
def toggle_rule(rule_id):
    """启用/禁用规则"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'enabled' not in data:
            return jsonify({'error': '缺少enabled字段'}), 400
        
        rule = MonitoringService.toggle_rule(rule_id, user_id, data['enabled'])
        
        if not rule:
            return jsonify({'error': '规则不存在'}), 404
        
        status = '启用' if data['enabled'] else '禁用'
        return jsonify({
            'message': f'规则已{status}',
            'rule': rule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """获取用户的预警列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        level = request.args.get('level')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # 验证参数
        if level and level not in ['high', 'medium', 'low']:
            return jsonify({'error': '无效的预警等级'}), 400
        
        if status and status not in ['pending', 'sent', 'read']:
            return jsonify({'error': '无效的状态'}), 400
        
        # 获取预警列表
        alerts = MonitoringService.get_user_alerts(user_id, level, status, limit)
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'total': len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    """获取指定预警详情"""
    try:
        user_id = get_jwt_identity()
        
        alert = MonitoringService.get_alert_by_id(alert_id, user_id)
        
        if not alert:
            return jsonify({'error': '预警不存在'}), 404
        
        return jsonify(alert.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts/<int:alert_id>/read', methods=['POST'])
@jwt_required()
def mark_alert_read(alert_id):
    """标记预警为已读"""
    try:
        user_id = get_jwt_identity()
        
        alert = MonitoringService.mark_alert_read(alert_id, user_id)
        
        if not alert:
            return jsonify({'error': '预警不存在'}), 404
        
        return jsonify({
            'message': '预警已标记为已读',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts/statistics', methods=['GET'])
@jwt_required()
def get_alert_statistics():
    """获取预警统计信息"""
    try:
        user_id = get_jwt_identity()
        
        statistics = MonitoringService.get_alert_statistics(user_id)
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
