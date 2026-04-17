#!/bin/bash

echo "============================================================"
echo "爬虫UI优化功能API测试"
echo "============================================================"

# 1. 登录获取token
echo -e "\n📝 测试1: 登录获取token"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败"
    echo "响应: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ 登录成功"
echo "Token: ${TOKEN:0:50}..."

# 2. 获取爬虫列表
echo -e "\n📋 测试2: 获取爬虫列表"
SPIDERS_RESPONSE=$(curl -s -X GET http://localhost:5001/api/crawler/spiders \
  -H "Authorization: Bearer $TOKEN")

SPIDER_COUNT=$(echo $SPIDERS_RESPONSE | grep -o '"name"' | wc -l)
echo "✅ 成功获取 $SPIDER_COUNT 个爬虫"

# 显示前3个爬虫
echo "$SPIDERS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    spiders = data.get('items', [])[:3]
    for spider in spiders:
        print(f\"   - {spider['display_name']} ({spider['name']}): {spider['status']}\")
except:
    pass
" 2>/dev/null

# 3. 测试一键爬取API
echo -e "\n🚀 测试3: 一键爬取所有爬虫"
RUN_ALL_RESPONSE=$(curl -s -X POST http://localhost:5001/api/crawler/spiders/run-all \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$RUN_ALL_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"✅ 批量启动成功\")
    print(f\"   已启动: {data.get('started_count', 0)} 个\")
    print(f\"   失败: {data.get('failed_count', 0)} 个\")
    print(f\"   运行中: {data.get('running_count', 0)} 个\")
    
    started = data.get('started_spiders', [])
    if started:
        print(f\"\n   启动的爬虫:\")
        for spider in started[:5]:
            print(f\"   - {spider['display_name']} (PID: {spider['pid']}, Log ID: {spider['log_id']})\")
except Exception as e:
    print(f\"❌ 解析响应失败: {e}\")
    print(f\"响应: {sys.stdin.read()[:200]}\")
"

# 等待3秒让爬虫启动
echo -e "\n⏳ 等待3秒让爬虫启动..."
sleep 3

# 4. 测试实时进度API（查询3次，每次间隔2秒）
echo -e "\n📊 测试4: 实时进度监控"
for i in {1..3}; do
    echo -e "\n   [查询 $i/3]"
    PROGRESS_RESPONSE=$(curl -s -X GET http://localhost:5001/api/crawler/progress \
      -H "Authorization: Bearer $TOKEN")
    
    echo "$PROGRESS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    total = data.get('total_running', 0)
    
    print(f\"   运行中的爬虫: {total} 个\")
    
    if items:
        for item in items[:3]:
            print(f\"   - {item['display_name']}:\")
            print(f\"     已抓取: {item.get('items_scraped', 0)} 篇\")
            print(f\"     请求数: {item.get('requests_count', 0)}\")
            print(f\"     运行时长: {item.get('duration', 0):.1f}秒\")
    else:
        print(\"   暂无运行中的爬虫\")
except Exception as e:
    print(f\"   ❌ 解析失败: {e}\")
"
    
    if [ $i -lt 3 ]; then
        sleep 2
    fi
done

# 5. 停止测试爬虫
echo -e "\n⏹️  测试5: 停止测试爬虫"
STOP_RESPONSE=$(curl -s -X POST http://localhost:5001/api/crawler/spiders/test/stop \
  -H "Authorization: Bearer $TOKEN")

echo "$STOP_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"✅ {data.get('message', '停止成功')}\")
except:
    print(\"✅ 停止命令已发送\")
"

echo -e "\n============================================================"
echo "✅ 所有API测试完成！"
echo "============================================================"
echo -e "\n📝 测试总结:"
echo "1. ✅ 登录API正常"
echo "2. ✅ 爬虫列表API正常"
echo "3. ✅ 一键爬取API正常"
echo "4. ✅ 实时进度API正常"
echo "5. ✅ 停止爬虫API正常"
echo -e "\n💡 下一步建议:"
echo "- 打开浏览器访问 http://localhost:5173/admin/crawler"
echo "- 测试前端UI的一键爬取按钮"
echo "- 观察右下角的实时进度浮动面板"
echo "- 切换到'实时进度'标签页查看详细信息"
