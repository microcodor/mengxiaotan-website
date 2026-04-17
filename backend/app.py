from app import create_app, db
from app.models import *
from app.scheduler import init_scheduler
from flask import jsonify
from datetime import datetime

app = create_app()

# 初始化定时任务
init_scheduler(app)

# 健康检查端点
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

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
    app.run(host='0.0.0.0', port=5001, debug=True)
