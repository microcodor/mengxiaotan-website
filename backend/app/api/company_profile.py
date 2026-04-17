# -*- coding: utf-8 -*-
"""
企业画像API
"""
from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import company_profile_bp
from app.models import Company, User
from app.services.company_profile_service import CompanyProfileService
from app import db
import logging

logger = logging.getLogger(__name__)


@company_profile_bp.route('/<int:company_id>')
class CompanyProfileDetail(MethodView):
    @jwt_required()
    def get(self, company_id):
        """
        获取企业画像
        
        需要基础版或更高订阅
        """
        from app.services.subscription_service import SubscriptionService
        
        user_id = int(get_jwt_identity())
        
        # 检查订阅权限
        status = SubscriptionService.get_user_subscription_status(user_id)
        if not status['has_subscription']:
            return jsonify({
                'success': False,
                'error': '需要订阅基础版才能使用企业画像功能'
            }), 403
        
        # 检查是否是试用版
        if status.get('is_trial'):
            return jsonify({
                'success': False,
                'error': '企业画像功能仅限基础版用户，请升级订阅'
            }), 403
        
        # 检查企业是否存在
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'error': '企业不存在'
            }), 404
        
        # 检查权限（只能查看自己公司的画像）
        user = User.query.get(user_id)
        if user.company_id != company_id and user.role != 'admin':
            return jsonify({
                'success': False,
                'error': '无权查看该企业画像'
            }), 403
        
        try:
            # 生成企业画像
            service = CompanyProfileService()
            profile = service.build_company_profile(company_id)
            
            # 生成摘要
            summary = service.get_profile_summary(profile)
            profile['summary'] = summary
            
            return jsonify({
                'success': True,
                'data': profile
            }), 200
            
        except Exception as e:
            logger.error(f"生成企业画像失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'生成企业画像失败: {str(e)}'
            }), 500


@company_profile_bp.route('/<int:company_id>/summary')
class CompanyProfileSummary(MethodView):
    @jwt_required()
    def get(self, company_id):
        """
        获取企业画像摘要（快速预览）
        """
        from app.services.subscription_service import SubscriptionService
        
        user_id = int(get_jwt_identity())
        
        # 检查订阅权限
        status = SubscriptionService.get_user_subscription_status(user_id)
        if not status['has_subscription']:
            return jsonify({
                'success': False,
                'error': '需要订阅基础版才能使用企业画像功能'
            }), 403
        
        if status.get('is_trial'):
            return jsonify({
                'success': False,
                'error': '企业画像功能仅限基础版用户，请升级订阅'
            }), 403
        
        # 检查企业是否存在
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'error': '企业不存在'
            }), 404
        
        # 检查权限
        user = User.query.get(user_id)
        if user.company_id != company_id and user.role != 'admin':
            return jsonify({
                'success': False,
                'error': '无权查看该企业画像'
            }), 403
        
        try:
            # 生成企业画像
            service = CompanyProfileService()
            profile = service.build_company_profile(company_id)
            
            # 只返回摘要信息
            summary_data = {
                'company_id': profile['company_id'],
                'company_name': profile['company_name'],
                'overall_score': profile['overall_score'],
                'risk_level': profile['risks']['overall_risk_level'],
                'opportunity_level': profile['opportunities']['overall_opportunity_level'],
                'strengths_count': len(profile['competitiveness']['strengths']),
                'risks_count': (
                    len(profile['risks']['environmental_risks']) +
                    len(profile['risks']['capacity_risks']) +
                    len(profile['risks']['policy_risks']) +
                    len(profile['risks']['market_risks'])
                ),
                'opportunities_count': (
                    len(profile['opportunities']['policy_opportunities']) +
                    len(profile['opportunities']['market_opportunities']) +
                    len(profile['opportunities']['technology_opportunities'])
                ),
                'summary': service.get_profile_summary(profile)
            }
            
            return jsonify({
                'success': True,
                'data': summary_data
            }), 200
            
        except Exception as e:
            logger.error(f"生成企业画像摘要失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'生成企业画像摘要失败: {str(e)}'
            }), 500


@company_profile_bp.route('/<int:company_id>/export')
class CompanyProfileExport(MethodView):
    @jwt_required()
    def get(self, company_id):
        """
        导出企业画像报告（PDF/Word）
        """
        from app.services.subscription_service import SubscriptionService
        
        user_id = int(get_jwt_identity())
        
        # 检查订阅权限
        status = SubscriptionService.get_user_subscription_status(user_id)
        if not status['has_subscription']:
            return jsonify({
                'success': False,
                'error': '需要订阅基础版才能使用企业画像功能'
            }), 403
        
        if status.get('is_trial'):
            return jsonify({
                'success': False,
                'error': '企业画像功能仅限基础版用户，请升级订阅'
            }), 403
        
        # 检查企业是否存在
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'error': '企业不存在'
            }), 404
        
        # 检查权限
        user = User.query.get(user_id)
        if user.company_id != company_id and user.role != 'admin':
            return jsonify({
                'success': False,
                'error': '无权导出该企业画像'
            }), 403
        
        # 获取导出格式
        export_format = request.args.get('format', 'json')  # json, pdf, word
        
        try:
            # 生成企业画像
            service = CompanyProfileService()
            profile = service.build_company_profile(company_id)
            
            if export_format == 'json':
                # JSON格式直接返回
                return jsonify({
                    'success': True,
                    'data': profile,
                    'format': 'json'
                }), 200
            
            elif export_format == 'pdf':
                # TODO: 实现PDF导出
                return jsonify({
                    'success': False,
                    'error': 'PDF导出功能开发中'
                }), 501
            
            elif export_format == 'word':
                # TODO: 实现Word导出
                return jsonify({
                    'success': False,
                    'error': 'Word导出功能开发中'
                }), 501
            
            else:
                return jsonify({
                    'success': False,
                    'error': '不支持的导出格式'
                }), 400
            
        except Exception as e:
            logger.error(f"导出企业画像失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'导出企业画像失败: {str(e)}'
            }), 500
