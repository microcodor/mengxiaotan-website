#!/usr/bin/env python3
"""
修复爬虫状态不一致问题

当爬虫进程意外终止时，数据库状态可能残留为 'running'，
但 Redis 中没有 PID 记录，导致无法正常停止。

此脚本会：
1. 检查所有状态为 'running' 的数据源
2. 验证 Redis 中是否有对应的 PID
3. 验证进程是否真的在运行
4. 修复状态不一致的记录
"""
import os
import sys
import redis
import pymysql
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'password',
    'database': 'energy_station',
    'charset': 'utf8mb4'
}

# Redis配置
REDIS_CONFIG = {
    'host': '127.0.0.1',
    'port': 6380,
    'db': 0
}

# 爬虫名称映射
SPIDER_NAMES = {
    '全国温室气体自愿减排交易系统': 'ccer',
    '我的钢铁网': 'mysteel',
    '中国有色金属报': 'cnmn_paper',
    '上海有色金属网': 'smm_metal',
    '新华网': 'xinhua_real',
    '中国电力网': 'chinapower',
    '北极星电力网': 'power',
    '国家发改委': 'ndrc',
    '国家能源局（测试版）': 'nea',
    '国家能源局': 'real_nea',
    '人民网': 'peopledaily',
    '中国煤炭市场网': 'coal',
    '中国新能源网': 'newenergy',
    '中国能源网': 'cnenergy',
    '综合能源新闻': 'energy_news',
    '测试数据源': 'test'
}


def check_process_exists(pid):
    """检查进程是否存在"""
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def main():
    print("=" * 80)
    print("爬虫状态修复工具")
    print("=" * 80)
    print()
    
    # 连接数据库
    try:
        db = pymysql.connect(**DB_CONFIG)
        cursor = db.cursor(pymysql.cursors.DictCursor)
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return
    
    # 连接Redis
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        print("✓ Redis连接成功")
    except Exception as e:
        print(f"✗ Redis连接失败: {e}")
        return
    
    print()
    print("-" * 80)
    print("检查状态不一致的爬虫...")
    print("-" * 80)
    print()
    
    # 查询所有状态为 running 的数据源
    cursor.execute("SELECT id, name, status FROM sources WHERE status='running'")
    running_sources = cursor.fetchall()
    
    if not running_sources:
        print("✓ 没有发现状态为 'running' 的数据源")
        return
    
    print(f"发现 {len(running_sources)} 个状态为 'running' 的数据源:")
    print()
    
    fixed_count = 0
    
    for source in running_sources:
        source_id = source['id']
        source_name = source['name']
        spider_name = SPIDER_NAMES.get(source_name)
        
        print(f"检查: {source_name} (ID: {source_id})")
        
        if not spider_name:
            print(f"  ⚠️  未找到对应的爬虫名称，跳过")
            print()
            continue
        
        # 检查 Redis 中的 PID
        redis_key = f'crawler:{spider_name}:pid'
        pid = r.get(redis_key)
        
        if pid:
            pid = int(pid)
            print(f"  Redis PID: {pid}")
            
            # 检查进程是否存在
            if check_process_exists(pid):
                print(f"  ✓ 进程正在运行")
            else:
                print(f"  ✗ 进程不存在，清理 Redis 记录")
                r.delete(redis_key)
                r.delete(f'crawler:{spider_name}:log_id')
                r.delete(f'crawler:{spider_name}:log_file')
                
                print(f"  修复数据库状态为 'active'")
                cursor.execute(
                    "UPDATE sources SET status='active' WHERE id=%s",
                    (source_id,)
                )
                db.commit()
                fixed_count += 1
                print(f"  ✓ 已修复")
        else:
            print(f"  ✗ Redis 中没有 PID 记录")
            print(f"  修复数据库状态为 'active'")
            cursor.execute(
                "UPDATE sources SET status='active' WHERE id=%s",
                (source_id,)
            )
            db.commit()
            fixed_count += 1
            print(f"  ✓ 已修复")
        
        print()
    
    print("-" * 80)
    print(f"修复完成！共修复 {fixed_count} 个状态不一致的记录")
    print("-" * 80)
    
    # 关闭连接
    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
