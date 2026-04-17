#!/bin/bash

echo "🔧 安装后端依赖（解决 SSL 问题）"
echo "=================================="

cd backend

# 1. 清理旧环境
echo ""
echo "🗑️  清理旧的虚拟环境..."
rm -rf venv

# 2. 创建新虚拟环境
echo ""
echo "📦 创建新的虚拟环境..."
python3 -m venv venv

# 3. 激活虚拟环境
echo ""
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 4. 升级 pip（使用清华镜像，跳过 SSL 验证）
echo ""
echo "⬆️  升级 pip..."
python -m pip install --upgrade pip \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# 5. 安装依赖（使用清华镜像，跳过 SSL 验证）
echo ""
echo "📥 安装依赖包..."
python -m pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# 6. 验证安装
echo ""
echo "✅ 验证安装..."
python -c "import flask; print(f'✓ Flask {flask.__version__}')"
python -c "import flask_sqlalchemy; print('✓ Flask-SQLAlchemy 已安装')"
python -c "import flask_jwt_extended; print('✓ Flask-JWT-Extended 已安装')"
python -c "import redis; print('✓ Redis 已安装')"
python -c "import apscheduler; print('✓ APScheduler 已安装')"

echo ""
echo "🎉 安装完成！"
echo ""
echo "现在可以运行："
echo "  cd .."
echo "  ./start.sh"
echo ""

cd ..
