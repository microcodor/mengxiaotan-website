# 爬虫日志功能总结

## ✅ 确认：爬虫是真实运行的

### 运行机制
- **真实进程**: 使用 `subprocess.Popen` 启动真实的 Scrapy 爬虫进程
- **进程管理**: 每个爬虫运行在独立的进程中，PID 保存在 Redis
- **状态跟踪**: 数据库记录爬虫状态（running/success/failed）
- **真实抓取**: 爬虫会访问真实网站并抓取数据到数据库

### 启动流程
```
用户点击"启动" 
  → 创建 CrawlLog 记录
  → 启动 Scrapy 进程
  → 保存 PID 到 Redis
  → 输出重定向到日志文件
  → 更新 Source 状态
```

### 停止流程
```
用户点击"停止"
  → 从 Redis 获取 PID
  → 发送 SIGTERM 信号
  → 更新 CrawlLog 状态
  → 清除 Redis 数据
```

---

## 📝 新增日志功能

### 1. 日志文件
- **位置**: `logs/crawler/{spider_name}_{log_id}.log`
- **内容**: 
  - 启动信息（爬虫名称、启动时间、启动用户）
  - Scrapy 运行日志（请求、响应、抓取内容）
  - 错误和警告信息
  - 统计信息（抓取数量、耗时）

### 2. 新增 API 端点

#### 获取日志详情（包含完整日志内容）
```http
GET /api/crawler/logs/{log_id}
```

#### 实时查看日志（最后N行）
```http
GET /api/crawler/logs/{log_id}/tail?lines=100
```

### 3. 日志内容示例

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

2026-04-12 16:30:05 [scrapy.core.engine] INFO: Spider opened
2026-04-12 16:30:10 [scrapy.core.scraper] DEBUG: Scraped from <200 https://...>
  {'title': '钢铁行业最新动态', 'url': '...', ...}
2026-04-12 16:30:15 [scrapy.core.scraper] DEBUG: Scraped from <200 https://...>
  {'title': '钢材价格走势分析', 'url': '...', ...}
...
2026-04-12 16:35:00 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
  {'item_scraped_count': 20, 'finish_time': ..., ...}
```

---

## 🎯 你能看到的内容

### 1. 启动/停止日志
- 谁启动了爬虫
- 什么时候启动的
- 爬虫名称和数据源
- 进程 ID

### 2. 抓取过程日志
- 访问了哪些 URL
- 抓取到了哪些文章
- 文章标题和链接
- 保存到数据库的记录

### 3. 错误日志
- 网络错误
- 解析错误
- 数据库错误
- 详细的错误堆栈

### 4. 统计信息
- 总请求数
- 成功响应数
- 抓取的文章数
- 运行时长

---

## 🔌 如何查看日志

### 方法 1: 通过 API（推荐）
```bash
# 获取日志详情
curl -H "Authorization: Bearer {token}" \
  http://localhost:5001/api/crawler/logs/123

# 实时查看最后100行
curl -H "Authorization: Bearer {token}" \
  http://localhost:5001/api/crawler/logs/123/tail?lines=100
```

### 方法 2: 直接查看文件
```bash
# 实时查看
tail -f logs/crawler/mysteel_123.log

# 查看最后100行
tail -n 100 logs/crawler/mysteel_123.log

# 搜索特定内容
grep "Scraped" logs/crawler/mysteel_123.log
```

### 方法 3: 通过前端（需要实现）
- 在管理后台的"爬虫管理"页面
- 点击"查看日志"按钮
- 实时刷新日志内容

---

## 📊 日志示例

### 成功抓取
```
2026-04-12 16:30:10 [scrapy.core.scraper] DEBUG: Scraped from <200 https://www.mysteel.com/news/1.html>
  {'title': '钢铁行业最新动态',
   'url': 'https://www.mysteel.com/news/1.html',
   'content': '...',
   'published_at': '2026-04-12'}
[Pipeline] 保存文章: 钢铁行业最新动态
[Pipeline] 文章已保存到数据库，ID: 109
```

### 错误情况
```
2026-04-12 16:30:15 [scrapy.core.scraper] ERROR: Error downloading <GET https://www.example.com>
  Traceback (most recent call last):
    ...
  ConnectionError: Connection refused
```

---

## 🚀 下一步

### 后端（已完成）
- ✅ 日志文件创建
- ✅ 日志内容记录
- ✅ API 端点实现
- ✅ 实时日志查看

### 前端（待实现）
- [ ] 日志查看页面
- [ ] 实时刷新功能
- [ ] 日志搜索和过滤
- [ ] 日志下载功能
- [ ] 日志高亮显示

---

## 📝 测试步骤

1. **启动爬虫**
   ```bash
   # 通过 API 启动
   curl -X POST -H "Authorization: Bearer {token}" \
     http://localhost:5001/api/crawler/spiders/test/run
   ```

2. **查看日志文件**
   ```bash
   ls -la logs/crawler/
   tail -f logs/crawler/test_*.log
   ```

3. **通过 API 查看日志**
   ```bash
   # 获取日志列表
   curl -H "Authorization: Bearer {token}" \
     http://localhost:5001/api/crawler/logs
   
   # 查看特定日志
   curl -H "Authorization: Bearer {token}" \
     http://localhost:5001/api/crawler/logs/{log_id}
   ```

4. **验证内容**
   - 日志文件包含启动信息
   - 日志文件包含 Scrapy 输出
   - 可以看到抓取的文章标题
   - 可以看到保存到数据库的记录

---

## ✅ 总结

**爬虫管理系统**:
- ✅ 真实运行 Scrapy 爬虫（不是模拟）
- ✅ 详细的日志记录（启动、运行、抓取、错误）
- ✅ 可以看到抓取的内容（文章标题、URL、保存记录）
- ✅ 支持实时查看日志
- ✅ 支持停止运行中的爬虫

**日志内容包括**:
- ✅ 启动信息（谁、何时、什么爬虫）
- ✅ 抓取过程（访问的URL、抓取的内容）
- ✅ 保存记录（保存到数据库的文章）
- ✅ 错误信息（网络错误、解析错误）
- ✅ 统计信息（抓取数量、耗时）

**查看方式**:
- ✅ API 端点（推荐）
- ✅ 直接查看文件
- ⏳ 前端页面（待实现）

详细文档请查看 `CRAWLER_LOGGING.md`
