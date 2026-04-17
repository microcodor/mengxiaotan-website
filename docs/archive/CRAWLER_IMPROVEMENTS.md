# 爬虫功能改进方案

## 当前问题

1. ✅ **爬虫可以运行** - Scrapy正常启动
2. ❌ **没有抓取到数据** - CSS选择器不匹配或网站结构变化
3. ❌ **看不到进度** - 前端没有实时更新机制
4. ❌ **停止按钮无效** - 进程管理有问题

## 问题分析

### 1. 爬虫未抓取数据
从日志看：`scraped 0 items`，说明：
- 爬虫启动成功
- 页面请求成功（200状态码）
- 但没有解析出任何item

**可能原因：**
- CSS选择器不匹配实际页面结构
- 网站使用JavaScript动态加载内容
- 网站结构已更新

### 2. 前端看不到进度
当前实现：
- 点击运行后发送API请求
- 后端启动爬虫进程
- 前端每10秒刷新一次状态

**问题：**
- 10秒刷新间隔太长
- 没有实时进度显示
- 爬虫运行状态更新不及时

### 3. 停止按钮无效
当前实现使用`pgrep`和`kill`：
```python
result = subprocess.run(['pgrep', '-f', f'scrapy crawl {spider_name}'])
```

**问题：**
- macOS上pgrep可能不可用
- 进程查找不准确
- 没有保存进程ID

## 解决方案

### 方案1：修复爬虫数据抓取（优先）

#### 1.1 使用通用的测试爬虫
创建一个简单的测试爬虫，抓取固定的测试数据：

```python
class TestSpider(scrapy.Spider):
    name = 'test'
    
    def start_requests(self):
        # 直接生成测试数据
        yield {
            'title': '测试文章',
            'summary': '这是一篇测试文章',
            'content': '测试内容',
            'source': '测试来源',
            'category': 'test'
        }
```

#### 1.2 使用RSS源
很多政府网站提供RSS订阅，更稳定：
```python
from scrapy.spiders import XMLFeedSpider

class RSSSpider(XMLFeedSpider):
    name = 'ndrc_rss'
    start_urls = ['https://www.ndrc.gov.cn/rss/xxgk.xml']
    iterator = 'iternodes'
    itertag = 'item'
```

#### 1.3 使用Selenium处理动态页面
如果网站使用JavaScript：
```python
from scrapy_selenium import SeleniumRequest

def start_requests(self):
    yield SeleniumRequest(url=url, callback=self.parse)
```

### 方案2：改进进度显示

#### 2.1 使用WebSocket实时推送
```python
# 后端
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('subscribe_crawler')
def handle_subscribe(data):
    spider_name = data['spider']
    # 订阅爬虫状态
```

#### 2.2 使用轮询优化
```typescript
// 前端 - 运行时每2秒刷新
const { data } = useQuery({
  queryKey: ['spiders'],
  queryFn: () => api.get('/crawler/spiders'),
  refetchInterval: isAnyRunning ? 2000 : 10000, // 有爬虫运行时2秒，否则10秒
})
```

#### 2.3 显示详细进度
在CrawlLog中记录更多信息：
- 当前抓取页数
- 已抓取文章数
- 错误数
- 预计剩余时间

### 方案3：改进进程管理

#### 3.1 保存进程ID
```python
# 启动时保存PID
process = subprocess.Popen(...)
redis_client.set(f'crawler:{spider_name}:pid', process.pid)

# 停止时使用保存的PID
pid = redis_client.get(f'crawler:{spider_name}:pid')
if pid:
    os.kill(int(pid), signal.SIGTERM)
```

#### 3.2 使用Celery任务队列
```python
from celery import Celery

@celery.task
def run_spider(spider_name):
    # 在Celery worker中运行爬虫
    # 可以方便地管理和监控
```

## 快速修复方案（推荐）

### 步骤1：创建测试爬虫
创建一个能确保抓取到数据的测试爬虫。

### 步骤2：优化轮询频率
运行时改为2秒刷新一次。

### 步骤3：改进进程管理
使用Redis保存PID。

### 步骤4：添加详细日志
在前端显示爬虫日志输出。

## 实施计划

### 立即执行（30分钟）
1. ✅ 创建测试爬虫验证流程
2. ✅ 优化前端轮询频率
3. ✅ 改进进程管理（使用Redis）
4. ✅ 添加更详细的状态显示

### 短期优化（1-2小时）
1. 修复现有爬虫的CSS选择器
2. 添加爬虫日志查看功能
3. 添加爬虫配置管理
4. 优化错误处理

### 长期优化（1-2天）
1. 实现WebSocket实时推送
2. 使用Celery任务队列
3. 添加爬虫性能监控
4. 实现分布式爬虫

## 测试步骤

### 1. 测试爬虫基本功能
```bash
cd crawler
../backend/venv/bin/scrapy crawl test
```

### 2. 测试API接口
```bash
# 启动爬虫
curl -X POST http://localhost:5001/api/crawler/spiders/test/run \
  -H "Authorization: Bearer $TOKEN"

# 查看状态
curl http://localhost:5001/api/crawler/spiders \
  -H "Authorization: Bearer $TOKEN"

# 停止爬虫
curl -X POST http://localhost:5001/api/crawler/spiders/test/stop \
  -H "Authorization: Bearer $TOKEN"
```

### 3. 测试前端界面
1. 访问 http://localhost:5173/admin/crawler
2. 点击"运行"按钮
3. 观察状态变化
4. 查看日志记录
5. 测试停止功能

## 预期效果

修复后应该能够：
- ✅ 爬虫成功抓取数据
- ✅ 前端实时显示运行状态
- ✅ 显示抓取进度（页数、文章数）
- ✅ 停止按钮正常工作
- ✅ 查看详细日志
- ✅ 错误提示清晰
