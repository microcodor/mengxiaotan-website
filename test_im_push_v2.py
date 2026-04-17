#!/usr/bin/env python3
"""
测试IM推送V2.0 API
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_v2_apis():
    """测试V2.0 API"""
    
    print("=" * 60)
    print("测试IM推送V2.0 API")
    print("=" * 60)
    
    # 登录获取token
    print("\n1. 登录获取token...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"phone": "13800138000", "password": "admin123"},
            timeout=5
        )
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"   ✅ 登录成功")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return
    
    # 测试获取IM应用配置
    print("\n2. 测试获取IM应用配置...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/push-settings/im-apps",
            headers=headers,
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取IM应用配置")
            print(f"   企业微信: {data.get('enterprise_wechat', {}).get('enabled', False)}")
            print(f"   钉钉: {data.get('dingtalk', {}).get('enabled', False)}")
            print(f"   飞书: {data.get('feishu', {}).get('enabled', False)}")
        else:
            print(f"   ❌ 失败: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试更新IM应用配置
    print("\n3. 测试更新IM应用配置...")
    try:
        test_config = {
            "enterprise_wechat": {
                "enabled": True,
                "corp_id": "ww_test_corp_id",
                "agent_id": "1000002",
                "secret": "test_secret_123"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/push-settings/im-apps",
            headers=headers,
            json=test_config,
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 成功更新IM应用配置")
            data = response.json()
            print(f"   消息: {data.get('message')}")
        else:
            print(f"   ❌ 失败: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试获取推送渠道配置
    print("\n4. 测试获取推送渠道配置...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/push-settings/channels",
            headers=headers,
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取推送渠道配置")
            print(f"   订阅等级: {data.get('subscription_level')}")
            print(f"   可用渠道: {data.get('allowed_channels')}")
        else:
            print(f"   ❌ 失败: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试更新推送渠道配置
    print("\n5. 测试更新推送渠道配置...")
    try:
        channel_config = {
            "enterprise_wechat": "test_user_id",
            "email": "test@example.com"
        }
        response = requests.post(
            f"{BASE_URL}/api/push-settings/channels",
            headers=headers,
            json=channel_config,
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 成功更新推送渠道配置")
            data = response.json()
            print(f"   消息: {data.get('message')}")
        else:
            print(f"   ❌ 失败: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 验证配置已保存
    print("\n6. 验证配置已保存...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/push-settings/im-apps",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            wechat = data.get('enterprise_wechat', {})
            if wechat.get('enabled') and wechat.get('corp_id'):
                print(f"   ✅ IM应用配置已保存")
                print(f"   CorpID: {wechat.get('corp_id')}")
                print(f"   Secret: {wechat.get('secret', 'N/A')}")  # 应该是脱敏的
            else:
                print(f"   ⚠️  配置未保存或为空")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_v2_apis()
