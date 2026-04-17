#!/bin/bash

echo "🚀 启动后端服务（端口5001）"
echo "================================"

# 检查虚拟环境
if [ ! -d "backend/venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: cd backend && python -m venv venv"
    exit 1
fi

# 检查数据库
if ! docker ps | grep -q energy_mysql; then
    echo "⚠️  MySQL未运行，正在启动..."
    docker-compose up -d mysql redis
    echo "⏳ 等待数据库启动..."
    sleep 5
fi

# 启动后端
cd backend
source venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "🔧 启动Flask应用..."
echo ""

python run_backend.py
