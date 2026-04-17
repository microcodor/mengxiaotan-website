"""
退款处理器 (RefundProcessor)

处理退款申请的创建、审批和状态管理功能。
"""

from datetime import datetime
from typing import Dict, Optional
from flask import current_app
from app import db
from app.models import Order, RefundApplication, Subscription


class RefundProcessor:
    """退款处理器"""
    
    def create_refund_application(self, order_id: int, user_id: int, reason: str) -> Dict:
        """
        创建退款申请
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            reason: 退款原因
            
        Returns:
            {
                'application_id': int,
                'status': str,
                'created_at': datetime
            }
            
        Raises:
            ValueError: 当订单不存在、不属于用户、状态不是paid或已有待处理退款申请时
        """
        # 验证订单存在
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"订单不存在: {order_id}")
        
        # 验证订单属于该用户
        if order.user_id != user_id:
            raise ValueError(f"订单不属于该用户: order_id={order_id}, user_id={user_id}")
        
        # 验证订单状态为 paid
        if order.payment_status != 'paid':
            raise ValueError(f"订单状态必须为已支付才能申请退款，当前状态: {order.payment_status}")
        
        # 检查是否已有待处理的退款申请
        existing_application = RefundApplication.query.filter_by(
            order_id=order_id,
            status='pending'
        ).first()
        
        if existing_application:
            raise ValueError(f"该订单已有待处理的退款申请: application_id={existing_application.id}")
        
        try:
            # 使用数据库事务确保原子性
            # 创建退款申请记录
            application = RefundApplication(
                order_id=order_id,
                user_id=user_id,
                reason=reason,
                status='pending',
                applied_at=datetime.utcnow()
            )
            db.session.add(application)
            
            # 更新订单状态为 refund_pending
            order.payment_status = 'refund_pending'
            order.refund_reason = reason
            order.refund_status = 'pending'
            order.refund_applied_at = datetime.utcnow()
            
            # 提交事务
            db.session.commit()
            
            current_app.logger.info(
                f"退款申请创建成功: application_id={application.id}, "
                f"order_id={order_id}, user_id={user_id}"
            )
            
            # 发送通知
            self.notify_user(application.id, 'pending')
            
            return {
                'application_id': application.id,
                'status': application.status,
                'created_at': application.created_at
            }
            
        except Exception as e:
            # 回滚事务
            db.session.rollback()
            current_app.logger.error(f"创建退款申请失败: {str(e)}")
            raise ValueError(f"创建退款申请失败: {str(e)}")
    
    def approve_refund(self, application_id: int, admin_id: int) -> bool:
        """
        批准退款申请
        
        Args:
            application_id: 退款申请ID
            admin_id: 管理员ID
            
        Returns:
            是否成功
            
        Raises:
            ValueError: 当申请不存在或状态不是pending时
        """
        application = RefundApplication.query.get(application_id)
        if not application:
            raise ValueError(f"退款申请不存在: {application_id}")
        
        if application.status != 'pending':
            raise ValueError(f"退款申请状态必须为待处理，当前状态: {application.status}")
        
        try:
            # 更新退款申请状态
            application.status = 'approved'
            application.processed_by = admin_id
            application.processed_at = datetime.utcnow()
            
            # 更新订单状态
            order = application.order
            order.payment_status = 'refunded'
            order.refund_status = 'approved'
            order.refund_processed_at = datetime.utcnow()
            order.refund_processed_by = admin_id
            
            # 更新关联的订阅状态为 cancelled
            subscription = Subscription.query.filter_by(
                user_id=application.user_id,
                plan_id=order.plan_id,
                status='active'
            ).first()
            
            if subscription:
                subscription.status = 'cancelled'
                current_app.logger.info(f"订阅已取消: subscription_id={subscription.id}")
            
            db.session.commit()
            
            current_app.logger.info(
                f"退款申请已批准: application_id={application_id}, "
                f"admin_id={admin_id}, order_id={order.id}"
            )
            
            # 发送通知
            self.notify_user(application_id, 'approved')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"批准退款失败: {str(e)}")
            raise ValueError(f"批准退款失败: {str(e)}")
    
    def reject_refund(self, application_id: int, admin_id: int, reason: str) -> bool:
        """
        拒绝退款申请
        
        Args:
            application_id: 退款申请ID
            admin_id: 管理员ID
            reason: 拒绝原因
            
        Returns:
            是否成功
            
        Raises:
            ValueError: 当申请不存在或状态不是pending时
        """
        application = RefundApplication.query.get(application_id)
        if not application:
            raise ValueError(f"退款申请不存在: {application_id}")
        
        if application.status != 'pending':
            raise ValueError(f"退款申请状态必须为待处理，当前状态: {application.status}")
        
        try:
            # 更新退款申请状态
            application.status = 'rejected'
            application.processed_by = admin_id
            application.processed_at = datetime.utcnow()
            application.reject_reason = reason
            
            # 恢复订单状态为 paid
            order = application.order
            order.payment_status = 'paid'
            order.refund_status = 'rejected'
            order.refund_processed_at = datetime.utcnow()
            order.refund_processed_by = admin_id
            
            db.session.commit()
            
            current_app.logger.info(
                f"退款申请已拒绝: application_id={application_id}, "
                f"admin_id={admin_id}, order_id={order.id}, reason={reason}"
            )
            
            # 发送通知
            self.notify_user(application_id, 'rejected')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"拒绝退款失败: {str(e)}")
            raise ValueError(f"拒绝退款失败: {str(e)}")
    
    def get_pending_applications(self, page: int = 1, per_page: int = 20) -> Dict:
        """
        获取待处理的退款申请列表
        
        Args:
            page: 页码（从1开始）
            per_page: 每页数量
            
        Returns:
            {
                'applications': list,
                'total': int,
                'page': int,
                'per_page': int,
                'pages': int
            }
        """
        query = RefundApplication.query.filter_by(status='pending').order_by(
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
                'plan_name': app.order.plan.name if app.order.plan else None
            })
        
        return {
            'applications': applications,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }
    
    def notify_user(self, application_id: int, status: str) -> bool:
        """
        通知用户退款状态变更
        
        Args:
            application_id: 退款申请ID
            status: 退款状态 ('pending', 'approved', 'rejected')
            
        Returns:
            是否成功
        """
        from app.services.multi_channel_pusher import MultiChannelPusher
        
        try:
            # 获取退款申请信息
            application = RefundApplication.query.get(application_id)
            if not application:
                current_app.logger.error(f"退款申请不存在: {application_id}")
                return False
            
            # 获取订单信息
            order = application.order
            if not order:
                current_app.logger.error(f"订单不存在: order_id={application.order_id}")
                return False
            
            # 构造通知内容
            subject, content = self._build_notification_content(application, order, status)
            
            # 使用 MultiChannelPusher 发送通知
            pusher = MultiChannelPusher()
            result = pusher.push(
                user_id=application.user_id,
                subject=subject,
                content=content,
                html=True
            )
            
            # 检查是否至少有一个渠道成功
            has_success = any(
                channel_result.get('success', False)
                for channel_result in result.values()
            )
            
            if has_success:
                current_app.logger.info(
                    f"退款状态通知发送成功: application_id={application_id}, "
                    f"status={status}, user_id={application.user_id}"
                )
            else:
                current_app.logger.warning(
                    f"退款状态通知发送失败（所有渠道失败）: application_id={application_id}, "
                    f"status={status}, result={result}"
                )
            
            # 即使通知失败也返回True，不影响退款操作
            return True
            
        except Exception as e:
            # 通知失败不应影响退款操作，记录错误日志
            current_app.logger.error(
                f"退款状态通知发送异常: application_id={application_id}, "
                f"status={status}, error={str(e)}"
            )
            return True
    
    def _build_notification_content(self, application: RefundApplication, 
                                    order: Order, status: str) -> tuple:
        """
        构造通知内容
        
        Args:
            application: 退款申请对象
            order: 订单对象
            status: 退款状态
            
        Returns:
            (subject, content) 元组
        """
        # 获取套餐名称
        plan_name = order.plan.name if order.plan else "未知套餐"
        
        # 根据状态构造不同的通知内容
        if status == 'pending':
            subject = "退款申请已提交"
            content = f"""
            <h3>退款申请已提交</h3>
            <p>您好，您的退款申请已成功提交，我们将尽快处理。</p>
            <p><strong>申请详情：</strong></p>
            <ul>
                <li>订单号：{order.order_no}</li>
                <li>套餐名称：{plan_name}</li>
                <li>订单金额：¥{order.amount}</li>
                <li>申请时间：{application.applied_at.strftime('%Y-%m-%d %H:%M:%S') if application.applied_at else '未知'}</li>
                <li>退款原因：{application.reason}</li>
            </ul>
            <p>我们会在1-3个工作日内完成审核，请耐心等待。</p>
            """
        
        elif status == 'approved':
            subject = "退款申请已批准"
            content = f"""
            <h3>退款申请已批准</h3>
            <p>您好，您的退款申请已通过审核。</p>
            <p><strong>退款详情：</strong></p>
            <ul>
                <li>订单号：{order.order_no}</li>
                <li>套餐名称：{plan_name}</li>
                <li>退款金额：¥{order.amount}</li>
                <li>申请时间：{application.applied_at.strftime('%Y-%m-%d %H:%M:%S') if application.applied_at else '未知'}</li>
                <li>处理时间：{application.processed_at.strftime('%Y-%m-%d %H:%M:%S') if application.processed_at else '未知'}</li>
            </ul>
            <p>退款将在3-5个工作日内原路退回，请注意查收。</p>
            <p>您的订阅已取消，感谢您的使用。</p>
            """
        
        elif status == 'rejected':
            subject = "退款申请已拒绝"
            reject_reason = application.reject_reason or "未提供拒绝原因"
            content = f"""
            <h3>退款申请已拒绝</h3>
            <p>您好，您的退款申请未通过审核。</p>
            <p><strong>申请详情：</strong></p>
            <ul>
                <li>订单号：{order.order_no}</li>
                <li>套餐名称：{plan_name}</li>
                <li>订单金额：¥{order.amount}</li>
                <li>申请时间：{application.applied_at.strftime('%Y-%m-%d %H:%M:%S') if application.applied_at else '未知'}</li>
                <li>处理时间：{application.processed_at.strftime('%Y-%m-%d %H:%M:%S') if application.processed_at else '未知'}</li>
                <li><strong>拒绝原因：</strong>{reject_reason}</li>
            </ul>
            <p>您的订阅仍然有效，可以继续使用服务。</p>
            <p>如有疑问，请联系客服。</p>
            """
        
        else:
            # 未知状态，使用通用模板
            subject = "退款申请状态更新"
            content = f"""
            <h3>退款申请状态更新</h3>
            <p>您好，您的退款申请状态已更新。</p>
            <p><strong>申请详情：</strong></p>
            <ul>
                <li>订单号：{order.order_no}</li>
                <li>套餐名称：{plan_name}</li>
                <li>当前状态：{status}</li>
            </ul>
            """
        
        return subject, content
