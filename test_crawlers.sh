#!/bin/bash

# 爬虫测试脚本
# 测试所有Scrapy爬虫并记录结果

echo "=========================================="
echo "爬虫系统批量测试"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 进入爬虫目录
cd crawler

# 定义爬虫列表（按优先级排序）
spiders=(
    "xinhua_real:新华网能源"
    "chinapower:中国电力网"
    "nea:国家能源局(测试版)"
    "coal:中国煤炭网"
    "newenergy:中国新能源网"
    "cnenergy:中国能源网"
    "ndrc:国家发改委"
    "power:北极星电力网"
    "peopledaily:人民网能源"
    "energy_news:综合能源新闻"
    "test:测试爬虫"
)

# 创建结果文件
result_file="../crawler_test_results_$(date '+%Y%m%d_%H%M%S').txt"
echo "测试结果将保存到: $result_file"
echo ""

# 测试每个爬虫
for spider_info in "${spiders[@]}"
do
    IFS=':' read -r spider_name spider_display <<< "$spider_info"
    
    echo "=========================================="
    echo "测试爬虫: $spider_display ($spider_name)"
    echo "=========================================="
    
    # 记录开始时间
    start_time=$(date +%s)
    
    # 运行爬虫并捕获输出
    output=$(scrapy crawl $spider_name -s LOG_LEVEL=INFO 2>&1)
    exit_code=$?
    
    # 记录结束时间
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    # 提取关键信息
    item_count=$(echo "$output" | grep -o "item_scraped_count': [0-9]*" | grep -o "[0-9]*" | tail -1)
    if [ -z "$item_count" ]; then
        item_count=0
    fi
    
    # 判断测试结果
    if [ $exit_code -eq 0 ] && [ $item_count -gt 0 ]; then
        status="✅ 成功"
        echo "✅ 测试成功！"
    elif [ $exit_code -eq 0 ] && [ $item_count -eq 0 ]; then
        status="⚠️  无数据"
        echo "⚠️  爬虫运行成功但未抓取到数据"
    else
        status="❌ 失败"
        echo "❌ 爬虫运行失败"
    fi
    
    echo "抓取数量: $item_count 篇"
    echo "耗时: ${duration}秒"
    echo ""
    
    # 写入结果文件
    {
        echo "=========================================="
        echo "爬虫: $spider_display ($spider_name)"
        echo "状态: $status"
        echo "抓取数量: $item_count 篇"
        echo "耗时: ${duration}秒"
        echo "退出码: $exit_code"
        echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
    } >> "$result_file"
    
    # 等待3秒再测试下一个
    sleep 3
done

echo "=========================================="
echo "所有爬虫测试完成！"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""
echo "详细结果已保存到: $result_file"

# 生成汇总报告
echo ""
echo "=========================================="
echo "测试汇总"
echo "=========================================="

cd ..
if [ -f "$result_file" ]; then
    success_count=$(grep -c "✅ 成功" "$result_file")
    warning_count=$(grep -c "⚠️  无数据" "$result_file")
    fail_count=$(grep -c "❌ 失败" "$result_file")
    total_count=${#spiders[@]}
    
    echo "总测试数: $total_count"
    echo "成功: $success_count"
    echo "无数据: $warning_count"
    echo "失败: $fail_count"
    echo ""
    
    # 显示每个爬虫的结果
    echo "详细结果:"
    grep -E "(爬虫:|状态:|抓取数量:)" "$result_file" | paste - - - | column -t -s $'\t'
fi
