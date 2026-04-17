#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试定时任务管理API
"""
import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_schedule_api():
    """测试定时任务API(需要先登录获取token)"""
    
    print("=" * 60)
    print("定时任务管理API测试")
    print("=" * 60)
    
    # 注意: 需要先登录获取JWT token
    print("\n⚠️  提示: 此测试需要管理员JWT token")
    print("请先在浏览器中登录管理后台,然后从开发者工具中获取token")
    print("\n如果你有token,请修改下面的TOKEN变量")
    
    TOKEN = "YOUR_JWT_TOKEN_HERE"
    
    if TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("\n❌ 请先设置JWT token")
        print("\n获取token的步骤:")
        print("1. 在浏览器中访问 http://localhost:5173/login")
        print("2. 使用管理员账号登录")
        print("3. 打开浏览器开发者工具 -> Application -> Local Storage")
        print("4. 找到 'token' 字段,复制其值")
        print("5. 将token值粘贴到此脚本的TOKEN变量中")
        return
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1. 获取所有定时任务
    print("\n1️⃣  获取所有定时任务...")
    try:
        response = requests.get(f"{BASE_URL}/crawler/schedule", headers=headers)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('items', [])
            print(f"✅ 成功获取 {len(jobs)} 个定时任务")
            
            for job in jobs:
                status = "已暂停" if job.get('is_paused') else "运行中"
                print(f"\n  📋 {job['name']}")
                print(f"     ID: {job['id']}")
                print(f"     状态: {status}")
                print(f"     类型: {job.get('type', 'unknown')}")
                print(f"     触发器: {job['trigger']}")
                if job.get('next_run_time'):
                    print(f"     下次运行: {job['next_run_time']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    # 2. 测试暂停任务(可选)
    print("\n\n2️⃣  测试暂停任务(跳过,避免影响生产环境)")
    print("   如需测试,请手动调用:")
    print(f"   POST {BASE_URL}/crawler/schedule/<job_id>/pause")
    
    # 3. 测试恢复任务(可选)
    print("\n3️⃣  测试恢复任务(跳过,避免影响生产环境)")
    print("   如需测试,请手动调用:")
    print(f"   POST {BASE_URL}/crawler/schedule/<job_id>/resume")
    
    # 4. 测试立即触发(可选)
    print("\n4️⃣  测试立即触发(跳过,避免影响生产环境)")
    print("   如需测试,请手动调用:")
    print(f"   POST {BASE_URL}/crawler/schedule/<job_id>/trigger")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_schedule_api()
