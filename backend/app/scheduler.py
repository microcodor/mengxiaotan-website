# -*- coding: utf-8 -*-
"""
定时任务调度器
使用 APScheduler 实现爬虫自动运行
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = None


def run_crawler(spider_name):
    """
    运行指定的爬虫
    
    Args:
        spider_name: 爬虫名称
    """
    from app.services.monitor_service import monitor_service
    
    try:
        logger.info(f"开始运行爬虫: {spider_name}")
        
        # 获取项目根目录
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        crawler_dir = os.path.join(os.path.dirname(backend_dir), 'crawler')
        
        # 切换到爬虫目录并运行
        result = subprocess.run(
            ['scrapy', 'crawl', spider_name],
            cwd=crawler_dir,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            logger.info(f"爬虫 {spider_name} 运行成功")
            logger.debug(f"输出: {result.stdout}")
            
            # 记录成功结果
            monitor_service.record_crawl_result(
                spider_name=spider_name,
                status='success',
                articles_count=0  # TODO: 从输出中解析文章数
            )
        else:
            logger.error(f"爬虫 {spider_name} 运行失败")
            logger.error(f"错误: {result.stderr}")
            
            # 记录失败结果
            monitor_service.record_crawl_result(
                spider_name=spider_name,
                status='failed',
                error_msg=result.stderr[:500]  # 限制错误信息长度
            )
            
    except subprocess.TimeoutExpired:
        error_msg = f"爬虫 {spider_name} 运行超时"
        logger.error(error_msg)
        monitor_service.record_crawl_result(
            spider_name=spider_name,
            status='failed',
            error_msg=error_msg
        )
    except Exception as e:
        error_msg = f"运行爬虫 {spider_name} 时发生错误: {str(e)}"
        logger.error(error_msg)
        monitor_service.record_crawl_result(
            spider_name=spider_name,
            status='failed',
            error_msg=str(e)
        )


def run_all_crawlers():
    """运行所有可用的爬虫"""
    logger.info("=" * 60)
    logger.info(f"开始批量运行爬虫 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 可用的爬虫列表
    available_spiders = [
        'xinhua_real',      # 新华网能源
        'chinapower',       # 中国电力网
        'nea',              # 国家能源局
        'coal',             # 中国煤炭网
        'newenergy',        # 中国新能源网
        'power',            # 北极星电力网
        'cnenergy',         # 中国能源网
        'ndrc',             # 国家发改委
        'peopledaily',      # 人民网能源
    ]
    
    success_count = 0
    fail_count = 0
    
    for spider_name in available_spiders:
        try:
            run_crawler(spider_name)
            success_count += 1
        except Exception as e:
            logger.error(f"爬虫 {spider_name} 执行失败: {str(e)}")
            fail_count += 1
    
    logger.info("=" * 60)
    logger.info(f"批量运行完成 - 成功: {success_count}, 失败: {fail_count}")
    logger.info("=" * 60)


def generate_daily_brief():
    """生成每日AI简报"""
    from app.services.ai_brief_generator import AIBriefGenerator
    from config import Config
    from datetime import date, timedelta
    
    logger.info("=" * 60)
    logger.info(f"开始生成每日简报 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 初始化生成器
        generator = AIBriefGenerator(
            api_key=Config.MINIMAX_API_KEY,
            group_id=Config.MINIMAX_GROUP_ID,
            api_url=Config.MINIMAX_API_URL
        )
        
        # 生成昨天的简报
        target_date = date.today() - timedelta(days=1)
        result = generator.generate_daily_brief(target_date)
        
        if result:
            logger.info(f"简报生成成功: {result['brief_id']}")
            
            # 推送简报
            push_result = generator.push_brief_to_users(result['brief_id'])
            logger.info(f"简报推送完成: {push_result}")
        else:
            logger.error("简报生成失败")
            
    except Exception as e:
        logger.error(f"生成每日简报时发生错误: {str(e)}")
    
    logger.info("=" * 60)


def check_trial_expiry():
    """检查试用期到期并发送提醒"""
    from app.services.subscription_service import SubscriptionService
    from app.services.multi_channel_pusher import MultiChannelPusher
    
    logger.info("=" * 60)
    logger.info(f"检查试用期到期 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 获取即将到期的试用订阅
        expiring_subscriptions = SubscriptionService.check_trial_expiry()
        
        if not expiring_subscriptions:
            logger.info("没有即将到期的试用订阅")
            return
        
        logger.info(f"找到 {len(expiring_subscriptions)} 个即将到期的试用订阅")
        
        # 发送提醒
        pusher = MultiChannelPusher()
        
        for subscription in expiring_subscriptions:
            try:
                user_id = subscription.user_id
                end_date = subscription.end_date.strftime('%Y-%m-%d %H:%M')
                
                message = f"""
【试用期到期提醒】

您的蒙小碳免费试用即将到期！

到期时间：{end_date}

升级到基础版，享受更多专业服务：
• 企业画像构建
• 战略级内参（2份/月）
• 数字分身沙盘
• 动态监测预警

立即升级：https://mengxiaotan.com/subscription

