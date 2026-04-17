# 监控系统增强报告

## 📊 监控数据来源确认

### ✅ 所有监控数据都是真实的

监控系统从以下数据库表获取真实数据：

1. **CrawlLog** - 爬虫运行日志
2. **Source** - 数据源状态
3. **User** - 用户数据
4. **Article** - 文章数据
5. **Subscription** - 订阅数据
6. **Order** - 订单数据
7. **DailyBrief** - AI简报数据

**没有任何模拟数据或假数据！**

---

## 🎯 新增业务指标监控

### 1. 用户指标 (User Metrics)

#### 监控项目：
- **总用户数**: 系统注册用户总数
- **新增用户**: 统计周期内新注册用户
- **活跃用户**: 统计周期内有登录行为的用户
- **活跃率**: 活跃用户 / 总用户数 × 100%

#### 数据来源：
```python
# 总用户数
total_users = User.query.count()

# 新增用户
new_users = User.query.filter(User.created_at >= start_date).count()

# 活跃用户
active_users = User.query.filter(User.last_login_at >= start_date).count()

# 活跃率
active_rate = (active_users / total_users * 100) if total_users > 0 else 0
```

#### 业务价值：
- 了解用户增长趋势
- 评估用户活跃度
- 发现用户流失问题

---

### 2. 文章指标 (Article Metrics)

#### 监控项目：
- **文章总数**: 数据库中所有文章数量
- **新增文章**: 统计周期内新增文章
- **已审核文章**: 统计周期内审核通过的文章
- **待审核文章**: 当前待审核的文章数
- **审核率**: 已审核 / 新增文章 × 100%

#### 数据来源：
```python
# 文章总数
total_articles_db = Article.query.count()

# 新增文章
new_articles = Article.query.filter(Article.created_at >= start_date).count()

# 已审核文章
reviewed_articles = Article.query.filter(
    Article.created_at >= start_date,
    Article.is_reviewed == True
).count()

# 待审核文章
pending_articles = Article.query.filter(Article.is_reviewed == False).count()

# 审核率
review_rate = (reviewed_articles / new_articles * 100) if new_articles > 0 else 0
```

#### 业务价值：
- 监控内容生产效率
- 评估审核工作量
- 发现内容积压问题

---

### 3. 订阅指标 (Subscription Metrics)

#### 监控项目：
- **活跃订阅**: 当前有效的订阅数
- **新增订阅**: 统计周期内新增订阅
- **即将到期**: 7天内即将到期的订阅

#### 数据来源：
```python
# 活跃订阅
active_subscriptions = Subscription.query.filter_by(status='active').count()

# 新增订阅
new_subscriptions = Subscription.query.filter(
    Subscription.start_date >= start_date
).count()

# 即将到期
expiring_soon = Subscription.query.filter(
    Subscription.status == 'active',
    Subscription.end_date <= datetime.utcnow() + timedelta(days=7),
    Subscription.end_date > datetime.utcnow()
).count()
```

#### 业务价值：
- 监控订阅增长
- 提前预警到期订阅
- 评估续费转化率

---

### 4. 订单指标 (Order Metrics)

#### 监控项目：
- **订单总数**: 所有订单数量
- **待处理订单**: 待确认支付的订单
- **已支付订单**: 统计周期内已支付订单
- **总收入**: 统计周期内的总收入金额

#### 数据来源：
```python
# 订单总数
total_orders = Order.query.count()

# 待处理订单
pending_orders = Order.query.filter_by(payment_status='pending').count()

# 已支付订单
paid_orders = Order.query.filter(
    Order.payment_status == 'paid',
    Order.payment_time >= start_date
).count()

# 总收入
total_revenue = db.session.query(
    func.sum(Order.amount)
).filter(
    Order.payment_status == 'paid',
    Order.payment_time >= start_date
).scalar() or 0
```

#### 业务价值：
- 监控收入趋势
- 发现待处理订单
- 评估支付转化率

---

### 5. AI简报指标 (Brief Metrics)

#### 监控项目：
- **简报总数**: 生成的AI简报总数
- **最近生成**: 统计周期内生成的简报数

