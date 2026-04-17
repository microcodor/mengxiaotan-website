#!/bin/bash

echo "=========================================="
echo "开始运行所有爬虫"
echo "=========================================="
echo ""

cd crawler

# 真实抓取的爬虫
echo "1. 运行 xinhua_real (新华网)..."
scrapy crawl xinhua_real -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ xinhua_real 完成"
echo ""

echo "2. 运行 chinapower (中国电力网)..."
scrapy crawl chinapower -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ chinapower 完成"
echo ""

echo "3. 运行 coal (中国煤炭网)..."
scrapy crawl coal -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ coal 完成"
echo ""

# Playwright爬虫（这些会比较慢）
echo "4. 运行 power (北极星电力网 - Playwright)..."
timeout 180 scrapy crawl power -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ power 完成"
echo ""

echo "5. 运行 nea (国家能源局 - Playwright)..."
timeout 180 scrapy crawl nea -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ nea 完成"
echo ""

echo "6. 运行 ndrc (国家发改委 - Playwright)..."
timeout 180 scrapy crawl ndrc -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ ndrc 完成"
echo ""

echo "7. 运行 peopledaily (人民网 - Playwright)..."
timeout 180 scrapy crawl peopledaily -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ peopledaily 完成"
echo ""

echo "8. 运行 newenergy (中国新能源网 - Playwright)..."
timeout 180 scrapy crawl newenergy -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ newenergy 完成"
echo ""

echo "9. 运行 cnenergy (中国能源网 - Playwright)..."
timeout 180 scrapy crawl cnenergy -s LOG_LEVEL=ERROR 2>&1 | grep -E "(成功抓取|ERROR)" | tail -5
echo "✅ cnenergy 完成"
echo ""

cd ..

echo "=========================================="
echo "所有爬虫运行完成！"
echo "=========================================="
echo ""
echo "正在统计数据..."
python3 check_data.py
