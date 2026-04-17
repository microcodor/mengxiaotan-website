#!/bin/bash

echo "🚀 启动后端服务"
echo "================================"

cd backend

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在"
    exit 1
fi

# 使用5001端口启动（避免5000端口冲突）
export FLASK_APP=app.py
export FLASK_ENV=development

echo "🔧 启动Flask应用（端口5001）..."
python -c "
from app import create_app
from app.scheduler import init_scheduler

app = create_app()
init_scheduler()

print('=' * 60)
print('🚀 后端服务已启动')
print('=' * 60)
print('📡 地址: http://0.0.0.0:5001')
print('👤 管理员: admin / admin123')
print('=' * 60)

app.run(host='0.0.0.0', port=5001, debug=True)
"
