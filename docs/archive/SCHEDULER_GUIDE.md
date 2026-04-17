# 定时任务系统使用指南

## 功能概述

定时任务系统使用 APScheduler 实现爬虫的自动调度，无需手动运行爬虫，系统会在指定时间自动执行。

## 功能特点

✅ **自动运行**：每天3次自动运行所有爬虫（08:00、12:00、18:00）  
✅ **任务管理**：支持暂停、恢复、立即触发任务  
✅ **状态监控**：实时查看任务状态和下次运行时间  
✅ **手动触发**：支持手动立即运行所有爬虫或单个爬虫  
✅ **可配置**：可通过环境变量启用/禁用定时任务  

## 默认任务配置

系统默认配置了3个定时任务：

| 任务名称 | 任务ID | 运行时间 | 说明 |
|---------|--------|---------|------|
| 早间爬虫任务 | morning_crawl | 每天 08:00 | 抓取早间新闻 |
| 午间爬虫任务 | noon_crawl | 每天 12:00 | 抓取午间新闻 |
| 晚间爬虫任务 | evening_crawl | 每天 18:00 | 抓取晚间新闻 |

## 使用方法

### 1. 启用定时任务

定时任务默认启用，如需禁用，在 `.env` 文件中设置：

```bash
ENABLE_SCHEDULER=false
```

### 2. 访问管理页面

登录管理后台，访问"定时任务"菜单：

```
http://localhost:5173/admin/scheduler
```

### 3. 查看任务状态

页面显示：
- 调度器状态（已启用/未启用）
- 运行状态（运行中/已停止）
- 任务数量
- 任务列表（任务名称、ID、触发器、下次运行时间）

### 4. 管理任务

**立即运行**
- 点击任务行的"播放"按钮，立即触发该任务
- 点击页面右上角"立即运行所有爬虫"按钮，运行所有爬虫

**暂停任务**
- 点击任务行的"暂停"按钮，暂停该任务
- 暂停后任务将不会自动运行

**恢复任务**
- 暂停的任务可以通过API恢复（前端待实现）

## API接口

### 获取调度器状态

```http
GET /api/scheduler/status
Authorization: Bearer <token>
```

**响应**：
```json
{
  "enabled": true,
  "running": true,
  "jobs_count": 3,
  "message": "定时任务调度器正在运行"
}
```

### 获取任务列表

```http
GET /api/scheduler/jobs
Authorization: Bearer <token>
```

**响应**：
```json
{
  "enabled": true,
  "jobs": [
    {
      "id": "morning_crawl",
      "name": "早间爬虫任务",
      "next_run_time": "2026-04-12T08:00:00+08:00",
      "trigger": "cron[hour='8', minute='0']"
    }
  ],
  "total": 3
}
```

### 暂停任务

```http
POST /api/scheduler/jobs/{job_id}/pause
Authorization: Bearer <token>
```

### 恢复任务

```http
POST /api/scheduler/jobs/{job_id}/resume
Authorization: Bearer <token>
```

### 立即触发任务

```http
POST /api/scheduler/jobs/{job_id}/trigger
Authorization: Bearer <token>
```

### 运行所有爬虫

```http
POST /api/scheduler/run-all
Authorization: Bearer <token>
```

### 运行单个爬虫

```http
POST /api/scheduler/run-single
Authorization: Bearer <token>
Content-Type: application/json

{
  "spider_name": "xinhua_real"
}
```

## 技术实现

### 后端架构

```
backend/
├── app/
│   ├── scheduler.py          # 调度器核心逻辑
│   ├── api/
│   │   └── scheduler.py      # 定时任务API
│   └── __init__.py           # 初始化调度器
└── config.py                 # 调度器配置
```

### 核心组件

**1. 调度器（scheduler.py）**
- 使用 APScheduler 的 BackgroundScheduler
- 时区设置为 Asia/Shanghai
- 支持 Cron 触发器和间隔触发器

**2. 任务执行**
- 使用 subprocess 运行 Scrapy 爬虫
- 10分钟超时保护
- 完整的日志记录

**3. API接口（api/scheduler.py）**
- 任务管理接口
- 状态查询接口
- 手动触发接口

### 前端页面

```
frontend/src/pages/admin/Scheduler.tsx
```

功能：
- 实时显示调度器状态
- 任务列表展示
- 任务操作（暂停、触发）
- 手动运行爬虫
- 自动刷新（30秒）

## 配置选项

### 环境变量

