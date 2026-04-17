from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import subscriptions_bp
from app.models import SubscriptionPlan, Subscription, Order, User
from app.schemas import SubscriptionPlanSchema, SubscriptionSchema, OrderSchema
from app.services.payment_proof_manager import PaymentProofManager
from app import db
from datetime import datetime, timedelta
import uuid

@subscriptions_bp.route('/plans')
class SubscriptionPlanList(MethodView):
    @subscriptions_bp.response(200, SubscriptionPlanSchema(many=True))
    def get(self):
        """获取订阅套餐列表"""
        plans = SubscriptionPlan.query.filter_by(is_active=True)\
            .order_by(SubscriptionPlan.sort_order).all()
        return plans

@subscriptions_bp.route('/my')
class MySubscription(MethodView):
    @jwt_required()
    @subscriptions_bp.response(200, SubscriptionSchema)
    def get(self):
        """获取我的订阅"""
        user_id = int(get_jwt_identity())
        subscription = Subscription.query.filter_by(user_id=user_id, status='active')\
            .order_by(Subscription.end_date.desc()).first()
        
        if not subscription:
            return {'message': '暂无订阅'}, 404
        
        return subscription


@subscriptions_bp.route('/status')
class SubscriptionStatus(MethodView):
    @jwt_required()
    def get(self):
        """获取用户订阅状态（包括试用资格）"""
        from app.services.subscription_service import SubscriptionService
        from flask import jsonify
        
        user_id = int(get_jwt_identity())
        status = SubscriptionService.get_user_subscription_status(user_id)
        
        return jsonify({
            'success': True,
            'data': status
        }), 200

@subscriptions_bp.route('/subscribe')
class Subscribe(MethodView):
    @jwt_required()
    @subscriptions_bp.arguments(SubscriptionSchema)
    @subscriptions_bp.response(201, SubscriptionSchema)
    def post(self, data):
        """创建订阅"""
        from app.services.subscription_service import SubscriptionService
        
        user_id = int(get_jwt_identity())
        plan = SubscriptionPlan.query.get_or_404(data['plan_id'])
        
        # 获取支付周期（如果有）
        payment_cycle = data.get('payment_cycle', 'monthly')
        
        try:
            # 如果是免费试用
            if plan.name == '免费订阅':
                result = SubscriptionService.create_trial_subscription(user_id)
            else:
                # 付费订阅
                result = SubscriptionService.create_paid_subscription(
                    user_id=user_id,
                    plan_id=plan.id,
                    payment_cycle=payment_cycle
                )
            
            # 返回创建的订阅
            subscription = Subscription.query.get(result['subscription_id'])
            return subscription
            
        except ValueError as e:
            return {'message': str(e)}, 400

@subscriptions_bp.route('/<int:subscription_id>/settings')
class SubscriptionSettings(MethodView):
    @jwt_required()
    @subscriptions_bp.arguments(SubscriptionSchema(partial=True))
    @subscriptions_bp.response(200, SubscriptionSchema)
    def put(self, data, subscription_id):
        """更新订阅设置"""
        user_id = int(get_jwt_identity())
        subscription = Subscription.query.filter_by(id=subscription_id, user_id=user_id).first_or_404()
        
        if 'push_channels' in data:
            subscription.push_channels = data['push_channels']
        if 'custom_keywords' in data:
            subscription.custom_keywords = data['custom_keywords']
        if 'auto_renew' in data:
            subscription.auto_renew = data['auto_renew']
        
        db.session.commit()
        return subscription

