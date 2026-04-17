# 多网站爬虫实施方案

## 测试结果总结

### ✅ 可直接抓取（使用Scrapy）

1. **新华网能源** - 已实现 ✅
   - URL: http://www.news.cn/energy/
   - 状态: 38个新闻链接
   - 方案: Scrapy（已验证）

2. **中国电力网** - 推荐实现 🌟
   - URL: http://www.chinapower.com.cn/
   - 状态: 595个新闻链接！
   - 方案: Scrapy + 编码处理

### ⚠️ 需要JavaScript渲染（使用Playwright）

3. **国家能源局**
   - URL: https://www.nea.gov.cn/xwzx/nyyw.htm
   - 状态: Vue.js动态渲染
   - 方案: Playwright

4. **国家发改委**
   - URL: https://www.ndrc.gov.cn/fggz/fgzy/
   - 状态: 动态渲染
   - 方案: Playwright

5. **北极星电力网**
   - URL: https://news.bjx.com.cn/list/power.html
   - 状态: 动态渲染
   - 方案: Playwright

6. **人民网能源**
   - URL: http://energy.people.com.cn/
   - 状态: 重定向或动态加载
   - 方案: Playwright

### ❌ 暂不可用

7. **中国能源网** - 404错误
8. **中国煤炭网** - 404错误
9. **光伏们** - 连接错误

## 实施优先级

### 第一阶段：快速见效（本周）

**目标：实现3-5个稳定的新闻源，每日抓取100+篇文章**

1. ✅ **新华网能源**（已完成）
   - 每次15-20篇
   - 已验证稳定

2. 🔥 **中国电力网**（优先级最高）
   - 潜力最大：595个链接
   - 使用Scrapy，快速实现
   - 预计每次50+篇

3. **北极星电力网**
   - 行业权威网站
   - 使用Playwright
   - 预计每次20-30篇

### 第二阶段：政府权威源（下周）

**目标：添加政府官方数据源**

4. **国家能源局**
   - 使用Playwright
   - 预计每次10-15篇

5. **国家发改委**
   - 使用Playwright
   - 预计每次10-15篇

### 第三阶段：垂直领域（本月）

**目标：覆盖更多细分领域**

6. 寻找替代的煤炭、新能源网站
7. 添加行业协会网站
8. 添加地方能源局网站

## 具体实施方案

### 方案A：Scrapy爬虫（适用于静态网站）

**适用网站：新华网、中国电力网**

**优点：**
- 速度快
- 资源占用少
- 易于维护
- 支持并发

**实现步骤：**
```python
# 1. 创建爬虫文件
scrapy genspider site_name domain.com

# 2. 配置选择器
def parse(self, response):
    for link in response.css('a[href]'):
        # 提取链接和标题
        
# 3. 解析文章内容
def parse_article(self, response):
    # 提取正文
```

**示例代码：**
```python
class ChinaPowerSpider(scrapy.Spider):
    name = 'chinapower'
    start_urls = ['http://www.chinapower.com.cn/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 4,
    }
    
    def parse(self, response):
        # 查找新闻链接
        for link in response.css('a[href*=".html"]'):
            yield scrapy.Request(
                response.urljoin(link.css('::attr(href)').get()),
                callback=self.parse_article
            )
    
    def parse_article(self, response):
        # 提取文章内容
        item = ArticleItem()
        item['title'] = response.css('h1::text').get()
        item['content'] = '\n'.join(response.css('div.content p::text').getall())
        yield item
```

### 方案B：Playwright爬虫（适用于动态网站）

**适用网站：国家能源局、发改委、北极星**

**优点：**
- 支持JavaScript渲染
- 可以处理复杂交互
- 模拟真实浏览器

**缺点：**
- 速度较慢
- 资源占用大

**实现步骤：**
```python
# 1. 安装Playwright
pip install playwright
playwright install chromium

# 2. 创建异步爬虫
async def fetch_with_playwright(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)
        html = await page.content()
        await browser.close()
        return html
```

**示例代码：**
```python
class NeaPlaywrightSpider(scrapy.Spider):
    name = 'nea_playwright'
    
    def start_requests(self):
        yield scrapy.Request(
            'https://www.nea.gov.cn/xwzx/nyyw.htm',
            callback=self.parse_with_playwright
        )
    
    def parse_with_playwright(self, response):
        # 使用Playwright获取渲染后的HTML
        loop = asyncio.new_event_loop()
        html = loop.run_until_complete(
            fetch_with_playwright(response.url)
        )
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        # 提取新闻链接
```

### 方案C：混合方案（推荐）

**策略：根据网站特点选择最佳方案**

1. **优先使用Scrapy**
   - 测试网站是否可以直接抓取
   - 如果可以，使用Scrapy（快速高效）

2. **必要时使用Playwright**
   - 如果Scrapy无法获取内容
   - 切换到Playwright方案

3. **智能降级**
   - 如果Playwright也失败
   - 记录日志，跳过该网站
   - 定期重试

