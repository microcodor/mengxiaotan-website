from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from flask_smorest import abort
from app.api import users_bp
from app.models import User, UserFavorite, UserHistory, Article, Company
from app.schemas import UserSchema, ArticleSchema
from app import db

@users_bp.route('/profile')
class UserProfile(MethodView):
    @jwt_required()
    def get(self):
        """获取用户资料"""
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        
        # 获取企业信息
        company = None
        if user.company_id:
            comp = Company.query.get(user.company_id)
            if comp:
                company = {
                    'id': comp.id,
                    'name': comp.name,
                    'short_name': comp.short_name
                }
        
        return {
            'id': user.id,
            'phone': user.phone,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'role': user.role,
            'status': user.status,
            'position': user.position,
            'company': company,
            'created_at': user.created_at.isoformat()
        }
    
    @jwt_required()
    def put(self):
        """更新用户资料"""
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        
        if 'nickname' in data:
            user.nickname = data['nickname']
        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'position' in data:
            user.position = data['position']
        
        db.session.commit()
        
        return {'message': '资料更新成功'}

@users_bp.route('/favorites')
class UserFavorites(MethodView):
    @jwt_required()
    @users_bp.response(200, ArticleSchema(many=True))
    def get(self):
        """获取用户收藏"""
        user_id = int(get_jwt_identity())
        favorites = UserFavorite.query.filter_by(user_id=user_id)\
            .order_by(UserFavorite.created_at.desc()).all()
        
        article_ids = [f.article_id for f in favorites]
        articles = Article.query.filter(Article.id.in_(article_ids)).all()
        
        return articles

@users_bp.route('/history')
class UserHistoryView(MethodView):
    @jwt_required()
    @users_bp.response(200, ArticleSchema(many=True))
    def get(self):
        """获取浏览历史"""
        user_id = int(get_jwt_identity())
        history = UserHistory.query.filter_by(user_id=user_id)\
            .order_by(UserHistory.created_at.desc()).limit(50).all()
        
        article_ids = [h.article_id for h in history]
        articles = Article.query.filter(Article.id.in_(article_ids)).all()
        
        # 按历史记录顺序排序
        article_dict = {a.id: a for a in articles}
        sorted_articles = [article_dict[aid] for aid in article_ids if aid in article_dict]
        
        return sorted_articles
