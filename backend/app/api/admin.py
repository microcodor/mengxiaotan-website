from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from app.api import admin_bp
from app.models import User, Article, Source, CrawlLog, BroadcastTask, OperationLog
from app.schemas import ArticleSchema, UserSchema
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc

def admin_required():
    """管理员权限装饰器"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user

@admin_bp.route('/dashboard')
class Dashboard(MethodView):
    @jwt_required()
    def get(self):
        """获取仪表盘数据"""
        admin_required()
        
        # 统计数据
        total_users = User.query.count()
        total_articles = Article.query.count()
        today_articles = Article.query.filter(
            Article.created_at >= datetime.utcnow().date()
        ).count()
        
        # 近7天文章趋势
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        articles_trend = db.session.query(
            func.date(Article.created_at).label('date'),
            func.count(Article.id).label('count')
        ).filter(Article.created_at >= seven_days_ago)\
         .group_by(func.date(Article.created_at))\
         .all()
        
        # 分类统计
        category_stats = db.session.query(
            Article.category,
            func.count(Article.id).label('count')
        ).group_by(Article.category).all()
        
        # 抓取状态
        crawl_status = db.session.query(
            Source.name,
            Source.status,
            Source.last_crawl_at
        ).all()
        
        return {
            'total_users': total_users,
            'total_articles': total_articles,
            'today_articles': today_articles,
            'articles_trend': [{'date': str(t.date), 'count': t.count} for t in articles_trend],
            'category_stats': [{'category': c.category, 'count': c.count} for c in category_stats],
            'crawl_status': [{'name': s.name, 'status': s.status, 'last_crawl': s.last_crawl_at} for s in crawl_status]
        }

@admin_bp.route('/articles')
class AdminArticleList(MethodView):
    @jwt_required()
    def get(self):
        """获取所有文章（含未审核）- 支持分页、搜索、筛选"""
        admin_required()
        
        from flask import request
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()  # reviewed, pending
        
        # 构建查询
        query = Article.query
        
        # 关键词搜索（标题或内容）
        if keyword:
            query = query.filter(
                or_(
                    Article.title.like(f'%{keyword}%'),
                    Article.content.like(f'%{keyword}%')
                )
            )
        
        # 分类筛选
        if category:
            query = query.filter_by(category=category)
        
        # 状态筛选
        if status == 'reviewed':
            query = query.filter_by(is_reviewed=True)
        elif status == 'pending':
            query = query.filter_by(is_reviewed=False)
        
        # 分页
        pagination = query.order_by(desc(Article.created_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        items = []
        for article in pagination.items:
            items.append({
                'id': article.id,
                'title': article.title,
                'summary': article.summary,
                'source': article.source,
                'category': article.category,
                'is_reviewed': article.is_reviewed,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'created_at': article.created_at.isoformat()
            })
        
        return {
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }


@admin_bp.route('/articles/batch-review')
class AdminArticleBatchReview(MethodView):
    @jwt_required()
    def post(self):
        """批量审核文章"""
        user = admin_required()
        
        from flask import request
        
        data = request.get_json() or {}
        ids = data.get('ids', [])
        
        if not ids:
            abort(400, message='请选择要审核的文章')
        
        # 批量更新
        Article.query.filter(Article.id.in_(ids)).update(
            {'is_reviewed': True},
            synchronize_session=False
        )
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='batch_review_articles',
            module='article',
            details={'count': len(ids), 'ids': ids}
        )
        db.session.add(log)
        db.session.commit()
        
        return {'message': f'已审核 {len(ids)} 篇文章'}


@admin_bp.route('/articles/batch-delete')
class AdminArticleBatchDelete(MethodView):
    @jwt_required()
    def post(self):
        """批量删除文章"""
        user = admin_required()
        
        from flask import request
        
        data = request.get_json() or {}
        ids = data.get('ids', [])
        
        if not ids:
            abort(400, message='请选择要删除的文章')
        
        # 批量删除
        deleted_count = Article.query.filter(Article.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='batch_delete_articles',
            module='article',
            details={'count': deleted_count, 'ids': ids}
        )
        db.session.add(log)
        db.session.commit()
        
        return {'message': f'已删除 {deleted_count} 篇文章'}

@admin_bp.route('/articles/<int:article_id>')
class AdminArticleDetail(MethodView):
    @jwt_required()
    @admin_bp.arguments(ArticleSchema(partial=True))
    @admin_bp.response(200, ArticleSchema)
    def put(self, data, article_id):
        """更新文章"""
        user = admin_required()
        article = Article.query.get_or_404(article_id)
        
        for key, value in data.items():
            if hasattr(article, key):
                setattr(article, key, value)
        
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='update_article',
            module='article',
            target_id=article_id,
            details={'fields': list(data.keys())}
        )
        db.session.add(log)
        db.session.commit()
        
        return article
    
    @jwt_required()
    def delete(self, article_id):
        """删除文章"""
        user = admin_required()
        article = Article.query.get_or_404(article_id)
        
        db.session.delete(article)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='delete_article',
            module='article',
            target_id=article_id
        )
        db.session.add(log)
        db.session.commit()
        
        return {'message': '删除成功'}

@admin_bp.route('/articles/<int:article_id>/review')
class ArticleReview(MethodView):
    @jwt_required()
    def post(self, article_id):
        """审核文章"""
        user = admin_required()
        article = Article.query.get_or_404(article_id)
        
        article.is_reviewed = True
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='review_article',
            module='article',
            target_id=article_id
        )
        db.session.add(log)
        db.session.commit()
        
        return {'message': '审核通过'}

@admin_bp.route('/users')
class AdminUserList(MethodView):
    @jwt_required()
    @admin_bp.response(200, UserSchema(many=True))
    def get(self):
        """获取用户列表"""
        admin_required()
        
        users = User.query.order_by(desc(User.created_at)).limit(100).all()
        return users


@admin_bp.route('/daily-brief')
class AdminDailyBrief(MethodView):
    @jwt_required()
    def get(self):
        """获取今日简报"""
        admin_required()
        
        from app.models import DailyBrief
        from datetime import date
        
        today = date.today()
        brief = DailyBrief.query.filter_by(brief_date=today).first()
        
        if brief:
            return {
                'brief_date': str(brief.brief_date),
                'content': brief.content,
                'ai_suggestion': brief.ai_suggestion,
                'generated_at': brief.generated_at.isoformat()
            }
        
        return {'message': '今日简报尚未生成'}, 404
    
    @jwt_required()
    def post(self):
        """生成今日简报"""
        admin_required()
        
        from app.models import DailyBrief
        from app.services.ai_service import ai_service
        from datetime import date
        
        # 获取今日文章
        today = datetime.utcnow().date()
        articles = Article.query.filter(
            func.date(Article.published_at) == today,
            Article.is_reviewed == True
        ).order_by(desc(Article.published_at)).limit(50).all()
        
        if not articles:
            abort(400, message='今日暂无文章')
        
        # 转换为字典格式
        articles_data = [
            {
                'title': a.title,
                'summary': a.summary,
                'category': a.category,
                'source': a.source
            }
            for a in articles
        ]
        
        # 生成简报
        brief_data = ai_service.generate_daily_brief(articles_data)
        
        if not brief_data:
            abort(500, message='简报生成失败')
        
        # 保存到数据库
        today_date = date.today()
        existing = DailyBrief.query.filter_by(brief_date=today_date).first()
        if existing:
            existing.content = brief_data['content']
            existing.ai_suggestion = brief_data['ai_suggestion']
            existing.generated_at = datetime.utcnow()
        else:
            brief = DailyBrief(
                brief_date=today_date,
                content=brief_data['content'],
                ai_suggestion=brief_data['ai_suggestion']
            )
            db.session.add(brief)
        
        db.session.commit()
        
        return {
            'message': '简报生成成功',
            'brief': brief_data
        }

@admin_bp.route('/sources')
class AdminSourceList(MethodView):
    @jwt_required()
    def get(self):
        """获取所有数据源"""
        admin_required()
        
        sources = Source.query.order_by(Source.priority, Source.name).all()
        
        return {
            'items': [
                {
                    'id': s.id,
                    'name': s.name,
                    'url': s.url,
                    'type': s.type,
                    'priority': s.priority,
                    'status': s.status,
                    'last_crawl_at': s.last_crawl_at.isoformat() if s.last_crawl_at else None,
                    'error_msg': s.error_msg
                }
                for s in sources
            ]
        }

@admin_bp.route('/crawl-logs')
class AdminCrawlLogs(MethodView):
    @jwt_required()
    def get(self):
        """获取抓取日志"""
        admin_required()
        
        logs = CrawlLog.query.order_by(desc(CrawlLog.started_at)).limit(50).all()
        
        return {
            'items': [
                {
                    'id': log.id,
                    'source_id': log.source_id,
                    'status': log.status,
                    'articles_count': log.articles_count,
                    'error_msg': log.error_msg,
                    'started_at': log.started_at.isoformat() if log.started_at else None,
                    'finished_at': log.finished_at.isoformat() if log.finished_at else None
                }
                for log in logs
            ]
        }

@admin_bp.route('/orders')
class AdminOrderList(MethodView):
    @jwt_required()
    def get(self):
        """获取所有订单"""
        admin_required()
        
        from app.models import Order
        from flask import request
        
        status = request.args.get('status')
        query = Order.query
        
        if status:
            query = query.filter_by(payment_status=status)
        
        orders = query.order_by(desc(Order.created_at)).all()
        
        return {
            'items': [
                {
                    'id': o.id,
                    'order_no': o.order_no,
                    'user_id': o.user_id,
                    'user': {
                        'id': o.user.id,
                        'phone': o.user.phone,
                        'nickname': o.user.nickname
                    } if o.user else None,
                    'plan': {
                        'id': o.plan.id,
                        'name': o.plan.name,
                        'price': str(o.plan.price)
                    } if o.plan else None,
                    'amount': str(o.amount),
                    'payment_method': o.payment_method,
                    'payment_status': o.payment_status,
                    'payment_time': o.payment_time.isoformat() if o.payment_time else None,
                    'payment_proof': o.payment_proof,
                    'contact_info': o.contact_info,
                    'remark': o.remark,
                    'admin_note': o.admin_note,
                    'confirmed_at': o.confirmed_at.isoformat() if o.confirmed_at else None,
                    'created_at': o.created_at.isoformat()
                }
                for o in orders
            ]
        }

@admin_bp.route('/orders/<int:order_id>/confirm')
class AdminOrderConfirm(MethodView):
    @jwt_required()
    def post(self, order_id):
        """确认订单支付"""
        user = admin_required()
        
        from app.models import Order, Subscription
        
        order = Order.query.get_or_404(order_id)
        
        if order.payment_status != 'pending':
            abort(400, message='订单状态不允许确认')
        
        # 更新订单状态
        order.payment_status = 'paid'
        order.payment_time = datetime.utcnow()
        order.confirmed_by = user.id
        order.confirmed_at = datetime.utcnow()
        
        # 创建订阅
        plan = order.plan
        
        # 检查用户是否已有活跃订阅
        existing = Subscription.query.filter_by(
            user_id=order.user_id, 
            status='active'
        ).first()
        
        if existing and existing.end_date > datetime.utcnow():
            # 从现有订阅结束时间开始
            start_date = existing.end_date
        else:
            start_date = datetime.utcnow()
        
        end_date = start_date + timedelta(days=plan.duration_days)
        
        subscription = Subscription(
            user_id=order.user_id,
            plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        db.session.add(subscription)
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='confirm_order',
            module='order',
            target_id=order_id,
            details={'order_no': order.order_no}
        )
        db.session.add(log)
        
        db.session.commit()
        
        return {'message': '订单确认成功'}

@admin_bp.route('/orders/<int:order_id>/reject')
class AdminOrderReject(MethodView):
    @jwt_required()
    def post(self, order_id):
        """拒绝订单"""
        user = admin_required()
        
        from app.models import Order
        from flask import request
        
        order = Order.query.get_or_404(order_id)
        
        if order.payment_status != 'pending':
            abort(400, message='订单状态不允许拒绝')
        
        data = request.get_json() or {}
        admin_note = data.get('admin_note', '')
        
        order.payment_status = 'cancelled'
        order.admin_note = admin_note
        
        # 记录操作日志
        log = OperationLog(
            user_id=user.id,
            action='reject_order',
            module='order',
            target_id=order_id,
            details={'order_no': order.order_no, 'reason': admin_note}
        )
        db.session.add(log)
        
        db.session.commit()
        
        return {'message': '订单已拒绝'}


@admin_bp.route('/refunds')
class AdminRefundList(MethodView):
    @jwt_required()
    def get(self):
        """获取退款申请列表"""
        user = admin_required()
        
        from app.services.refund_processor import RefundProcessor
        from flask import request
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')  # pending, approved, rejected
        
        processor = RefundProcessor()
        
        # 如果指定了状态过滤
        if status:
            from app.models import RefundApplication
            query = RefundApplication.query.filter_by(status=status).order_by(
                RefundApplication.applied_at.desc()
            )
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            applications = []
            for app in pagination.items:
                applications.append({
                    'id': app.id,
                    'order_id': app.order_id,
                    'order_no': app.order.order_no,
                    'user_id': app.user_id,
                    'user_phone': app.user.phone,
                    'amount': float(app.order.amount),
                    'reason': app.reason,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'processed_at': app.processed_at.isoformat() if app.processed_at else None,
                    'processed_by': app.processed_by,
                    'reject_reason': app.reject_reason,
                    'plan_name': app.order.plan.name if app.order.plan else None
                })
            
            return {
                'items': applications,
                'total': pagination.total,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'pages': pagination.pages
            }
        else:
            # 默认返回待处理的申请
            result = processor.get_pending_applications(page=page, per_page=per_page)
            return {
                'items': result['applications'],
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'pages': result['pages']
            }


@admin_bp.route('/refunds/<int:application_id>')
class AdminRefundDetail(MethodView):
    @jwt_required()
    def get(self, application_id):
        """获取退款申请详情"""
        user = admin_required()
        
        from app.models import RefundApplication
        
        application = RefundApplication.query.get_or_404(application_id)
        
        return {
            'id': application.id,
            'order_id': application.order_id,
            'order': {
                'id': application.order.id,
                'order_no': application.order.order_no,
                'amount': float(application.order.amount),
                'payment_method': application.order.payment_method,
                'payment_status': application.order.payment_status,
                'payment_proof': application.order.payment_proof,
                'payment_info': application.order.payment_info,
                'created_at': application.order.created_at.isoformat()
            },
            'user': {
                'id': application.user.id,
                'phone': application.user.phone,
                'nickname': application.user.nickname
            },
            'plan': {
                'id': application.order.plan.id,
                'name': application.order.plan.name,
                'price': float(application.order.plan.price)
            } if application.order.plan else None,
            'reason': application.reason,
            'status': application.status,
            'applied_at': application.applied_at.isoformat() if application.applied_at else None,
            'processed_by': application.processed_by,
            'processed_at': application.processed_at.isoformat() if application.processed_at else None,
            'reject_reason': application.reject_reason,
            'processor': {
                'id': application.processor.id,
                'nickname': application.processor.nickname
            } if application.processor else None
        }


@admin_bp.route('/refunds/<int:application_id>/approve')
class AdminRefundApprove(MethodView):
    @jwt_required()
    def post(self, application_id):
        """批准退款申请"""
        user = admin_required()
        
        from app.services.refund_processor import RefundProcessor
        
        processor = RefundProcessor()
        
        try:
            success = processor.approve_refund(application_id, user.id)
            
            if success:
                # 记录操作日志
                log = OperationLog(
                    user_id=user.id,
                    action='approve_refund',
                    module='refund',
                    target_id=application_id,
                    details={'application_id': application_id}
                )
                db.session.add(log)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': '退款申请已批准'
                }
            else:
                abort(500, message='批准退款失败')
                
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=f'批准退款失败: {str(e)}')


@admin_bp.route('/refunds/<int:application_id>/reject')
class AdminRefundReject(MethodView):
    @jwt_required()
    def post(self, application_id):
        """拒绝退款申请"""
        user = admin_required()
        
        from app.services.refund_processor import RefundProcessor
        from flask import request
        
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        if not reason:
            abort(400, message='拒绝原因不能为空')
        
        processor = RefundProcessor()
        
        try:
            success = processor.reject_refund(application_id, user.id, reason)
            
            if success:
                # 记录操作日志
                log = OperationLog(
                    user_id=user.id,
                    action='reject_refund',
                    module='refund',
                    target_id=application_id,
                    details={'application_id': application_id, 'reason': reason}
                )
                db.session.add(log)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': '退款申请已拒绝'
                }
            else:
                abort(500, message='拒绝退款失败')
                
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=f'拒绝退款失败: {str(e)}')
