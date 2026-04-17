#!/bin/bash

echo "🛑 停止蒙小碳·能源站"
echo "===================="

# 检测操作系统
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="Linux";;
    Darwin*)    OS="Mac";;
    CYGWIN*)    OS="Windows";;
    MINGW*)     OS="Windows";;
    MSYS*)      OS="Windows";;
    *)          OS="unknown";;
esac

echo "📍 检测到操作系统: $OS"

# 检测 Docker Compose 命令
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose 未找到"
    exit 1
fi

# 停止 Docker 容器
echo ""
echo "📦 停止 Docker 容器..."
$DOCKER_COMPOSE_CMD down

# 停止占用端口的进程
echo ""
echo "🔍 清理端口占用..."

PORTS=(5001 5173)
PORT_NAMES=("后端服务" "前端服务")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    
    if [ "$OS" = "Mac" ] || [ "$OS" = "Linux" ]; then
        # Mac/Linux 使用 lsof
        PID=$(lsof -ti:$PORT 2>/dev/null)
        if [ ! -z "$PID" ]; then
            echo "⚠️  停止 $NAME (端口 $PORT, PID: $PID)"
            kill -9 $PID 2>/dev/null
            sleep 1
            echo "✓ $NAME 已停止"
        fi
    elif [ "$OS" = "Windows" ]; then
        # Windows 使用 netstat
        PID=$(netstat -ano | grep ":$PORT " | awk '{print $5}' | head -1)
        if [ ! -z "$PID" ] && [ "$PID" != "0" ]; then
            echo "⚠️  停止 $NAME (端口 $PORT, PID: $PID)"
            taskkill //PID $PID //F 2>/dev/null
            sleep 1
            echo "✓ $NAME 已停止"
        fi
    fi
done

# 额外清理：查找并停止相关进程
echo ""
echo "🔧 清理残留进程..."
if [ "$OS" = "Windows" ]; then
    taskkill //F //IM python.exe 2>/dev/null || true
    taskkill //F //IM node.exe 2>/dev/null || true
else
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "flask run" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
fi

echo ""
echo "✅ 所有服务已停止"
echo "===================="
