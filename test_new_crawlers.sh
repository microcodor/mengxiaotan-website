#!/bin/bash

# 测试新增爬虫脚本
# 使用方法: ./test_new_crawlers.sh

echo "========================================="
echo "测试新增爬虫"
echo "========================================="
echo ""

cd crawler

echo "1. 测试 CCER 爬虫（全国温室气体自愿减排交易系统）"
echo "-----------------------------------------"
scrapy crawl ccer -s LOG_LEVEL=INFO
echo ""
echo "✓ CCER 爬虫测试完成"
echo ""

echo "2. 测试 MySteel 爬虫（我的钢铁网）"
echo "-----------------------------------------"
scrapy crawl mysteel -s LOG_LEVEL=INFO
echo ""
echo "✓ MySteel 爬虫测试完成"
echo ""

echo "3. 测试 CNMN Paper 爬虫（中国有色金属报）"
echo "-----------------------------------------"
scrapy crawl cnmn_paper -s LOG_LEVEL=INFO
echo ""
echo "✓ CNMN Paper 爬虫测试完成"
echo ""

echo "4. 测试 SMM Metal 爬虫（上海有色金属网）"
echo "-----------------------------------------"
scrapy crawl smm_metal -s LOG_LEVEL=INFO
echo ""
echo "✓ SMM Metal 爬虫测试完成"
echo ""

echo "========================================="
echo "所有新爬虫测试完成！"
echo "========================================="
echo ""
echo "查看数据统计："
cd ../backend
source venv/bin/activate
python check_data.py
