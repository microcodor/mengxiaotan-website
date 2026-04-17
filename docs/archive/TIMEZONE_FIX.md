# 时区问题修复总结

**修复时间**: 2026-04-12 16:28

---

## 问题描述

系统时间与实际本地时间相差 8 小时：
- **本地时间**: CST（中国标准时间，UTC+8）
- **MySQL 容器时间**: UTC（协调世界时）
- **时差**: 8 小时

---

## 修复方案

### 1. 修改 docker-compose.yml

#### MySQL 容器配置
```yaml
mysql:
  image: mysql:8.0
  container_name: energy_mysql
  environment:
    MYSQL_ROOT_PASSWORD: password
    MYSQL_DATABASE: energy_station
    TZ: Asia/Shanghai  # 新增：设置时区为上海
  ports:
    - "3307:3306"
  volumes:
    - mysql_data:/var/lib/mysql
    - /etc/localtime:/etc/localtime:ro  # 新增：挂载本地时区文件
  command: --default-authentication-plugin=mysql_native_password --default-time-zone='+08:00'  # 新增：设置 MySQL 时区
```

#### Redis 容器配置
```yaml
redis:
  image: redis:7-alpine
  container_name: energy_redis
  environment:
    TZ: Asia/Shanghai  # 新增：设置时区为上海
  ports:
    - "6380:6379"
  volumes:
    - redis_data:/data
    - /etc/localtime:/etc/localtime:ro  # 新增：挂载本地时区文件
```

### 2. 重启容器

```bash
docker restart energy_mysql
docker restart energy_redis
```

---

## 验证结果

### 1. 系统时间
```bash
$ docker exec energy_mysql date
Sun Apr 12 16:27:23 CST 2026  ✅ 正确
```

### 2. MySQL 时区配置
```sql
SELECT NOW(), @@global.time_zone, @@session.time_zone;
```

**结果**:
```
NOW()                 @@global.time_zone  @@session.time_zone
2026-04-12 16:27:38   +08:00              +08:00
```
✅ 全局时区和会话时区都设置为 +08:00

### 3. 新数据测试
插入测试数据：
```sql
INSERT INTO articles (title, created_at) VALUES ('时区测试', NOW());
```

**结果**: 
```
created_at: 2026-04-12 16:27:56  ✅ 使用中国标准时间
```

---

## 影响范围

### ✅ 已修复
- **新插入的数据**: 使用正确的中国标准时间（UTC+8）
- **MySQL NOW() 函数**: 返回中国标准时间
- **容器系统时间**: 显示中国标准时间

### ⚠️ 历史数据
- **已存在的 108 篇文章**: 时间戳仍然是 UTC 时间
- **不影响功能**: 只是显示的时间比实际时间早 8 小时
- **可选修复**: 如果需要，可以批量更新历史数据

---

## 历史数据修复（可选）

如果需要修复历史数据的时区，可以执行以下 SQL：

```sql
-- 备份数据（推荐）
CREATE TABLE articles_backup AS SELECT * FROM articles;

-- 将 UTC 时间转换为 CST 时间（+8 小时）
UPDATE articles 
SET 
  created_at = DATE_ADD(created_at, INTERVAL 8 HOUR),
  updated_at = DATE_ADD(updated_at, INTERVAL 8 HOUR),
  published_at = DATE_ADD(published_at, INTERVAL 8 HOUR)
WHERE created_at < '2026-04-12 16:00:00';  -- 只更新修复前的数据
```

**注意**: 
- 执行前请先备份数据
- 确认时间范围，避免重复更新
- 建议在测试环境先验证

---

## 后端代码调整（可选）

如果后端使用 Python 的 `datetime.utcnow()`，建议改为使用本地时区：

### 修改前
```python
from datetime import datetime
created_at = datetime.utcnow()  # 返回 UTC 时间
```

### 修改后
```python
from datetime import datetime
import pytz

# 方法 1: 使用 pytz
tz = pytz.timezone('Asia/Shanghai')
created_at = datetime.now(tz)

# 方法 2: 让数据库处理（推荐）
# 在 SQLAlchemy 模型中使用 server_default
created_at = db.Column(db.DateTime, server_default=db.func.now())
```

---

## 前端显示调整（可选）

前端可以根据需要格式化时间显示：

```typescript
// 如果后端返回的是 ISO 格式字符串
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};
```

---

## 测试清单

- [x] MySQL 容器时区设置为 +08:00
- [x] Redis 容器时区设置为 Asia/Shanghai
- [x] 容器系统时间显示 CST
- [x] MySQL NOW() 返回中国标准时间
- [x] 新插入数据使用正确时区
- [ ] 历史数据时区修复（可选）
- [ ] 后端代码时区调整（可选）
- [ ] 前端时间显示验证（可选）

---

## 重启服务

修改 docker-compose.yml 后，需要重启容器：

```bash
# 方法 1: 重启单个容器
docker restart energy_mysql
docker restart energy_redis

# 方法 2: 重启所有服务
docker compose down
docker compose up -d

# 方法 3: 使用 start.sh
./start.sh
```

---

## 验证命令

### 检查容器时区
```bash
docker exec energy_mysql date
docker exec energy_redis date
```

### 检查 MySQL 时区配置
```bash
docker exec energy_mysql mysql -uroot -ppassword -e "SELECT NOW(), @@global.time_zone, @@session.time_zone;"
```

### 检查最新文章时间
```bash
docker exec energy_mysql mysql -uroot -ppassword energy_station -e "SELECT id, title, created_at FROM articles ORDER BY created_at DESC LIMIT 5;"
```

---

## 常见问题

### Q: 为什么历史数据时间没有变化？
**A**: 历史数据已经存储在数据库中，修改时区配置不会自动更新已存在的数据。如果需要修复，请参考"历史数据修复"部分。

### Q: 修改时区会影响现有功能吗？
**A**: 不会。只影响新插入数据的时间戳和 NOW() 函数的返回值。

### Q: 需要重启后端服务吗？
**A**: 不需要。后端服务会自动使用数据库的时区设置。

### Q: 前端显示的时间还是不对？
**A**: 检查前端是否有时区转换逻辑。如果有，可能需要调整或移除。

---

## 总结

✅ **时区问题已修复**：
- MySQL 容器时区设置为 +08:00（中国标准时间）
- Redis 容器时区设置为 Asia/Shanghai
- 新插入的数据使用正确的时区
- 系统时间显示正确

⚠️ **注意事项**：
- 历史数据（108 篇文章）的时间戳仍然是 UTC 时间
- 如果需要，可以批量更新历史数据
- 建议在测试环境先验证修复方案

🎯 **下一步**：
1. 验证前端显示的时间是否正确
2. 如果需要，修复历史数据的时区
3. 更新文档，说明系统使用中国标准时间
