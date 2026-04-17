#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试爬虫运行"""
import os
import sys
import subprocess

# 添加项目路径
sys.path.insert(0, os.path.abspath('.'))

# 获取路径
project_root = os.path.abspath('.')
crawler_path = os.path.join(project_root, 'crawler')
scrapy_cmd = os.path.join(project_root, 'backend/venv/bin/scrapy')

print("=" * 60)
print("测试爬虫运行")
print("=" * 60)
print(f"项目根目录: {project_root}")
print(f"爬虫目录: {crawler_path}")
print(f"Scrapy命令: {scrapy_cmd}")
print(f"爬虫目录存在: {os.path.exists(crawler_path)}")
print(f"Scrapy存在: {os.path.exists(scrapy_cmd)}")
print("=" * 60)

if not os.path.exists(scrapy_cmd):
    print("❌ Scrapy不存在")
    sys.exit(1)

if not os.path.exists(crawler_path):
    print("❌ 爬虫目录不存在")
    sys.exit(1)

# 测试运行test爬虫
print("\n🚀 启动test爬虫...")
try:
    process = subprocess.Popen(
        [scrapy_cmd, 'crawl', 'test'],
        cwd=crawler_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"✅ 进程已启动，PID: {process.pid}")
    print("⏳ 等待完成...")
    
    stdout, stderr = process.communicate(timeout=30)
    
    print("\n📋 输出:")
    if stdout:
        print(stdout[-500:])  # 最后500字符
    
    if stderr:
        print("\n⚠️ 错误:")
        print(stderr[-500:])
    
    print(f"\n✅ 进程退出码: {process.returncode}")
    
except subprocess.TimeoutExpired:
    print("⏰ 超时，终止进程")
    process.kill()
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
