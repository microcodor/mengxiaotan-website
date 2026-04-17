@echo off
chcp 65001 >nul
echo 🔍 检查端口占用情况
echo ====================
echo.

echo 检查项目所需端口:
echo.

REM 检查 MySQL 3306
netstat -ano | findstr ":3306" >nul 2>nul
if %errorlevel% equ 0 (
    echo ❌ 端口 3306 ^(MySQL 默认^) 已被占用
    echo    进程信息:
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3306"') do (
        tasklist /FI "PID eq %%a" 2>nul | findstr /V "INFO:"
    )
    set MYSQL_3306=1
) else (
    echo ✅ 端口 3306 ^(MySQL 默认^) 可用
    set MYSQL_3306=0
)

echo.

REM 检查 MySQL 3307
netstat -ano | findstr ":3307" >nul 2>nul
if %errorlevel% equ 0 (
    echo ❌ 端口 3307 ^(MySQL 备用^) 已被占用
    set MYSQL_3307=1
) else (
    echo ✅ 端口 3307 ^(MySQL 备用^) 可用
    set MYSQL_3307=0
)

echo.

REM 检查 Redis 6379
netstat -ano | findstr ":6379" >nul 2>nul
if %errorlevel% equ 0 (
    echo ❌ 端口 6379 ^(Redis^) 已被占用
    set REDIS=1
) else (
    echo ✅ 端口 6379 ^(Redis^) 可用
    set REDIS=0
)

echo.

REM 检查后端 5000
netstat -ano | findstr ":5000" >nul 2>nul
if %errorlevel% equ 0 (
    echo ❌ 端口 5000 ^(后端 API^) 已被占用
    set BACKEND=1
) else (
    echo ✅ 端口 5000 ^(后端 API^) 可用
    set BACKEND=0
)

echo.

REM 检查前端 5173
netstat -ano | findstr ":5173" >nul 2>nul
if %errorlevel% equ 0 (
    echo ❌ 端口 5173 ^(前端开发服务器^) 已被占用
    set FRONTEND=1
) else (
    echo ✅ 端口 5173 ^(前端开发服务器^) 可用
    set FRONTEND=0
)

echo.
echo ====================
echo 检查结果汇总:
echo.

if %MYSQL_3306% equ 1 (
    if %MYSQL_3307% equ 0 (
        echo 💡 建议: MySQL 3306 端口被占用，项目已配置使用 3307 端口
        echo    无需额外操作，直接运行 start.bat 即可
    ) else (
        echo ⚠️  警告: MySQL 3306 和 3307 端口都被占用
        echo    解决方案:
        echo    1. 停止占用端口的 MySQL 服务
        echo    2. 或修改 docker-compose.yml 使用其他端口
    )
) else (
    echo ✅ MySQL 可以使用默认 3306 端口
)

echo.

if %REDIS% equ 1 (
    echo ⚠️  警告: Redis 6379 端口被占用
    echo    解决方案: 停止占用端口的 Redis 服务
)

if %BACKEND% equ 1 (
    echo ⚠️  警告: 后端 5000 端口被占用
    echo    解决方案:
    echo    查看占用进程: netstat -ano ^| findstr :5000
    echo    停止进程: taskkill /PID [PID] /F
)

if %FRONTEND% equ 1 (
    echo ⚠️  警告: 前端 5173 端口被占用
    echo    解决方案:
    echo    查看占用进程: netstat -ano ^| findstr :5173
    echo    停止进程: taskkill /PID [PID] /F
)

echo.
echo ====================
echo.

if %MYSQL_3306% equ 1 (
    echo 🔧 快速解决 MySQL 端口冲突:
    echo.
    echo # 方案1: 停止本地 MySQL 服务
    echo net stop MySQL80
    echo.
    echo # 方案2: 项目已配置使用 3307 端口，直接启动即可
    echo start.bat
    echo.
) else (
    echo ✅ 所有端口都可用，可以直接运行:
    echo    start.bat
)

pause
