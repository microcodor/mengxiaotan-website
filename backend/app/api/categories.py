"""
分类管理 API
"""
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from flask import request
from app.api import categories_bp
from app.models import Category, User, Article
from app import db
from sqlalchemy import func


def admin_required():
    """管理员权限装饰器"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user


@categories_bp.route('/')
class CategoryList(MethodView):
    def get(self):
        """获取分类列表（公开接口）"""
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        query = Category.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        categories = query.order_by(Category.sort_order, Category.id).all()
        
        # 统计每个分类的文章数
        result = []
        for cat in categories:
            article_count = Article.query.filter_by(category=cat.code, is_reviewed=True).count()
            result.append({
                'id': cat.id,
                'code': cat.code,
                'name': cat.name,
                'description': cat.description,
                'icon': cat.icon,
                'sort_order': cat.sort_order,
                'is_active': cat.is_active,
                'article_count': article_count,
                'created_at': cat.created_at.isoformat(),
                'updated_at': cat.updated_at.isoformat()
            })
        
        return {'items': result}
    
    @jwt_required()
    def post(self):
        """创建分类"""
        admin_required()
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('code') or not data.get('name'):
            abort(400, message='分类代码和名称不能为空')
        
        # 检查代码是否已存在
        existing = Category.query.filter_by(code=data['code']).first()
        if existing:
            abort(400, message='分类代码已存在')
        
        category = Category(
            code=data['code'],
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon'),
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return {
            'id': category.id,
            'code': category.code,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'sort_order': category.sort_order,
            'is_active': category.is_active,
            'message': '分类创建成功'
        }, 201


@categories_bp.route('/<int:category_id>')
class CategoryDetail(MethodView):
    def get(self, category_id):
        """获取分类详情"""
        category = Category.query.get_or_404(category_id)
        
        # 统计文章数
        article_count = Article.query.filter_by(category=category.code, is_reviewed=True).count()
        
        return {
            'id': category.id,
            'code': category.code,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'sort_order': category.sort_order,
            'is_active': category.is_active,
            'article_count': article_count,
            'created_at': category.created_at.isoformat(),
            'updated_at': category.updated_at.isoformat()
        }
    
    @jwt_required()
    def put(self, category_id):
        """更新分类"""
        admin_required()
        
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        # 如果修改代码，检查是否重复
        if data.get('code') and data['code'] != category.code:
            existing = Category.query.filter_by(code=data['code']).first()
            if existing:
                abort(400, message='分类代码已存在')
            category.code = data['code']
        
        if data.get('name'):
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'icon' in data:
            category.icon = data['icon']
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        db.session.commit()
        
        return {
            'id': category.id,
            'code': category.code,
            'name': category.name,
            'message': '分类更新成功'
        }
    
    @jwt_required()
    def delete(self, category_id):
        """删除分类"""
        admin_required()
        
        category = Category.query.get_or_404(category_id)
        
        # 检查是否有文章使用该分类
        article_count = Article.query.filter_by(category=category.code).count()
        if article_count > 0:
            abort(400, message=f'该分类下还有 {article_count} 篇文章，无法删除')
        
        db.session.delete(category)
        db.session.commit()
        
        return {'message': '分类删除成功'}


@categories_bp.route('/stats')
class CategoryStats(MethodView):
    @jwt_required()
    def get(self):
        """获取分类统计信息"""
        admin_required()
        
        # 按分类统计文章数
        stats = db.session.query(
            Article.category,
            func.count(Article.id).label('total'),
            func.sum(func.cast(Article.is_reviewed, db.Integer)).label('reviewed')
        ).group_by(Article.category).all()
        
        # 获取分类信息
        categories = {cat.code: cat.name for cat in Category.query.all()}
        
        result = []
        for category_code, total, reviewed in stats:
            result.append({
                'code': category_code,
                'name': categories.get(category_code, category_code),
                'total': total,
                'reviewed': reviewed or 0,
                'pending': total - (reviewed or 0)
            })
        
        return {'items': result}


# 注册蓝图时不需要再次导入api，因为已经在__init__.py中注册了
