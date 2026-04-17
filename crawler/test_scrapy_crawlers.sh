#!/bin/bash

# 测试Scrapy爬虫 - 抓取本月数据
# 每个爬虫限制20篇文章

echo "============================================================"
echo "测试Scrapy爬虫 - 抓取本月数据"
echo "时间: $(date)"
echo "============================================================"

# 计数器
SUCCESS=0
FAILED=0

# 运行爬虫的函数
run_crawler() {
    local name=$1
    local spider=$2
    
    echo ""
    echo "------------------------------------------------------------"
    echo "[$((SUCCESS + FAILED + 1))] 测试: $name"
    echo "------------------------------------------------------------"
    
    # 限制20篇文章
    if scrapy crawl $spider -s CLOSESPIDER_ITEMCOUNT=20 2>&1 | tail -20; then
        echo "✅ $name 完成"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "❌ $name 失败"
        FAILED=$((FAILED + 1))
    fi
    
    # 等待1秒
    sleep 1
}

# 测试重要的爬虫
run_crawler "国家能源局" "nea"
run_crawler "新华网" "xinhua_energy"
run_crawler "中国能源网" "cnenergy"

# 总结
echo ""
echo "============================================================"
echo "测试完成"
echo "时间: $(date)"
echo "------------------------------------------------------------"
echo "✅ 成功: $SUCCESS"
echo "❌ 失败: $FAILED"
echo "============================================================"
echo ""

# 查询数据库统计
echo "本月文章统计："
/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql -h localhost -P 3306 -u root -pjinchun123 energy_station -e "
SELECT source, COUNT(*) as count
FROM articles
WHERE YEAR(created_at) = 2026 AND MONTH(created_at) = 4
GROUP BY source
ORDER BY count DESC;
" 2>/dev/null

exit 0