## 编码问题处理

### 问题：中文乱码

**原因：**
- 网站使用GBK/GB2312编码
- Requests默认使用ISO-8859-1

**解决方案：**
```python
# 方法1：手动设置编码
response.encoding = 'utf-8'  # 或 'gbk', 'gb2312'

# 方法2：自动检测编码
import chardet
encoding = chardet.detect(response.content)['encoding']
response.encoding = encoding

# 方法3：在Scrapy中配置
class MySpider(scrapy.Spider):
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept-Charset': 'utf-8, gbk, gb2312',
        }
    }
```

## 反爬虫应对策略

### 1. User-Agent轮换

```python
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
]

# 随机选择
import random
headers = {'User-Agent': random.choice(USER_AGENTS)}
```

### 2. 请求延迟

```python
custom_settings = {
    'DOWNLOAD_DELAY': 2,  # 2秒延迟
    'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机延迟
}
```

### 3. 使用代理

```python
# 配置代理池
PROXIES = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
]

# 在请求中使用
meta = {'proxy': random.choice(PROXIES)}
```

### 4. Cookie管理

```python
# 保持会话
session = requests.Session()

# 或在Scrapy中
custom_settings = {
    'COOKIES_ENABLED': True,
}
```

## 数据质量保证

### 1. 内容验证

```python
def validate_article(item):
    # 检查必填字段
    if not item.get('title') or not item.get('content'):
        return False
    
    # 检查内容长度
    if len(item['content']) < 100:
        return False
    
    # 检查是否包含关键词
    keywords = ['能源', '电力', '煤炭', '新能源']
    if not any(kw in item['content'] for kw in keywords):
        return False
    
    return True
```

### 2. 去重机制

```python
# 基于URL去重
seen_urls = set()

def is_duplicate(url):
    if url in seen_urls:
        return True
    seen_urls.add(url)
    return False

# 或使用数据库唯一索引
# CREATE UNIQUE INDEX idx_source_url ON articles(source_url);
```

### 3. 错误处理

```python
def parse_article(self, response):
    try:
        item = self.extract_item(response)
        if validate_article(item):
            yield item
        else:
            self.logger.warning(f'Invalid article: {response.url}')
    except Exception as e:
        self.logger.error(f'Error parsing {response.url}: {str(e)}')
```

## 性能优化

### 1. 并发控制

```python
custom_settings = {
    'CONCURRENT_REQUESTS': 8,  # 并发请求数
    'CONCURRENT_REQUESTS_PER_DOMAIN': 4,  # 每个域名的并发数
}
```

### 2. 缓存策略

```python
custom_settings = {
    'HTTPCACHE_ENABLED': True,
    'HTTPCACHE_EXPIRATION_SECS': 3600,  # 1小时
    'HTTPCACHE_DIR': 'httpcache',
}
```

### 3. 增量更新

```python
def should_crawl(url):
    # 检查URL是否已存在
    existing = Article.query.filter_by(source_url=url).first()
    if existing:
        # 检查是否需要更新
        if (datetime.now() - existing.created_at).days < 7:
            return False
    return True
```

## 监控和告警

### 1. 爬虫健康检查

```python
def check_crawler_health():
    # 检查最近1小时的抓取量
    recent_count = Article.query.filter(
        Article.created_at > datetime.now() - timedelta(hours=1)
    ).count()
    
    if recent_count < 10:
        send_alert('爬虫抓取量异常')
```

### 2. 错误率监控

```python
def monitor_error_rate():
    total_requests = get_total_requests()
    failed_requests = get_failed_requests()
    error_rate = failed_requests / total_requests
    
    if error_rate > 0.1:  # 错误率超过10%
        send_alert(f'错误率过高: {error_rate:.2%}')
```

### 3. 数据质量监控

```python
def monitor_data_quality():
    # 检查平均文章长度
    avg_length = db.session.query(
        func.avg(func.length(Article.content))
    ).scalar()
    
    if avg_length < 500:
        send_alert(f'文章平均长度过短: {avg_length}')
```

## 实施时间表

### Week 1
- [x] 新华网能源（已完成）
- [ ] 中国电力网（Scrapy）
- [ ] 北极星电力网（Playwright）

### Week 2
- [ ] 国家能源局（Playwright）
- [ ] 国家发改委（Playwright）
- [ ] 配置定时任务

### Week 3
- [ ] 添加5个新网站
- [ ] 优化性能
- [ ] 完善监控

### Week 4
- [ ] 数据分析功能
- [ ] 用户界面优化
- [ ] 系统测试和优化

## 预期成果

### 数据规模
- **每日抓取**: 200-500篇文章
- **每月抓取**: 6,000-15,000篇文章
- **数据源**: 10+个权威网站

### 数据质量
- **平均文章长度**: 1,000-5,000字
- **内容完整性**: >95%
- **去重准确率**: >99%

### 系统性能
- **抓取速度**: 10-20篇/分钟
- **系统稳定性**: >99%
- **错误率**: <5%