如有疑问，请联系客服。
                """.strip()
                
                pusher.push(user_id, message, channels=['enterprise_wechat'])
                logger.info(f"已向用户 {user_id} 发送试用期到期提醒")
                
            except Exception as e:
                logger.error(f"向用户 {subscription.user_id} 发送提醒失败: {str(e)}")
        
        logger.info(f"试用期到期提醒发送完成")
        
    except Exception as e:
        logger.error(f"检查试用期到期时发生错误: {str(e)}")
    
    logger.info("=" * 60)


def expire_trial_subscriptions():
    """将已过期的试用订阅标记为过期"""
    from app.services.subscription_service import SubscriptionService
    
    logger.info("=" * 60)
    logger.info(f"处理过期试用订阅 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        count = SubscriptionService.expire_trial_subscriptions()
        logger.info(f"已将 {count} 个试用订阅标记为过期")
        
    except Exception as e:
        logger.error(f"处理过期试用订阅时发生错误: {str(e)}")
    
    logger.info("=" * 60)


def init_scheduler(app):
    """
    初始化定时任务调度器
    
    Args:
        app: Flask应用实例
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("调度器已经初始化，跳过")
        return scheduler
    
    logger.info("初始化定时任务调度器...")
    
    # 创建后台调度器
    scheduler = BackgroundScheduler(
        timezone='Asia/Shanghai',
        job_defaults={
            'coalesce': True,  # 合并错过的任务
            'max_instances': 1,  # 同一任务最多只能有1个实例运行
            'misfire_grace_time': 300  # 错过任务的宽限时间（秒）
        }
    )
    
    # 从配置中读取是否启用定时任务
    enable_scheduler = app.config.get('ENABLE_SCHEDULER', True)
    
    if not enable_scheduler:
        logger.info("定时任务已禁用（ENABLE_SCHEDULER=False）")
        return scheduler
    
    # 添加定时任务
    # 任务1: 每天晚上8点运行所有爬虫
    scheduler.add_job(
        func=run_all_crawlers,
        trigger=CronTrigger(hour=20, minute=0),
        id='evening_crawl',
        name='每日爬虫任务',
        replace_existing=True
    )
    logger.info("✓ 添加任务: 每日爬虫任务 (每天 20:00)")
    
    # 任务2: 每天早上9点生成AI简报
    scheduler.add_job(
        func=generate_daily_brief,
        trigger=CronTrigger(hour=9, minute=0),
        id='daily_brief',
        name='每日AI简报生成',
        replace_existing=True
    )
    logger.info("✓ 添加任务: 每日AI简报生成 (每天 09:00)")
    
    # 任务3: 每天早上8点检查试用期到期
    scheduler.add_job(
        func=check_trial_expiry,
        trigger=CronTrigger(hour=8, minute=0),
        id='check_trial_expiry',
        name='检查试用期到期',
        replace_existing=True
    )
    logger.info("✓ 添加任务: 检查试用期到期 (每天 08:00)")
    
    # 任务4: 每天凌晨1点处理过期试用订阅
    scheduler.add_job(
        func=expire_trial_subscriptions,
        trigger=CronTrigger(hour=1, minute=0),
        id='expire_trial_subscriptions',
        name='处理过期试用订阅',
        replace_existing=True
    )
    logger.info("✓ 添加任务: 处理过期试用订阅 (每天 01:00)")
    
    # 可选：添加测试任务（每小时运行一次，用于测试）
    # scheduler.add_job(
    #     func=run_all_crawlers,
    #     trigger=IntervalTrigger(hours=1),
    #     id='hourly_crawl',
    #     name='每小时爬虫任务（测试）',
    #     replace_existing=True
    # )
    # logger.info("✓ 添加任务: 每小时爬虫任务（测试）")
    
    # 启动调度器
    scheduler.start()
    logger.info("✓ 定时任务调度器启动成功")
    
    # 打印所有任务
    logger.info("\n当前定时任务列表:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} (ID: {job.id})")
        logger.info(f"    下次运行: {job.next_run_time}")
    
    return scheduler


def shutdown_scheduler():
    """关闭调度器"""
    global scheduler
    
    if scheduler is not None:
        logger.info("正在关闭定时任务调度器...")
        scheduler.shutdown()
        scheduler = None
        logger.info("✓ 定时任务调度器已关闭")


def get_scheduler():
    """获取调度器实例"""
    return scheduler


def list_jobs():
    """列出所有定时任务"""
    if scheduler is None:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    
    return jobs


def pause_job(job_id):
    """暂停指定任务"""
    if scheduler is None:
        return False
    
    try:
        scheduler.pause_job(job_id)
        logger.info(f"任务 {job_id} 已暂停")
        return True
    except Exception as e:
        logger.error(f"暂停任务 {job_id} 失败: {str(e)}")
        return False


def resume_job(job_id):
    """恢复指定任务"""
    if scheduler is None:
        return False
    
    try:
        scheduler.resume_job(job_id)
        logger.info(f"任务 {job_id} 已恢复")
        return True
    except Exception as e:
        logger.error(f"恢复任务 {job_id} 失败: {str(e)}")
        return False


def trigger_job(job_id):
    """立即触发指定任务"""
    if scheduler is None:
        return False
    
    try:
        job = scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"任务 {job_id} 已触发")
            return True
        else:
            logger.error(f"任务 {job_id} 不存在")
            return False
    except Exception as e:
        logger.error(f"触发任务 {job_id} 失败: {str(e)}")
        return False