```bash
# 启用/禁用定时任务
ENABLE_SCHEDULER=true

# 时区（默认：Asia/Shanghai）
SCHEDULER_TIMEZONE=Asia/Shanghai
```

### 修改运行时间

编辑 `backend/app/scheduler.py`，修改 CronTrigger 参数：

```python
# 修改早间任务为 7:00
scheduler.add_job(
    func=run_all_crawlers,
    trigger=CronTrigger(hour=7, minute=0),  # 改为7点
    id='morning_crawl',
    name='早间爬虫任务',
    replace_existing=True
)
```

### 添加新任务

在 `init_scheduler()` 函数中添加：

```python
# 添加每小时运行一次的任务
scheduler.add_job(
    func=run_all_crawlers,
    trigger=IntervalTrigger(hours=1),
    id='hourly_crawl',
    name='每小时爬虫任务',
    replace_existing=True
)
```

## 日志查看

### 后端日志

定时任务的执行日志会输出到后端控制台：

```bash
# 查看后端日志
cd backend
source venv/bin/activate
python app.py
```

日志示例：
```
2026-04-11 08:00:00,123 INFO ============================================================
2026-04-11 08:00:00,124 INFO 开始批量运行爬虫 - 2026-04-11 08:00:00
2026-04-11 08:00:00,125 INFO ============================================================
2026-04-11 08:00:01,234 INFO 开始运行爬虫: xinhua_real
2026-04-11 08:00:15,456 INFO 爬虫 xinhua_real 运行成功
...
2026-04-11 08:05:30,789 INFO ============================================================
2026-04-11 08:05:30,790 INFO 批量运行完成 - 成功: 9, 失败: 0
2026-04-11 08:05:30,791 INFO ============================================================
```

### 爬虫日志

爬虫的详细日志在爬虫管理页面查看：

```
http://localhost:5173/admin/crawler
```

## 常见问题

### Q1: 定时任务没有运行？

**A**: 检查以下几点：
1. 确认 `ENABLE_SCHEDULER=true`
2. 查看后端日志是否有错误
3. 确认调度器状态为"运行中"
4. 检查任务的下次运行时间

### Q2: 如何修改运行频率？

**A**: 编辑 `backend/app/scheduler.py`，修改 CronTrigger 参数。例如：
- 每小时运行：`IntervalTrigger(hours=1)`
- 每30分钟运行：`IntervalTrigger(minutes=30)`
- 每天特定时间：`CronTrigger(hour=8, minute=30)`

### Q3: 任务运行失败怎么办？

**A**: 
1. 查看后端日志中的错误信息
2. 检查爬虫是否正常（在爬虫管理页面手动测试）
3. 确认数据库和Redis连接正常
4. 检查爬虫目录路径是否正确

### Q4: 如何禁用某个任务？

**A**: 
1. 在管理页面点击"暂停"按钮
2. 或在代码中注释掉对应的 `scheduler.add_job()` 调用

### Q5: 可以添加更多任务吗？

**A**: 可以！在 `backend/app/scheduler.py` 的 `init_scheduler()` 函数中添加新任务。

## 性能优化

### 1. 并发控制

默认配置：
- 同一任务最多只能有1个实例运行（`max_instances=1`）
- 错过的任务会合并执行（`coalesce=True`）
- 错过任务的宽限时间为5分钟（`misfire_grace_time=300`）

### 2. 超时设置

爬虫运行超时时间为10分钟，可在 `run_crawler()` 函数中修改：

```python
result = subprocess.run(
    ['scrapy', 'crawl', spider_name],
    timeout=600  # 修改超时时间（秒）
)
```

### 3. 资源占用

- 调度器使用后台线程，资源占用极小
- 爬虫运行时会占用CPU和内存
- 建议错开高峰时段运行

## 监控告警

### 未来计划

1. **邮件告警**：任务失败时发送邮件通知
2. **企业微信告警**：任务失败时推送企业微信消息
3. **运行统计**：记录每次运行的成功率和耗时
4. **性能监控**：监控系统资源使用情况

## 总结

定时任务系统让爬虫实现了自动化运行，无需人工干预。系统会在每天的早、中、晚三个时段自动抓取最新资讯，确保数据的时效性。

**关键特性**：
- ✅ 自动运行（每天3次）
- ✅ 任务管理（暂停、恢复、触发）
- ✅ 状态监控（实时查看）
- ✅ 手动触发（随时运行）
- ✅ 可配置（灵活调整）

**下一步**：
- 添加监控告警功能
- 优化任务调度策略
- 增加运行统计报表

---

**最后更新**: 2026-04-11  
**版本**: 1.0.0
