#!/bin/bash

# 测试当日文章爬取功能
# 使用后端虚拟环境运行爬虫

echo "============================================================"
echo "测试当日文章爬取功能"
echo "============================================================"
echo ""

# 检查后端虚拟环境
if [ ! -d "../backend/venv" ]; then
    echo "❌ 后端虚拟环境不存在，请先运行 ./start_local.sh"
    exit 1
fi

echo "✓ 找到后端虚拟环境"
echo ""

# 激活虚拟环境
source ../backend/venv/bin/activate

# 检查crawl4ai是否安装
if python -c "import crawl4ai" 2>/dev/null; then
    echo "✓ crawl4ai 已安装"
else
    echo "❌ crawl4ai 未安装"
    echo "正在安装 crawl4ai..."
    pip install -q crawl4ai
    echo "✓ crawl4ai 安装完成"
fi

echo ""
echo "============================================================"
echo "测试1: 人民网爬虫（限制3篇）"
echo "============================================================"
echo ""

python crawl4ai_peopledaily.py

echo ""
echo "============================================================"
echo "测试完成"
echo "============================================================"
echo ""
echo "请检查："
echo "1. 是否只保存了今天的文章"
echo "2. 是否正确跳过了非当日文章"
echo "3. 日期提取是否准确"
echo ""
