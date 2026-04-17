@echo off
chcp 65001 >nul
echo 🔧 修复 Python 依赖问题
echo ====================
echo.

REM 检测 Python
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python 未安装
        pause
        exit /b 1
    )
)

echo ✓ 使用 Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

cd backend

REM 删除旧的虚拟环境
if exist "venv" (
    echo 🗑️  删除旧的虚拟环境...
    rmdir /s /q venv
    echo.
)

REM 创建虚拟环境
echo 📦 创建虚拟环境...
%PYTHON_CMD% -m venv venv
echo.

REM 激活虚拟环境
echo 🔌 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

REM 升级 pip
echo ⬆️  升级 pip、setuptools 和 wheel...
python -m pip install --upgrade pip setuptools wheel -q
echo.

REM 尝试安装依赖
echo 📥 安装依赖...
echo.

echo 尝试方案 1: 使用默认源...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ 依赖安装成功！
    goto :success
)

echo.
echo ❌ 方案 1 失败，尝试方案 2: 使用清华镜像...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% equ 0 (
    echo.
    echo ✅ 使用清华镜像安装成功！
    goto :success
)

echo.
echo ❌ 方案 2 失败，尝试方案 3: 使用阿里云镜像...
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

if %errorlevel% equ 0 (
    echo.
    echo ✅ 使用阿里云镜像安装成功！
    goto :success
)

echo.
echo ❌ 方案 3 失败，尝试方案 4: 逐个安装核心包...
echo.

pip install Flask -q
pip install Flask-SQLAlchemy -q
pip install Flask-Migrate -q
pip install Flask-JWT-Extended -q
pip install Flask-CORS -q
pip install Flask-Smorest -q
pip install python-dotenv -q
pip install PyMySQL -q
pip install cryptography -q
pip install redis -q
pip install APScheduler -q
pip install requests -q
pip install marshmallow -q
pip install apispec -q
pip install gunicorn -q

echo.
echo ✅ 核心包安装完成！

:success
echo.
echo 📦 已安装的核心包：
pip list | findstr /I "Flask SQLAlchemy redis APScheduler PyMySQL"
echo.
echo ✅ 依赖修复完成！
echo.
echo 现在可以运行：
echo   cd ..
echo   start.bat
echo.

cd ..
pause
