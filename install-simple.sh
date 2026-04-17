#!/bin/bash

echo "🔧 简单直接的安装方案"
echo "===================="
echo ""

cd backend

# 删除旧环境
if [ -d "venv" ]; then
    echo "🗑️  删除旧环境..."
    rm -rf venv
fi

# 创建新环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 显示路径
echo ""
echo "✓ Python: $(which python)"
echo "✓ pip: $(which pip)"
echo ""

# 升级 pip
echo "⬆️  升级 pip..."
python -m pip install --upgrade pip
echo ""

# 安装依赖（不使用 -q，显示详细输出）
echo "📥 安装依赖（使用清华镜像）..."
echo "这可能需要几分钟，请耐心等待..."
echo ""

python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 安装成功！"
    echo ""
    echo "已安装的包："
    python -m pip list | grep -E "Flask|SQLAlchemy|redis|APScheduler|PyMySQL"
    echo ""
    echo "测试导入："
    python -c "import flask; print(f'✅ Flask {flask.__version__}')"
    python -c "import flask_sqlalchemy; print('✅ Flask-SQLAlchemy OK')"
    python -c "import redis; print('✅ Redis OK')"
    echo ""
    echo "🎉 全部完成！现在可以运行："
    echo "   cd .."
    echo "   ./start.sh"
else
    echo ""
    echo "❌ 安装失败"
    echo ""
    echo "请查看上面的错误信息"
    echo "或尝试手动安装："
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python -m pip install Flask"
fi

cd ..
