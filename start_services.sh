#!/bin/bash

echo "🚀 启动蒙小碳IM推送服务"
echo "========================"

# 检查后端是否运行
if lsof -i:5001 > /dev/null 2>&1; then
    echo "✅ 后端服务已在运行 (端口5001)"
else
    echo "🔧 启动后端服务..."
    cd backend
    ./venv/bin/python run_production.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    cd ..
    sleep 3
fi

# 检查前端是否运行
if lsof -i:5173 > /dev/null 2>&1; then
    echo "✅ 前端服务已在运行 (端口5173)"
else
    echo "🎨 启动前端服务..."
    cd frontend
    npm run dev > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    cd ..
    sleep 5
fi

echo ""
echo "========================"
echo "✅ 服务启动完成!"
echo "========================"
echo ""
echo "📱 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:5001"
echo ""
echo "🔑 测试账号:"
echo "   管理员: 13800138000 / admin123"
echo ""
echo "📝 推送设置:"
echo "   http://localhost:5173/dashboard/push"
echo ""
echo "📊 查看日志:"
echo "   后端: tail -f /tmp/backend.log"
echo "   前端: tail -f /tmp/frontend.log"
echo ""
