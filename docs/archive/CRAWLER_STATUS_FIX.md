# 爬虫状态问题修复说明

## 问题描述
用户尝试停止 **ccer**（全国温室气体自愿减排交易系统）爬虫时，提示"未在运行"，但实际上无法启动新的爬虫任务。

## 问题原因

### 状态不一致
系统使用两个地方存储爬虫运行状态：

1. **数据库 `sources` 表**：存储持久化状态
   - ccer 状态：`running` ❌
   
2. **Redis**：存储临时运行信息（PID、日志文件等）
   - ccer PID：不存在 ❌

3. **实际进程**：
   - ccer 进程：不存在 ❌

### 为什么会出现这种情况？

当爬虫进程**意外终止**时（如系统重启、进程崩溃、手动 kill 等），可能导致：
- Redis 中的 PID 记录丢失（Redis 重启或过期）
- 数据库状态没有更新（仍然是 `running`）
- 实际进程已经不存在

### 停止接口的逻辑
```python
def post(self, spider_name):
    # 从Redis获取PID
    pid = redis_client.get(f'crawler:{spider_name}:pid')
    
    if not pid:
        return {'message': f'爬虫 {spider_name} 未在运行'}  # ← 这里返回了
```

因为 Redis 中没有 PID，所以返回"未在运行"，但数据库状态仍然是 `running`。

## 已完成的修复

### 1. 手动修复数据库状态
```sql
UPDATE sources 
SET status='active' 
WHERE name='全国温室气体自愿减排交易系统';
```

✅ **修复完成**，现在可以正常启动 ccer 爬虫了。

### 2. 创建自动修复脚本
创建了 `fix_crawler_status.py` 脚本，可以自动检测和修复所有状态不一致的爬虫。

## 使用方法

### 方法1：手动修复（已完成）
状态已经修复，现在可以：
1. 在管理后台找到"全国温室气体自愿减排交易系统"
2. 点击"启动"按钮
3. 爬虫应该能正常启动

### 方法2：使用修复脚本（预防未来问题）
```bash
# 安装依赖
pip install pymysql redis

# 运行修复脚本
python3 fix_crawler_status.py
```

脚本会：
- 检查所有状态为 `running` 的数据源
- 验证 Redis 中是否有对应的 PID
- 验证进程是否真的在运行
- 自动修复状态不一致的记录

### 方法3：直接 SQL 修复
```bash
# 修复所有状态不一致的爬虫
docker exec energy_mysql mysql -u root -ppassword energy_station \
  --default-character-set=utf8mb4 \
  -e "UPDATE sources SET status='active' WHERE status='running';"
```

## 预防措施

### 1. 改进停止接口逻辑
建议修改 `backend/app/api/crawler.py` 中的 `SpiderStop` 方法：

```python
def post(self, spider_name):
    """停止爬虫"""
    admin_required()
    
    from app import redis_client
    
    try:
        # 从Redis获取PID
        pid = redis_client.get(f'crawler:{spider_name}:pid')
        log_id = redis_client.get(f'crawler:{spider_name}:log_id')
        
        # 即使 Redis 中没有 PID，也尝试清理数据库状态
        source_names = {...}
        source = Source.query.filter_by(name=source_names.get(spider_name)).first()
        
        if not pid:
            # 清理数据库状态
            if source and source.status == 'running':
                source.status = 'active'
                db.session.commit()
                return {'message': f'爬虫 {spider_name} 状态已重置'}
            return {'message': f'爬虫 {spider_name} 未在运行'}
        
        # ... 原有的停止逻辑
```

### 2. 添加健康检查定时任务
在 `backend/app/scheduler.py` 中添加：

```python
@scheduler.task('cron', id='check_crawler_status', hour='*/1')
def check_crawler_status():
    """每小时检查爬虫状态一致性"""
    from app import redis_client
    from app.models import Source
    
    sources = Source.query.filter_by(status='running').all()
    
    for source in sources:
        spider_name = get_spider_name(source.name)
        if not spider_name:
            continue
        
        pid = redis_client.get(f'crawler:{spider_name}:pid')
        
        if not pid:
            # Redis 中没有 PID，重置状态
            source.status = 'active'
            db.session.commit()
            logger.warning(f'重置爬虫状态: {source.name}')
```

### 3. 优雅关闭处理
在爬虫启动时，添加信号处理：

```python
import signal
import atexit

def cleanup_on_exit(spider_name, log_id):
    """进程退出时清理状态"""
    from app import redis_client, db
    from app.models import Source, CrawlLog
    
    # 清理 Redis
    redis_client.delete(f'crawler:{spider_name}:pid')
    redis_client.delete(f'crawler:{spider_name}:log_id')
    
    # 更新数据库
    source = Source.query.filter_by(name=spider_name).first()
    if source:
        source.status = 'active'
        db.session.commit()
    
    log = CrawlLog.query.get(log_id)
    if log and log.status == 'running':
        log.status = 'failed'
        log.error_msg = '进程意外终止'
        log.finished_at = datetime.now()
        db.session.commit()

# 注册清理函数
atexit.register(cleanup_on_exit, spider_name, log_id)
signal.signal(signal.SIGTERM, lambda s, f: cleanup_on_exit(spider_name, log_id))
```

## 相关问题排查

### 如何检查爬虫真实状态？

```bash
# 1. 检查数据库状态
docker exec energy_mysql mysql -u root -ppassword energy_station \
  --default-character-set=utf8mb4 \
  -e "SELECT id, name, status FROM sources WHERE status='running';"

# 2. 检查 Redis PID
docker exec energy_redis redis-cli KEYS "crawler:*:pid"
docker exec energy_redis redis-cli GET "crawler:ccer:pid"

# 3. 检查实际进程
ps aux | grep "scrapy.*ccer" | grep -v grep
```

### 如何清理所有残留状态？

```bash
# 清理数据库
docker exec energy_mysql mysql -u root -ppassword energy_station \
  --default-character-set=utf8mb4 \
  -e "UPDATE sources SET status='active' WHERE status='running';"

# 清理 Redis
docker exec energy_redis redis-cli --scan --pattern "crawler:*" | xargs docker exec energy_redis redis-cli DEL
```

## 总结

### 问题
- ccer 爬虫数据库状态为 `running`
- Redis 中没有 PID 记录
- 实际进程不存在
- 停止接口返回"未在运行"

### 解决方案
✅ 已修复数据库状态为 `active`
✅ 创建了自动修复脚本
✅ 提供了预防措施建议

### 现在可以做什么
1. 在管理后台启动 ccer 爬虫
2. 爬虫应该能正常运行
3. 如果再次遇到类似问题，运行 `fix_crawler_status.py`

---
**修复时间**: 2026-04-12 17:30
**修复人**: AI Assistant
**状态**: ✅ 已修复
