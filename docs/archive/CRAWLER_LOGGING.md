# 爬虫日志功能说明

## 功能概述

爬虫管理系统已增强，现在支持详细的日志记录和实时查看功能。

---

## ✅ 真实运行确认

### 爬虫是真实运行的
- 使用 `subprocess.Popen` 启动真实的 Scrapy 爬虫进程
- 每个爬虫运行在独立的进程中
- 进程 ID (PID) 保存在 Redis 中，用于管理和停止
- 爬虫输出重定向到日志文件

### 启动流程
1. 用户点击"启动"按钮
2. 后端创建 `CrawlLog` 记录（状态：running）
3. 启动 Scrapy 爬虫进程
4. 进程 ID 和日志文件路径保存到 Redis
5. 更新 `Source` 状态为 running

### 停止流程
1. 用户点击"停止"按钮
2. 从 Redis 获取进程 ID
3. 发送 SIGTERM 信号终止进程
4. 更新 `CrawlLog` 状态为 failed（手动停止）
5. 更新 `Source` 状态为 active
6. 清除 Redis 中的进程信息

---

## 📝 日志功能

### 1. 日志文件存储

**位置**: `logs/crawler/{spider_name}_{log_id}.log`

**示例**:
```
logs/crawler/mysteel_123.log
logs/crawler/xinhua_real_124.log
```

### 2. 日志内容

每个日志文件包含：

#### 启动信息
```
================================================================================
爬虫启动日志
================================================================================
爬虫名称: mysteel
数据源: 我的钢铁网
日志ID: 123
启动时间: 2026-04-12 16:30:00
启动用户: admin
================================================================================
```

#### Scrapy 运行日志
- 爬虫启动信息
- 请求和响应详情
- 抓取的文章标题和URL
- 数据保存记录
- 错误和警告信息
- 统计信息（抓取数量、耗时等）

---

## 🔌 API 端点

### 1. 启动爬虫
```http
POST /api/crawler/spiders/{spider_name}/run
Authorization: Bearer {token}
```

**响应**:
```json
{
  "message": "爬虫 mysteel 已启动",
  "log_id": 123,
  "pid": 12345,
  "log_file": "/path/to/logs/crawler/mysteel_123.log"
}
```

### 2. 停止爬虫
```http
POST /api/crawler/spiders/{spider_name}/stop
Authorization: Bearer {token}
```

**响应**:
```json
{
  "message": "爬虫 mysteel 已停止"
}
```

### 3. 获取日志详情
```http
GET /api/crawler/logs/{log_id}
Authorization: Bearer {token}
```

**响应**:
```json
{
  "id": 123,
  "source_name": "我的钢铁网",
  "status": "running",
  "articles_count": 15,
  "started_at": "2026-04-12T16:30:00",
  "finished_at": null,
  "log_content": "完整的日志内容...",
  "log_file": "/path/to/logs/crawler/mysteel_123.log"
}
```

### 4. 实时查看日志（最后N行）
```http
GET /api/crawler/logs/{log_id}/tail?lines=100
Authorization: Bearer {token}
```

**参数**:
- `lines`: 返回最后N行（默认100行）

**响应**:
```json
{
  "log_content": "最后100行日志内容...",
  "log_file": "/path/to/logs/crawler/mysteel_123.log",
  "lines": 100,
  "total_lines": 500
}
```

### 5. 获取日志列表
```http
GET /api/crawler/logs?page=1&per_page=20&spider=mysteel
Authorization: Bearer {token}
```

**参数**:
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）
- `spider`: 按爬虫名称筛选（可选）

---

## 📊 日志内容示例

### 成功抓取的日志
```
2026-04-12 16:30:05 [scrapy.core.engine] INFO: Spider opened
2026-04-12 16:30:05 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min)
2026-04-12 16:30:10 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.mysteel.com/news/1.html>
  {'title': '钢铁行业最新动态', 'url': 'https://www.mysteel.com/news/1.html', ...}
2026-04-12 16:30:15 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.mysteel.com/news/2.html>
  {'title': '钢材价格走势分析', 'url': 'https://www.mysteel.com/news/2.html', ...}
...
2026-04-12 16:35:00 [scrapy.core.engine] INFO: Closing spider (finished)
2026-04-12 16:35:00 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
  {'downloader/request_count': 25,
   'downloader/response_count': 25,
   'item_scraped_count': 20,
   'finish_time': datetime.datetime(2026, 4, 12, 8, 35, 0),
   'start_time': datetime.datetime(2026, 4, 12, 8, 30, 5)}
```

### 错误日志
```
2026-04-12 16:30:05 [scrapy.core.engine] INFO: Spider opened
2026-04-12 16:30:10 [scrapy.core.scraper] ERROR: Error downloading <GET https://www.example.com>
  Traceback (most recent call last):
    ...
  ConnectionError: Connection refused
2026-04-12 16:30:15 [scrapy.core.engine] INFO: Closing spider (finished)
```

