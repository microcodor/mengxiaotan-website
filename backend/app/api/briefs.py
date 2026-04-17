"""
AI简报相关API
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from app import db
from app.models import DailyBrief, User
from app.services.ai_brief_generator import AIBriefGenerator
from app.api import briefs_bp as bp
from config import Config
import logging

logger = logging.getLogger(__name__)


def require_admin():
    """检查管理员权限"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': '权限不足'}), 403
    return None


@bp.route('', methods=['GET'])
@jwt_required()
def get_briefs():
    """
    获取简报列表
    
    Query参数:
    - page: 页码（默认1）
    - per_page: 每页数量（默认10）
    - start_date: 开始日期（可选）
    - end_date: 结束日期（可选）
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = DailyBrief.query
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(DailyBrief.brief_date >= start)
            except ValueError:
                return jsonify({'error': '开始日期格式错误，应为YYYY-MM-DD'}), 400
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(DailyBrief.brief_date <= end)
            except ValueError:
                return jsonify({'error': '结束日期格式错误，应为YYYY-MM-DD'}), 400
        
        # 按日期降序排序
        query = query.order_by(DailyBrief.brief_date.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        briefs = []
        for brief in pagination.items:
            briefs.append({
                'id': brief.id,
                'brief_date': brief.brief_date.strftime('%Y-%m-%d'),
                'content': brief.content,
                'ai_suggestion': brief.ai_suggestion,
                'generated_at': brief.generated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'data': {
                'briefs': briefs,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取简报列表失败: {e}")
        return jsonify({'error': '获取简报列表失败'}), 500


@bp.route('/<string:brief_date>', methods=['GET'])
@jwt_required()
def get_brief_by_date(brief_date):
    """
    获取指定日期的简报
    
    Path参数:
    - brief_date: 日期（格式: YYYY-MM-DD）
    """
    try:
        # 解析日期
        try:
            target_date = datetime.strptime(brief_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式错误，应为YYYY-MM-DD'}), 400
        
        # 查询简报
        brief = DailyBrief.query.filter_by(brief_date=target_date).first()
        
        if not brief:
            return jsonify({'error': '简报不存在'}), 404
        
        # 检查用户订阅等级，决定是否返回AI建议
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        from app.models import Subscription, SubscriptionPlan
        subscription = Subscription.query.join(SubscriptionPlan).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active',
            Subscription.end_date > datetime.utcnow()
        ).first()
        
        include_suggestion = False
        if subscription and subscription.plan.name == '高级版':
            include_suggestion = True
        
        response_data = {
            'id': brief.id,
            'brief_date': brief.brief_date.strftime('%Y-%m-%d'),
            'content': brief.content,
            'generated_at': brief.generated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 只有高级版用户才返回AI建议
        if include_suggestion:
            response_data['ai_suggestion'] = brief.ai_suggestion
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"获取简报失败: {e}")
        return jsonify({'error': '获取简报失败'}), 500


@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_brief():
    """
    手动生成简报（管理员功能）
    
    Body参数:
    - date: 日期（可选，默认为昨天，格式: YYYY-MM-DD）
    """
    # 检查管理员权限
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        data = request.get_json() or {}
        target_date_str = data.get('date')
        
        # 解析日期
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '日期格式错误，应为YYYY-MM-DD'}), 400
        else:
            # 默认为昨天
            target_date = date.today() - timedelta(days=1)
        
        # 初始化生成器
        generator = AIBriefGenerator(
            api_key=Config.MINIMAX_API_KEY,
            group_id=Config.MINIMAX_GROUP_ID,
            api_url=Config.MINIMAX_API_URL
        )
        
        # 生成简报
        result = generator.generate_daily_brief(target_date)
        
        if not result:
            return jsonify({'error': '简报生成失败，请稍后重试'}), 500
        
        # 推送简报
        push_result = generator.push_brief_to_users(result['brief_id'])
        
        return jsonify({
            'success': True,
            'data': {
                'brief_id': result['brief_id'],
                'brief_date': target_date.strftime('%Y-%m-%d'),
                'status': result['status'],
                'generated_at': result['generated_at'].strftime('%Y-%m-%d %H:%M:%S'),
                'push_result': push_result
            },
            'message': '简报生成成功'
        })
        
    except Exception as e:
        logger.error(f"生成简报失败: {e}")
        return jsonify({'error': f'生成简报失败: {str(e)}'}), 500


@bp.route('/preview', methods=['POST'])
@jwt_required()
def preview_brief():
    """
    预览简报（管理员功能）
    不保存到数据库，仅返回生成的内容
    
    Body参数:
    - date: 日期（可选，默认为昨天，格式: YYYY-MM-DD）
    """
    # 检查管理员权限
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        data = request.get_json() or {}
        target_date_str = data.get('date')
        
        # 解析日期
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '日期格式错误，应为YYYY-MM-DD'}), 400
        else:
            # 默认为昨天
            target_date = date.today() - timedelta(days=1)
        
        # 初始化生成器
        generator = AIBriefGenerator(
            api_key=Config.MINIMAX_API_KEY,
            group_id=Config.MINIMAX_GROUP_ID,
            api_url=Config.MINIMAX_API_URL
        )
        
        # 收集文章
        articles = generator.collect_articles(target_date, limit=30)
        
        if not articles:
            return jsonify({'error': f'没有找到 {target_date} 的文章'}), 404
        
        # 构造Prompt
        prompt = generator._build_prompt(articles)
        
        # 调用API
        ai_response = generator.call_minimax_api(prompt)
        
        if not ai_response:
            return jsonify({'error': 'AI生成失败'}), 500
        
        # 格式化内容
        brief_content = generator.format_brief_content(articles, ai_response)
        ai_suggestion = generator._extract_ai_suggestion(ai_response)
        
        return jsonify({
            'success': True,
            'data': {
                'brief_date': target_date.strftime('%Y-%m-%d'),
                'content': brief_content,
                'ai_suggestion': ai_suggestion,
                'article_count': len(articles)
            },
            'message': '简报预览生成成功'
        })
        
    except Exception as e:
        logger.error(f"预览简报失败: {e}")
        return jsonify({'error': f'预览简报失败: {str(e)}'}), 500


@bp.route('/latest', methods=['GET'])
@jwt_required()
def get_latest_brief():
    """获取最新的简报"""
    try:
        brief = DailyBrief.query.order_by(DailyBrief.brief_date.desc()).first()
        
        if not brief:
            return jsonify({'error': '暂无简报'}), 404
        
        # 检查用户订阅等级
        user_id = get_jwt_identity()
        from app.models import Subscription, SubscriptionPlan
        subscription = Subscription.query.join(SubscriptionPlan).filter(
            Subscription.user_id == user_id,
            Subscription.status == 'active',
            Subscription.end_date > datetime.utcnow()
        ).first()
        
        include_suggestion = False
        if subscription and subscription.plan.name == '高级版':
            include_suggestion = True
        
        response_data = {
            'id': brief.id,
            'brief_date': brief.brief_date.strftime('%Y-%m-%d'),
            'content': brief.content,
            'generated_at': brief.generated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if include_suggestion:
            response_data['ai_suggestion'] = brief.ai_suggestion
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"获取最新简报失败: {e}")
        return jsonify({'error': '获取最新简报失败'}), 500