#### 数据来源：
```python
# 简报总数
total_briefs = DailyBrief.query.count()

# 最近生成
recent_briefs = DailyBrief.query.filter(
    DailyBrief.generated_at >= start_date
).count()
```

#### 业务价值：
- 监控AI服务运行状态
- 评估简报生成频率

---

## 🏗️ 监控架构

### 数据流向

```
┌─────────────────┐
│  业务系统        │
│  - 用户注册      │
│  - 文章发布      │
│  - 订单支付      │
│  - 爬虫运行      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  数据库表        │
│  - users         │
│  - articles      │
│  - orders        │
│  - crawl_logs    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MonitorService  │
│  - 数据聚合      │
│  - 指标计算      │
│  - 告警检查      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Monitor API     │
│  - /statistics   │
│  - /health       │
│  - /failures     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  前端监控页面    │
│  - 实时刷新      │
│  - 可视化展示    │
│  - 告警通知      │
└─────────────────┘
```

---

## 📡 API接口

### GET /api/monitor/statistics

**功能**: 获取监控统计数据

**参数**:
- `days`: 统计天数（1-90，默认7）

**返回**:
```json
{
  "period_days": 7,
  "total_runs": 150,
  "success_runs": 145,
  "failed_runs": 5,
  "success_rate": 96.67,
  "total_articles": 1234,
  "spiders": [...],
  "business_metrics": {
    "users": {
      "total": 500,
      "new": 50,
      "active": 200,
      "active_rate": 40.0
    },
    "articles": {
      "total": 5000,
      "new": 500,
      "reviewed": 480,
      "pending": 20,
      "review_rate": 96.0
    },
    "subscriptions": {
      "active": 100,
      "new": 10,
      "expiring_soon": 5
    },
    "orders": {
      "total": 150,
      "pending": 5,
      "paid": 10,
      "revenue": 15000.00
    },
    "briefs": {
      "total": 30,
      "recent": 7
    },
    "categories": [...]
  }
}
```

### GET /api/monitor/health

**功能**: 检查系统健康状态

**返回**:
```json
{
  "is_healthy": true,
  "db_healthy": true,
  "recent_runs": 5,
  "error_sources": 0,
  "checked_at": "2026-04-17T12:00:00"
}
```

### GET /api/monitor/failures

**功能**: 获取最近失败记录

**参数**:
- `limit`: 返回数量（1-100，默认10）

**返回**:
```json
{
  "failures": [
    {
      "spider_name": "新华网",
      "error_msg": "连接超时",
      "failed_at": "2026-04-17T11:30:00"
    }
  ],
  "total": 1
}
```

### POST /api/monitor/test-alert

**功能**: 测试告警功能

**返回**:
```json
{
  "message": "测试告警已发送，请检查企业微信和邮箱"
}
```

---

## 🎨 前端展示

### 监控页面布局

```
┌─────────────────────────────────────────────────────┐
│ 监控告警                    [时间范围] [刷新] [测试]  │
├─────────────────────────────────────────────────────┤
│ 系统健康状态                                         │
│ [✓ 健康] [✓ 数据库] [5 次运行] [0 个错误]          │
├─────────────────────────────────────────────────────┤
│ 爬虫统计                                            │
│ [150 总运行] [145 成功] [5 失败] [96.67% 成功率]   │
├─────────────────────────────────────────────────────┤
│ 用户指标                                            │
│ [500 总用户] [50 新增] [200 活跃] [40% 活跃率]     │
├─────────────────────────────────────────────────────┤
│ 文章指标                                            │
│ [5000 总数] [500 新增] [480 已审核] [20 待审核]    │
├─────────────────────────────────────────────────────┤
│ 订阅指标              │ 订单指标                     │
│ [100 活跃]            │ [150 总数]                  │
│ [10 新增]             │ [5 待处理]                  │
│ [5 即将到期]          │ [10 已支付]                 │
│                       │ [¥15000 收入]               │
├─────────────────────────────────────────────────────┤
│ AI简报指标                                          │
│ [30 总数] [7 最近生成]                              │
├─────────────────────────────────────────────────────┤
│ 爬虫运行统计表格                                     │
├─────────────────────────────────────────────────────┤
│ 最近失败记录                                         │
└─────────────────────────────────────────────────────┘
```

---

