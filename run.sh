#!/bin/bash

echo "🚀 启动蒙小碳能源站"
echo "================================"

# 启动数据库
echo "📦 启动数据库..."
docker-compose up -d mysql redis
sleep 3

# 启动后端
echo "🔧 启动后端（端口5001）..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端（端口5173）..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "================================"
echo "✅ 所有服务已启动"
echo "================================"
echo "🌐 前端地址: http://localhost:5173"
echo "📡 后端地址: http://localhost:5001"
echo "👤 管理员账号: 13800138000 / admin123"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "================================"

# 等待用户中断
wait
