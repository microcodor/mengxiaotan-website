# 监控告警系统使用指南

## 功能概述

监控告警系统实时监控爬虫运行状态，当出现异常时自动发送告警通知，帮助管理员及时发现和处理问题。

## 功能特点

✅ **自动监控**：实时监控爬虫运行状态  
✅ **智能告警**：连续失败3次自动触发告警  
✅ **多渠道通知**：支持企业微信、邮件告警  
✅ **运行统计**：详细的运行数据统计和分析  
✅ **健康检查**：系统健康状态实时监控  
✅ **失败追踪**：记录和展示最近的失败记录  

## 告警机制

### 触发条件

当满足以下条件时，系统会自动发送告警：

1. **连续失败**：同一爬虫连续失败 3 次
2. **运行超时**：爬虫运行超过 10 分钟
3. **异常错误**：爬虫运行过程中发生异常

### 告警渠道

1. **企业微信**
   - 实时推送到企业微信
   - 支持 @all 通知所有人
   - 需要配置企业微信参数

2. **邮件**
   - 发送到指定邮箱
   - 支持多个收件人
   - 需要配置 SMTP 服务器

## 配置方法

### 1. 企业微信配置

在 `.env` 文件中配置：

```bash
# 企业微信配置
WECHAT_WORK_CORPID=your_corpid
WECHAT_WORK_CORPSECRET=your_corpsecret
WECHAT_WORK_AGENTID=your_agentid
```

### 2. 邮件配置

在 `.env` 文件中配置：

```bash
# SMTP 服务器配置
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password

# 告警接收邮箱（多个用逗号分隔）
ALERT_EMAILS=admin1@example.com,admin2@example.com
```

### 常用 SMTP 配置

**QQ 邮箱**
```bash
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_qq@qq.com
SMTP_PASSWORD=your_authorization_code  # 授权码，不是密码
```

**163 邮箱**
```bash
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SMTP_USER=your_email@163.com
SMTP_PASSWORD=your_authorization_code
```

**Gmail**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 使用方法

### 1. 访问监控页面

登录管理后台，访问"监控告警"菜单：

```
http://localhost:5173/admin/monitor
```

### 2. 查看系统健康状态

页面顶部显示4个健康指标：

- **总体状态**：系统整体健康状况
- **数据库**：数据库连接状态
- **最近1小时运行**：最近1小时的爬虫运行次数
- **错误爬虫**：当前处于错误状态的爬虫数量

### 3. 查看运行统计

统计卡片显示：

- **总运行次数**：统计周期内的总运行次数
- **成功次数**：成功运行的次数
- **失败次数**：失败运行的次数
- **成功率**：成功率百分比

可以选择统计周期：
- 最近1天
- 最近7天
- 最近30天
- 最近90天

### 4. 查看爬虫统计

表格展示每个爬虫的详细统计：

- 爬虫名称
- 总运行次数
- 成功次数
- 成功率（颜色标识：绿色≥80%，黄色≥50%，红色<50%）
- 抓取文章数

### 5. 查看失败记录

显示最近10条失败记录，包括：

- 爬虫名称
- 失败时间
- 错误信息

### 6. 测试告警

点击"测试告警"按钮，系统会发送一条测试告警消息，用于验证告警功能是否正常。

## API接口

### 获取统计信息

```http
GET /api/monitor/statistics?days=7
Authorization: Bearer <token>
```

**参数**：
- `days`: 统计天数（1-90）

**响应**：
```json
{
  "period_days": 7,
  "total_runs": 63,
  "success_runs": 60,
  "failed_runs": 3,
  "success_rate": 95.24,
  "total_articles": 1575,
  "spiders": [
    {
      "name": "xinhua_real",
      "total_runs": 21,
      "success_runs": 21,
      "success_rate": 100.0,
      "total_articles": 357
    }
  ]
}
```

### 获取失败记录

```http
GET /api/monitor/failures?limit=10
Authorization: Bearer <token>
```

**参数**：
- `limit`: 返回数量（1-100）

**响应**：
```json
{
  "failures": [
    {
      "spider_name": "test_spider",
      "error_msg": "Connection timeout",
      "failed_at": "2026-04-11T12:00:00"
    }
  ],
  "total": 1
}
```

