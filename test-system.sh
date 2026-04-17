#!/bin/bash

echo "🧪 系统完整测试"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_command() {
    local name=$1
    local command=$2
    
    echo -n "测试 $name... "
    if eval "$command" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 1. 检查必要的命令
echo ""
echo "📋 检查系统依赖"
echo "--------------------------------"

test_command "Python3" "command -v python3"
test_command "Docker" "command -v docker"
test_command "Docker Compose" "docker compose version || docker-compose --version"
test_command "Node.js" "command -v node"
test_command "npm" "command -v npm"

# 2. 检查 Python 版本
echo ""
echo "🐍 检查 Python 环境"
echo "--------------------------------"

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "Python 版本: $PYTHON_VERSION"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo -e "${GREEN}✓${NC} Python 版本满足要求 (>= 3.9)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Python 版本过低，需要 3.9+"
    ((TESTS_FAILED++))
fi

# 3. 检查 Node.js 版本
echo ""
echo "📦 检查 Node.js 环境"
echo "--------------------------------"

NODE_VERSION=$(node --version)
echo "Node.js 版本: $NODE_VERSION"

if node -e "process.exit(parseInt(process.version.slice(1)) >= 18 ? 0 : 1)"; then
    echo -e "${GREEN}✓${NC} Node.js 版本满足要求 (>= 18)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Node.js 版本过低，需要 18+"
    ((TESTS_FAILED++))
fi

# 4. 检查端口占用
echo ""
echo "🔌 检查端口占用"
echo "--------------------------------"

check_port() {
    local port=$1
    local name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC}  端口 $port ($name) 已被占用"
        lsof -Pi :$port -sTCP:LISTEN | grep LISTEN
        return 1
    else
        echo -e "${GREEN}✓${NC} 端口 $port ($name) 可用"
        ((TESTS_PASSED++))
        return 0
    fi
}

check_port 5000 "后端"
check_port 5173 "前端"
check_port 3307 "MySQL"
check_port 6379 "Redis"

# 5. 检查 Docker 容器
echo ""
echo "🐳 检查 Docker 容器"
echo "--------------------------------"

if docker ps --format '{{.Names}}' | grep -q "energy_mysql"; then
    echo -e "${GREEN}✓${NC} MySQL 容器运行中"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  MySQL 容器未运行"
fi

if docker ps --format '{{.Names}}' | grep -q "energy_redis"; then
    echo -e "${GREEN}✓${NC} Redis 容器运行中"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Redis 容器未运行"
fi

# 6. 检查后端虚拟环境
echo ""
echo "🔧 检查后端环境"
echo "--------------------------------"

if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} 虚拟环境已创建"
    ((TESTS_PASSED++))
    
    # 检查关键包
    cd backend
    source venv/bin/activate 2>/dev/null
    
    echo -n "检查 Flask... "
    if python -c "import flask" 2>/dev/null; then
        FLASK_VERSION=$(python -c "import flask; print(flask.__version__)")
        echo -e "${GREEN}✓${NC} (v$FLASK_VERSION)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "检查 SQLAlchemy... "
    if python -c "import flask_sqlalchemy" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo -n "检查 Redis... "
    if python -c "import redis" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
    
    deactivate 2>/dev/null
    cd ..
else
    echo -e "${RED}✗${NC} 虚拟环境未创建"
    echo "   运行: ./install-backend.sh"
    ((TESTS_FAILED++))
fi

# 7. 检查前端依赖
echo ""
echo "🎨 检查前端环境"
echo "--------------------------------"

if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✓${NC} Node 模块已安装"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Node 模块未安装"
    echo "   运行: cd frontend && npm install"
fi

# 8. 检查配置文件
echo ""
echo "⚙️  检查配置文件"
echo "--------------------------------"

if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓${NC} 后端 .env 文件存在"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  后端 .env 文件不存在（将使用默认配置）"
fi

if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓${NC} docker-compose.yml 存在"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} docker-compose.yml 不存在"
    ((TESTS_FAILED++))
fi

# 9. 测试数据库连接
echo ""
echo "🗄️  测试数据库连接"
echo "--------------------------------"

if docker ps --format '{{.Names}}' | grep -q "energy_mysql"; then
    echo -n "测试 MySQL 连接... "
    if docker exec energy_mysql mysql -uroot -ppassword -e "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
fi

if docker ps --format '{{.Names}}' | grep -q "energy_redis"; then
    echo -n "测试 Redis 连接... "
    if docker exec energy_redis redis-cli ping | grep -q "PONG"; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
fi

# 总结
echo ""
echo "================================"
echo "📊 测试总结"
echo "================================"
echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！系统可以启动${NC}"
    echo ""
    echo "运行以下命令启动系统："
    echo "  ./start.sh"
    exit 0
else
    echo -e "${YELLOW}⚠️  发现 $TESTS_FAILED 个问题${NC}"
    echo ""
    echo "建议操作："
    if [ ! -d "backend/venv" ] || ! python3 -c "import flask" 2>/dev/null; then
        echo "  1. 安装后端依赖: ./install-backend.sh"
    fi
    if [ ! -d "frontend/node_modules" ]; then
        echo "  2. 安装前端依赖: cd frontend && npm install"
    fi
    if ! docker ps --format '{{.Names}}' | grep -q "energy_mysql"; then
        echo "  3. 启动 Docker 容器: docker compose up -d mysql redis"
    fi
    exit 1
fi
