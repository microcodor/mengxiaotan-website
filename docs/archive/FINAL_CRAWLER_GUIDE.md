# 🚀 能源新闻爬虫系统 - 最终使用指南

## ✅ 已实现功能

### 1. 真实新闻爬虫

**新华网能源频道爬虫（xinhua_real）**
- ✅ 每次抓取 15-20 篇真实新闻
- ✅ 完整文章内容（平均 1,000-8,000 字）
- ✅ 自动去重机制
- ✅ 质量控制（过滤无效内容）

**已验证抓取的文章：**
1. 新华网科技观察丨绿氢成本破局 (8,977字)
2. 能源强国建设系列谈 (7,447字)
3. AI算力时代电力协同 (6,401字)
4. 电力不出境价值已出海 (5,735字)
5. 液氢燃料航空涡轮动力 (1,138字)
...共17篇

### 2. 综合测试爬虫

**综合能源新闻爬虫（energy_news）**
- 每次抓取 9 篇高质量测试文章
- 覆盖：国家能源局、煤炭、电力、新能源
- 用于系统测试和演示

## 🎯 快速开始

### 方法1：一键运行（推荐）

```bash
# 运行真实新闻爬虫
cd crawler
../backend/venv/bin/scrapy crawl xinhua_real

# 查看抓取结果
../backend/venv/bin/python3 << 'EOF'
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3307, user='root', 
                       password='password', database='energy_station')
cursor = cursor.execute('''
    SELECT COUNT(*), SUM(LENGTH(content))
    FROM articles
    WHERE source = '新华网' AND DATE(created_at) = CURDATE()
''')
result = cursor.fetchone()
print(f"今日抓取: {result[0]}篇, 总计{result[1]}字")
conn.close()
EOF
```

### 方法2：管理后台

1. 访问：http://localhost:5173/admin
2. 登录：13800138000 / admin123
3. 进入"爬虫管理"
4. 点击"新华网能源（真实）"的"运行"按钮
5. 等待30-60秒
6. 查看"爬取日志"和"统计信息"

### 方法3：API调用

```bash
# 获取Token
TOKEN=$(curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}' \
  | jq -r '.access_token')

# 启动爬虫
curl -X POST http://localhost:5001/api/crawler/spiders/xinhua_real/run \
  -H "Authorization: Bearer $TOKEN"

# 查看日志
curl http://localhost:5001/api/crawler/logs \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 数据查看

### 查看今日抓取统计

```bash
./backend/venv/bin/python3 -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3307, user='root',
                       password='password', database='energy_station')
cursor = conn.cursor()

print('=== 今日抓取统计 ===')
cursor.execute('''
    SELECT source, COUNT(*) as count, 
           AVG(LENGTH(content)) as avg_len,
           SUM(LENGTH(content)) as total_len
    FROM articles
    WHERE DATE(created_at) = CURDATE()
    GROUP BY source
    ORDER BY count DESC
''')

for row in cursor.fetchall():
    print(f'{row[0]:20s} | {row[1]:3d}篇 | 平均{int(row[2]):5d}字 | 总计{int(row[3]):7d}字')

conn.close()
"
```

### 查看最新文章

```bash
./backend/venv/bin/python3 -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3307, user='root',
                       password='password', database='energy_station')
cursor = conn.cursor()

print('=== 最新文章 ===')
cursor.execute('''
    SELECT title, source, LENGTH(content), created_at
    FROM articles
    ORDER BY id DESC
    LIMIT 10
''')

for i, row in enumerate(cursor.fetchall(), 1):
    print(f'{i}. {row[1]} | {row[0][:50]}... ({row[2]}字)')

conn.close()
"
```

## 🔧 配置定时任务

编辑 `backend/app/scheduler.py`，添加：

```python
def run_xinhua_crawler():
    """运行新华网爬虫"""
    import subprocess
    import os
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    crawler_path = os.path.join(project_root, 'crawler')
    scrapy_cmd = os.path.join(project_root, 'backend/venv/bin/scrapy')
    
    subprocess.Popen(
        [scrapy_cmd, 'crawl', 'xinhua_real'],
        cwd=crawler_path
    )

