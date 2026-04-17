#!/bin/bash

echo "🚀 启动蒙小碳·能源站"
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

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "   下载地址: https://www.docker.com/get-started"
    exit 1
fi

# 检查 Docker Compose 命令
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✓ 使用 docker-compose 命令"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "✓ 使用 docker compose 命令"
else
    echo "❌ Docker Compose 未安装或不可用"
    echo "   请安装 Docker Compose 或更新 Docker Desktop"
    exit 1
fi

# 检查 Python 命令
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python 未安装，请先安装 Python 3.9+"
    exit 1
fi

echo "✓ 使用 Python 命令: $PYTHON_CMD"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    echo "   下载地址: https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js 版本: $(node --version)"

# 检查并清理端口占用
echo ""
echo "🔍 检查端口占用..."

# 定义需要检查的端口
PORTS=(5001 5173 3307 6380)
PORT_NAMES=("后端服务" "前端服务" "MySQL" "Redis")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    
    if [ "$OS" = "Mac" ] || [ "$OS" = "Linux" ]; then
        # Mac/Linux 使用 lsof
        PID=$(lsof -ti:$PORT 2>/dev/null)
        if [ ! -z "$PID" ]; then
            echo "⚠️  端口 $PORT ($NAME) 被占用，PID: $PID"
            echo "   正在终止进程..."
            kill -9 $PID 2>/dev/null
            sleep 1
            echo "✓ 端口 $PORT 已释放"
        fi
    elif [ "$OS" = "Windows" ]; then
        # Windows 使用 netstat
        PID=$(netstat -ano | grep ":$PORT " | awk '{print $5}' | head -1)
        if [ ! -z "$PID" ] && [ "$PID" != "0" ]; then
            echo "⚠️  端口 $PORT ($NAME) 被占用，PID: $PID"
            echo "   正在终止进程..."
            taskkill //PID $PID //F 2>/dev/null
            sleep 1
            echo "✓ 端口 $PORT 已释放"
        fi
    fi
done

echo "✓ 端口检查完成"

# 启动 Docker 服务
echo ""
echo "📦 启动 Docker 容器..."
$DOCKER_COMPOSE_CMD up -d mysql redis

if [ $? -ne 0 ]; then
    echo "❌ Docker 容器启动失败"
    exit 1
fi

echo "⏳ 等待数据库启动..."
sleep 10

# 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
cd backend

# 根据操作系统选择虚拟环境激活方式
if [ "$OS" = "Windows" ]; then
    # Windows 环境
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/Scripts/activate 2>/dev/null || . venv/Scripts/activate
else
    # Linux/Mac 环境
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    source venv/bin/activate
fi

# 安装依赖
echo "📦 安装 Python 依赖..."
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "⚠️  使用国内镜像源重试..."
    python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 初始化数据库
$PYTHON_CMD init_db.py

if [ $? -ne 0 ]; then
    echo "❌ 数据库初始化失败"
    cd ..
    exit 1
fi

cd ..

# 启动后端
echo ""
echo "🔧 启动后端服务..."
cd backend

if [ "$OS" = "Windows" ]; then
    source venv/Scripts/activate 2>/dev/null || . venv/Scripts/activate
else
    source venv/bin/activate
fi

export FLASK_APP=app.py
export FLASK_ENV=development

# 根据操作系统选择后台运行方式
if [ "$OS" = "Windows" ]; then
    start /B $PYTHON_CMD app.py
    BACKEND_PID=$!
else
    $PYTHON_CMD app.py &
    BACKEND_PID=$!
fi

cd ..

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "🎨 启动前端服务..."
cd frontend

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

npm install

if [ $? -ne 0 ]; then
    echo "❌ 前端依赖安装失败"
    kill $BACKEND_PID 2>/dev/null
    cd ..
    exit 1
fi

# 根据操作系统选择后台运行方式
if [ "$OS" = "Windows" ]; then
    start /B npm run dev
    FRONTEND_PID=$!
else
    npm run dev &
    FRONTEND_PID=$!
fi

cd ..

# 等待服务启动
sleep 3

echo ""
echo "✅ 启动完成！"
echo "===================="
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端地址: http://localhost:5001"
echo "📊 管理后台: http://localhost:5173/admin"
echo "📈 数据看板: http://localhost:5173/dashboard"
echo ""
echo "🗄️  数据库信息："
echo "   MySQL: localhost:3307"
echo "   Redis: localhost:6380"
echo ""
echo "👤 登录信息："
echo "   管理员: 13800138000 / admin123"
echo "   测试用户: 13900139000 / test123"
echo ""
echo "📝 查看日志："
echo "   后端日志: $DOCKER_COMPOSE_CMD logs -f backend"
echo "   数据库日志: $DOCKER_COMPOSE_CMD logs -f mysql"
echo ""
echo "🛑 停止服务："
echo "   按 Ctrl+C 或运行 ./stop.sh"
echo ""

# 等待用户中断
if [ "$OS" = "Windows" ]; then
    echo "Windows 环境下请手动关闭窗口或使用 stop.sh 停止服务"
    wait
else
    trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; $DOCKER_COMPOSE_CMD down; echo '✅ 服务已停止'; exit" INT TERM
    wait
fi
