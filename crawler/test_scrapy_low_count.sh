#!/bin/bash

# 测试文章数少于10的Scrapy爬虫
# 2026-04-16

echo "========================================"
echo "测试文章数少于10的Scrapy爬虫"
echo "========================================"
echo ""

# 需要测试的爬虫列表
# 根据数据库统计，以下平台文章数少于10：
# - 国家能源局: 4篇 (nea)
# - 中国有色金属报: 3篇 (cnmn_paper)
# - 北极星电力网: 3篇 (power)
# - 中国新能源网: 2篇 (newenergy)
# - 中国煤炭市场网: 2篇 (coal)
# - 国家发改委: 2篇 (ndrc)
# - 中国煤炭工业协会: 1篇 (coal_association - 可能没有对应爬虫)

CRAWLERS=(
    "nea:国家能源局"
    "cnmn_paper:中国有色金属报"
    "power:北极星电力网"
    "newenergy:中国新能源网"
    "coal:中国煤炭市场网"
    "ndrc:国家发改委"
)

# 测试结果统计
SUCCESS=0
FAILED=0
TOTAL=${#CRAWLERS[@]}

# 测试每个爬虫
for crawler_info in "${CRAWLERS[@]}"; do
    IFS=':' read -r crawler_name platform_name <<< "$crawler_info"
    
    echo "========================================"
    echo "测试爬虫: $platform_name ($crawler_name)"
    echo "========================================"
    echo ""
    
    # 运行爬虫（5分钟超时）
    timeout 300 scrapy crawl "$crawler_name" 2>&1
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✅ $platform_name 测试成功"
        ((SUCCESS++))
    elif [ $EXIT_CODE -eq 124 ]; then
        echo ""
        echo "⚠️  $platform_name 超时（5分钟）"
        ((FAILED++))
    else
        echo ""
        echo "❌ $platform_name 测试失败 (退出码: $EXIT_CODE)"
        ((FAILED++))
    fi
    
    echo ""
    echo ""
done

# 打印总结
echo "========================================"
echo "测试总结"
echo "========================================"
echo "总计: $TOTAL 个爬虫"
echo "成功: $SUCCESS 个"
echo "失败: $FAILED 个"
echo ""

# 查询数据库统计
echo "========================================"
echo "数据库统计"
echo "========================================"
cd ../backend
source venv/bin/activate
python3 << 'EOF'
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='jinchun123', database='energy_station')
cursor = conn.cursor()

cursor.execute("""
    SELECT source, COUNT(*) as count 
    FROM articles 
    WHERE DATE_FORMAT(created_at, '%Y-%m') = '2026-04'
    GROUP BY source 
    ORDER BY count DESC
""")

results = cursor.fetchall()
print('本月各平台文章数:')
print(f"{'排名':<6} {'平台':<25} {'文章数':>10}")
print('-' * 43)
total = 0
for idx, row in enumerate(results, 1):
    print(f"{idx:<6} {row[0]:<25} {row[1]:>10}")
    total += row[1]

print('-' * 43)
print(f"{'总计':>31} {total:>10}")
print(f"\n平台数: {len(results)} 个")

conn.close()
EOF