# 添加定时任务
scheduler.add_job(
    func=run_xinhua_crawler,
    trigger='cron',
    hour='6,12,18',  # 每天6点、12点、18点
    minute=0,
    id='crawl_xinhua_real',
    name='抓取新华网能源新闻'
)
```

## 📈 扩展更多网站

基于成功经验，可以快速添加更多新闻源：

### 模板代码

```python
# crawler/energy_crawler/spiders/your_spider.py
import scrapy
from energy_crawler.items import ArticleItem
from datetime import datetime

class YourSpider(scrapy.Spider):
    name = 'your_spider'
    start_urls = ['http://your-site.com/news/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def parse(self, response):
        # 查找文章链接
        for link in response.css('a[href]'):
            href = link.css('::attr(href)').get()
            title = link.css('::text').get()
            
            if href and title and len(title) > 10:
                yield scrapy.Request(
                    response.urljoin(href),
                    callback=self.parse_article,
                    meta={'title': title}
                )
    
    def parse_article(self, response):
        item = ArticleItem()
        item['title'] = response.meta['title']
        item['source'] = '您的网站名'
        item['source_url'] = response.url
        item['category'] = 'energy'
        item['published_at'] = datetime.now()
        
        # 提取正文
        paragraphs = response.css('div.content p::text').getall()
        item['content'] = '\n\n'.join([p.strip() for p in paragraphs if p.strip()])
        item['summary'] = item['content'][:200] + '...'
        item['tags'] = ['能源', '您的网站名']
        
        if len(item['content']) > 100:
            yield item
```

## 🛠️ 故障排查

### 问题1：爬虫无法启动

```bash
# 检查MySQL是否运行
docker ps | grep mysql

# 如果没有运行，启动它
docker compose up -d mysql redis
```

### 问题2：抓取不到数据

```bash
# 测试网站是否可访问
curl -I http://www.news.cn/energy/

# 查看爬虫日志
tail -f crawler/.scrapy/logs/xinhua_real.log
```

### 问题3：数据库连接失败

```bash
# 测试数据库连接
mysql -h 127.0.0.1 -P 3307 -u root -ppassword energy_station -e "SELECT COUNT(*) FROM articles;"
```

## 📝 最佳实践

### 1. 礼貌爬取

- ✅ 设置合理的延迟（2-3秒）
- ✅ 限制并发请求（4-8个）
- ✅ 遵守robots.txt
- ✅ 使用真实的User-Agent

### 2. 数据质量

- ✅ 过滤无效内容（少于100字）
- ✅ 自动去重（基于URL）
- ✅ 验证数据完整性
- ✅ 记录错误日志

### 3. 性能优化

- ✅ 使用HTTP缓存
- ✅ 启用压缩传输
- ✅ 合理使用代理
- ✅ 监控爬虫状态

## 🎯 下一步计划

### 本周目标

- [x] 新华网能源频道 - **已完成**
- [ ] 人民网能源频道
- [ ] 中国能源报
- [ ] 北极星电力网
- [ ] 配置定时自动运行

### 本月目标

- [ ] 实现10+个新闻源
- [ ] 每日自动抓取500+篇文章
- [ ] 添加文章分类和标签
- [ ] 实现全文搜索功能
- [ ] 添加数据分析和可视化

## 📞 技术支持

### 相关文档

- `REAL_CRAWLER_SUCCESS.md` - 成功案例说明
- `CRAWLER_STATUS.md` - 爬虫系统状态
- `CRAWLER_SOLUTION.md` - 完整解决方案

### 常用命令

```bash
# 列出所有爬虫
cd crawler && ../backend/venv/bin/scrapy list

# 运行特定爬虫
../backend/venv/bin/scrapy crawl xinhua_real

# 查看爬虫设置
../backend/venv/bin/scrapy settings --get DOWNLOAD_DELAY

# 清理缓存
rm -rf .scrapy/httpcache
```

## 🎉 总结

我们成功实现了：

✅ **真实新闻爬虫** - 每次抓取15-20篇完整文章
✅ **完整内容** - 平均3000+字的高质量文章
✅ **自动化系统** - 可定时运行，无需人工干预
✅ **质量保证** - 自动去重、内容验证、错误处理
✅ **易于扩展** - 可快速添加更多新闻源

**Python爬虫确实很厉害！** 只要选择合适的工具和方法，就能抓取到真实、完整的新闻数据！
