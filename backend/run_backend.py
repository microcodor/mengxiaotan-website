#!/usr/bin/env python
"""
后端服务启动脚本
使用5001端口避免与系统ControlCenter冲突
"""
from app import create_app
from app.scheduler import init_scheduler

app = create_app()
init_scheduler(app)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 蒙小碳能源站 - 后端服务")
    print("=" * 50)
    print(f"📡 服务地址: http://0.0.0.0:5001")
    print(f"📝 API文档: http://localhost:5001/api")
    print(f"👤 管理员账号: admin / admin123")
    print("=" * 50)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True)
