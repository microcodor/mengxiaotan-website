#!/bin/bash

# 快速启动脚本（跳过检查）

echo "🚀 快速启动蒙小碳·能源站"
echo "===================================="

# 启动后端
echo "🔧 启动后端服务..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "✓ 后端服务已启动 (PID: $BACKEND_PID)"
cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✓ 前端服务已启动 (PID: $FRONTEND_PID)"
cd ..

# 保存PID
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo ""
echo "✅ 启动完成！"
echo "===================================="
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端地址: http://localhost:5001"
echo "📊 管理后台: http://localhost:5173/admin"
echo ""
echo "👤 登录信息："
echo "   管理员: 13800138000 / admin123"
echo "   测试用户: 13900139000 / test123"
echo ""
echo "🛑 停止服务: ./stop_local.sh 或按 Ctrl+C"
echo ""

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo '✓ 服务已停止'; exit 0" INT TERM

wait
