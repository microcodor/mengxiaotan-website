@echo off
chcp 65001 >nul
echo 🚀 启动蒙小碳·能源站
echo ====================
echo.

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    echo    下载地址: https://www.docker.com/get-started
    pause
    exit /b 1
)

REM 检查 Docker Compose
docker compose version >nul 2>nul
if %errorlevel% equ 0 (
    set DOCKER_COMPOSE_CMD=docker compose
    echo ✓ 使用 docker compose 命令
) else (
    docker-compose --version >nul 2>nul
    if %errorlevel% equ 0 (
        set DOCKER_COMPOSE_CMD=docker-compose
        echo ✓ 使用 docker-compose 命令
    ) else (
        echo ❌ Docker Compose 未安装或不可用
        echo    请更新 Docker Desktop
        pause
        exit /b 1
    )
)

REM 检查 Python
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python 未安装，请先安装 Python 3.9+
        echo    下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo ✓ 使用 Python 命令: %PYTHON_CMD%

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装，请先安装 Node.js 18+
    echo    下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✓ Node.js 版本: %NODE_VERSION%

echo.
echo 📦 启动 Docker 容器...
%DOCKER_COMPOSE_CMD% up -d mysql redis

if %errorlevel% neq 0 (
    echo ❌ Docker 容器启动失败
    pause
    exit /b 1
)

echo ⏳ 等待数据库启动...
timeout /t 10 /nobreak >nul

echo.
echo 🗄️  初始化数据库...
cd backend

REM 创建虚拟环境
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
)

REM 激活虚拟环境并安装依赖
call venv\Scripts\activate.bat
echo 📦 安装 Python 依赖...
pip install --upgrade pip -q
pip install -r requirements.txt -q

if %errorlevel% neq 0 (
    echo ⚠️  使用国内镜像源重试...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

REM 初始化数据库
%PYTHON_CMD% init_db.py

if %errorlevel% neq 0 (
    echo ❌ 数据库初始化失败
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo 🔧 启动后端服务...
cd backend
call venv\Scripts\activate.bat
set FLASK_APP=app.py
set FLASK_ENV=development

REM 在新窗口启动后端
start "蒙小碳-后端服务" cmd /k "%PYTHON_CMD% app.py"

cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

echo.
echo 🎨 启动前端服务...
cd frontend

REM 检查 npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm 未安装
    cd ..
    pause
    exit /b 1
)

REM 安装依赖
call npm install

if %errorlevel% neq 0 (
    echo ❌ 前端依赖安装失败
    cd ..
    pause
    exit /b 1
)

REM 在新窗口启动前端
start "蒙小碳-前端服务" cmd /k "npm run dev"

cd ..

REM 等待服务启动
timeout /t 3 /nobreak >nul

echo.
echo ✅ 启动完成！
echo ====================
echo 📱 前端地址: http://localhost:5173
echo 🔌 后端地址: http://localhost:5000
echo 📊 管理后台: http://localhost:5173/admin
echo 📈 数据看板: http://localhost:5173/dashboard
echo.
echo 👤 登录信息：
echo    管理员: 13800138000 / admin123
echo    测试用户: 13900139000 / test123
echo.
echo 📝 查看日志：
echo    后端日志: %DOCKER_COMPOSE_CMD% logs -f backend
echo    数据库日志: %DOCKER_COMPOSE_CMD% logs -f mysql
echo.
echo 🛑 停止服务：
echo    运行 stop.bat 或关闭服务窗口
echo.
echo 按任意键退出此窗口（服务将继续运行）...
pause >nul