### 获取健康状态

```http
GET /api/monitor/health
Authorization: Bearer <token>
```

**响应**：
```json
{
  "is_healthy": true,
  "db_healthy": true,
  "recent_runs": 3,
  "error_sources": 0,
  "checked_at": "2026-04-11T12:00:00"
}
```

### 测试告警

```http
POST /api/monitor/test-alert
Authorization: Bearer <token>
```

**响应**：
```json
{
  "message": "测试告警已发送，请检查企业微信和邮箱"
}
```

## 告警消息格式

### 企业微信消息

```
【爬虫告警】

爬虫名称: xinhua_real
告警时间: 2026-04-11 12:00:00
告警原因: 连续失败 3 次

错误信息:
Connection timeout

请及时处理！
```

### 邮件消息

**主题**：【爬虫告警】xinhua_real 运行失败

**正文**：同企业微信消息

## 监控数据

### 数据记录

系统会自动记录每次爬虫运行的结果：

- 爬虫名称
- 运行状态（success/failed）
- 抓取文章数
- 错误信息
- 开始时间
- 结束时间

### 数据存储

监控数据存储在以下表中：

- `crawl_logs`: 爬虫运行日志
- `sources`: 数据源状态

### 数据清理

建议定期清理历史数据：

```sql
-- 删除90天前的日志
DELETE FROM crawl_logs WHERE finished_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

## 性能优化

### 1. 告警频率控制

系统已实现智能告警：
- 连续失败3次才触发告警
- 避免频繁告警骚扰

### 2. 数据库优化

- 为 `finished_at` 字段添加索引
- 定期清理历史数据
- 使用分页查询

### 3. 告警发送优化

- 异步发送告警消息
- 失败重试机制
- 超时保护

## 常见问题

### Q1: 没有收到告警消息？

**A**: 检查以下几点：
1. 企业微信配置是否正确
2. 邮件配置是否正确
3. 查看后端日志是否有错误
4. 使用"测试告警"功能验证

### Q2: 如何修改告警阈值？

**A**: 编辑 `backend/app/services/monitor_service.py`：

```python
def __init__(self):
    self.alert_threshold = 3  # 修改为你想要的次数
```

### Q3: 如何添加更多告警渠道？

**A**: 在 `send_alert()` 方法中添加新的告警渠道代码。

### Q4: 统计数据不准确？

**A**: 
1. 检查爬虫是否正确记录运行结果
2. 查看数据库中的 `crawl_logs` 表
3. 确认时区设置正确

### Q5: 如何禁用告警？

**A**: 暂时没有禁用开关，可以：
1. 不配置企业微信和邮件
2. 或注释掉 `send_alert()` 方法中的发送代码

## 最佳实践

### 1. 告警配置

- 配置多个告警渠道（企业微信 + 邮件）
- 设置多个接收人
- 定期测试告警功能

### 2. 监控检查

- 每天查看监控页面
- 关注成功率变化
- 及时处理失败记录

### 3. 数据分析

- 定期分析运行统计
- 识别问题爬虫
- 优化爬虫策略

### 4. 系统维护

- 定期清理历史数据
- 优化数据库性能
- 更新告警规则

## 未来计划

### 高优先级
1. **告警规则配置**：支持自定义告警规则
2. **告警历史**：记录所有告警历史
3. **告警统计**：告警数量和频率统计

### 中优先级
4. **短信告警**：支持短信告警
5. **钉钉告警**：支持钉钉机器人
6. **Webhook**：支持自定义 Webhook

### 低优先级
7. **告警分级**：支持告警级别（警告、错误、严重）
8. **告警静默**：支持告警静默期
9. **告警聚合**：相同告警聚合发送

## 总结

监控告警系统提供了完整的爬虫运行监控和告警功能，帮助管理员及时发现和处理问题，确保系统稳定运行。

**关键特性**：
- ✅ 自动监控（实时）
- ✅ 智能告警（连续失败3次）
- ✅ 多渠道通知（企业微信、邮件）
- ✅ 运行统计（详细数据）
- ✅ 健康检查（系统状态）

**下一步**：
- 配置告警渠道
- 测试告警功能
- 定期查看监控数据

---

**最后更新**: 2026-04-12  
**版本**: 1.0.0
