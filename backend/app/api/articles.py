from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.api import articles_bp
from app.models import Article, UserFavorite, UserHistory
from app.schemas import ArticleSchema, ArticleListQuerySchema
from app import db
from sqlalchemy import or_, desc

@articles_bp.route('/')
class ArticleList(MethodView):
    @articles_bp.arguments(ArticleListQuerySchema, location='query')
    def get(self, query_args):
        """获取文章列表"""
        page = query_args.get('page', 1)
        per_page = query_args.get('per_page', 20)
        
        query = Article.query.filter_by(is_reviewed=True)
        
        # 分类筛选
        if query_args.get('category'):
            query = query.filter_by(category=query_args['category'])
        
        # 关键词搜索
        if query_args.get('keyword'):
            keyword = f"%{query_args['keyword']}%"
            query = query.filter(
                or_(
                    Article.title.like(keyword),
                    Article.summary.like(keyword),
                    Article.content.like(keyword)
                )
            )
        
        # 日期范围
        if query_args.get('start_date'):
            query = query.filter(Article.published_at >= query_args['start_date'])
        if query_args.get('end_date'):
            query = query.filter(Article.published_at <= query_args['end_date'])
        
        # 排序：优先按创建时间倒序（最新的在前），置顶文章不影响时间排序
        query = query.order_by(desc(Article.created_at))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 获取分类映射
        from app.models import Category
        categories = {cat.code: cat.name for cat in Category.query.all()}
        
        # 为每篇文章添加分类中文名
        items = []
        for article in pagination.items:
            # 安全处理 datetime 字段（可能已经是字符串）
            def safe_isoformat(dt):
                if dt is None:
                    return None
                if isinstance(dt, str):
                    return dt
                return dt.isoformat()
            
            article_dict = {
                'id': article.id,
                'title': article.title,
                'summary': article.summary,
                'content': article.content,
                'cover_image': article.cover_image,
                'source': article.source,
                'source_url': article.source_url,
                'category': article.category,
                'category_name': categories.get(article.category, article.category),
                'tags': article.tags,
                'view_count': article.view_count,
                'like_count': article.like_count,
                'is_top': article.is_top,
                'is_carousel': article.is_carousel,
                'published_at': safe_isoformat(article.published_at),
                'created_at': safe_isoformat(article.created_at)
            }
            items.append(article_dict)
        
        return {
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }, 200

