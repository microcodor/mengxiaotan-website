#!/bin/bash

echo "🚀 快速启动后端服务"
echo "===================="

cd backend

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "✓ 激活虚拟环境..."
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行 start.sh"
    exit 1
fi

# 检查端口占用
echo ""
echo "🔍 检查端口 5001..."
PID=$(lsof -ti:5001 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "⚠️  端口 5001 被占用，PID: $PID"
    echo "   正在终止进程..."
    kill -9 $PID 2>/dev/null
    sleep 1
    echo "✓ 端口 5001 已释放"
fi

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development

# 启动后端
echo ""
echo "🔧 启动后端服务（端口 5001）..."
python app.py

