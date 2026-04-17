#!/bin/bash

# 本地开发环境启动脚本
# 使用本地PostgreSQL和Redis

set -e

echo "🚀 启动蒙小碳·能源站（本地开发环境）"
echo "===================================="

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_TYPE=Linux;;
    Darwin*)    OS_TYPE=Mac;;
    *)          OS_TYPE="UNKNOWN:${OS}"
esac

echo "📍 检测到操作系统: $OS_TYPE"

# 检查Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到Python，请先安装Python 3.8+"
    exit 1
fi

echo "✓ 使用 Python 命令: $PYTHON_CMD"

# 检查Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js 版本: $NODE_VERSION"
else
    echo "❌ 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

# 检查MySQL连接
echo ""
echo "🔍 检查MySQL连接..."

# 查找MySQL命令
MYSQL_CMD=""
if command -v mysql &> /dev/null; then
    MYSQL_CMD="mysql"
elif [ -f "/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql" ]; then
    MYSQL_CMD="/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql"
elif [ -f "/usr/local/mysql/bin/mysql" ]; then
    MYSQL_CMD="/usr/local/mysql/bin/mysql"
fi

if [ -n "$MYSQL_CMD" ]; then
    if $MYSQL_CMD -h localhost -P 3306 -u root -pjinchun123 -e "SELECT 1" &> /dev/null; then
        echo "✓ MySQL连接成功"
    else
        echo "⚠️  MySQL连接失败，请确保MySQL正在运行"
        echo "   Host: localhost:3306"
        echo "   User: root"
        echo "   Password: jinchun123"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  未找到mysql命令，跳过MySQL连接检查"
fi

# 检查Redis连接
echo ""
echo "🔍 检查Redis连接..."
if command -v redis-cli &> /dev/null; then
    if redis-cli -h localhost -p 6379 -a 123456 PING &> /dev/null; then
        echo "✓ Redis连接成功"
    else
        echo "⚠️  Redis连接失败，请确保Redis正在运行"
        echo "   Host: localhost:6379"
        echo "   Password: 123456"
        read -p "是否继续？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  未找到redis-cli命令，跳过Redis连接检查"
fi

# 检查端口占用
echo ""
echo "🔍 检查端口占用..."

check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  端口 $port ($service) 被占用"
        local pid=$(lsof -ti:$port)
        echo "   PID: $pid"
        read -p "   是否终止该进程？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 $pid 2>/dev/null || true
            echo "✓ 端口 $port 已释放"
        fi
    else
        echo "✓ 端口 $port ($service) 可用"
    fi
}

check_port 5001 "后端服务"
check_port 5173 "前端服务"

echo "✓ 端口检查完成"

# 安装后端依赖
echo ""
echo "📦 安装后端依赖..."
cd backend

if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

echo "激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✓ 后端依赖安装完成"

# 初始化数据库
echo ""
echo "🗄️  初始化数据库..."

# 创建数据库（如果不存在）
echo "检查数据库是否存在..."

# 查找MySQL命令
MYSQL_CMD=""
if command -v mysql &> /dev/null; then
    MYSQL_CMD="mysql"
elif [ -f "/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql" ]; then
    MYSQL_CMD="/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql"
elif [ -f "/usr/local/mysql/bin/mysql" ]; then
    MYSQL_CMD="/usr/local/mysql/bin/mysql"
fi

if [ -n "$MYSQL_CMD" ]; then
    if $MYSQL_CMD -h localhost -P 3306 -u root -pjinchun123 -e "USE energy_station;" &> /dev/null; then
        echo "✓ 数据库 energy_station 已存在"
    else
        echo "创建数据库 energy_station..."
        $MYSQL_CMD -h localhost -P 3306 -u root -pjinchun123 -e "CREATE DATABASE energy_station CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true
        echo "✓ 数据库创建完成"
    fi
else
    echo "⚠️  未找到mysql命令，跳过数据库创建"
fi

# 运行数据库迁移
echo "运行数据库迁移..."
$PYTHON_CMD init_db.py

echo "✓ 数据库初始化完成"

# 启动后端服务
echo ""
echo "🔧 启动后端服务..."
$PYTHON_CMD app.py &
BACKEND_PID=$!
echo "✓ 后端服务已启动 (PID: $BACKEND_PID)"

cd ..

# 安装前端依赖
echo ""
echo "📦 安装前端依赖..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "安装Node.js依赖..."
    npm install
else
    echo "✓ Node.js依赖已安装"
fi

# 启动前端服务
echo ""
echo "🎨 启动前端服务..."
npm run dev &
FRONTEND_PID=$!
echo "✓ 前端服务已启动 (PID: $FRONTEND_PID)"

cd ..

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 3

# 显示启动信息
echo ""
echo "✅ 启动完成！"
echo "===================================="
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端地址: http://localhost:5001"
echo "📊 管理后台: http://localhost:5173/admin"
echo "📈 数据看板: http://localhost:5173/dashboard"
echo ""
echo "🗄️  数据库信息："
echo "   MySQL: localhost:3306"
echo "   Database: energy_station"
echo "   User: root"
echo ""
echo "   Redis: localhost:6379"
echo ""
echo "👤 登录信息："
echo "   管理员: 13800138000 / admin123"
echo "   测试用户: 13900139000 / test123"
echo ""
echo "📝 查看日志："
echo "   后端日志: tail -f backend/logs/app.log"
echo ""
echo "🛑 停止服务："
echo "   按 Ctrl+C 或运行 ./stop_local.sh"
echo ""

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo '✓ 服务已停止'; exit 0" INT TERM

wait
