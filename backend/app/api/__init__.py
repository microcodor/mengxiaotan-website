from flask_smorest import Blueprint

auth_bp = Blueprint('auth', 'auth', url_prefix='/api/auth', description='认证相关接口')
articles_bp = Blueprint('articles', 'articles', url_prefix='/api/articles', description='文章相关接口')
users_bp = Blueprint('users', 'users', url_prefix='/api/users', description='用户相关接口')
subscriptions_bp = Blueprint('subscriptions', 'subscriptions', url_prefix='/api/subscriptions', description='订阅相关接口')
permissions_bp = Blueprint('permissions', 'permissions', url_prefix='/api/permissions', description='权限相关接口')
admin_bp = Blueprint('admin', 'admin', url_prefix='/api/admin', description='管理后台接口')
push_bp = Blueprint('push', 'push', url_prefix='/api/push', description='推送相关接口')
crawler_bp = Blueprint('crawler', 'crawler', url_prefix='/api/crawler', description='爬虫管理接口')
categories_bp = Blueprint('categories', 'categories', url_prefix='/api/categories', description='分类管理接口')
company_bp = Blueprint('company', 'company', url_prefix='/api/company', description='企业信息管理接口')
scheduler_bp = Blueprint('scheduler', 'scheduler', url_prefix='/api/scheduler', description='定时任务管理接口')
monitor_bp = Blueprint('monitor', 'monitor', url_prefix='/api/monitor', description='监控告警接口')
briefs_bp = Blueprint('briefs', 'briefs', url_prefix='/api/briefs', description='AI简报相关接口')
company_profile_bp = Blueprint('company_profile', 'company_profile', url_prefix='/api/company-profile', description='企业画像接口')
simulation_bp = Blueprint('simulation', 'simulation', url_prefix='/api/simulation', description='数字分身沙盘接口')
reports_bp = Blueprint('reports', 'reports', url_prefix='/api/reports', description='定制报告接口')
monitoring_bp = Blueprint('monitoring', 'monitoring', url_prefix='/api/monitoring', description='动态监测预警接口')

from app.api import auth, articles, users, subscriptions, permissions, admin, push, crawler, categories, company, scheduler, monitor, briefs, company_profile, simulation, reports, monitoring

# 导入push_settings的blp
from app.api.push_settings import blp as push_settings_bp
