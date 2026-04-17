#!/bin/bash

echo "========================================="
echo "  能源爬虫系统测试脚本"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 进入爬虫目录
cd crawler

echo -e "${BLUE}1. 清理缓存...${NC}"
rm -rf httpcache .scrapy/httpcache
echo "✓ 缓存已清理"
echo ""

echo -e "${BLUE}2. 运行综合能源新闻爬虫...${NC}"
echo "   这将抓取以下内容："
echo "   - 国家能源局新闻 (3篇)"
echo "   - 煤炭行业新闻 (2篇)"
echo "   - 电力行业新闻 (2篇)"
echo "   - 新能源新闻 (2篇)"
echo ""

../backend/venv/bin/scrapy crawl energy_news 2>&1 | grep -E "(成功抓取|Article saved|item_scraped_count|Spider closed)"

echo ""
echo -e "${BLUE}3. 查询数据库中的文章...${NC}"
../backend/venv/bin/python3 << 'PYTHON'
import pymysql
from datetime import datetime

conn = pymysql.connect(
    host='127.0.0.1',
    port=3307,
    user='root',
    password='password',
    database='energy_station'
)
cursor = conn.cursor()

print("\n" + "="*60)
print("  今日抓取统计")
print("="*60)

cursor.execute("""
    SELECT source, category, COUNT(*) as count
    FROM articles
    WHERE DATE(created_at) = CURDATE()
    GROUP BY source, category
    ORDER BY source
""")

total = 0
for row in cursor.fetchall():
    print(f"  {row[0]:20s} | {row[1]:15s} | {row[2]:2d} 篇")
    total += row[2]

print("="*60)
print(f"  总计: {total} 篇")
print("="*60)

print("\n" + "="*60)
print("  最新文章列表")
print("="*60)

cursor.execute("""
    SELECT id, title, source, category, created_at
    FROM articles
    ORDER BY id DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"标题: {row[1]}")
    print(f"来源: {row[2]} | 分类: {row[3]}")
    print(f"时间: {row[4]}")

conn.close()
PYTHON

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  测试完成！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "提示："
echo "  - 可以在管理后台查看文章：http://localhost:5173/admin"
echo "  - 查看爬虫管理页面：http://localhost:5173/admin/crawler"
echo ""
