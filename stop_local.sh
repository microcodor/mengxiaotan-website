#!/bin/bash

# 本地开发环境停止脚本

echo "🛑 停止蒙小碳·能源站（本地开发环境）"
echo "===================================="

# 停止后端服务
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        echo "✓ 后端服务已停止"
    fi
    rm -f .backend.pid
fi

# 停止前端服务
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✓ 前端服务已停止"
    fi
    rm -f .frontend.pid
fi

# 清理端口
echo ""
echo "🔍 清理端口..."

cleanup_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "清理端口 $port ($service)..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        echo "✓ 端口 $port 已清理"
    fi
}

cleanup_port 5001 "后端服务"
cleanup_port 5173 "前端服务"

echo ""
echo "✅ 所有服务已停止"
