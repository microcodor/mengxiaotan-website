#!/usr/bin/env python3
"""
生产模式启动脚本(不使用debug模式)
"""
from app import create_app, db
from app.models import *
from app.scheduler import init_scheduler

app = create_app()

# 初始化定时任务
init_scheduler(app)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Article': Article,
        'Subscription': Subscription,
        'SubscriptionPlan': SubscriptionPlan
    }

if __name__ == '__main__':
    # 不使用debug模式,避免reloader导致的问题
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
