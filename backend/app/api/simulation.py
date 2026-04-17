"""
数字分身沙盘API
Digital Twin Sandbox API
"""
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.simulation_service import SimulationService
from app import db
import json

simulation_bp = Blueprint('simulation', 'simulation', url_prefix='/api/simulation', description='数字分身沙盘接口')


@simulation_bp.route('/scenarios', methods=['POST'])
@jwt_required()
def create_scenario():
    """创建模拟场景"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'code': 400, 'message': '场景名称不能为空'}), 400
        
        if not data.get('company_id'):
            return jsonify({'code': 400, 'message': '企业ID不能为空'}), 400
        
        # 验证用户权限（只能为自己的企业创建场景）
        user = db.session.execute(
            'SELECT company_id FROM users WHERE id = :id',
            {'id': current_user_id}
        ).fetchone()
        
        if not user or user[0] != data['company_id']:
            return jsonify({'code': 403, 'message': '无权限为该企业创建场景'}), 403
        
        # 检查场景数量限制（基础版最多5个）
        scenario_count = db.session.execute(
            'SELECT COUNT(*) FROM simulation_scenarios WHERE user_id = :user_id AND status != "deleted"',
            {'user_id': current_user_id}
        ).fetchone()[0]
        
        if scenario_count >= 5:
            return jsonify({'code': 400, 'message': '场景数量已达上限（5个）'}), 400
        
        # 构建场景配置
        config = {
            'policies': data.get('policies', []),
            'price_changes': data.get('price_changes', []),
            'time_range': data.get('time_range', 3)
        }
        
        # 插入场景记录
        cursor = db.session.execute(
            '''INSERT INTO simulation_scenarios 
               (company_id, user_id, name, description, time_range, config, status)
               VALUES (:company_id, :user_id, :name, :description, :time_range, :config, :status)''',
            {
                'company_id': data['company_id'],
                'user_id': current_user_id,
                'name': data['name'],
                'description': data.get('description', ''),
                'time_range': data.get('time_range', 3),
                'config': json.dumps(config, ensure_ascii=False),
                'status': 'draft'
            }
        )
        db.session.commit()
        
        scenario_id = cursor.lastrowid
        
        return jsonify({
            'code': 200,
            'message': '场景创建成功',
            'data': {
                'scenario_id': scenario_id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建场景失败: {str(e)}'}), 500


@simulation_bp.route('/scenarios/<int:scenario_id>/simulate', methods=['POST'])
@jwt_required()
def simulate_scenario(scenario_id):
    """执行场景模拟"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取场景信息
        scenario = db.session.execute(
            'SELECT * FROM simulation_scenarios WHERE id = :id',
            {'id': scenario_id}
        ).fetchone()
        
        if not scenario:
            return jsonify({'code': 404, 'message': '场景不存在'}), 404
        
        # 验证权限
        if scenario[2] != current_user_id:  # user_id
            return jsonify({'code': 403, 'message': '无权限访问该场景'}), 403
        
        # 更新场景状态为运行中
        db.session.execute(
            'UPDATE simulation_scenarios SET status = :status WHERE id = :id',
            {'status': 'running', 'id': scenario_id}
        )
        db.session.commit()
        
        # 执行模拟
        simulation_service = SimulationService(db)
        config = json.loads(scenario[6])  # config字段
        config['name'] = scenario[3]  # name字段
        config['description'] = scenario[4]  # description字段
        
        result = simulation_service.simulate_scenario(scenario[1], config)  # company_id
        
        # 保存模拟结果
        db.session.execute(
            '''INSERT INTO simulation_results 
               (scenario_id, base_case, simulated_case, impact, time_series)
               VALUES (:scenario_id, :base_case, :simulated_case, :impact, :time_series)''',
            {
                'scenario_id': scenario_id,
                'base_case': json.dumps(result['base_case'], ensure_ascii=False),
                'simulated_case': json.dumps(result['simulated_case'], ensure_ascii=False),
                'impact': json.dumps(result['impact'], ensure_ascii=False),
                'time_series': json.dumps(result['time_series'], ensure_ascii=False)
            }
        )
        
        # 更新场景状态为完成
        db.session.execute(
            'UPDATE simulation_scenarios SET status = :status WHERE id = :id',
            {'status': 'completed', 'id': scenario_id}
        )
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '模拟完成',
            'data': result
        })
        
    except Exception as e:
        db.session.rollback()
        # 更新场景状态为失败
        db.session.execute(
            'UPDATE simulation_scenarios SET status = :status WHERE id = :id',
            {'status': 'failed', 'id': scenario_id}
        )
        db.session.commit()
        return jsonify({'code': 500, 'message': f'模拟失败: {str(e)}'}), 500


