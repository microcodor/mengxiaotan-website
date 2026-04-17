#!/bin/bash

# 每日爬取脚本
# 结合Crawl4AI和Scrapy爬虫

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 日志文件
LOG_FILE="/tmp/daily_crawl_$(date +%Y%m%d).log"

echo "============================================================" | tee -a $LOG_FILE
echo "每日爬取任务开始" | tee -a $LOG_FILE
echo "时间: $(date)" | tee -a $LOG_FILE
echo "项目目录: $PROJECT_DIR" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE

# 激活虚拟环境
echo "" | tee -a $LOG_FILE
echo "激活虚拟环境..." | tee -a $LOG_FILE
cd "$PROJECT_DIR/backend"
source venv/bin/activate

# 运行Crawl4AI爬虫
echo "" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE
echo "运行Crawl4AI爬虫" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE

cd "$PROJECT_DIR/crawler"

echo "" | tee -a $LOG_FILE
echo "[1] 人民网..." | tee -a $LOG_FILE
python crawl4ai_peopledaily.py >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 人民网完成" | tee -a $LOG_FILE
else
    echo "❌ 人民网失败" | tee -a $LOG_FILE
fi

# 运行Scrapy爬虫
echo "" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE
echo "运行Scrapy爬虫" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE

# 高优先级爬虫
echo "" | tee -a $LOG_FILE
echo "[2] 国家能源局..." | tee -a $LOG_FILE
scrapy crawl nea >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 国家能源局完成" | tee -a $LOG_FILE
else
    echo "❌ 国家能源局失败" | tee -a $LOG_FILE
fi

echo "" | tee -a $LOG_FILE
echo "[3] 新华网..." | tee -a $LOG_FILE
scrapy crawl xinhua_energy >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 新华网完成" | tee -a $LOG_FILE
else
    echo "❌ 新华网失败" | tee -a $LOG_FILE
fi

echo "" | tee -a $LOG_FILE
echo "[4] 中国能源网..." | tee -a $LOG_FILE
scrapy crawl cnenergy >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 中国能源网完成" | tee -a $LOG_FILE
else
    echo "❌ 中国能源网失败" | tee -a $LOG_FILE
fi

# 查询今天的文章数量
echo "" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE
echo "今天爬取的文章统计" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE

/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql -h localhost -P 3306 -u root -pjinchun123 energy_station -e "
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source
ORDER BY count DESC;
" 2>/dev/null | tee -a $LOG_FILE

echo "" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE
echo "每日爬取任务完成" | tee -a $LOG_FILE
echo "时间: $(date)" | tee -a $LOG_FILE
echo "日志文件: $LOG_FILE" | tee -a $LOG_FILE
echo "============================================================" | tee -a $LOG_FILE

exit 0