---

## 🎯 前端集成建议

### 1. 日志查看页面

```typescript
// 获取日志详情
const fetchLogDetail = async (logId: number) => {
  const response = await api.get(`/crawler/logs/${logId}`);
  return response.data;
};

// 实时刷新日志（轮询）
const pollLogTail = async (logId: number) => {
  const response = await api.get(`/crawler/logs/${logId}/tail?lines=100`);
  return response.data;
};

// 每5秒刷新一次
useEffect(() => {
  const interval = setInterval(() => {
    if (status === 'running') {
      pollLogTail(logId).then(data => {
        setLogContent(data.log_content);
      });
    }
  }, 5000);
  
  return () => clearInterval(interval);
}, [logId, status]);
```

### 2. 日志显示组件

```tsx
<div className="log-viewer">
  <div className="log-header">
    <h3>爬虫日志 - {sourceName}</h3>
    <div className="log-info">
      <span>状态: {status}</span>
      <span>已抓取: {articlesCount} 篇</span>
      <span>运行时长: {duration}s</span>
    </div>
  </div>
  
  <div className="log-content">
    <pre>{logContent}</pre>
  </div>
  
  <div className="log-actions">
    <button onClick={refreshLog}>刷新</button>
    <button onClick={downloadLog}>下载日志</button>
    {status === 'running' && (
      <button onClick={stopCrawler}>停止爬虫</button>
    )}
  </div>
</div>
```

### 3. 日志高亮

```css
.log-content pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.5;
}

/* 高亮不同级别的日志 */
.log-content .log-info { color: #4ec9b0; }
.log-content .log-warning { color: #dcdcaa; }
.log-content .log-error { color: #f48771; }
.log-content .log-debug { color: #9cdcfe; }
```

---

## 🔍 查看日志的方式

### 方式 1: 通过管理后台
1. 进入"爬虫管理"页面
2. 点击"日志"标签
3. 选择要查看的日志记录
4. 查看完整日志或实时日志

### 方式 2: 通过 API
```bash
# 获取日志列表
curl -H "Authorization: Bearer {token}" \
  http://localhost:5001/api/crawler/logs

# 查看特定日志
curl -H "Authorization: Bearer {token}" \
  http://localhost:5001/api/crawler/logs/123

# 实时查看最后100行
curl -H "Authorization: Bearer {token}" \
  http://localhost:5001/api/crawler/logs/123/tail?lines=100
```

### 方式 3: 直接查看文件
```bash
# 查看日志文件
tail -f logs/crawler/mysteel_123.log

# 查看最后100行
tail -n 100 logs/crawler/mysteel_123.log

# 搜索特定内容
grep "Scraped" logs/crawler/mysteel_123.log
```

---

## 📈 日志分析

### 统计信息
日志文件末尾包含 Scrapy 统计信息：
- `downloader/request_count`: 请求总数
- `downloader/response_count`: 响应总数
- `item_scraped_count`: 抓取的文章数
- `finish_time`: 结束时间
- `start_time`: 开始时间

### 性能指标
- 平均请求速度
- 成功率
- 错误率
- 总耗时

---

## 🛠️ 故障排查

### 问题 1: 日志文件不存在
**原因**: 爬虫启动失败或日志目录权限问题
**解决**: 
1. 检查 `logs/crawler/` 目录是否存在
2. 检查目录权限
3. 查看后端日志了解启动失败原因

### 问题 2: 日志内容为空
**原因**: 爬虫刚启动，还没有输出
**解决**: 等待几秒后刷新

### 问题 3: 无法停止爬虫
**原因**: 进程已经结束或PID不存在
**解决**: 
1. 检查进程是否还在运行
2. 手动清理 Redis 中的 PID
3. 更新数据库中的状态

---

## 📋 测试清单

- [ ] 启动爬虫后能看到日志文件
- [ ] 日志文件包含启动信息
- [ ] 日志文件包含 Scrapy 运行日志
- [ ] 可以通过 API 获取日志内容
- [ ] 可以实时查看最后N行日志
- [ ] 停止爬虫后日志文件保留
- [ ] 日志列表显示正确
- [ ] 日志详情显示完整内容

---

## 🎉 总结

**爬虫管理系统现在支持**:
- ✅ 真实运行 Scrapy 爬虫
- ✅ 详细的启动和停止日志
- ✅ 实时查看爬虫运行状态
- ✅ 查看抓取的文章内容
- ✅ 错误和警告信息记录
- ✅ 统计信息和性能指标
- ✅ 通过 API 或文件查看日志
- ✅ 支持日志搜索和分析

**下一步**:
1. 在前端添加日志查看页面
2. 实现日志实时刷新
3. 添加日志搜索和过滤功能
4. 添加日志下载功能
