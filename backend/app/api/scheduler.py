# -*- coding: utf-8 -*-
"""
定时任务管理 API
"""
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from flask import request
from app.api import scheduler_bp
from app.models import User
from app.scheduler import (
    get_scheduler,
    list_jobs,
    pause_job,
    resume_job,
    trigger_job,
    run_all_crawlers,
    run_crawler
)
import logging

logger = logging.getLogger(__name__)


def admin_required():
    """管理员权限装饰器"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user


@scheduler_bp.route('/jobs')
class SchedulerJobs(MethodView):
    @jwt_required()
    def get(self):
        """获取所有定时任务"""
        admin_required()
        
        scheduler = get_scheduler()
        if scheduler is None:
            return {
                'enabled': False,
                'jobs': [],
                'message': '定时任务调度器未启用'
            }
        
        jobs = list_jobs()
        
        return {
            'enabled': True,
            'jobs': jobs,
            'total': len(jobs)
        }


@scheduler_bp.route('/jobs/<job_id>/pause')
class PauseJob(MethodView):
    @jwt_required()
    def post(self, job_id):
        """暂停指定任务"""
        admin_required()
        
        success = pause_job(job_id)
        
        if success:
            return {'message': f'任务 {job_id} 已暂停'}
        else:
            abort(400, message=f'暂停任务 {job_id} 失败')


@scheduler_bp.route('/jobs/<job_id>/resume')
class ResumeJob(MethodView):
    @jwt_required()
    def post(self, job_id):
        """恢复指定任务"""
        admin_required()
        
        success = resume_job(job_id)
        
        if success:
            return {'message': f'任务 {job_id} 已恢复'}
        else:
            abort(400, message=f'恢复任务 {job_id} 失败')


@scheduler_bp.route('/jobs/<job_id>/trigger')
class TriggerJob(MethodView):
    @jwt_required()
    def post(self, job_id):
        """立即触发指定任务"""
        admin_required()
        
        success = trigger_job(job_id)
        
        if success:
            return {'message': f'任务 {job_id} 已触发'}
        else:
            abort(400, message=f'触发任务 {job_id} 失败')


@scheduler_bp.route('/run-all')
class RunAllCrawlers(MethodView):
    @jwt_required()
    def post(self):
        """立即运行所有爬虫"""
        admin_required()
        
        try:
            # 在后台线程中运行
            import threading
            thread = threading.Thread(target=run_all_crawlers)
            thread.daemon = True
            thread.start()
            
            return {'message': '已开始运行所有爬虫，请查看日志'}
        except Exception as e:
            logger.error(f"运行所有爬虫失败: {str(e)}")
            abort(500, message=f'运行失败: {str(e)}')


@scheduler_bp.route('/run-single')
class RunSingleCrawler(MethodView):
    @jwt_required()
    def post(self):
        """运行单个爬虫"""
        admin_required()
        
        data = request.get_json()
        spider_name = data.get('spider_name')
        
        if not spider_name:
            abort(400, message='请提供爬虫名称')
        
        try:
            # 在后台线程中运行
            import threading
            thread = threading.Thread(target=run_crawler, args=(spider_name,))
            thread.daemon = True
            thread.start()
            
            return {'message': f'已开始运行爬虫 {spider_name}，请查看日志'}
        except Exception as e:
            logger.error(f"运行爬虫 {spider_name} 失败: {str(e)}")
            abort(500, message=f'运行失败: {str(e)}')


@scheduler_bp.route('/status')
class SchedulerStatus(MethodView):
    @jwt_required()
    def get(self):
        """获取调度器状态"""
        admin_required()
        
        scheduler = get_scheduler()
        
        if scheduler is None:
            return {
                'enabled': False,
                'running': False,
                'message': '定时任务调度器未启用'
            }
        
        return {
            'enabled': True,
            'running': scheduler.running,
            'jobs_count': len(scheduler.get_jobs()),
            'message': '定时任务调度器正在运行'
        }
