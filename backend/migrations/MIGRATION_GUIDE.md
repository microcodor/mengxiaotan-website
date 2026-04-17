# 订阅系统完善 - 迁移快速指南

## 快速开始

### 1. 备份数据库（重要！）

```bash
mysqldump -u root -p energy_station > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. 执行迁移

**推荐方式 - 使用 Python 脚本:**

```bash
cd backend
python migrations/run_subscription_enhancement_migration.py
```

**备选方式 - 使用 SQL 脚本:**

```bash
mysql -u root -p energy_station < backend/migrations/add_subscription_enhancement_fields.sql
```

### 3. 验证迁移

```bash
# 进入 MySQL
mysql -u root -p energy_station

# 检查 orders 表
DESCRIBE orders;

# 检查 refund_applications 表
DESCRIBE refund_applications;

# 退出
exit
```

## 迁移内容摘要

### Order 表新增字段 (6个)
- ✅ `payment_info` - OCR支付信息 (JSON)
- ✅ `refund_reason` - 退款原因 (TEXT)
- ✅ `refund_status` - 退款状态 (VARCHAR)
- ✅ `refund_applied_at` - 申请时间 (DATETIME)
- ✅ `refund_processed_at` - 处理时间 (DATETIME)
- ✅ `refund_processed_by` - 处理人ID (INT)

### RefundApplication 表 (新建)
- ✅ 完整的退款申请管理表
- ✅ 包含所有必需字段和索引
- ✅ 外键关联到 orders 和 users 表

## 回滚迁移

如果需要回滚：

```bash
cd backend
python migrations/run_subscription_enhancement_migration.py --rollback
```

## 常见问题

**Q: 迁移失败怎么办？**
A: 查看错误日志，使用 `--rollback` 回滚，修复问题后重新执行

**Q: 可以重复执行迁移吗？**
A: 可以，Python 脚本会跳过已存在的字段和表

**Q: 需要停止应用服务吗？**
A: 建议在低峰期执行，短暂停止服务以避免数据不一致

## 相关文档

- 详细文档: `README_subscription_enhancement.md`
- 设计文档: `.kiro/specs/subscription-enhancement/design.md`
- 需求文档: `.kiro/specs/subscription-enhancement/requirements.md`
