from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from flask import request
from app.api import push_bp
from app.models import User, BroadcastTask, BroadcastLog, Subscription
from app import db
from datetime import datetime
from app.services.push_service import push_manager


def admin_required():
    """管理员权限装饰器"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user


@push_bp.route('/test')
class PushTest(MethodView):
    @jwt_required()
    def post(self):
        """测试推送"""
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        content = data.get('content', '这是一条测试消息')
        message_type = data.get('message_type', 'text')
        
        # 发送测试推送
        results = push_manager.send_to_user(
            user_id,
            content,
            channels=['wechat_work'],
            message_type=message_type,
            title=data.get('title', '测试推送'),
            url=data.get('url', '')
        )
        
        return {
            'message': '测试推送已发送',
            'results': results
        }


@push_bp.route('/broadcast')
class BroadcastCreate(MethodView):
    @jwt_required()
    def post(self):
        """创建推送任务"""
        user = admin_required()
        data = request.get_json() or {}
        
        title = data.get('title')
        content = data.get('content')
        target_type = data.get('target_type', 'all')  # all, plan, custom
        target_ids = data.get('target_ids', [])
        channel = data.get('channel', 'enterprise_wechat')
        scheduled_at = data.get('scheduled_at')
        
        if not title or not content:
            abort(400, message='标题和内容不能为空')
        
        # 创建推送任务
        task = BroadcastTask(
            title=title,
            content=content,
            target_type=target_type,
            target_ids=target_ids,
            channel=channel,
            scheduled_at=datetime.fromisoformat(scheduled_at) if scheduled_at else None,
            status='pending',
            created_by=user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 如果是立即发送，执行推送
        if not scheduled_at:
            self._execute_broadcast(task)
        
        return {
            'message': '推送任务创建成功',
            'task_id': task.id,
            'status': task.status
        }
    
    def _execute_broadcast(self, task: BroadcastTask):
        """执行推送任务"""
        # 获取目标用户
        user_ids = self._get_target_users(task)
        
        if not user_ids:
            task.status = 'failed'
            db.session.commit()
            return
        
        # 更新任务状态
        task.status = 'sending'
        db.session.commit()
        
        # 发送推送
        results = push_manager.send_to_users(
            user_ids,
            task.content,
            channels=['wechat_work'],
            message_type='text',
            title=task.title
        )
        
        # 记录推送日志
        for user_id in user_ids:
            log = BroadcastLog(
                task_id=task.id,
                user_id=user_id,
                channel='enterprise_wechat',
                content=task.content,
                status='sent',
                sent_at=datetime.utcnow()
            )
            db.session.add(log)
        
        # 更新任务状态
        task.status = 'completed'
        db.session.commit()
    
    def _get_target_users(self, task: BroadcastTask) -> list:
        """获取目标用户列表"""
        if task.target_type == 'all':
            # 所有活跃订阅用户
            subscriptions = Subscription.query.filter(
                Subscription.status == 'active',
                Subscription.end_date > datetime.utcnow()
            ).all()
            return [sub.user_id for sub in subscriptions]
        
        elif task.target_type == 'plan':
            # 指定套餐的用户
            subscriptions = Subscription.query.filter(
                Subscription.status == 'active',
                Subscription.end_date > datetime.utcnow(),
                Subscription.plan_id.in_(task.target_ids)
            ).all()
            return [sub.user_id for sub in subscriptions]
        
        elif task.target_type == 'custom':
            # 自定义用户列表
            return task.target_ids
        
        return []


@push_bp.route('/broadcast/<int:task_id>')
class BroadcastDetail(MethodView):
    @jwt_required()
    def get(self, task_id):
        """获取推送任务详情"""
        admin_required()
        
        task = BroadcastTask.query.get_or_404(task_id)
        
        # 获取推送日志
        logs = BroadcastLog.query.filter_by(task_id=task_id).all()
        
        return {
            'id': task.id,
            'title': task.title,
            'content': task.content,
            'target_type': task.target_type,
            'target_ids': task.target_ids,
            'channel': task.channel,
            'status': task.status,
            'scheduled_at': task.scheduled_at.isoformat() if task.scheduled_at else None,
            'created_at': task.created_at.isoformat(),
            'logs': [
                {
                    'user_id': log.user_id,
                    'status': log.status,
                    'sent_at': log.sent_at.isoformat() if log.sent_at else None,
                    'read_at': log.read_at.isoformat() if log.read_at else None,
                    'error_msg': log.error_msg
                }
                for log in logs
            ]
        }


@push_bp.route('/broadcast/list')
class BroadcastList(MethodView):
    @jwt_required()
    def get(self):
        """获取推送任务列表"""
        admin_required()
        
        tasks = BroadcastTask.query.order_by(BroadcastTask.created_at.desc()).limit(50).all()
        
        return {
            'items': [
                {
                    'id': task.id,
                    'title': task.title,
                    'target_type': task.target_type,
                    'channel': task.channel,
                    'status': task.status,
                    'scheduled_at': task.scheduled_at.isoformat() if task.scheduled_at else None,
                    'created_at': task.created_at.isoformat()
                }
                for task in tasks
            ]
        }


@push_bp.route('/daily-brief')
class DailyBriefPush(MethodView):
    @jwt_required()
    def post(self):
        """推送每日简报"""
        admin_required()
        
        from app.models import DailyBrief
        from datetime import date
        
        # 获取今日简报
        today = date.today()
        brief = DailyBrief.query.filter_by(brief_date=today).first()
        
        if not brief:
            abort(404, message='今日简报尚未生成')
        
        # 发送推送
        results = push_manager.send_daily_brief({
            'content': brief.content,
            'ai_suggestion': brief.ai_suggestion
        })
        
        return results


@push_bp.route('/article/<int:article_id>')
class ArticlePush(MethodView):
    @jwt_required()
    def post(self, article_id):
        """推送文章"""
        admin_required()
        
        data = request.get_json() or {}
        user_ids = data.get('user_ids')  # 可选，不指定则发送给所有用户
        
        results = push_manager.send_article_notification(article_id, user_ids)
        
        return results


@push_bp.route('/settings')
class PushSettings(MethodView):
    @jwt_required()
    def get(self):
        """获取推送设置"""
        user_id = int(get_jwt_identity())
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            return {
                'push_channels': {},
                'custom_keywords': []
            }
        
        return {
            'push_channels': subscription.push_channels or {},
            'custom_keywords': subscription.custom_keywords or []
        }
    
    @jwt_required()
    def put(self):
        """更新推送设置"""
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not subscription:
            abort(404, message='未找到活跃订阅')
        
        if 'push_channels' in data:
            subscription.push_channels = data['push_channels']
        
        if 'custom_keywords' in data:
            subscription.custom_keywords = data['custom_keywords']
        
        db.session.commit()
        
        return {
            'message': '推送设置已更新',
            'push_channels': subscription.push_channels,
            'custom_keywords': subscription.custom_keywords
        }


@push_bp.route('/settings/admin/user/<int:target_user_id>')
class AdminUserPushSettings(MethodView):
    @jwt_required()
    def get(self, target_user_id):
        """管理员获取指定用户的推送设置"""
        admin_required()
        
        user = User.query.get_or_404(target_user_id)
        
        # 获取用户的活跃订阅
        subscription = Subscription.query.filter_by(
            user_id=target_user_id,
            status='active'
        ).first()
        
        # 确定订阅等级
        subscription_level = 'free'
        if subscription and subscription.plan:
            plan_name = subscription.plan.name.lower()
            if '高级' in plan_name or 'premium' in plan_name:
                subscription_level = 'premium'
            elif '基础' in plan_name or 'standard' in plan_name:
                subscription_level = 'standard'
        
        # 根据订阅等级确定允许的推送渠道
        allowed_channels = ['enterprise_wechat']  # 所有用户都支持企业微信
        if subscription_level in ['standard', 'premium']:
            allowed_channels.extend(['dingtalk', 'feishu', 'email'])
        if subscription_level == 'premium':
            allowed_channels.append('sms')
        
        return {
            'user_id': user.id,
            'username': user.phone or user.nickname or f'用户{user.id}',
            'company_name': user.company_name,
            'subscription_level': subscription_level,
            'allowed_channels': allowed_channels,
            'configured_channels': subscription.push_channels if subscription else {}
        }
    
    @jwt_required()
    def put(self, target_user_id):
        """管理员更新指定用户的推送设置"""
        admin_required()
        
        user = User.query.get_or_404(target_user_id)
        data = request.get_json() or {}
        
        # 获取或创建订阅记录
        subscription = Subscription.query.filter_by(
            user_id=target_user_id,
            status='active'
        ).first()
        
        if not subscription:
            # 如果没有活跃订阅，创建一个免费订阅
            from app.models import SubscriptionPlan
            from datetime import timedelta
            
            free_plan = SubscriptionPlan.query.filter_by(name='免费订阅').first()
            if not free_plan:
                abort(400, message='用户没有活跃订阅，且系统未配置免费订阅套餐')
            
            subscription = Subscription(
                user_id=target_user_id,
                plan_id=free_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db.session.add(subscription)
        
        # 更新推送渠道配置
        push_channels = {}
        for channel in ['enterprise_wechat', 'dingtalk', 'feishu', 'email', 'sms']:
            if channel in data and data[channel]:
                push_channels[channel] = data[channel].strip()
        
        subscription.push_channels = push_channels
        db.session.commit()
        
        return {
            'message': '推送设置已更新',
            'configured_channels': push_channels
        }


@push_bp.route('/settings/admin/user/<int:target_user_id>/test')
class AdminUserPushTest(MethodView):
    @jwt_required()
    def post(self, target_user_id):
        """管理员测试指定用户的推送"""
        admin_required()
        
        user = User.query.get_or_404(target_user_id)
        data = request.get_json() or {}
        
        channel = data.get('channel')
        message = data.get('message', '这是一条测试消息')
        
        if not channel:
            abort(400, message='请指定推送渠道')
        
        # 检查用户是否配置了该渠道
        subscription = Subscription.query.filter_by(
            user_id=target_user_id,
            status='active'
        ).first()
        
        if not subscription or not subscription.push_channels:
            abort(400, message='用户未配置推送渠道')
        
        if channel not in subscription.push_channels:
            abort(400, message=f'用户未配置{channel}渠道')
        
        # 发送测试推送
        channel_map = {
            'enterprise_wechat': 'wechat_work',
            'dingtalk': 'dingtalk',
            'feishu': 'feishu',
            'email': 'email',
            'sms': 'sms'
        }
        
        service_name = channel_map.get(channel)
        if not service_name:
            abort(400, message='不支持的推送渠道')
        
        try:
            result = push_manager.send_to_user(
                target_user_id,
                f"【测试消息】\n\n{message}\n\n发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                channels=[service_name],
                message_type='text'
            )
            
            success = result.get(service_name, False)
            
            return {
                'success': success,
                'message': '测试推送已发送' if success else '测试推送发送失败',
                'channel': channel
            }
        except Exception as e:
            logger.error(f"测试推送失败: {str(e)}")
            return {
                'success': False,
                'message': f'测试推送失败: {str(e)}'
            }, 500