@articles_bp.route('/<int:article_id>')
class ArticleDetail(MethodView):
    def get(self, article_id):
        """获取文章详情"""
        article = Article.query.get_or_404(article_id)
        
        # 增加浏览量（处理 None 值）
        if article.view_count is None:
            article.view_count = 0
        article.view_count += 1
        db.session.commit()
        
        # 记录浏览历史（如果已登录）
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                history = UserHistory(user_id=int(user_id), article_id=article_id)
                db.session.add(history)
                db.session.commit()
        except:
            pass
        
        # 获取分类中文名
        from app.models import Category
        category = Category.query.filter_by(code=article.category).first()
        category_name = category.name if category else article.category
        
        # 安全处理 datetime 字段（可能已经是字符串）
        def safe_isoformat(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            return dt.isoformat()
        
        return {
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'content': article.content,
            'cover_image': article.cover_image,
            'source': article.source,
            'source_url': article.source_url,
            'category': article.category,
            'category_name': category_name,
            'tags': article.tags,
            'view_count': article.view_count or 0,
            'like_count': article.like_count or 0,
            'is_top': article.is_top,
            'is_carousel': article.is_carousel,
            'published_at': safe_isoformat(article.published_at),
            'created_at': safe_isoformat(article.created_at),
            'updated_at': safe_isoformat(article.updated_at)
        }, 200

@articles_bp.route('/carousel')
class CarouselArticles(MethodView):
    def get(self):
        """获取轮播文章（焦点资讯）- 返回最新的5篇文章"""
        articles = Article.query.filter_by(is_reviewed=True)\
            .order_by(desc(Article.created_at)).limit(5).all()
        
        # 获取分类映射
        from app.models import Category
        categories = {cat.code: cat.name for cat in Category.query.all()}
        
        # 安全处理 datetime 字段
        def safe_isoformat(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            return dt.isoformat()
        
        result = []
        for article in articles:
            result.append({
                'id': article.id,
                'title': article.title,
                'summary': article.summary,
                'content': article.content,
                'cover_image': article.cover_image,
                'source': article.source,
                'source_url': article.source_url,
                'category': article.category,
                'category_name': categories.get(article.category, article.category),
                'tags': article.tags,
                'view_count': article.view_count,
                'like_count': article.like_count,
                'is_top': article.is_top,
                'is_carousel': article.is_carousel,
                'published_at': safe_isoformat(article.published_at),
                'created_at': safe_isoformat(article.created_at),
                'updated_at': safe_isoformat(article.updated_at)
            })
        
        return result, 200

@articles_bp.route('/top')
class TopArticles(MethodView):
    def get(self):
        """获取置顶文章"""
        articles = Article.query.filter_by(is_top=True, is_reviewed=True)\
            .order_by(desc(Article.published_at)).limit(10).all()
        
        # 获取分类映射
        from app.models import Category
        categories = {cat.code: cat.name for cat in Category.query.all()}
        
        # 安全处理 datetime 字段
        def safe_isoformat(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            return dt.isoformat()
        
        result = []
        for article in articles:
            result.append({
                'id': article.id,
                'title': article.title,
                'summary': article.summary,
                'content': article.content,
                'cover_image': article.cover_image,
                'source': article.source,
                'source_url': article.source_url,
                'category': article.category,
                'category_name': categories.get(article.category, article.category),
                'tags': article.tags,
                'view_count': article.view_count,
                'like_count': article.like_count,
                'is_top': article.is_top,
                'is_carousel': article.is_carousel,
                'published_at': safe_isoformat(article.published_at),
                'created_at': safe_isoformat(article.created_at),
                'updated_at': safe_isoformat(article.updated_at)
            })
        
        return result, 200

@articles_bp.route('/<int:article_id>/favorite')
class ArticleFavorite(MethodView):
    @jwt_required()
    def post(self, article_id):
        """收藏文章"""
        user_id = int(get_jwt_identity())
        article = Article.query.get_or_404(article_id)
        
        existing = UserFavorite.query.filter_by(user_id=user_id, article_id=article_id).first()
        if existing:
            abort(400, message='已收藏该文章')
        
        favorite = UserFavorite(user_id=user_id, article_id=article_id)
        db.session.add(favorite)
        db.session.commit()
        
        return {'message': '收藏成功'}
    
    @jwt_required()
    def delete(self, article_id):
        """取消收藏"""
        user_id = int(get_jwt_identity())
        favorite = UserFavorite.query.filter_by(user_id=user_id, article_id=article_id).first_or_404()
        
        db.session.delete(favorite)
        db.session.commit()
        
        return {'message': '取消收藏成功'}


@articles_bp.route('/daily-brief')
class DailyBriefView(MethodView):
    def get(self):
        """获取今日简报（公开接口）"""
        from app.models import DailyBrief
        from datetime import date
        
        today = date.today()
        brief = DailyBrief.query.filter_by(brief_date=today).first()
        
        if not brief:
            # 如果今日简报不存在，返回默认内容
            from app.services.ai_service import ai_service
            return {
                'brief_date': str(today),
                'ai_suggestion': ai_service._mock_response('一句话建议'),
                'content': {}
            }
        
        return {
            'brief_date': str(brief.brief_date),
            'content': brief.content,
            'ai_suggestion': brief.ai_suggestion,
            'generated_at': brief.generated_at.isoformat()
        }
