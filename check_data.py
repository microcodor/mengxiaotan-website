#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计数据库中各平台的数据量
"""
import pymysql
from datetime import datetime

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    port=3307,
    user='root',
    password='password',
    database='energy_station',
    charset='utf8mb4'
)

cursor = conn.cursor()

print("=" * 80)
print("能源资讯平台 - 数据统计报告")
print(f"统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

# 1. 总体统计
cursor.execute("SELECT COUNT(*) FROM articles")
total_articles = cursor.fetchone()[0]

cursor.execute("SELECT SUM(LENGTH(content)) FROM articles")
total_chars = cursor.fetchone()[0] or 0

print("📊 总体统计")
print("-" * 80)
print(f"总文章数: {total_articles:,} 篇")
print(f"总字数: {total_chars:,} 字 ({total_chars/10000:.1f} 万字)")
print()

# 2. 按来源统计
print("📈 各平台数据统计")
print("-" * 80)
print(f"{'序号':<4} {'平台名称':<20} {'文章数':<10} {'平均长度':<12} {'总字数':<15} {'占比':<8}")
print("-" * 80)

cursor.execute("""
    SELECT 
        source,
        COUNT(*) as count,
        ROUND(AVG(LENGTH(content))) as avg_length,
        SUM(LENGTH(content)) as total_chars
    FROM articles 
    GROUP BY source 
    ORDER BY count DESC
""")

results = cursor.fetchall()
for idx, (source, count, avg_length, total_chars_source) in enumerate(results, 1):
    percentage = (count / total_articles * 100) if total_articles > 0 else 0
    total_chars_source = total_chars_source or 0
    avg_length = avg_length or 0
    print(f"{idx:<4} {source:<20} {count:<10,} {int(avg_length):<12,} {int(total_chars_source):<15,} {percentage:>6.1f}%")

print("-" * 80)
print()

# 3. 按分类统计
print("📂 按分类统计")
print("-" * 80)
cursor.execute("""
    SELECT 
        category,
        COUNT(*) as count
    FROM articles 
    GROUP BY category 
    ORDER BY count DESC
""")

results = cursor.fetchall()
for category, count in results:
    percentage = (count / total_articles * 100) if total_articles > 0 else 0
    print(f"{category:<20} {count:>6,} 篇 ({percentage:>5.1f}%)")

print()

# 4. 最近抓取统计
print("⏰ 最近抓取统计")
print("-" * 80)
cursor.execute("""
    SELECT 
        DATE(created_at) as date,
        COUNT(*) as count
    FROM articles 
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    GROUP BY DATE(created_at)
    ORDER BY date DESC
""")

results = cursor.fetchall()
if results:
    for date, count in results:
        print(f"{date}: {count:>4,} 篇")
else:
    print("暂无最近7天的数据")

print()

# 5. 今日统计
print("📅 今日统计")
print("-" * 80)
cursor.execute("""
    SELECT 
        source,
        COUNT(*) as count
    FROM articles 
    WHERE DATE(created_at) = CURDATE()
    GROUP BY source
    ORDER BY count DESC
""")

results = cursor.fetchall()
if results:
    today_total = sum(count for _, count in results)
    print(f"今日总计: {today_total} 篇")
    print()
    for source, count in results:
        print(f"  {source:<20} {count:>4} 篇")
else:
    print("今日暂无新数据")

print()
print("=" * 80)

cursor.close()
conn.close()