@subscriptions_bp.route('/orders')
class OrderList(MethodView):
    @jwt_required()
    @subscriptions_bp.response(200, OrderSchema(many=True))
    def get(self):
        """获取我的订单列表"""
        user_id = int(get_jwt_identity())
        orders = Order.query.filter_by(user_id=user_id)\
            .order_by(Order.created_at.desc()).all()
        return orders
    
    @jwt_required()
    @subscriptions_bp.arguments(OrderSchema)
    @subscriptions_bp.response(201, OrderSchema)
    def post(self, data):
        """创建订单"""
        from app.services.subscription_service import SubscriptionService
        
        user_id = int(get_jwt_identity())
        plan = SubscriptionPlan.query.get_or_404(data['plan_id'])
        
        # 获取支付周期
        payment_cycle = 'monthly'
        if 'remark' in data and data['remark']:
            if '年付' in data['remark']:
                payment_cycle = 'yearly'
        
        # 计算实际金额和时长
        try:
            actual_amount = SubscriptionService.calculate_order_amount(plan.id, payment_cycle)
            actual_duration = SubscriptionService.calculate_duration_days(plan.id, payment_cycle)
        except ValueError as e:
            return {'message': str(e)}, 400
        
        # 生成订单号
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        
        order = Order(
            order_no=order_no,
            user_id=user_id,
            plan_id=plan.id,
            amount=actual_amount,
            payment_method=data['payment_method'],
            contact_info=data.get('contact_info'),
            remark=data.get('remark')
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 如果是免费试用，自动创建订阅
        if plan.name == '免费订阅':
            try:
                SubscriptionService.create_trial_subscription(user_id)
                # 更新订单状态为已支付（免费）
                order.payment_status = 'paid'
                order.payment_time = datetime.utcnow()
                db.session.commit()
            except ValueError as e:
                # 如果已经试用过，返回错误但订单已创建
                pass
        
        return order

@subscriptions_bp.route('/orders/<int:order_id>')
class OrderDetail(MethodView):
    @jwt_required()
    @subscriptions_bp.response(200, OrderSchema)
    def get(self, order_id):
        """获取订单详情"""
        user_id = int(get_jwt_identity())
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        return order
    
    @jwt_required()
    @subscriptions_bp.arguments(OrderSchema(partial=True))
    @subscriptions_bp.response(200, OrderSchema)
    def put(self, data, order_id):
        """更新订单（上传支付凭证）"""
        user_id = int(get_jwt_identity())
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        if order.payment_status != 'pending':
            return {'message': '订单状态不允许修改'}, 400
        
        if 'payment_proof' in data:
            order.payment_proof = data['payment_proof']
        if 'contact_info' in data:
            order.contact_info = data['contact_info']
        if 'remark' in data:
            order.remark = data['remark']
        
        db.session.commit()
        return order

@subscriptions_bp.route('/orders/<int:order_id>/cancel')
class OrderCancel(MethodView):
    @jwt_required()
    @subscriptions_bp.response(200, OrderSchema)
    def post(self, order_id):
        """取消订单"""
        user_id = int(get_jwt_identity())
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        if order.payment_status != 'pending':
            return {'message': '订单状态不允许取消'}, 400
        
        order.payment_status = 'cancelled'
        db.session.commit()
        
        return order


@subscriptions_bp.route('/orders/<int:order_id>/payment-proof')
class OrderPaymentProof(MethodView):
    @jwt_required()
    def post(self, order_id):
        """上传支付凭证"""
        user_id = int(get_jwt_identity())
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        # 检查订单状态
        if order.payment_status != 'pending':
            return jsonify({
                'success': False,
                'error': '订单状态不允许上传支付凭证'
            }), 400
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        
        file = request.files['file']
        
        # 使用 PaymentProofManager 处理上传
        manager = PaymentProofManager()
        result = manager.upload_proof(file, order_id)
        
        if result['success']:
            # 更新订单的支付凭证字段
            order.payment_proof = result['file_url']
            
            # 如果有OCR结果，存储到payment_info字段
            if 'ocr_result' in result and result['ocr_result']:
                order.payment_info = result['ocr_result']
            
            db.session.commit()
            
            response_data = {
                'success': True,
                'data': {
                    'file_url': result['file_url'],
                    'order_id': order_id
                },
                'message': '支付凭证上传成功'
            }
            
            # 如果有OCR结果，添加到响应中
            if 'ocr_result' in result:
                response_data['data']['ocr_result'] = result['ocr_result']
            
            return jsonify(response_data), 200
        else:
            return jsonify(result), 400
    
    @jwt_required()
    def get(self, order_id):
        """获取支付凭证 - 仅订单所有者和管理员可访问"""
        user_id = int(get_jwt_identity())
        
        # 获取当前用户信息
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        # 获取订单
        order = Order.query.get_or_404(order_id)
        
        # 权限验证：仅订单所有者和管理员可访问
        is_owner = order.user_id == user_id
        is_admin = current_user.role == 'admin'
        
        if not (is_owner or is_admin):
            return jsonify({
                'success': False,
                'error': '无权访问该订单的支付凭证'
            }), 403
        
        if not order.payment_proof:
            return jsonify({
                'success': False,
                'error': '该订单暂无支付凭证'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'file_url': order.payment_proof,
                'order_id': order_id,
                'payment_info': order.payment_info  # 包含OCR提取的信息
            }
        }), 200
    
    @jwt_required()
    def delete(self, order_id):
        """删除支付凭证"""
        user_id = int(get_jwt_identity())
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        # 检查订单状态
        if order.payment_status != 'pending':
            return jsonify({
                'success': False,
                'error': '订单状态不允许删除支付凭证'
            }), 400
        
        if not order.payment_proof:
            return jsonify({
                'success': False,
                'error': '该订单暂无支付凭证'
            }), 404
        
        # 删除支付凭证
        order.payment_proof = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '支付凭证已删除'
        }), 200