@simulation_bp.route('/scenarios', methods=['GET'])
@jwt_required()
def get_scenarios():
    """获取用户的场景列表"""
    try:
        current_user_id = get_jwt_identity()
        
        scenarios = db.session.execute(
            '''SELECT s.*, c.name as company_name 
               FROM simulation_scenarios s
               LEFT JOIN companies c ON s.company_id = c.id
               WHERE s.user_id = :user_id AND s.status != "deleted"
               ORDER BY s.created_at DESC''',
            {'user_id': current_user_id}
        ).fetchall()
        
        scenario_list = []
        for scenario in scenarios:
            scenario_list.append({
                'id': scenario[0],
                'company_id': scenario[1],
                'company_name': scenario[11],
                'name': scenario[3],
                'description': scenario[4],
                'time_range': scenario[5],
                'status': scenario[7],
                'created_at': scenario[8].isoformat() if scenario[8] else None,
                'updated_at': scenario[9].isoformat() if scenario[9] else None
            })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': scenario_list
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取场景列表失败: {str(e)}'}), 500


@simulation_bp.route('/scenarios/<int:scenario_id>', methods=['GET'])
@jwt_required()
def get_scenario(scenario_id):
    """获取场景详情"""
    try:
        current_user_id = get_jwt_identity()
        
        scenario = db.session.execute(
            '''SELECT s.*, c.name as company_name 
               FROM simulation_scenarios s
               LEFT JOIN companies c ON s.company_id = c.id
               WHERE s.id = :id''',
            {'id': scenario_id}
        ).fetchone()
        
        if not scenario:
            return jsonify({'code': 404, 'message': '场景不存在'}), 404
        
        # 验证权限
        if scenario[2] != current_user_id:
            return jsonify({'code': 403, 'message': '无权限访问该场景'}), 403
        
        # 获取最新的模拟结果
        result = db.session.execute(
            '''SELECT * FROM simulation_results 
               WHERE scenario_id = :scenario_id 
               ORDER BY created_at DESC LIMIT 1''',
            {'scenario_id': scenario_id}
        ).fetchone()
        
        scenario_data = {
            'id': scenario[0],
            'company_id': scenario[1],
            'company_name': scenario[11],
            'name': scenario[3],
            'description': scenario[4],
            'time_range': scenario[5],
            'config': json.loads(scenario[6]),
            'status': scenario[7],
            'created_at': scenario[8].isoformat() if scenario[8] else None,
            'updated_at': scenario[9].isoformat() if scenario[9] else None
        }
        
        if result:
            scenario_data['result'] = {
                'base_case': json.loads(result[2]),
                'simulated_case': json.loads(result[3]),
                'impact': json.loads(result[4]),
                'time_series': json.loads(result[5]),
                'generated_at': result[6].isoformat() if result[6] else None
            }
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': scenario_data
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取场景详情失败: {str(e)}'}), 500


@simulation_bp.route('/scenarios/<int:scenario_id>', methods=['DELETE'])
@jwt_required()
def delete_scenario(scenario_id):
    """删除场景"""
    try:
        current_user_id = get_jwt_identity()
        
        scenario = db.session.execute(
            'SELECT user_id FROM simulation_scenarios WHERE id = :id',
            {'id': scenario_id}
        ).fetchone()
        
        if not scenario:
            return jsonify({'code': 404, 'message': '场景不存在'}), 404
        
        # 验证权限
        if scenario[0] != current_user_id:
            return jsonify({'code': 403, 'message': '无权限删除该场景'}), 403
        
        # 软删除（更新状态为deleted）
        db.session.execute(
            'UPDATE simulation_scenarios SET status = :status WHERE id = :id',
            {'status': 'deleted', 'id': scenario_id}
        )
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '场景删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除场景失败: {str(e)}'}), 500


