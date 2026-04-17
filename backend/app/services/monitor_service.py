# -*- coding: utf-8 -*-
"""
监控告警服务
"""
import logging
from datetime import datetime, timedelta
from app import db
from app.models import CrawlLog, Source
from app.services.push_service import push_manager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)


class MonitorService:
    """监控服务"""
    
    def __init__(self):
        self.alert_threshold = 3  # 连续失败3次触发告警
        self.check_interval = timedelta(hours=1)  # 检查间隔
    
    def record_crawl_result(self, spider_name, status, articles_count=0, error_msg=None):
        """
        记录爬虫运行结果
        
        Args:
            spider_name: 爬虫名称
            status: 状态（success/failed）
            articles_count: 抓取文章数
            error_msg: 错误信息
        """
        try:
            # 查找或创建数据源
            source = Source.query.filter_by(name=spider_name).first()
            if not source:
                source = Source(
                    name=spider_name,
                    url=f'https://{spider_name}.com',
                    type='crawler',
                    status='active'
                )
                db.session.add(source)
                db.session.flush()
            
            # 创建爬虫日志
            crawl_log = CrawlLog(
                source_id=source.id,
                status=status,
                articles_count=articles_count,
                error_msg=error_msg,
                started_at=datetime.utcnow(),
                finished_at=datetime.utcnow()
            )
            db.session.add(crawl_log)
            
            # 更新数据源状态
            source.last_crawl_at = datetime.utcnow()
            if status == 'success':
                source.status = 'active'
                source.error_msg = None
            else:
                source.status = 'error'
                source.error_msg = error_msg
            
            db.session.commit()
            
            logger.info(f"记录爬虫结果: {spider_name} - {status} - {articles_count}篇")
            
            # 检查是否需要告警
            if status == 'failed':
                self.check_and_alert(spider_name)
                
        except Exception as e:
            logger.error(f"记录爬虫结果失败: {str(e)}")
            db.session.rollback()
    
    def check_and_alert(self, spider_name):
        """
        检查是否需要告警
        
        Args:
            spider_name: 爬虫名称
        """
        try:
            source = Source.query.filter_by(name=spider_name).first()
            if not source:
                return
            
            # 获取最近的日志
            recent_logs = CrawlLog.query.filter_by(source_id=source.id)\
                .order_by(CrawlLog.finished_at.desc())\
                .limit(self.alert_threshold)\
                .all()
            
            # 检查是否连续失败
            if len(recent_logs) >= self.alert_threshold:
                all_failed = all(log.status == 'failed' for log in recent_logs)
                
                if all_failed:
                    logger.warning(f"爬虫 {spider_name} 连续失败 {self.alert_threshold} 次，触发告警")
                    self.send_alert(spider_name, recent_logs[0].error_msg)
                    
        except Exception as e:
            logger.error(f"检查告警失败: {str(e)}")
    
    def send_alert(self, spider_name, error_msg):
        """
        发送告警
        
        Args:
            spider_name: 爬虫名称
            error_msg: 错误信息
        """
        alert_message = f"""
【爬虫告警】

爬虫名称: {spider_name}
告警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
告警原因: 连续失败 {self.alert_threshold} 次

错误信息:
{error_msg or '未知错误'}

请及时处理！
"""
        
        # 发送企业微信告警（发送给管理员）
        try:
            # 获取所有管理员用户
            from app.models import User
            admin_users = User.query.filter_by(role='admin').all()
            admin_ids = [user.id for user in admin_users]
            
            if admin_ids:
                wechat_service = push_manager.get_service('wechat_work')
                if wechat_service:
                    for admin_id in admin_ids:
                        try:
                            wechat_service.send(admin_id, alert_message, message_type='text')
                        except Exception as e:
                            logger.error(f"发送企业微信告警给用户 {admin_id} 失败: {str(e)}")
                    logger.info(f"企业微信告警已发送: {spider_name}")
                else:
                    logger.warning("企业微信服务未配置")
            else:
                logger.warning("没有找到管理员用户")
        except Exception as e:
            logger.error(f"发送企业微信告警失败: {str(e)}")
        
        # 发送邮件告警
        try:
            self.send_email_alert(spider_name, alert_message)
            logger.info(f"邮件告警已发送: {spider_name}")
        except Exception as e:
            logger.error(f"发送邮件告警失败: {str(e)}")
    
    def send_email_alert(self, spider_name, message):
        """
        发送邮件告警
        
        Args:
            spider_name: 爬虫名称
            message: 告警消息
        """
        try:
            # 从配置中获取邮件设置
            smtp_server = current_app.config.get('SMTP_SERVER')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_user = current_app.config.get('SMTP_USER')
            smtp_password = current_app.config.get('SMTP_PASSWORD')
            alert_emails = current_app.config.get('ALERT_EMAILS', [])
            
            if not all([smtp_server, smtp_user, smtp_password, alert_emails]):
                logger.warning("邮件配置不完整，跳过邮件告警")
                return
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(alert_emails)
            msg['Subject'] = f'【爬虫告警】{spider_name} 运行失败'
            
            # 邮件正文
            body = MIMEText(message, 'plain', 'utf-8')
            msg.attach(body)
            
            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            raise
    
    def get_crawl_statistics(self, days=7):
        """
        获取爬虫统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            dict: 统计信息
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 总运行次数
            total_runs = CrawlLog.query.filter(
                CrawlLog.finished_at >= start_date
            ).count()
            
            # 成功次数
            success_runs = CrawlLog.query.filter(
                CrawlLog.finished_at >= start_date,
                CrawlLog.status == 'success'
            ).count()
            
            # 失败次数
            failed_runs = CrawlLog.query.filter(
                CrawlLog.finished_at >= start_date,
                CrawlLog.status == 'failed'
            ).count()
            
            # 总文章数
            total_articles = db.session.query(
                db.func.sum(CrawlLog.articles_count)
            ).filter(
                CrawlLog.finished_at >= start_date,
                CrawlLog.status == 'success'
            ).scalar() or 0
            
            # 成功率
            success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0
            
            # 按爬虫统计
            spider_stats = db.session.query(
                Source.name,
                db.func.count(CrawlLog.id).label('total'),
                db.func.sum(db.case(
                    (CrawlLog.status == 'success', 1),
                    else_=0
                )).label('success'),
                db.func.sum(CrawlLog.articles_count).label('articles')
            ).join(
                CrawlLog, Source.id == CrawlLog.source_id
            ).filter(
                CrawlLog.finished_at >= start_date
            ).group_by(
                Source.name
            ).all()
            
            spider_list = []
            for stat in spider_stats:
                spider_list.append({
                    'name': stat.name,
                    'total_runs': stat.total,
                    'success_runs': stat.success,
                    'success_rate': (stat.success / stat.total * 100) if stat.total > 0 else 0,
                    'total_articles': stat.articles or 0
                })
            
            # 获取业务指标
            business_metrics = self.get_business_metrics(days)
            
            return {
                'period_days': days,
                'total_runs': total_runs,
                'success_runs': success_runs,
                'failed_runs': failed_runs,
                'success_rate': round(success_rate, 2),
                'total_articles': int(total_articles),
                'spiders': spider_list,
                'business_metrics': business_metrics
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    def get_business_metrics(self, days=7):
        """
        获取业务指标
        
        Args:
            days: 统计天数
            
        Returns:
            dict: 业务指标
        """
        try:
            from app.models import User, Article, Subscription, Order, DailyBrief
            from sqlalchemy import func
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # 用户相关指标
            total_users = User.query.count()
            new_users = User.query.filter(User.created_at >= start_date).count()
            active_users = User.query.filter(User.last_login_at >= start_date).count()
            
            # 文章相关指标
            total_articles_db = Article.query.count()
            new_articles = Article.query.filter(Article.created_at >= start_date).count()
            reviewed_articles = Article.query.filter(
                Article.created_at >= start_date,
                Article.is_reviewed == True
            ).count()
            pending_articles = Article.query.filter(Article.is_reviewed == False).count()
            
            # 订阅相关指标
            active_subscriptions = Subscription.query.filter_by(status='active').count()
            new_subscriptions = Subscription.query.filter(
                Subscription.start_date >= start_date
            ).count()
            expiring_soon = Subscription.query.filter(
                Subscription.status == 'active',
                Subscription.end_date <= datetime.utcnow() + timedelta(days=7),
                Subscription.end_date > datetime.utcnow()
            ).count()
            
            # 订单相关指标
            total_orders = Order.query.count()
            pending_orders = Order.query.filter_by(payment_status='pending').count()
            paid_orders = Order.query.filter(
                Order.payment_status == 'paid',
                Order.payment_time >= start_date
            ).count()
            
            # 计算总收入
            total_revenue = db.session.query(
                func.sum(Order.amount)
            ).filter(
                Order.payment_status == 'paid',
                Order.payment_time >= start_date
            ).scalar() or 0
            
            # AI简报相关指标
            total_briefs = DailyBrief.query.count()
            recent_briefs = DailyBrief.query.filter(
                DailyBrief.generated_at >= start_date
            ).count()
            
            # 分类分布
            category_distribution = db.session.query(
                Article.category,
                func.count(Article.id).label('count')
            ).filter(
                Article.created_at >= start_date
            ).group_by(Article.category).all()
            
            categories = [
                {'category': cat.category, 'count': cat.count}
                for cat in category_distribution
            ]
            
            return {
                'users': {
                    'total': total_users,
                    'new': new_users,
                    'active': active_users,
                    'active_rate': round((active_users / total_users * 100) if total_users > 0 else 0, 2)
                },
                'articles': {
                    'total': total_articles_db,
                    'new': new_articles,
                    'reviewed': reviewed_articles,
                    'pending': pending_articles,
                    'review_rate': round((reviewed_articles / new_articles * 100) if new_articles > 0 else 0, 2)
                },
                'subscriptions': {
                    'active': active_subscriptions,
                    'new': new_subscriptions,
                    'expiring_soon': expiring_soon
                },
                'orders': {
                    'total': total_orders,
                    'pending': pending_orders,
                    'paid': paid_orders,
                    'revenue': float(total_revenue)
                },
                'briefs': {
                    'total': total_briefs,
                    'recent': recent_briefs
                },
                'categories': categories
            }
            
        except Exception as e:
            logger.error(f"获取业务指标失败: {str(e)}")
            return {}
    
    def get_recent_failures(self, limit=10):
        """
        获取最近的失败记录
        
        Args:
            limit: 返回数量
            
        Returns:
            list: 失败记录列表
        """
        try:
            failures = db.session.query(
                CrawlLog, Source
            ).join(
                Source, CrawlLog.source_id == Source.id
            ).filter(
                CrawlLog.status == 'failed'
            ).order_by(
                CrawlLog.finished_at.desc()
            ).limit(limit).all()
            
            result = []
            for log, source in failures:
                result.append({
                    'spider_name': source.name,
                    'error_msg': log.error_msg,
                    'failed_at': log.finished_at.isoformat() if log.finished_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取失败记录失败: {str(e)}")
            return []
    
    def check_system_health(self):
        """
        检查系统健康状态
        
        Returns:
            dict: 健康状态信息
        """
        try:
            # 检查最近1小时是否有爬虫运行
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_runs = CrawlLog.query.filter(
                CrawlLog.finished_at >= one_hour_ago
            ).count()
            
            # 检查是否有爬虫处于错误状态
            error_sources = Source.query.filter_by(status='error').count()
            
            # 检查数据库连接
            db_healthy = True
            try:
                db.session.execute('SELECT 1')
            except:
                db_healthy = False
            
            # 总体健康状态
            is_healthy = db_healthy and error_sources == 0
            
            return {
                'is_healthy': is_healthy,
                'db_healthy': db_healthy,
                'recent_runs': recent_runs,
                'error_sources': error_sources,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"检查系统健康状态失败: {str(e)}")
            return {
                'is_healthy': False,
                'error': str(e)
            }


# 全局监控服务实例
monitor_service = MonitorService()
