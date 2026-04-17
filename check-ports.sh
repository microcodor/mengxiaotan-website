#!/bin/bash

echo "🔍 检查端口占用情况"
echo "===================="

# 检测操作系统
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="Linux";;
    Darwin*)    OS="Mac";;
    *)          OS="unknown";;
esac

echo "📍 操作系统: $OS"
echo ""

# 检查端口函数
check_port() {
    local port=$1
    local service=$2
    
    if [ "$OS" = "Mac" ]; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ 端口 $port ($service) 已被占用"
            echo "   进程信息:"
            lsof -Pi :$port -sTCP:LISTEN
            return 1
        else
            echo "✅ 端口 $port ($service) 可用"
            return 0
        fi
    elif [ "$OS" = "Linux" ]; then
        if ss -ltn | grep -q ":$port " 2>/dev/null || netstat -ltn 2>/dev/null | grep -q ":$port "; then
            echo "❌ 端口 $port ($service) 已被占用"
            echo "   进程信息:"
            ss -ltnp 2>/dev/null | grep ":$port " || netstat -ltnp 2>/dev/null | grep ":$port "
            return 1
        else
            echo "✅ 端口 $port ($service) 可用"
            return 0
        fi
    fi
}

# 检查所需端口
echo "检查项目所需端口:"
echo ""

check_port 3306 "MySQL (默认)"
MYSQL_3306=$?

check_port 3307 "MySQL (备用)"
MYSQL_3307=$?

echo ""
check_port 6379 "Redis"
REDIS=$?

echo ""
check_port 5000 "后端 API"
BACKEND=$?

echo ""
check_port 5173 "前端开发服务器"
FRONTEND=$?

echo ""
echo "===================="
echo "检查结果汇总:"
echo ""

# 判断是否需要修改配置
if [ $MYSQL_3306 -eq 1 ]; then
    if [ $MYSQL_3307 -eq 0 ]; then
        echo "💡 建议: MySQL 3306 端口被占用，项目已配置使用 3307 端口"
        echo "   无需额外操作，直接运行 ./start.sh 即可"
    else
        echo "⚠️  警告: MySQL 3306 和 3307 端口都被占用"
        echo "   解决方案:"
        echo "   1. 停止占用端口的 MySQL 服务"
        echo "   2. 或修改 docker-compose.yml 使用其他端口（如 3308）"
    fi
else
    echo "✅ MySQL 可以使用默认 3306 端口"
    echo "   如果想使用默认端口，可以修改配置文件"
fi

echo ""

if [ $REDIS -eq 1 ]; then
    echo "⚠️  警告: Redis 6379 端口被占用"
    echo "   解决方案:"
    echo "   1. 停止占用端口的 Redis 服务: redis-cli shutdown"
    echo "   2. 或修改 docker-compose.yml 使用其他端口"
fi

if [ $BACKEND -eq 1 ]; then
    echo "⚠️  警告: 后端 5000 端口被占用"
    echo "   解决方案: 停止占用端口的进程"
    if [ "$OS" = "Mac" ]; then
        echo "   查看进程: lsof -i :5000"
        echo "   停止进程: kill -9 \$(lsof -t -i:5000)"
    fi
fi

if [ $FRONTEND -eq 1 ]; then
    echo "⚠️  警告: 前端 5173 端口被占用"
    echo "   解决方案: 停止占用端口的进程"
    if [ "$OS" = "Mac" ]; then
        echo "   查看进程: lsof -i :5173"
        echo "   停止进程: kill -9 \$(lsof -t -i:5173)"
    fi
fi

echo ""
echo "===================="

# 提供快速解决方案
if [ $MYSQL_3306 -eq 1 ] || [ $REDIS -eq 1 ] || [ $BACKEND -eq 1 ] || [ $FRONTEND -eq 1 ]; then
    echo ""
    echo "🔧 快速解决方案:"
    echo ""
    
    if [ $MYSQL_3306 -eq 1 ]; then
        echo "# 停止本地 MySQL (如果是通过 Homebrew 安装)"
        echo "brew services stop mysql"
        echo ""
    fi
    
    if [ $REDIS -eq 1 ]; then
        echo "# 停止本地 Redis"
        echo "redis-cli shutdown"
        echo "# 或"
        echo "brew services stop redis"
        echo ""
    fi
    
    echo "# 然后重新运行启动脚本"
    echo "./start.sh"
else
    echo ""
    echo "✅ 所有端口都可用，可以直接运行:"
    echo "   ./start.sh"
fi

echo ""
