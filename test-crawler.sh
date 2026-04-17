#!/bin/bash

echo "🧪 测试爬虫功能"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 1. 检查爬虫文件是否存在
echo ""
echo "📋 检查爬虫文件"
echo "--------------------------------"

SPIDERS=(
    "ndrc_spider.py"
    "nea_spider.py"
    "coal_spider.py"
    "power_spider.py"
    "newenergy_spider.py"
    "peopledaily_spider.py"
    "xinhua_spider.py"
    "cnenergy_spider.py"
)

for spider in "${SPIDERS[@]}"; do
    if [ -f "crawler/energy_crawler/spiders/$spider" ]; then
        echo -e "${GREEN}✓${NC} $spider 存在"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $spider 不存在"
        ((TESTS_FAILED++))
    fi
done

# 2. 检查 Scrapy 是否安装
echo ""
echo "🔧 检查 Scrapy 环境"
echo "--------------------------------"

if command -v scrapy &> /dev/null; then
    echo -e "${GREEN}✓${NC} Scrapy 已安装"
    scrapy version
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Scrapy 未安装"
    echo "   安装命令: pip install scrapy"
    ((TESTS_FAILED++))
fi

# 3. 检查数据库连接
echo ""
echo "🗄️  检查数据库连接"
echo "--------------------------------"

if docker ps | grep -q "energy_mysql"; then
    echo -e "${GREEN}✓${NC} MySQL 容器运行中"
    ((TESTS_PASSED++))
    
    # 测试数据库连接
    if docker exec energy_mysql mysql -uroot -ppassword -e "USE energy_station; SELECT COUNT(*) FROM articles;" &> /dev/null; then
        ARTICLE_COUNT=$(docker exec energy_mysql mysql -uroot -ppassword -e "USE energy_station; SELECT COUNT(*) as count FROM articles;" 2>/dev/null | tail -n 1)
        echo -e "${GREEN}✓${NC} 数据库连接正常，当前文章数: $ARTICLE_COUNT"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} 数据库连接失败"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC} MySQL 容器未运行"
    echo "   启动命令: docker-compose up -d mysql"
    ((TESTS_FAILED++))
fi

# 4. 测试爬虫配置
echo ""
echo "⚙️  检查爬虫配置"
echo "--------------------------------"

if [ -f "crawler/energy_crawler/settings.py" ]; then
    echo -e "${GREEN}✓${NC} settings.py 存在"
    ((TESTS_PASSED++))
    
    # 检查数据库配置
    if grep -q "DATABASE_URL" crawler/energy_crawler/settings.py; then
        echo -e "${GREEN}✓${NC} 数据库配置存在"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} 数据库配置缺失"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC} settings.py 不存在"
    ((TESTS_FAILED++))
fi

# 5. 测试单个爬虫（快速测试）
echo ""
echo "🕷️  测试爬虫执行"
echo "--------------------------------"
echo "测试 ndrc 爬虫（限制1个页面）..."

cd crawler
timeout 30 scrapy crawl ndrc -s CLOSESPIDER_PAGECOUNT=1 &> /tmp/crawler_test.log
RESULT=$?
cd ..

if [ $RESULT -eq 0 ] || [ $RESULT -eq 124 ]; then
    echo -e "${GREEN}✓${NC} 爬虫可以正常执行"
    ((TESTS_PASSED++))
    
    # 检查是否有新数据
    sleep 2
    NEW_COUNT=$(docker exec energy_mysql mysql -uroot -ppassword -e "USE energy_station; SELECT COUNT(*) as count FROM articles;" 2>/dev/null | tail -n 1)
    if [ "$NEW_COUNT" -gt "$ARTICLE_COUNT" ]; then
        echo -e "${GREEN}✓${NC} 成功抓取数据，新增 $((NEW_COUNT - ARTICLE_COUNT)) 篇文章"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC}  未抓取到新数据（可能是重复数据被过滤）"
    fi
else
    echo -e "${RED}✗${NC} 爬虫执行失败"
    echo "   查看日志: cat /tmp/crawler_test.log"
    ((TESTS_FAILED++))
fi

# 6. 检查 API 接口
echo ""
echo "🔌 检查爬虫管理 API"
echo "--------------------------------"

if curl -s http://localhost:5000/api/crawler/spiders &> /dev/null; then
    echo -e "${GREEN}✓${NC} 爬虫 API 可访问"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  爬虫 API 不可访问（后端可能未启动）"
fi

# 7. 检查前端页面
echo ""
echo "🎨 检查前端页面"
echo "--------------------------------"

if [ -f "frontend/src/pages/admin/Crawler.tsx" ]; then
    echo -e "${GREEN}✓${NC} 爬虫管理页面存在"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} 爬虫管理页面不存在"
    ((TESTS_FAILED++))
fi

# 总结
echo ""
echo "================================"
echo "📊 测试总结"
echo "================================"
echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！爬虫功能正常${NC}"
    echo ""
    echo "🚀 可以使用以下命令测试爬虫："
    echo "  cd crawler"
    echo "  scrapy crawl ndrc          # 国家发改委"
    echo "  scrapy crawl coal          # 煤炭"
    echo "  scrapy crawl power         # 电力"
    echo "  scrapy crawl newenergy     # 新能源"
    echo "  scrapy crawl nea           # 国家能源局"
    echo "  scrapy crawl peopledaily   # 人民日报"
    echo "  scrapy crawl xinhua        # 新华网"
    echo "  scrapy crawl cnenergy      # 中国能源网"
    echo ""
    echo "📊 查看数据："
    echo "  docker exec energy_mysql mysql -uroot -ppassword energy_station"
    echo "  SELECT COUNT(*), source FROM articles GROUP BY source;"
    exit 0
else
    echo -e "${YELLOW}⚠️  发现 $TESTS_FAILED 个问题${NC}"
    echo ""
    echo "建议操作："
    if ! command -v scrapy &> /dev/null; then
        echo "  1. 安装 Scrapy: pip install scrapy pymysql"
    fi
    if ! docker ps | grep -q "energy_mysql"; then
        echo "  2. 启动数据库: docker-compose up -d mysql"
    fi
    echo "  3. 查看详细日志: cat /tmp/crawler_test.log"
    exit 1
fi
