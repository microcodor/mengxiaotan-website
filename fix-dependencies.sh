#!/bin/bash

echo "🔧 修复 Python 依赖问题"
echo "===================="

# 检测 Python 命令
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python 未安装"
    exit 1
fi

echo "✓ 使用 Python: $PYTHON_CMD"
$PYTHON_CMD --version

# 检查 Python 版本
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')
echo "✓ Python 版本: $PYTHON_VERSION"

# 检查版本是否满足要求 (>= 3.9)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python 版本过低，需要 3.9 或更高版本"
    echo "   当前版本: $PYTHON_VERSION"
    exit 1
fi

cd backend

# 删除旧的虚拟环境
if [ -d "venv" ]; then
    echo ""
    echo "🗑️  删除旧的虚拟环境..."
    rm -rf venv
fi

# 创建新的虚拟环境
echo ""
echo "📦 创建虚拟环境..."
$PYTHON_CMD -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ 虚拟环境创建失败"
    echo "   可能需要安装: $PYTHON_CMD -m pip install virtualenv"
    exit 1
fi

# 激活虚拟环境
echo ""
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 确认使用的是虚拟环境中的 Python
echo "✓ 虚拟环境 Python: $(which python)"
echo "✓ 虚拟环境 pip: $(which pip)"

# 升级 pip
echo ""
echo "⬆️  升级 pip、setuptools 和 wheel..."
python -m pip install --upgrade pip setuptools wheel -q

# 尝试安装依赖
echo ""
echo "📥 安装依赖..."
echo ""

# 方案1: 直接安装（使用系统默认源）
echo "尝试方案 1: 使用默认源..."
python -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖安装成功！"
else
    # 方案2: 使用清华镜像
    echo ""
    echo "❌ 方案 1 失败，尝试方案 2: 使用清华镜像..."
    python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 使用清华镜像安装成功！"
    else
        # 方案3: 使用阿里云镜像
        echo ""
        echo "❌ 方案 2 失败，尝试方案 3: 使用阿里云镜像..."
        python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 使用阿里云镜像安装成功！"
        else
            # 方案4: 逐个安装核心包
            echo ""
            echo "❌ 方案 3 失败，尝试方案 4: 逐个安装核心包..."
            
            CORE_PACKAGES=(
                "Flask"
                "Flask-SQLAlchemy"
                "Flask-Migrate"
                "Flask-JWT-Extended"
                "Flask-CORS"
                "Flask-Smorest"
                "python-dotenv"
                "PyMySQL"
                "cryptography"
                "redis"
                "APScheduler"
                "requests"
                "marshmallow"
                "apispec"
                "gunicorn"
            )
            
            FAILED_PACKAGES=()
            
            for package in "${CORE_PACKAGES[@]}"; do
                echo "  安装 $package..."
                python -m pip install "$package" -q
                if [ $? -ne 0 ]; then
                    FAILED_PACKAGES+=("$package")
                fi
            done
            
            if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
                echo ""
                echo "✅ 所有核心包安装成功！"
            else
                echo ""
                echo "❌ 以下包安装失败:"
                for package in "${FAILED_PACKAGES[@]}"; do
                    echo "  - $package"
                done
                echo ""
                echo "请尝试手动安装失败的包"
                exit 1
            fi
        fi
    fi
fi

# 显示已安装的包
echo ""
echo "📦 已安装的核心包："
python -m pip list | grep -E "Flask|SQLAlchemy|redis|APScheduler|PyMySQL" || python -m pip list

echo ""
echo "✅ 依赖修复完成！"
echo ""
echo "现在可以运行："
echo "  cd .."
echo "  ./start.sh"
echo ""

cd ..
