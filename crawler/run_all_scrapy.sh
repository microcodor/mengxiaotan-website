#!/bin/bash

# 批量运行Scrapy爬虫
# 用于每日自动爬取

echo "============================================================"
echo "开始批量运行Scrapy爬虫"
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
    echo "[$((SUCCESS + FAILED + 1))] 运行: $name"
    echo "------------------------------------------------------------"
    
    if scrapy crawl $spider 2>&1 | tee /tmp/scrapy_${spider}.log; then
        echo "✅ $name 完成"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "❌ $name 失败"
        FAILED=$((FAILED + 1))
    fi
}

# 高优先级爬虫（官方权威来源）
echo ""
echo "=== 高优先级爬虫 ==="
run_crawler "国家能源局" "nea"
run_crawler "新华网能源" "xinhua_energy"
run_crawler "国家发改委" "ndrc"

# 中优先级爬虫（行业网站）
echo ""
echo "=== 中优先级爬虫 ==="
run_crawler "中国能源网" "cnenergy"
run_crawler "有色金属网" "smm_metal"
run_crawler "中国有色金属报" "cnmn_paper"

# 低优先级爬虫（其他来源）
echo ""
echo "=== 低优先级爬虫 ==="
run_crawler "中国电力网" "chinapower"
run_crawler "北极星电力网" "power"
run_crawler "中国煤炭市场网" "coal"
run_crawler "中国新能源网" "newenergy"

# 总结
echo ""
echo "============================================================"
echo "批量运行完成"
echo "时间: $(date)"
echo "------------------------------------------------------------"
echo "✅ 成功: $SUCCESS"
echo "❌ 失败: $FAILED"
echo "📊 总计: $((SUCCESS + FAILED))"
echo "============================================================"
echo ""

# 查询今天的文章数量
echo "今天爬取的文章数量："
/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql -h localhost -P 3306 -u root -pjinchun123 energy_station -e "
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source
ORDER BY count DESC;
" 2>/dev/null

exit 0