@simulation_bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_scenarios():
    """对比多个场景"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        scenario_ids = data.get('scenario_ids', [])
        if not scenario_ids or len(scenario_ids) < 2:
            return jsonify({'code': 400, 'message': '至少需要2个场景进行对比'}), 400
        
        if len(scenario_ids) > 5:
            return jsonify({'code': 400, 'message': '最多对比5个场景'}), 400
        
        # 获取所有场景
        scenarios = []
        for scenario_id in scenario_ids:
            scenario = db.session.execute(
                'SELECT * FROM simulation_scenarios WHERE id = :id',
                {'id': scenario_id}
            ).fetchone()
            
            if not scenario:
                return jsonify({'code': 404, 'message': f'场景{scenario_id}不存在'}), 404
            
            # 验证权限
            if scenario[2] != current_user_id:
                return jsonify({'code': 403, 'message': f'无权限访问场景{scenario_id}'}), 403
            
            # 获取模拟结果
            result = db.session.execute(
                '''SELECT * FROM simulation_results 
                   WHERE scenario_id = :scenario_id 
                   ORDER BY created_at DESC LIMIT 1''',
                {'scenario_id': scenario_id}
            ).fetchone()
            
            if not result:
                return jsonify({'code': 400, 'message': f'场景{scenario_id}尚未执行模拟'}), 400
            
            scenarios.append({
                'id': scenario[0],
                'name': scenario[3],
                'base_case': json.loads(result[2]),
                'simulated_case': json.loads(result[3]),
                'impact': json.loads(result[4]),
                'time_series': json.loads(result[5])
            })
        
        # 找出最优和最差场景
        best_scenario = max(scenarios, key=lambda x: x['simulated_case']['net_profit'])
        worst_scenario = min(scenarios, key=lambda x: x['simulated_case']['net_profit'])
        
        comparison = {
            'scenarios': scenarios,
            'best_scenario': best_scenario['name'],
            'worst_scenario': worst_scenario['name'],
            'comparison_summary': {
                'profit_range': {
                    'min': worst_scenario['simulated_case']['net_profit'],
                    'max': best_scenario['simulated_case']['net_profit'],
                    'diff': best_scenario['simulated_case']['net_profit'] - worst_scenario['simulated_case']['net_profit']
                },
                'roe_range': {
                    'min': worst_scenario['simulated_case']['roe'],
                    'max': best_scenario['simulated_case']['roe'],
                    'diff': best_scenario['simulated_case']['roe'] - worst_scenario['simulated_case']['roe']
                }
            }
        }
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': comparison
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'场景对比失败: {str(e)}'}), 500


@simulation_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """获取预设场景模板"""
    templates = [
        {
            'id': 1,
            'name': '碳税政策影响分析',
            'description': '模拟碳税政策对企业利润的影响',
            'config': {
                'time_range': 3,
                'policies': [
                    {
                        'type': 'carbon_tax',
                        'rate': 50
                    }
                ],
                'price_changes': []
            }
        },
        {
            'id': 2,
            'name': '煤炭价格上涨影响',
            'description': '模拟煤炭价格上涨20%对企业成本的影响',
            'config': {
                'time_range': 3,
                'policies': [],
                'price_changes': [
                    {
                        'type': 'raw_material',
                        'change': 20
                    }
                ]
            }
        },
        {
            'id': 3,
            'name': '新能源补贴政策',
            'description': '模拟新能源补贴政策对企业收入的影响',
            'config': {
                'time_range': 5,
                'policies': [
                    {
                        'type': 'subsidy',
                        'subsidy_type': 'production',
                        'rate': 100
                    }
                ],
                'price_changes': []
            }
        },
        {
            'id': 4,
            'name': '双碳政策综合影响',
            'description': '模拟碳税+配额政策的综合影响',
            'config': {
                'time_range': 5,
                'policies': [
                    {
                        'type': 'carbon_tax',
                        'rate': 50
                    },
                    {
                        'type': 'quota',
                        'penalty_rate': 100
                    }
                ],
                'price_changes': []
            }
        },
        {
            'id': 5,
            'name': '能源价格波动影响',
            'description': '模拟能源价格上涨15%对企业成本的影响',
            'config': {
                'time_range': 3,
                'policies': [],
                'price_changes': [
                    {
                        'type': 'energy',
                        'change': 15
                    }
                ]
            }
        }
    ]
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': templates
    })