@subscriptions_bp.route('/orders/<int:order_id>/payment-proof/download')
class OrderPaymentProofDownload(MethodView):
    @jwt_required()
    def get(self, order_id):
        """下载支付凭证文件 - 仅订单所有者和管理员可访问"""
        from flask import send_from_directory, current_app
        import os
        
        user_id = int(get_jwt_identity())
        
        # 获取当前用户信息
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        # 获取订单
        order = Order.query.get_or_404(order_id)
        
        # 权限验证：仅订单所有者和管理员可访问
        is_owner = order.user_id == user_id
        is_admin = current_user.role == 'admin'
        
        if not (is_owner or is_admin):
            return jsonify({
                'success': False,
                'error': '无权访问该订单的支付凭证'
            }), 403
        
        if not order.payment_proof:
            return jsonify({
                'success': False,
                'error': '该订单暂无支付凭证'
            }), 404
        
        # 解析文件路径
        # payment_proof格式: /uploads/payment_proofs/{year}/{month}/{filename}
        file_url = order.payment_proof
        if file_url.startswith('/'):
            file_url = file_url[1:]  # 移除开头的斜杠
        
        # 构建完整文件路径
        file_path = os.path.join(current_app.root_path, '..', file_url)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '支付凭证文件不存在'
            }), 404
        
        # 获取文件所在目录和文件名
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        # 发送文件
        return send_from_directory(
            directory,
            filename,
            as_attachment=True,
            download_name=f"payment_proof_{order_id}_{filename}"
        )


@subscriptions_bp.route('/keywords')
class KeywordManagement(MethodView):
    @jwt_required()
    def get(self):
        """获取用户关键词"""
        user_id = int(get_jwt_identity())
        
        # 获取用户的活跃订阅
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': '没有活跃订阅'
            }), 404
        
        # 检查订阅等级（仅高级版支持关键词定制）
        plan = subscription.plan
        if plan.name not in ['高级版', 'Premium']:
            return jsonify({
                'success': False,
                'error': '关键词定制功能仅限高级版用户',
                'current_plan': plan.name
            }), 403
        
        keywords = subscription.custom_keywords or []
        
        return jsonify({
            'success': True,
            'data': {
                'keywords': keywords,
                'count': len(keywords),
                'max_allowed': 20
            }
        }), 200
    
    @jwt_required()
    def put(self):
        """更新用户关键词"""
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'keywords' not in data:
            return jsonify({
                'success': False,
                'error': '缺少 keywords 字段'
            }), 400
        
        keywords = data['keywords']
        
        # 验证关键词列表
        if not isinstance(keywords, list):
            return jsonify({
                'success': False,
                'error': 'keywords 必须是数组'
            }), 400
        
        # 验证关键词数量（最多20个）
        if len(keywords) > 20:
            return jsonify({
                'success': False,
                'error': '关键词数量不能超过20个',
                'current_count': len(keywords),
                'max_allowed': 20
            }), 400
        
        # 验证每个关键词长度
        for keyword in keywords:
            if not isinstance(keyword, str) or len(keyword) == 0:
                return jsonify({
                    'success': False,
                    'error': '关键词必须是非空字符串'
                }), 400
            if len(keyword) > 50:
                return jsonify({
                    'success': False,
                    'error': f'关键词 "{keyword}" 长度超过50个字符'
                }), 400
        
        # 获取用户的活跃订阅
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).first()
        
        if not subscription:
            return jsonify({
                'success': False,
                'error': '没有活跃订阅'
            }), 404
        
        # 检查订阅等级（仅高级版支持关键词定制）
        plan = subscription.plan
        if plan.name not in ['高级版', 'Premium']:
            return jsonify({
                'success': False,
                'error': '关键词定制功能仅限高级版用户',
                'current_plan': plan.name
            }), 403
        
        # 更新关键词
        subscription.custom_keywords = keywords
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'keywords': keywords,
                'count': len(keywords),
                'max_allowed': 20
            },
            'message': '关键词更新成功'
        }), 200