## 🔔 告警机制

### 自动告警触发条件

1. **爬虫连续失败3次**
   - 自动发送告警
   - 通知所有管理员

2. **系统健康检查异常**
   - 数据库连接失败
   - 爬虫长时间未运行

### 告警渠道

1. **企业微信**
   - 实时推送
   - 发送给所有管理员

2. **邮件**
   - 配置SMTP服务器
   - 发送到指定邮箱列表

### 告警内容

```
【爬虫告警】

爬虫名称: 新华网
告警时间: 2026-04-17 12:00:00
告警原因: 连续失败 3 次

错误信息:
连接超时

请及时处理！
```

---

## 📈 监控指标说明

### 关键指标 (KPI)

1. **爬虫成功率**: >= 95% 为健康
2. **用户活跃率**: >= 30% 为良好
3. **文章审核率**: >= 90% 为及时
4. **订单支付率**: 监控转化效率

### 预警阈值

| 指标 | 正常 | 警告 | 严重 |
|------|------|------|------|
| 爬虫成功率 | >= 95% | 80-95% | < 80% |
| 用户活跃率 | >= 30% | 15-30% | < 15% |
| 待审核文章 | < 50 | 50-100 | > 100 |
| 待处理订单 | < 10 | 10-20 | > 20 |
| 即将到期订阅 | < 10 | 10-20 | > 20 |

---

## 🔧 配置说明

### 环境变量配置

```bash
# 邮件告警配置
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=alert@example.com
SMTP_PASSWORD=your_password
ALERT_EMAILS=admin1@example.com,admin2@example.com

# 企业微信配置（在用户IM应用配置中设置）
```

### 监控服务配置

```python
# backend/app/services/monitor_service.py

class MonitorService:
    def __init__(self):
        self.alert_threshold = 3  # 连续失败次数阈值
        self.check_interval = timedelta(hours=1)  # 检查间隔
```

---

## 🚀 使用指南

### 查看监控数据

1. 访问 `/admin/monitor` 页面
2. 选择统计时间范围（1天/7天/30天/90天）
3. 点击"刷新"按钮更新数据
4. 页面每分钟自动刷新一次

### 测试告警功能

1. 点击"测试告警"按钮
2. 确认发送测试告警
3. 检查企业微信和邮箱是否收到告警

### 处理告警

1. 查看"最近失败记录"
2. 点击爬虫名称查看详情
3. 根据错误信息排查问题
4. 修复后重新运行爬虫

---

## 📊 数据统计周期

- **实时数据**: 系统健康状态、待处理订单
- **小时级**: 爬虫运行次数
- **天级**: 新增用户、新增文章、新增订阅
- **周期级**: 根据选择的天数统计（1/7/30/90天）

---

## 🎯 未来改进建议

### 1. 更多业务指标

- [ ] 用户留存率
- [ ] 订阅续费率
- [ ] 文章阅读量
- [ ] 推送送达率
- [ ] API调用统计

### 2. 可视化增强

- [ ] 趋势图表（折线图、柱状图）
- [ ] 实时数据流
- [ ] 告警历史记录
- [ ] 性能监控图表

### 3. 告警优化

- [ ] 告警级别（信息/警告/严重）
- [ ] 告警静默期
- [ ] 告警聚合
- [ ] 告警确认机制

### 4. 性能监控

- [ ] API响应时间
- [ ] 数据库查询性能
- [ ] 爬虫运行时长
- [ ] 内存和CPU使用率

### 5. 日志分析

- [ ] 错误日志聚合
- [ ] 访问日志分析
- [ ] 用户行为分析
- [ ] 异常检测

---

## ✅ 总结

### 监控数据来源

✅ **100% 真实数据**
- 所有数据来自数据库查询
- 没有任何模拟或假数据
- 实时反映系统运行状态

### 监控覆盖范围

✅ **全面覆盖**
- 爬虫运行监控
- 用户行为监控
- 内容生产监控
- 订阅订单监控
- AI服务监控

### 告警机制

✅ **自动化告警**
- 自动检测异常
- 多渠道通知
- 及时响应问题

---

**最后更新**: 2026-04-17  
**版本**: v2.0  
**状态**: ✅ 已完成并测试
