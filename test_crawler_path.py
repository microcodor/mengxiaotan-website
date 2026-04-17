#!/usr/bin/env python
"""测试爬虫路径配置"""
import os
import sys

# 模拟API文件的位置
api_file = 'backend/app/api/crawler.py'
api_dir = os.path.dirname(api_file)

print("=" * 60)
print("爬虫路径测试")
print("=" * 60)

# 计算路径
crawler_path = os.path.join(api_dir, '../../../crawler')
scrapy_cmd = os.path.join(api_dir, '../../../backend/venv/bin/scrapy')

# 转换为绝对路径
crawler_path_abs = os.path.abspath(crawler_path)
scrapy_cmd_abs = os.path.abspath(scrapy_cmd)

print(f"\n📁 爬虫目录:")
print(f"   相对路径: {crawler_path}")
print(f"   绝对路径: {crawler_path_abs}")
print(f"   存在: {os.path.exists(crawler_path_abs)}")

print(f"\n🔧 Scrapy命令:")
print(f"   相对路径: {scrapy_cmd}")
print(f"   绝对路径: {scrapy_cmd_abs}")
print(f"   存在: {os.path.exists(scrapy_cmd_abs)}")

if os.path.exists(scrapy_cmd_abs):
    print(f"   ✅ Scrapy已安装")
else:
    print(f"   ❌ Scrapy未找到")
    print(f"\n   请运行:")
    print(f"   cd backend && source venv/bin/activate && pip install scrapy")

print(f"\n📋 爬虫列表:")
if os.path.exists(crawler_path_abs):
    spiders_dir = os.path.join(crawler_path_abs, 'energy_crawler/spiders')
    if os.path.exists(spiders_dir):
        spiders = [f for f in os.listdir(spiders_dir) if f.endswith('_spider.py')]
        for spider in spiders:
            print(f"   - {spider}")
    else:
        print(f"   ❌ 爬虫目录不存在: {spiders_dir}")
else:
    print(f"   ❌ 爬虫根目录不存在")

print("\n" + "=" * 60)
