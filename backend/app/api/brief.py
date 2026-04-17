# -*- coding: utf-8 -*-
"""
简报API
"""
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_smorest import abort
from flask import request
from app.api import api_bp
from app.models import DailyBrief, User, Subscription, SubscriptionPlan
from app import db
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


@api_bp.route('/briefs')
class BriefList(MethodView):
    @jwt_required()
    def get(self):
        """获取简报列表"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='用户不存在')
        
        # 获取用户订阅等级
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # 确定用户版本
        version = 'standard'
        include_suggestion = False
        
        if subscription and subscription.plan:
            plan_name = subscription.plan.name.lower()
            if '高级' in plan_name or 'premium' in plan_name:
                version = 'premium'
                include_suggestion = True
        
        # 获取最近30天的简报
        thirty_days_ago = date.today() - timedelta(days=30)
        briefs = DailyBrief.query.filter(
            DailyBrief.brief_date >= thirty_days_ago
        ).order_by(DailyBrief.brief_date.desc()).all()
        
        return {
            'items': [brief.to_dict(version=version, include_suggestion=include_suggestion) for brief in briefs],
            'total': len(briefs),
            'user_version': version
        }


@api_bp.route('/briefs/<string:share_token>')
class BriefDetail(MethodView):
    def get(self, share_token):
        """通过分享token获取简报详情（公开访问）"""
        # 查找简报
        brief = DailyBrief.query.filter_by(share_token=share_token).first()
        
        if not brief:
            abort(404, message='简报不存在')
        
        # 获取版本参数
        version = request.args.get('v', 'standard')
        
        # 验证版本权限（如果有JWT token）
        include_suggestion = False
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            
            if user_id:
                user_id = int(user_id)
                subscription = Subscription.query.filter_by(
                    user_id=user_id,
                    status='active'
                ).first()
                
                if subscription and subscription.plan:
                    plan_name = subscription.plan.name.lower()
                    if '高级' in plan_name or 'premium' in plan_name:
                        include_suggestion = True
                        version = 'premium'
        except Exception as e:
            logger.debug(f"JWT验证失败（可选）: {e}")
        
        # 增加浏览次数
        brief.view_count += 1
        db.session.commit()
        
        return brief.to_dict(version=version, include_suggestion=include_suggestion)


@api_bp.route('/briefs/<string:share_token>/share')
class BriefShare(MethodView):
    def post(self, share_token):
        """记录分享次数"""
        brief = DailyBrief.query.filter_by(share_token=share_token).first()
        
        if not brief:
            abort(404, message='简报不存在')
        
        # 增加分享次数
        brief.share_count += 1
        db.session.commit()
        
        return {'message': '分享成功', 'share_count': brief.share_count}


@api_bp.route('/briefs/today')
class TodayBrief(MethodView):
    @jwt_required()
    def get(self):
        """获取今日简报"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='用户不存在')
        
        # 获取用户订阅等级
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # 确定用户版本
        version = 'standard'
        include_suggestion = False
        
        if subscription and subscription.plan:
            plan_name = subscription.plan.name.lower()
            if '高级' in plan_name or 'premium' in plan_name:
                version = 'premium'
                include_suggestion = True
        
        # 获取今日简报
        today = date.today()
        brief = DailyBrief.query.filter_by(brief_date=today).first()
        
        if not brief:
            # 尝试获取最近一天的简报
            brief = DailyBrief.query.order_by(DailyBrief.brief_date.desc()).first()
            
            if not brief:
                abort(404, message='暂无简报')
        
        return brief.to_dict(version=version, include_suggestion=include_suggestion)


@api_bp.route('/briefs/date/<string:brief_date>')
class BriefByDate(MethodView):
    @jwt_required()
    def get(self, brief_date):
        """根据日期获取简报"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='用户不存在')
        
        # 获取用户订阅等级
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # 确定用户版本
        version = 'standard'
        include_suggestion = False
        
        if subscription and subscription.plan:
            plan_name = subscription.plan.name.lower()
            if '高级' in plan_name or 'premium' in plan_name:
                version = 'premium'
                include_suggestion = True
        
        # 解析日期
        try:
            target_date = datetime.strptime(brief_date, '%Y-%m-%d').date()
        except ValueError:
            abort(400, message='日期格式错误，应为 YYYY-MM-DD')
        
        # 获取指定日期的简报
        brief = DailyBrief.query.filter_by(brief_date=target_date).first()
        
        if not brief:
            abort(404, message='该日期的简报不存在')
        
        return brief.to_dict(version=version, include_suggestion=include_suggestion)
