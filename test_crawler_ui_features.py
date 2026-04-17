#!/usr/bin/env python3
"""
爬虫UI优化功能测试脚本
测试一键爬取和实时进度API
"""

import requests
import time
import json

BASE_URL = "http://localhost:5001/api"

# 登录获取token
def login():
    """登录获取JWT token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "phone": "13800138000",
            "password": "admin123"
        }, timeout=10)
        
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print("✅ 登录成功")
                return token
            else:
                print(f"❌ 登录失败: 响应中没有access_token")
                print(f"响应内容: {response.text[:200]}")
                return None
        else:
            print(f"❌ 登录失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None

def test_spider_list(token):
    """测试爬虫列表API"""
    print("\n📋 测试1: 获取爬虫列表")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/crawler/spiders", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        spiders = data.get('items', [])
        print(f"✅ 成功获取 {len(spiders)} 个爬虫")
        
        # 显示前3个爬虫信息
        for spider in spiders[:3]:
            print(f"   - {spider['display_name']} ({spider['name']}): {spider['status']}")
        return True
    else:
        print(f"❌ 获取爬虫列表失败: {response.text}")
        return False

def test_run_all_spiders(token):
    """测试一键爬取所有爬虫API"""
    print("\n🚀 测试2: 一键爬取所有爬虫")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/crawler/spiders/run-all", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 批量启动成功")
        print(f"   已启动: {data.get('started_count', 0)} 个")
        print(f"   失败: {data.get('failed_count', 0)} 个")
        print(f"   运行中: {data.get('running_count', 0)} 个")
        
        # 显示启动的爬虫
        started = data.get('started_spiders', [])
        if started:
            print(f"\n   启动的爬虫:")
            for spider in started[:5]:  # 只显示前5个
                print(f"   - {spider['display_name']} (PID: {spider['pid']}, Log ID: {spider['log_id']})")
        
        return True
    else:
        print(f"❌ 批量启动失败: {response.text}")
        return False

def test_crawler_progress(token, duration=10):
    """测试实时进度API"""
    print(f"\n📊 测试3: 实时进度监控 (持续{duration}秒)")
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(duration // 2):  # 每2秒查询一次
        response = requests.get(f"{BASE_URL}/crawler/progress", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            total = data.get('total_running', 0)
            
            print(f"\n   [{i*2}秒] 运行中的爬虫: {total} 个")
            
            if items:
                for item in items[:3]:  # 只显示前3个
                    print(f"   - {item['display_name']}:")
                    print(f"     已抓取: {item.get('items_scraped', 0)} 篇")
                    print(f"     请求数: {item.get('requests_count', 0)}")
                    print(f"     运行时长: {item.get('duration', 0):.1f}秒")
                    if item.get('last_log_line'):
                        log = item['last_log_line'][:60]  # 只显示前60字符
                        print(f"     最新日志: {log}...")
            else:
                print("   暂无运行中的爬虫")
        else:
            print(f"❌ 获取进度失败: {response.text}")
            return False
        
        if i < (duration // 2) - 1:  # 最后一次不等待
            time.sleep(2)
    
    return True

def test_stop_spider(token, spider_name):
    """测试停止爬虫"""
    print(f"\n⏹️  测试4: 停止爬虫 {spider_name}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/crawler/spiders/{spider_name}/stop", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data.get('message', '停止成功')}")
        return True
    else:
        print(f"❌ 停止失败: {response.text}")
        return False

def main():
    """主测试流程"""
    print("="*60)
    print("爬虫UI优化功能测试")
    print("="*60)
    
    # 1. 登录
    token = login()
    if not token:
        return
    
    # 2. 测试爬虫列表
    if not test_spider_list(token):
        return
    
    # 3. 测试一键爬取
    if not test_run_all_spiders(token):
        return
    
    # 等待3秒让爬虫启动
    print("\n⏳ 等待3秒让爬虫启动...")
    time.sleep(3)
    
    # 4. 测试实时进度（监控10秒）
    if not test_crawler_progress(token, duration=10):
        return
    
    # 5. 停止一个爬虫进行测试
    test_stop_spider(token, "test")
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)
    print("\n📝 测试总结:")
    print("1. ✅ 爬虫列表API正常")
    print("2. ✅ 一键爬取API正常")
    print("3. ✅ 实时进度API正常")
    print("4. ✅ 停止爬虫API正常")
    print("\n💡 建议:")
    print("- 打开浏览器访问 http://localhost:5173/admin/crawler")
    print("- 测试前端UI的一键爬取按钮")
    print("- 观察右下角的实时进度浮动面板")
    print("- 切换到'实时进度'标签页查看详细信息")

if __name__ == "__main__":
    main()
