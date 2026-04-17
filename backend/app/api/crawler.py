"""
爬虫管理 API
"""
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from flask import request
from app.api import crawler_bp
from app.models import User, Source, CrawlLog
from app import db
from datetime import datetime
from sqlalchemy import desc
import subprocess
import os
import signal


def admin_required():
    """管理员权限装饰器"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ['admin', 'editor']:
        abort(403, message='需要管理员权限')
    return user


@crawler_bp.route('/test-run')
class TestRun(MethodView):
    @jwt_required()
    def post(self):
        """测试运行爬虫（简化版）"""
        admin_required()
        
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            crawler_path = os.path.join(project_root, 'crawler')
            scrapy_cmd = os.path.join(project_root, 'backend/venv/bin/scrapy')
            
            # 测试运行
            process = subprocess.Popen(
                [scrapy_cmd, 'list'],
                cwd=crawler_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=5)
            
            return {
                'success': True,
                'stdout': stdout,
                'stderr': stderr,
                'returncode': process.returncode
            }
        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, 500


@crawler_bp.route('/test-path')
class TestPath(MethodView):
    @jwt_required()
    def get(self):
        """测试路径配置"""
        admin_required()
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        crawler_path = os.path.join(project_root, 'crawler')
        scrapy_cmd = os.path.join(project_root, 'backend/venv/bin/scrapy')
        
        return {
            'project_root': project_root,
            'crawler_path': crawler_path,
            'crawler_exists': os.path.exists(crawler_path),
            'scrapy_cmd': scrapy_cmd,
            'scrapy_exists': os.path.exists(scrapy_cmd),
            'cwd': os.getcwd()
        }


@crawler_bp.route('/spiders')
class SpiderList(MethodView):
    @jwt_required()
    def get(self):
        """获取所有爬虫列表"""
        admin_required()
        
        # 定义所有爬虫
        spiders = [
            # 碳交易
            {
                'name': 'ccer',
                'display_name': '全国温室气体自愿减排交易系统',
                'category': 'carbon_trading',
                'description': '抓取CCER官方碳交易平台的交易数据和政策资讯，每次约10-15篇',
                'url': 'https://www.ccer.com.cn/',
                'status': 'active',
                'schedule': '从调度器获取',  # 将从调度器动态获取
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            # 钢铁行业
            {
                'name': 'mysteel',
                'display_name': '我的钢铁网',
                'category': 'steel',
                'description': '抓取我的钢铁网的钢铁行业资讯和价格信息，每次约20-25篇',
                'url': 'https://www.mysteel.com/',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            # 有色金属
            {
                'name': 'cnmn_paper',
                'display_name': '中国有色金属报',
                'category': 'nonferrous_metals',
                'description': '抓取中国有色金属报数字报的行业新闻，每次约15-20篇',
                'url': 'https://paper.cnmn.com.cn/',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'smm_metal',
                'display_name': '上海有色金属网',
                'category': 'nonferrous_metals',
                'description': '抓取上海有色金属网（SMM）的国际化行业资讯，每次约15-20篇',
                'url': 'https://www.metal.com/',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中高'
            },
            # 能源媒体
            {
                'name': 'xinhua_real',
                'display_name': '新华网能源',
                'category': 'media',
                'description': '抓取新华网能源频道的真实新闻，每次约15-20篇完整文章',
                'url': 'http://www.news.cn/energy/',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '简单'
            },
            {
                'name': 'chinapower',
                'display_name': '中国电力网',
                'category': 'power',
                'description': '抓取中国电力网的电力行业资讯，每次约30-40篇文章',
                'url': 'http://www.chinapower.com.cn/',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'power',
                'display_name': '北极星电力网',
                'category': 'power',
                'description': '抓取北极星电力网的新闻和政策',
                'url': 'https://news.bjx.com.cn',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'ndrc',
                'display_name': '国家发改委',
                'category': 'government',
                'description': '抓取国家发改委官网的政策文件和工作动态',
                'url': 'https://www.ndrc.gov.cn',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'nea',
                'display_name': '国家能源局（测试版）',
                'category': 'government',
                'description': '国家能源局测试数据爬虫',
                'url': 'http://www.nea.gov.cn',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '简单'
            },
            {
                'name': 'real_nea',
                'display_name': '国家能源局（真实）',
                'category': 'government',
                'description': '抓取国家能源局的能源要闻和媒体报道（使用Playwright）',
                'url': 'https://www.nea.gov.cn/xwzx/nyyw.htm',
                'status': 'testing',
                'schedule': '手动运行',
                'technology': 'Playwright',
                'difficulty': '困难'
            },
            {
                'name': 'peopledaily',
                'display_name': '人民网能源',
                'category': 'media',
                'description': '抓取人民网能源频道的新闻报道',
                'url': 'http://energy.people.com.cn',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '简单'
            },
            {
                'name': 'coal',
                'display_name': '中国煤炭网',
                'category': 'coal',
                'description': '抓取中国煤炭市场网的新闻和价格指数',
                'url': 'https://www.cctd.com.cn',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'newenergy',
                'display_name': '中国新能源网',
                'category': 'new_energy',
                'description': '抓取中国新能源网的新闻和技术文章',
                'url': 'https://www.china-nengyuan.com',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'cnenergy',
                'display_name': '中国能源网',
                'category': 'energy',
                'description': '抓取中国能源网的综合能源资讯',
                'url': 'http://www.cnenergy.org',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'energy_news',
                'display_name': '综合能源新闻',
                'category': 'comprehensive',
                'description': '抓取多个能源新闻源的综合爬虫，包括国家能源局、煤炭、电力、新能源等领域',
                'url': 'multiple',
                'status': 'active',
                'schedule': '从调度器获取',
                'technology': 'Scrapy',
                'difficulty': '中等'
            },
            {
                'name': 'test',
                'display_name': '测试爬虫',
                'category': 'test',
                'description': '用于测试爬虫系统功能的测试爬虫',
                'url': 'http://test.example.com',
                'status': 'active',
                'schedule': '手动运行',
                'technology': 'Scrapy',
                'difficulty': '简单'
            },
        ]
        
        # 从调度器获取真实的调度时间
        from app.scheduler import get_scheduler
        scheduler = get_scheduler()
        
        # 爬虫任务的调度时间（从调度器中获取）
        schedule_info = {}
        if scheduler:
            for job in scheduler.get_jobs():
                # 爬虫任务通常以 'crawl' 结尾或包含爬虫相关关键词
                if 'crawl' in job.id.lower():
                    # 提取触发器信息
                    trigger_str = str(job.trigger)
                    # 解析 CronTrigger 的时间
                    if 'cron' in trigger_str.lower():
                        # 从触发器中提取小时信息
                        import re
                        hour_match = re.search(r'hour=\'(\d+)\'', trigger_str)
                        minute_match = re.search(r'minute=\'(\d+)\'', trigger_str)
                        
                        if hour_match and minute_match:
                            hour = hour_match.group(1)
                            minute = minute_match.group(1)
                            schedule_time = f"每天 {hour}:{minute.zfill(2)}"
                            schedule_info[job.id] = schedule_time
        
        # 更新爬虫的调度时间
        # 由于现在所有爬虫都在一个任务中运行，我们需要找到 'evening_crawl' 任务
        evening_crawl_schedule = schedule_info.get('evening_crawl', '每天 20:00')
        
        for spider in spiders:
            # 除了手动运行的爬虫，其他都使用统一的调度时间
            if spider['schedule'] == '从调度器获取':
                spider['schedule'] = evening_crawl_schedule
        
        # 获取每个爬虫的最后执行记录
        for spider in spiders:
            source = Source.query.filter_by(name=spider['display_name']).first()
            if source:
                spider['source_id'] = source.id
                spider['last_crawl_at'] = source.last_crawl_at.isoformat() if source.last_crawl_at else None
                spider['status'] = source.status
                spider['error_msg'] = source.error_msg
                
                # 获取最近的爬取日志
                last_log = CrawlLog.query.filter_by(source_id=source.id)\
                    .order_by(desc(CrawlLog.started_at)).first()
                if last_log:
                    spider['last_log'] = {
                        'status': last_log.status,
                        'articles_count': last_log.articles_count,
                        'started_at': last_log.started_at.isoformat() if last_log.started_at else None,
                        'finished_at': last_log.finished_at.isoformat() if last_log.finished_at else None,
                    }
        
        return {'items': spiders}


@crawler_bp.route('/spiders/<spider_name>/run')
class SpiderRun(MethodView):
    @jwt_required()
    def post(self, spider_name):
        """手动运行爬虫"""
        user = admin_required()
        
        # 验证爬虫名称
        valid_spiders = [
            # 新增爬虫
            'ccer', 'mysteel', 'cnmn_paper', 'smm_metal',
            # 原有爬虫
            'xinhua_real', 'chinapower', 'power', 'ndrc', 'nea', 'real_nea',
            'peopledaily', 'coal', 'newenergy', 'cnenergy', 'energy_news', 'test'
        ]
        if spider_name not in valid_spiders:
            abort(400, message='无效的爬虫名称')
        
        # 检查是否已在运行
        from app import redis_client
        existing_pid = redis_client.get(f'crawler:{spider_name}:pid')
        if existing_pid:
            # 检查进程是否还在运行
            try:
                os.kill(int(existing_pid), 0)  # 0信号只检查进程是否存在
                abort(400, message='爬虫正在运行中')
            except OSError:
                # 进程不存在，清除旧的PID
                redis_client.delete(f'crawler:{spider_name}:pid')
        
        # 获取或创建 Source 记录
        source_names = {
            # 新增爬虫
            'ccer': '全国温室气体自愿减排交易系统',
            'mysteel': '我的钢铁网',
            'cnmn_paper': '中国有色金属报',
            'smm_metal': '上海有色金属网',
            # 原有爬虫
            'xinhua_real': '新华网',
            'chinapower': '中国电力网',
            'power': '北极星电力网',
            'ndrc': '国家发改委',
            'nea': '国家能源局（测试版）',
            'real_nea': '国家能源局',
            'peopledaily': '人民网',
            'coal': '中国煤炭市场网',
            'newenergy': '中国新能源网',
            'cnenergy': '中国能源网',
            'energy_news': '综合能源新闻',
            'test': '测试数据源'
        }
        
        source = Source.query.filter_by(name=source_names[spider_name]).first()
        if not source:
            source = Source(
                name=source_names[spider_name],
                url='',
                type='spider',
                status='active'
            )
            db.session.add(source)
            db.session.commit()
        
        # 创建爬取日志
        log = CrawlLog(
            source_id=source.id,
            status='running',
            started_at=datetime.now()
        )
        db.session.add(log)
        db.session.commit()
        
        # 异步执行爬虫
        try:
            # 获取项目根目录
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            crawler_path = os.path.join(project_root, 'crawler')
            scrapy_cmd = os.path.join(project_root, 'backend/venv/bin/scrapy')
            
            # 创建日志目录
            log_dir = os.path.join(project_root, 'logs', 'crawler')
            os.makedirs(log_dir, exist_ok=True)
            
            # 日志文件路径
            log_file = os.path.join(log_dir, f'{spider_name}_{log.id}.log')
            
            # 检查路径
            if not os.path.exists(crawler_path):
                abort(500, message=f'爬虫目录不存在: {crawler_path}')
            
            if not os.path.exists(scrapy_cmd):
                abort(500, message=f'Scrapy未安装: {scrapy_cmd}')
            
            # 打开日志文件
            log_file_handle = open(log_file, 'w', encoding='utf-8')
            
            # 写入启动信息
            log_file_handle.write(f"{'='*80}\n")
            log_file_handle.write(f"爬虫启动日志\n")
            log_file_handle.write(f"{'='*80}\n")
            log_file_handle.write(f"爬虫名称: {spider_name}\n")
            log_file_handle.write(f"数据源: {source_names[spider_name]}\n")
            log_file_handle.write(f"日志ID: {log.id}\n")
            log_file_handle.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file_handle.write(f"启动用户: {user.nickname or user.phone}\n")
            log_file_handle.write(f"{'='*80}\n\n")
            log_file_handle.flush()
            
            # 启动爬虫进程，输出重定向到日志文件
            process = subprocess.Popen(
                [scrapy_cmd, 'crawl', spider_name, '-s', f'LOG_FILE={log_file}'],
                cwd=crawler_path,
                stdout=log_file_handle,
                stderr=subprocess.STDOUT,
                text=True,
                env=os.environ.copy()
            )
            
            # 保存进程ID和日志文件路径到Redis
            redis_client.setex(
                f'crawler:{spider_name}:pid',
                3600,  # 1小时过期
                process.pid
            )
            redis_client.setex(
                f'crawler:{spider_name}:log_id',
                3600,
                log.id
            )
            redis_client.setex(
                f'crawler:{spider_name}:log_file',
                3600,
                log_file
            )
            
            # 更新 Source 状态
            source.status = 'running'
            source.last_crawl_at = datetime.now()
            db.session.commit()
            
            return {
                'message': f'爬虫 {spider_name} 已启动',
                'log_id': log.id,
                'pid': process.pid,
                'log_file': log_file
            }
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            
            log.status = 'failed'
            log.error_msg = f'{str(e)}\n{error_detail}'
            log.finished_at = datetime.now()
            
            source.status = 'error'
            source.error_msg = str(e)
            
            db.session.commit()
            
            # 记录详细错误到日志
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'爬虫启动失败: {spider_name}')
            logger.error(error_detail)
            
            abort(500, message=f'爬虫启动失败: {str(e)}')


@crawler_bp.route('/spiders/<spider_name>/stop')
class SpiderStop(MethodView):
    @jwt_required()
    def post(self, spider_name):
        """停止爬虫"""
        admin_required()
        
        from app import redis_client
        
        try:
            # 从Redis获取PID
            pid = redis_client.get(f'crawler:{spider_name}:pid')
            log_id = redis_client.get(f'crawler:{spider_name}:log_id')
            
            if not pid:
                return {'message': f'爬虫 {spider_name} 未在运行'}
            
            pid = int(pid)
            
            # 尝试终止进程
            try:
                os.kill(pid, signal.SIGTERM)
                
                # 等待进程结束
                import time
                for _ in range(5):
                    try:
                        os.kill(pid, 0)
                        time.sleep(0.5)
                    except OSError:
                        break
                else:
                    # 如果还没结束，强制杀死
                    os.kill(pid, signal.SIGKILL)
                
                # 更新日志状态
                if log_id:
                    log = CrawlLog.query.get(int(log_id))
                    if log and log.status == 'running':
                        log.status = 'failed'
                        log.error_msg = '手动停止'
                        log.finished_at = datetime.utcnow()
                        db.session.commit()
                
                # 更新Source状态
                source_names = {
                    # 新增爬虫
                    'ccer': '全国温室气体自愿减排交易系统',
                    'mysteel': '我的钢铁网',
                    'cnmn_paper': '中国有色金属报',
                    'smm_metal': '上海有色金属网',
                    # 原有爬虫
                    'xinhua_real': '新华网',
                    'chinapower': '中国电力网',
                    'power': '北极星电力网',
                    'ndrc': '国家发改委',
                    'nea': '国家能源局（测试版）',
                    'real_nea': '国家能源局',
                    'peopledaily': '人民网',
                    'coal': '中国煤炭市场网',
                    'newenergy': '中国新能源网',
                    'cnenergy': '中国能源网',
                    'energy_news': '综合能源新闻',
                    'test': '测试数据源'
                }
                source = Source.query.filter_by(name=source_names.get(spider_name)).first()
                if source:
                    source.status = 'active'
                    db.session.commit()
                
                # 清除Redis中的PID
                redis_client.delete(f'crawler:{spider_name}:pid')
                redis_client.delete(f'crawler:{spider_name}:log_id')
                
                return {'message': f'爬虫 {spider_name} 已停止'}
                
            except OSError as e:
                if e.errno == 3:  # No such process
                    # 进程已经不存在了
                    redis_client.delete(f'crawler:{spider_name}:pid')
                    redis_client.delete(f'crawler:{spider_name}:log_id')
                    return {'message': f'爬虫 {spider_name} 已停止'}
                else:
                    raise
                
        except Exception as e:
            abort(500, message=f'停止爬虫失败: {str(e)}')


@crawler_bp.route('/logs')
class CrawlLogList(MethodView):
    @jwt_required()
    def get(self):
        """获取爬取日志列表"""
        admin_required()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        spider_name = request.args.get('spider')
        
        query = CrawlLog.query
        
        # 按爬虫名称筛选
        if spider_name:
            source = Source.query.filter_by(name=spider_name).first()
            if source:
                query = query.filter_by(source_id=source.id)
        
        # 分页
        pagination = query.order_by(desc(CrawlLog.started_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        items = []
        for log in pagination.items:
            source = Source.query.get(log.source_id) if log.source_id else None
            items.append({
                'id': log.id,
                'source_name': source.name if source else None,
                'status': log.status,
                'articles_count': log.articles_count,
                'error_msg': log.error_msg,
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'finished_at': log.finished_at.isoformat() if log.finished_at else None,
                'duration': (log.finished_at - log.started_at).total_seconds() if log.finished_at and log.started_at else None
            })
        
        return {
            'items': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }


@crawler_bp.route('/logs/<int:log_id>')
class CrawlLogDetail(MethodView):
    @jwt_required()
    def get(self, log_id):
        """获取爬取日志详情"""
        admin_required()
        
        log = CrawlLog.query.get_or_404(log_id)
        source = Source.query.get(log.source_id) if log.source_id else None
        
        # 尝试读取日志文件
        log_content = None
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        log_file = os.path.join(project_root, 'logs', 'crawler', f'{source.name}_{log.id}.log')
        
        # 也尝试从 Redis 获取日志文件路径
        from app import redis_client
        redis_log_file = None
        for spider_name in ['ccer', 'mysteel', 'cnmn_paper', 'smm_metal', 'xinhua_real', 'chinapower', 
                           'power', 'ndrc', 'nea', 'real_nea', 'peopledaily', 'coal', 'newenergy', 
                           'cnenergy', 'energy_news', 'test']:
            redis_log_id = redis_client.get(f'crawler:{spider_name}:log_id')
            if redis_log_id and int(redis_log_id) == log_id:
                redis_log_file = redis_client.get(f'crawler:{spider_name}:log_file')
                if redis_log_file:
                    redis_log_file = redis_log_file.decode('utf-8') if isinstance(redis_log_file, bytes) else redis_log_file
                break
        
        # 优先使用 Redis 中的路径
        if redis_log_file and os.path.exists(redis_log_file):
            log_file = redis_log_file
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
            except Exception as e:
                log_content = f'读取日志文件失败: {str(e)}'
        
        return {
            'id': log.id,
            'source_id': log.source_id,
            'source_name': source.name if source else None,
            'status': log.status,
            'articles_count': log.articles_count,
            'error_msg': log.error_msg,
            'started_at': log.started_at.isoformat() if log.started_at else None,
            'finished_at': log.finished_at.isoformat() if log.finished_at else None,
            'duration': (log.finished_at - log.started_at).total_seconds() if log.finished_at and log.started_at else None,
            'log_content': log_content,
            'log_file': log_file if os.path.exists(log_file) else None
        }


@crawler_bp.route('/logs/<int:log_id>/tail')
class CrawlLogTail(MethodView):
    @jwt_required()
    def get(self, log_id):
        """实时查看爬虫日志（最后N行）"""
        admin_required()
        
        lines = request.args.get('lines', 100, type=int)
        
        log = CrawlLog.query.get_or_404(log_id)
        source = Source.query.get(log.source_id) if log.source_id else None
        
        # 获取日志文件路径
        from app import redis_client
        log_file = None
        
        # 从 Redis 获取日志文件路径
        for spider_name in ['ccer', 'mysteel', 'cnmn_paper', 'smm_metal', 'xinhua_real', 'chinapower', 
                           'power', 'ndrc', 'nea', 'real_nea', 'peopledaily', 'coal', 'newenergy', 
                           'cnenergy', 'energy_news', 'test']:
            redis_log_id = redis_client.get(f'crawler:{spider_name}:log_id')
            if redis_log_id and int(redis_log_id) == log_id:
                redis_log_file = redis_client.get(f'crawler:{spider_name}:log_file')
                if redis_log_file:
                    log_file = redis_log_file.decode('utf-8') if isinstance(redis_log_file, bytes) else redis_log_file
                break
        
        # 如果 Redis 中没有，尝试默认路径
        if not log_file:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            log_file = os.path.join(project_root, 'logs', 'crawler', f'{source.name}_{log.id}.log')
        
        if not os.path.exists(log_file):
            return {
                'log_content': '日志文件不存在',
                'log_file': log_file,
                'lines': 0
            }
        
        try:
            # 读取最后N行
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                log_content = ''.join(tail_lines)
            
            return {
                'log_content': log_content,
                'log_file': log_file,
                'lines': len(tail_lines),
                'total_lines': len(all_lines)
            }
        except Exception as e:
            return {
                'log_content': f'读取日志失败: {str(e)}',
                'log_file': log_file,
                'lines': 0
            }, 500


@crawler_bp.route('/progress')
class CrawlerProgress(MethodView):
    @jwt_required()
    def get(self):
        """获取所有运行中爬虫的实时进度"""
        admin_required()
        
        from app import redis_client
        import re
        
        # 所有爬虫名称
        all_spiders = [
            'ccer', 'mysteel', 'cnmn_paper', 'smm_metal',
            'xinhua_real', 'chinapower', 'power', 'ndrc', 'nea',
            'peopledaily', 'coal', 'newenergy', 'cnenergy', 'energy_news'
        ]
        
        source_names = {
            'ccer': '全国温室气体自愿减排交易系统',
            'mysteel': '我的钢铁网',
            'cnmn_paper': '中国有色金属报',
            'smm_metal': '上海有色金属网',
            'xinhua_real': '新华网',
            'chinapower': '中国电力网',
            'power': '北极星电力网',
            'ndrc': '国家发改委',
            'nea': '国家能源局（测试版）',
            'peopledaily': '人民网',
            'coal': '中国煤炭市场网',
            'newenergy': '中国新能源网',
            'cnenergy': '中国能源网',
            'energy_news': '综合能源新闻',
        }
        
        progress_list = []
        
        for spider_name in all_spiders:
            # 检查是否在运行
            pid = redis_client.get(f'crawler:{spider_name}:pid')
            log_id = redis_client.get(f'crawler:{spider_name}:log_id')
            log_file_path = redis_client.get(f'crawler:{spider_name}:log_file')
            
            if not pid or not log_id:
                continue
            
            # 解码
            if isinstance(log_file_path, bytes):
                log_file_path = log_file_path.decode('utf-8')
            
            log_id = int(log_id)
            
            # 获取日志记录
            log = CrawlLog.query.get(log_id)
            if not log:
                continue
            
            # 读取日志文件，提取进度信息
            progress_info = {
                'spider_name': spider_name,
                'display_name': source_names.get(spider_name, spider_name),
                'log_id': log_id,
                'status': 'running',
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'duration': (datetime.now() - log.started_at).total_seconds() if log.started_at else 0,
                'items_scraped': 0,
                'pages_crawled': 0,
                'requests_count': 0,
                'last_log_line': '',
            }
            
            # 尝试读取日志文件
            if log_file_path and os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                        # 提取最后一行非空日志
                        for line in reversed(lines):
                            if line.strip():
                                progress_info['last_log_line'] = line.strip()[-200:]  # 最后200字符
                                break
                        
                        # 从日志中提取统计信息
                        log_content = ''.join(lines[-100:])  # 最后100行
                        
                        # 提取抓取的文章数
                        items_match = re.search(r'scraped (\d+) items', log_content)
                        if items_match:
                            progress_info['items_scraped'] = int(items_match.group(1))
                        
                        # 提取爬取的页面数
                        pages_match = re.search(r'Crawled (\d+) pages', log_content)
                        if pages_match:
                            progress_info['pages_crawled'] = int(pages_match.group(1))
                        
                        # 提取请求数
                        requests_match = re.search(r"'downloader/request_count': (\d+)", log_content)
                        if requests_match:
                            progress_info['requests_count'] = int(requests_match.group(1))
                        
                        # 检查是否完成
                        if 'Spider closed' in log_content or 'finish_reason' in log_content:
                            progress_info['status'] = 'finishing'
                        
                except Exception as e:
                    progress_info['error'] = str(e)
            
            progress_list.append(progress_info)
        
        return {
            'items': progress_list,
            'total_running': len(progress_list)
        }


@crawler_bp.route('/stats')
class CrawlerStats(MethodView):
    @jwt_required()
    def get(self):
        """获取爬虫统计信息"""
        admin_required()
        
        from sqlalchemy import func
        from app.models import Article
        
        # 总文章数
        total_articles = Article.query.count()
        
        # 今日抓取数
        today = datetime.utcnow().date()
        today_articles = Article.query.filter(
            func.date(Article.created_at) == today
        ).count()
        
        # 按分类统计
        category_stats = db.session.query(
            Article.category,
            func.count(Article.id).label('count')
        ).group_by(Article.category).all()
        
        # 按来源统计
        source_stats = db.session.query(
            Article.source,
            func.count(Article.id).label('count')
        ).group_by(Article.source).all()
        
        # 最近7天趋势
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(Article.created_at).label('date'),
            func.count(Article.id).label('count')
        ).filter(Article.created_at >= seven_days_ago)\
         .group_by(func.date(Article.created_at)).all()
        
        # 爬虫状态统计
        sources = Source.query.all()
        spider_stats = {
            'total': len(sources),
            'active': len([s for s in sources if s.status == 'active']),
            'error': len([s for s in sources if s.status == 'error']),
            'running': len([s for s in sources if s.status == 'running'])
        }
        
        return {
            'total_articles': total_articles,
            'today_articles': today_articles,
            'category_stats': [{'category': c, 'count': count} for c, count in category_stats],
            'source_stats': [{'source': s, 'count': count} for s, count in source_stats],
            'daily_stats': [{'date': str(d), 'count': count} for d, count in daily_stats],
            'spider_stats': spider_stats
        }


@crawler_bp.route('/schedule')
class CrawlerSchedule(MethodView):
    @jwt_required()
    def get(self):
        """获取所有定时任务"""
        admin_required()
        
        from app.scheduler import list_jobs
        
        jobs = list_jobs()
        
        # 增强任务信息
        for job in jobs:
            # 判断任务是否暂停（通过检查next_run_time）
            job['is_paused'] = job['next_run_time'] is None
            
            # 添加任务类型标签
            if 'crawl' in job['id']:
                job['type'] = 'crawler'
            elif 'brief' in job['id']:
                job['type'] = 'ai_brief'
            elif 'trial' in job['id'] or 'subscription' in job['id']:
                job['type'] = 'subscription'
            else:
                job['type'] = 'other'
        
        return {'items': jobs}


@crawler_bp.route('/schedule/<job_id>/pause')
class CrawlerSchedulePause(MethodView):
    @jwt_required()
    def post(self, job_id):
        """暂停定时任务"""
        admin_required()
        
        from app.scheduler import pause_job
        
        success = pause_job(job_id)
        
        if success:
            return {'message': f'任务 {job_id} 已暂停'}
        else:
            abort(500, message=f'暂停任务 {job_id} 失败')


@crawler_bp.route('/schedule/<job_id>/resume')
class CrawlerScheduleResume(MethodView):
    @jwt_required()
    def post(self, job_id):
        """恢复定时任务"""
        admin_required()
        
        from app.scheduler import resume_job
        
        success = resume_job(job_id)
        
        if success:
            return {'message': f'任务 {job_id} 已恢复'}
        else:
            abort(500, message=f'恢复任务 {job_id} 失败')


@crawler_bp.route('/schedule/<job_id>/trigger')
class CrawlerScheduleTrigger(MethodView):
    @jwt_required()
    def post(self, job_id):
        """立即触发定时任务"""
        admin_required()
        
        from app.scheduler import trigger_job
        
        success = trigger_job(job_id)
        
        if success:
            return {'message': f'任务 {job_id} 已触发'}
        else:
            abort(500, message=f'触发任务 {job_id} 失败')


@crawler_bp.route('/spiders/run-all')
class SpiderRunAll(MethodView):
    @jwt_required()
    def post(self):
        """一键运行所有爬虫"""
        user = admin_required()
        
        # 所有可用的爬虫
        all_spiders = [
            'ccer', 'mysteel', 'cnmn_paper', 'smm_metal',
            'xinhua_real', 'chinapower', 'power', 'ndrc', 'nea',
            'peopledaily', 'coal', 'newenergy', 'cnenergy', 'energy_news'
        ]
        
        from app import redis_client
        
        # 检查哪些爬虫可以启动（未在运行中）
        available_spiders = []
        running_spiders = []
        
        for spider_name in all_spiders:
            existing_pid = redis_client.get(f'crawler:{spider_name}:pid')
            if existing_pid:
                try:
                    os.kill(int(existing_pid), 0)
                    running_spiders.append(spider_name)
                except OSError:
                    redis_client.delete(f'crawler:{spider_name}:pid')
                    available_spiders.append(spider_name)
            else:
                available_spiders.append(spider_name)
        
        if not available_spiders:
            return {
                'message': '所有爬虫都在运行中',
                'running_count': len(running_spiders),
                'running_spiders': running_spiders
            }, 400
        
        # 启动所有可用的爬虫
        started_spiders = []
        failed_spiders = []
        
        source_names = {
            'ccer': '全国温室气体自愿减排交易系统',
            'mysteel': '我的钢铁网',
            'cnmn_paper': '中国有色金属报',
            'smm_metal': '上海有色金属网',
            'xinhua_real': '新华网',
            'chinapower': '中国电力网',
            'power': '北极星电力网',
            'ndrc': '国家发改委',
            'nea': '国家能源局（测试版）',
            'peopledaily': '人民网',
            'coal': '中国煤炭市场网',
            'newenergy': '中国新能源网',
            'cnenergy': '中国能源网',
            'energy_news': '综合能源新闻',
        }
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        crawler_path = os.path.join(project_root, 'crawler')
        scrapy_cmd = os.path.join(project_root, 'backend/venv/bin/scrapy')
        log_dir = os.path.join(project_root, 'logs', 'crawler')
        os.makedirs(log_dir, exist_ok=True)
        
        for spider_name in available_spiders:
            try:
                # 获取或创建 Source 记录
                source = Source.query.filter_by(name=source_names[spider_name]).first()
                if not source:
                    source = Source(
                        name=source_names[spider_name],
                        url='',
                        type='spider',
                        status='active'
                    )
                    db.session.add(source)
                    db.session.commit()
                
                # 创建爬取日志
                log = CrawlLog(
                    source_id=source.id,
                    status='running',
                    started_at=datetime.now()
                )
                db.session.add(log)
                db.session.commit()
                
                # 日志文件路径
                log_file = os.path.join(log_dir, f'{spider_name}_{log.id}.log')
                
                # 打开日志文件
                log_file_handle = open(log_file, 'w', encoding='utf-8')
                
                # 写入启动信息
                log_file_handle.write(f"{'='*80}\n")
                log_file_handle.write(f"爬虫启动日志（批量启动）\n")
                log_file_handle.write(f"{'='*80}\n")
                log_file_handle.write(f"爬虫名称: {spider_name}\n")
                log_file_handle.write(f"数据源: {source_names[spider_name]}\n")
                log_file_handle.write(f"日志ID: {log.id}\n")
                log_file_handle.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file_handle.write(f"启动用户: {user.nickname or user.phone}\n")
                log_file_handle.write(f"启动方式: 批量启动\n")
                log_file_handle.write(f"{'='*80}\n\n")
                log_file_handle.flush()
                
                # 启动爬虫进程
                process = subprocess.Popen(
                    [scrapy_cmd, 'crawl', spider_name, '-s', f'LOG_FILE={log_file}'],
                    cwd=crawler_path,
                    stdout=log_file_handle,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=os.environ.copy()
                )
                
                # 保存进程ID到Redis
                redis_client.setex(f'crawler:{spider_name}:pid', 3600, process.pid)
                redis_client.setex(f'crawler:{spider_name}:log_id', 3600, log.id)
                redis_client.setex(f'crawler:{spider_name}:log_file', 3600, log_file)
                
                # 更新 Source 状态
                source.status = 'running'
                source.last_crawl_at = datetime.now()
                db.session.commit()
                
                started_spiders.append({
                    'name': spider_name,
                    'display_name': source_names[spider_name],
                    'log_id': log.id,
                    'pid': process.pid
                })
                
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                
                failed_spiders.append({
                    'name': spider_name,
                    'display_name': source_names.get(spider_name),
                    'error': str(e)
                })
                
                # 记录错误日志
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'批量启动爬虫失败: {spider_name}')
                logger.error(error_detail)
        
        return {
            'message': f'成功启动 {len(started_spiders)} 个爬虫',
            'started_count': len(started_spiders),
            'failed_count': len(failed_spiders),
            'running_count': len(running_spiders),
            'started_spiders': started_spiders,
            'failed_spiders': failed_spiders,
            'running_spiders': running_spiders
        }
