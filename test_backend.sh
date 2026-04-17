#!/bin/bash

echo "🔍 测试后端 API..."
echo ""

# 测试文章列表
echo "1. 测试文章列表 API..."
RESULT=$(curl -s -m 5 "http://localhost:5001/api/articles/?page=1&per_page=5" 2>&1)
if echo "$RESULT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✓ 总文章数: {data[\"total\"]}, 当前页: {len(data[\"items\"])} 篇')" 2>/dev/null; then
  echo "   ✅ 文章列表 API 正常"
else
  echo "   ❌ 文章列表 API 失败"
fi
echo ""

# 测试分类筛选
echo "2. 测试分类筛选 API..."
RESULT=$(curl -s -m 5 "http://localhost:5001/api/articles/?category=power&page=1&per_page=5" 2>&1)
if echo "$RESULT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✓ 电力分类: {data[\"total\"]} 篇')" 2>/dev/null; then
  echo "   ✅ 分类筛选 API 正常"
else
  echo "   ❌ 分类筛选 API 失败"
fi
echo ""

# 测试文章详情
echo "3. 测试文章详情 API..."
RESULT=$(curl -s -m 5 "http://localhost:5001/api/articles/92" 2>&1)
if echo "$RESULT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✓ 文章 {data[\"id\"]}: {data[\"title\"][:30]}...')" 2>/dev/null; then
  echo "   ✅ 文章详情 API 正常"
else
  echo "   ❌ 文章详情 API 失败"
fi
echo ""

# 测试轮播文章
echo "4. 测试轮播文章 API..."
RESULT=$(curl -s -m 5 "http://localhost:5001/api/articles/carousel" 2>&1)
if echo "$RESULT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✓ 轮播文章: {len(data)} 篇')" 2>/dev/null; then
  echo "   ✅ 轮播文章 API 正常"
else
  echo "   ❌ 轮播文章 API 失败"
fi
echo ""

echo "✅ 所有测试完成！"
echo ""
echo "📱 前端地址: http://localhost:5173"
echo "🔌 后端地址: http://localhost:5001"
