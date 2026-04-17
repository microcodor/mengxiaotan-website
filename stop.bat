@echo off
chcp 65001 >nul
echo 🛑 停止蒙小碳·能源站
echo ====================
echo.

REM 检测 Docker Compose 命令
docker compose version >nul 2>nul
if %errorlevel% equ 0 (
    set DOCKER_COMPOSE_CMD=docker compose
) else (
    docker-compose --version >nul 2>nul
    if %errorlevel% equ 0 (
        set DOCKER_COMPOSE_CMD=docker-compose
    ) else (
        echo ❌ Docker Compose 未找到
        pause
        exit /b 1
    )
)

REM 停止 Docker 容器
echo 📦 停止 Docker 容器...
%DOCKER_COMPOSE_CMD% down

REM 停止后端服务
echo 🔧 停止后端服务...
taskkill /FI "WINDOWTITLE eq 蒙小碳-后端服务*" /F >nul 2>nul

REM 停止前端服务
echo 🎨 停止前端服务...
taskkill /FI "WINDOWTITLE eq 蒙小碳-前端服务*" /F >nul 2>nul

REM 停止可能残留的进程
taskkill /F /IM python.exe /FI "MEMUSAGE gt 10000" >nul 2>nul
taskkill /F /IM node.exe /FI "MEMUSAGE gt 10000" >nul 2>nul

echo.
echo ✅ 所有服务已停止
pause