@subscriptions_bp.route('/test-keywords')
class TestKeywords(MethodView):
    @jwt_required()
    def post(self):
        """测试关键词匹配"""
        from app.services.keyword_push_engine import KeywordPushEngine
        from app.models import Article
        
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'keywords' not in data:
            return jsonify({
                'success': False,
                'error': '缺少 keywords 字段'
            }), 400
        
        keywords = data['keywords']
        
        if not isinstance(keywords, list) or len(keywords) == 0:
            return jsonify({
                'success': False,
                'error': 'keywords 必须是非空数组'
            }), 400
        
        # 获取最近的文章进行测试（最近7天）
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        articles = Article.query.filter(
            Article.published_at >= week_ago,
            Article.is_reviewed == True
        ).limit(100).all()
        
        if not articles:
            return jsonify({
                'success': False,
                'error': '没有可用的文章进行测试'
            }), 404
        
        # 使用关键词推送引擎匹配文章
        engine = KeywordPushEngine()
        matched_articles = engine.match_articles(keywords, articles)
        
        # 构造响应数据
        result_articles = []
        for article in matched_articles[:10]:  # 只返回前10篇
            score = engine.calculate_relevance_score(article, keywords)
            result_articles.append({
                'id': article.id,
                'title': article.title,
                'summary': article.summary[:100] if article.summary else '',
                'category': article.category,
                'source': article.source,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'relevance_score': round(score, 3)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'keywords': keywords,
                'total_articles': len(articles),
                'matched_count': len(matched_articles),
                'sample_articles': result_articles
            },
            'message': f'找到 {len(matched_articles)} 篇匹配文章'
        }), 200


@subscriptions_bp.route('/refunds')
class RefundApplicationList(MethodView):
    @jwt_required()
    def get(self):
        """获取我的退款申请列表"""
        user_id = int(get_jwt_identity())
        
        from app.models import RefundApplication
        
        applications = RefundApplication.query.filter_by(user_id=user_id)\
            .order_by(RefundApplication.applied_at.desc()).all()
        
        result = []
        for app in applications:
            result.append({
                'id': app.id,
                'order_id': app.order_id,
                'order_no': app.order.order_no,
                'amount': float(app.order.amount),
                'reason': app.reason,
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'processed_at': app.processed_at.isoformat() if app.processed_at else None,
                'reject_reason': app.reject_reason,
                'plan_name': app.order.plan.name if app.order.plan else None
            })
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
    
    @jwt_required()
    def post(self):
        """创建退款申请"""
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'order_id' not in data:
            return jsonify({
                'success': False,
                'error': '缺少 order_id 字段'
            }), 400
        
        if 'reason' not in data or not data['reason']:
            return jsonify({
                'success': False,
                'error': '退款原因不能为空'
            }), 400
        
        order_id = data['order_id']
        reason = data['reason']
        
        from app.services.refund_processor import RefundProcessor
        
        processor = RefundProcessor()
        
        try:
            result = processor.create_refund_application(order_id, user_id, reason)
            
            return jsonify({
                'success': True,
                'data': result,
                'message': '退款申请已提交'
            }), 201
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'创建退款申请失败: {str(e)}'
            }), 500


@subscriptions_bp.route('/refunds/<int:application_id>')
class RefundApplicationDetail(MethodView):
    @jwt_required()
    def get(self, application_id):
        """获取退款申请详情"""
        user_id = int(get_jwt_identity())
        
        from app.models import RefundApplication
        
        application = RefundApplication.query.filter_by(
            id=application_id,
            user_id=user_id
        ).first()
        
        if not application:
            return jsonify({
                'success': False,
                'error': '退款申请不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': application.id,
                'order_id': application.order_id,
                'order_no': application.order.order_no,
                'amount': float(application.order.amount),
                'reason': application.reason,
                'status': application.status,
                'applied_at': application.applied_at.isoformat() if application.applied_at else None,
                'processed_at': application.processed_at.isoformat() if application.processed_at else None,
                'reject_reason': application.reject_reason,
                'plan_name': application.order.plan.name if application.order.plan else None
            }
        }), 200
