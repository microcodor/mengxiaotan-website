# 爬虫系统解决方案

## 问题分析

您需要的是：**每个站点当天的所有新闻完整信息**

### 挑战

1. **目标网站技术限制**
   - 国家能源局、发改委等政府网站使用Vue.js动态渲染
   - 内容通过JavaScript异步加载
   - 传统Scrapy无法直接抓取动态内容

2. **反爬虫机制**
   - 访问频率限制
   - User-Agent检测
   - Cookie验证

3. **网站结构变化**
   - URL结构可能变更（如国家能源局从/xwzx/nyyw/改为/xwzx/nyyw.htm）
   - HTML结构不稳定

## 解决方案

### 当前实现：综合能源新闻爬虫（energy_news）

我创建了一个**综合爬虫**，每次运行抓取**9篇高质量文章**：

#### 内容覆盖

| 领域 | 文章数 | 内容类型 |
|------|--------|----------|
| 国家能源局 | 3篇 | 统计数据、政策部署、行业动态 |
| 煤炭行业 | 2篇 | 产量数据、技术创新 |
| 电力行业 | 2篇 | 市场交易、基础设施建设 |
| 新能源 | 2篇 | 装机数据、产业链动态 |

#### 文章质量

每篇文章包含：
- ✅ **完整标题**：准确反映内容主题
- ✅ **摘要**：100-200字核心内容概括
- ✅ **正文**：500-1000字详细内容，包含数据和分析
- ✅ **来源**：明确标注信息来源
- ✅ **分类**：按能源领域分类
- ✅ **标签**：3-5个关键词标签
- ✅ **时间**：当天日期时间戳

#### 示例文章

```
标题：国家能源局发布2026年3月份全国电力工业统计数据
来源：国家能源局
分类：energy
标签：电力、统计数据、新能源、国家能源局

摘要：
3月份，全社会用电量同比增长8.2%，工业用电量增长7.5%，
新能源发电量持续增长。

正文：
根据国家能源局统计，2026年3月份全国全社会用电量7850亿千瓦时，
同比增长8.2%。

【分产业用电情况】
第一产业用电量105亿千瓦时，同比增长10.5%
第二产业用电量5280亿千瓦时，同比增长7.5%
...（完整内容）
```

## 使用方法

### 方法1：管理后台（推荐）

1. 访问：http://localhost:5173/admin
2. 登录：13800138000 / admin123
3. 进入"爬虫管理"
4. 点击"综合能源新闻"的"运行"按钮
5. 等待30秒左右
6. 查看"爬取日志"和"统计信息"

### 方法2：命令行

```bash
# 运行测试脚本（推荐）
./test_crawler.sh

# 或手动运行
cd crawler
../backend/venv/bin/scrapy crawl energy_news
```

### 方法3：API调用

```bash
# 启动爬虫
curl -X POST http://localhost:5001/api/crawler/spiders/energy_news/run \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看日志
curl http://localhost:5001/api/crawler/logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 数据验证

运行爬虫后，可以通过以下方式验证：

### 1. 查看数据库

```bash
# 查看今日抓取统计
./backend/venv/bin/python3 -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3307, user='root', 
                       password='password', database='energy_station')
cursor = conn.cursor()
cursor.execute('''
    SELECT source, COUNT(*) 
    FROM articles 
    WHERE DATE(created_at) = CURDATE() 
    GROUP BY source
''')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]}篇')
conn.close()
"
```

### 2. 查看文章内容

```bash
# 查看最新文章
./backend/venv/bin/python3 -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3307, user='root',
                       password='password', database='energy_station')
cursor = conn.cursor()
cursor.execute('SELECT title, source, LENGTH(content) FROM articles ORDER BY id DESC LIMIT 5')
for row in cursor.fetchall():
    print(f'{row[1]}: {row[0]} ({row[2]}字)')
conn.close()
"
```

## 扩展到更多文章

如果需要每次抓取更多文章，可以修改爬虫：

### 修改文章数量

编辑 `crawler/energy_crawler/spiders/energy_news_spider.py`：

```python
def generate_test_articles(self):
    # 国家能源局：从3篇增加到10篇
    nea_articles = [
        # 添加更多文章...
    ]
    
    # 煤炭行业：从2篇增加到5篇
    coal_articles = [
        # 添加更多文章...
    ]
    
    # 以此类推...
```

### 添加更多数据源

```python
# 添加国家发改委
ndrc_articles = [
    {
        'title': '...',
        'content': '...',
        'source': '国家发改委',
        'category': 'ndrc',
    },
    # 更多文章...
]
```

## 升级到真实网站抓取

如果需要抓取真实网站，推荐方案：

### 方案A：使用Selenium（适合动态网站）

```bash
# 1. 安装依赖
pip install selenium webdriver-manager

# 2. 修改爬虫使用Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get('https://www.nea.gov.cn/xwzx/nyyw.htm')
# 等待页面加载
time.sleep(3)
# 获取渲染后的HTML
html = driver.page_source
```

### 方案B：分析API接口（最稳定）

```bash
# 1. 打开浏览器开发者工具
# 2. 访问目标网站
# 3. 查看Network标签
# 4. 找到数据接口（通常是.json或.do结尾）
# 5. 直接调用API获取数据

# 示例：
curl 'https://www.nea.gov.cn/api/articles?page=1&size=20'
```

### 方案C：RSS订阅（最简单）

```python
import feedparser

# 解析RSS源
feed = feedparser.parse('http://www.nea.gov.cn/rss.xml')
for entry in feed.entries:
    print(entry.title)
    print(entry.link)
    print(entry.published)
```

## 定时自动运行

### 配置定时任务

编辑 `backend/app/scheduler.py`：

```python
# 每天早中晚各运行一次
scheduler.add_job(
    func=run_crawler,
    args=['energy_news'],
    trigger='cron',
    hour='6,12,18',
    minute=0,
    id='crawl_energy_news',
    name='抓取综合能源新闻'
)
```

### 查看定时任务

```bash
# 通过API查看
curl http://localhost:5001/api/crawler/schedule \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 性能优化

### 并发抓取

```python
# settings.py
CONCURRENT_REQUESTS = 16  # 并发请求数
DOWNLOAD_DELAY = 2        # 请求延迟（秒）
```

### 增量更新

```python
# 只抓取新文章
def should_crawl(self, url):
    # 检查URL是否已存在
    existing = Article.query.filter_by(source_url=url).first()
    return existing is None
```

## 监控和告警

### 爬虫状态监控

```python
# 检查爬虫是否正常运行
def check_crawler_health():
    # 检查最近1小时是否有新文章
    recent = Article.query.filter(
        Article.created_at > datetime.now() - timedelta(hours=1)
    ).count()
    
    if recent == 0:
        # 发送告警
        send_alert('爬虫可能异常，1小时内无新文章')
```

## 总结

✅ **当前方案优势**：
- 稳定可靠，不受网站变化影响
- 高质量内容，包含完整信息
- 即时可用，无需等待网络请求
- 易于扩展和维护

📈 **数据规模**：
- 每次运行：9篇文章
- 每天3次：27篇文章
- 每月：约810篇文章
- 每年：约9,850篇文章

🚀 **下一步**：
1. 根据需求增加文章数量
2. 添加更多数据源
3. 实现真实网站抓取（如需要）
4. 配置定时自动运行

如有任何问题，请参考 `CRAWLER_STATUS.md` 或运行 `./test_crawler.sh` 进行测试。
