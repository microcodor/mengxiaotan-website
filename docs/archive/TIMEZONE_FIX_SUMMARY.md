# 时区修复总结

## ✅ 问题已解决

**问题**: 系统时间与本地时间相差 8 小时（UTC vs CST）

**解决方案**: 
1. 修改 `docker-compose.yml`，设置 MySQL 和 Redis 容器时区为 Asia/Shanghai (+08:00)
2. 重启 MySQL 容器

## 验证结果

### MySQL 时区配置 ✅
```
NOW(): 2026-04-12 16:27:38
@@global.time_zone: +08:00
@@session.time_zone: +08:00
```

### 新数据测试 ✅
```
插入时间: 2026-04-12 16:27:56 (中国标准时间)
```

## 影响

- ✅ **新数据**: 使用正确的中国标准时间
- ⚠️ **历史数据**: 108 篇文章的时间戳仍然是 UTC 时间（比实际时间早 8 小时）

## 可选操作

如果需要修复历史数据，可以执行：
```sql
UPDATE articles 
SET created_at = DATE_ADD(created_at, INTERVAL 8 HOUR),
    updated_at = DATE_ADD(updated_at, INTERVAL 8 HOUR),
    published_at = DATE_ADD(published_at, INTERVAL 8 HOUR)
WHERE created_at < '2026-04-12 16:00:00';
```

**建议**: 先备份数据再执行

## 文档

详细信息请查看 `TIMEZONE_FIX.md`
