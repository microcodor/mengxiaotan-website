#!/bin/bash

echo "🔐 修复 SSL 证书问题"
echo "===================="
echo ""

# 方案 1: 运行 Python 自带的证书安装脚本
echo "方案 1: 安装 Python SSL 证书..."
echo ""

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
CERT_SCRIPT="/Applications/Python ${PYTHON_VERSION}/Install Certificates.command"

if [ -f "$CERT_SCRIPT" ]; then
    echo "找到证书安装脚本: $CERT_SCRIPT"
    echo "正在安装证书..."
    "$CERT_SCRIPT"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 证书安装成功！"
        echo ""
        echo "现在可以运行："
        echo "  ./install-simple.sh"
        exit 0
    fi
else
    echo "未找到证书安装脚本"
fi

# 方案 2: 使用 certifi
echo ""
echo "方案 2: 使用 certifi 包..."
echo ""

cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate

# 先安装 certifi（不需要 SSL）
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org certifi

if [ $? -eq 0 ]; then
    echo "✅ certifi 安装成功"
    
    # 获取 certifi 证书路径
    CERT_PATH=$(python -c "import certifi; print(certifi.where())")
    echo "证书路径: $CERT_PATH"
    
    # 设置环境变量
    export SSL_CERT_FILE="$CERT_PATH"
    export REQUESTS_CA_BUNDLE="$CERT_PATH"
    
    echo ""
    echo "✅ SSL 证书配置完成！"
    echo ""
    echo "现在可以安装依赖："
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  export SSL_CERT_FILE=\"$CERT_PATH\""
    echo "  python -m pip install -r requirements.txt"
else
    echo "❌ certifi 安装失败"
fi

cd ..

echo ""
echo "===================="
echo "如果以上方案都失败，使用方案 3:"
echo "  使用国内镜像源（不需要验证 SSL）"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn"
