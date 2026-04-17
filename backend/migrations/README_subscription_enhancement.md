# 订阅系统完善 - 数据库迁移文档

## 概述

本迁移脚本为订阅系统完善功能添加必要的数据库表和字段，包括：

1. **扩展 Order 表**: 添加支付信息和退款相关字段
2. **创建 RefundApplication 表**: 用于管理退款申请流程

## 迁移内容

### 1. Order 表扩展

新增字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `payment_info` | JSON | OCR提取的支付信息 |
| `refund_reason` | TEXT | 退款原因 |
| `refund_status` | VARCHAR(20) | 退款状态: null, pending, approved, rejected |
| `refund_applied_at` | DATETIME | 退款申请时间 |
| `refund_processed_at` | DATETIME | 退款处理时间 |
| `refund_processed_by` | INT | 退款处理人ID (外键到 users.id) |

新增索引：
- `idx_refund_status` - 退款状态索引
- `idx_refund_applied_at` - 退款申请时间索引

新增外键：
- `fk_orders_refund_processor` - 退款处理人外键

### 2. RefundApplication 表

新建表结构：

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| `order_id` | INT | NOT NULL, FOREIGN KEY | 订单ID |
| `user_id` | INT | NOT NULL, FOREIGN KEY | 申请用户ID |
| `reason` | TEXT | NOT NULL | 退款原因 |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | 状态: pending, approved, rejected |
| `applied_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 申请时间 |
| `processed_by` | INT | FOREIGN KEY | 处理人ID |
| `processed_at` | DATETIME | | 处理时间 |
| `reject_reason` | TEXT | | 拒绝原因 |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

索引：
- `idx_order_id` - 订单ID索引
- `idx_user_id` - 用户ID索引
- `idx_status` - 状态索引
- `idx_applied_at` - 申请时间索引

外键：
- `order_id` → `orders.id`
- `user_id` → `users.id`
- `processed_by` → `users.id`

## 使用方法

### 方法一: 使用 Python 脚本（推荐）

Python 脚本提供了更好的错误处理和日志输出。

#### 执行迁移

```bash
cd backend
python migrations/run_subscription_enhancement_migration.py
```

#### 回滚迁移

```bash
cd backend
python migrations/run_subscription_enhancement_migration.py --rollback
```

### 方法二: 使用 SQL 脚本

直接在 MySQL 客户端执行 SQL 脚本。

```bash
mysql -u your_username -p your_database < backend/migrations/add_subscription_enhancement_fields.sql
```

或在 MySQL 客户端中：

```sql
USE your_database;
SOURCE backend/migrations/add_subscription_enhancement_fields.sql;
```

## 验证迁移

迁移完成后，可以通过以下 SQL 语句验证：

### 检查 orders 表新字段

```sql
DESCRIBE orders;
```

应该能看到以下新字段：
- payment_info
- refund_reason
- refund_status
- refund_applied_at
- refund_processed_at
- refund_processed_by

### 检查 refund_applications 表

```sql
DESCRIBE refund_applications;
```

应该能看到完整的表结构。

### 检查索引

```sql
SHOW INDEX FROM orders WHERE Key_name LIKE 'idx_refund%';
SHOW INDEX FROM refund_applications;
```

## 注意事项

1. **备份数据库**: 在执行迁移前，请务必备份数据库
   ```bash
   mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **测试环境**: 建议先在测试环境执行迁移，验证无误后再在生产环境执行

3. **幂等性**: Python 迁移脚本支持重复执行，已存在的字段和表会被跳过

4. **回滚**: 如果迁移出现问题，可以使用 `--rollback` 参数回滚更改

5. **权限**: 确保数据库用户有 ALTER TABLE 和 CREATE TABLE 权限

## 相关文件

- `add_subscription_enhancement_fields.sql` - SQL 迁移脚本
- `run_subscription_enhancement_migration.py` - Python 迁移脚本
- `backend/app/models.py` - 更新后的 SQLAlchemy 模型定义

## 依赖的需求

本迁移支持以下需求：

- **需求 2.3**: 退款申请记录存储
- **需求 2.4**: 订单状态更新为 refund_pending
- **需求 2.7**: 退款批准后更新订单状态
- **需求 2.10**: 退款处理日志记录

## 故障排除

### 问题: 外键约束失败

**原因**: 可能存在孤立的数据（引用不存在的用户ID）

**解决方案**: 
```sql
-- 检查孤立数据
SELECT * FROM orders WHERE refund_processed_by IS NOT NULL 
AND refund_processed_by NOT IN (SELECT id FROM users);

-- 清理孤立数据
UPDATE orders SET refund_processed_by = NULL 
WHERE refund_processed_by NOT IN (SELECT id FROM users);
```

### 问题: 字段已存在错误

**原因**: 迁移已经部分执行过

**解决方案**: Python 脚本会自动跳过已存在的字段，或者手动删除已创建的字段后重新执行

### 问题: 权限不足

**原因**: 数据库用户没有足够的权限

**解决方案**: 
```sql
GRANT ALTER, CREATE, INDEX, REFERENCES ON database_name.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

## 联系支持

如有问题，请查看：
- 设计文档: `.kiro/specs/subscription-enhancement/design.md`
- 需求文档: `.kiro/specs/subscription-enhancement/requirements.md`
- 任务列表: `.kiro/specs/subscription-enhancement/tasks.md`
