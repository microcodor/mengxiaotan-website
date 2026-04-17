# 爬虫数据库连接问题修复报告

**问题时间**: 2026-04-13  
**修复时间**: 2026-04-13 16:07  
**状态**: ✅ 已修复

---

## 🐛 问题描述

### 错误信息
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'localhost' ([Errno 61] Connection refused)")
```

### 问题场景
- **后端API**: 正常工作 ✅
- **前端页面**: 正常访问 ✅
- **爬虫启动**: 数据库连接失败 ❌

### 问题原因
爬虫使用独立的Scrapy进程，有自己的数据库配置文件。配置文件中的数据库连接信息不正确：

**错误配置** (`crawler/energy_crawler/settings.py`):
```python
DATABASE_URL = 'mysql+pymysql://root:password@localhost:3307/energy_station'
```

**问题点**:
1. ❌ 密码错误: `password` → 应该是 `jinchun123`
2. ❌ 端口错误: `3307` → 应该是 `3306`

---

## 🔧 修复方案

### 修改文件
`crawler/energy_crawler/settings.py`

### 修改内容
```python
# 修复前
DATABASE_URL = 'mysql+pymysql://root:password@localhost:3307/energy_station'

# 修复后
DATABASE_URL = 'mysql+pymysql://root:jinchun123@localhost:3306/energy_station'
```

---

## ✅ 验证结果

### 1. 爬虫启动测试
```bash
curl -X POST http://localhost:5001/api/crawler/spiders/test/run \
  -H "Authorization: Bearer $TOKEN"
```

**响应**:
```json
{
  "message": "爬虫 test 已启动",
  "pid": 28956,
  "log_id": 43,
  "log_file": "/Users/.../logs/crawler/test_43.log"
}
```

✅ **启动成功**

---

### 2. 爬虫运行日志
```
2026-04-14 00:07:33 [scrapy.core.engine] INFO: Spider opened
2026-04-14 00:07:33 [scrapy.core.engine] INFO: Closing spider (finished)
2026-04-14 00:07:33 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{
  'item_scraped_count': 3,
  'finish_reason': 'finished',
  ...
}
```

✅ **运行正常，无数据库错误**

---

### 3. 数据保存验证
查询文章列表API，确认爬虫数据已保存到数据库：

```bash
curl http://localhost:5001/api/articles/ -H "Authorization: Bearer $TOKEN"
```

✅ **数据保存成功**

---

## 📊 测试统计

### 爬虫运行统计
- 启动时间: 2026-04-14 00:07:27
- 完成时间: 2026-04-14 00:07:33
- 运行时长: 6秒
- 抓取文章: 3篇
- 数据库连接: 正常 ✅
- 数据保存: 成功 ✅

### 性能指标
- 请求数: 3
- 响应数: 3
- 成功率: 100%
- 抓取速度: 36 items/min
- 内存使用: 80.6 MB

---

## 🔍 根本原因分析

### 为什么后端正常，爬虫失败？

1. **独立进程**
   - 后端: Flask应用，使用 `backend/.env` 和 `backend/config.py`
   - 爬虫: Scrapy进程，使用 `crawler/energy_crawler/settings.py`

2. **配置分离**
   - 后端配置: ✅ 正确（已在环境切换时更新）
   - 爬虫配置: ❌ 错误（仍然是Docker环境的配置）

3. **配置来源**
   - 后端: 从 `.env` 文件读取，支持环境变量覆盖
   - 爬虫: 硬编码在 `settings.py` 中，需要手动修改

---

## 💡 改进建议

### 1. 统一配置管理
建议让爬虫也从环境变量读取配置：

```python
# crawler/energy_crawler/settings.py
import os
from dotenv import load_dotenv

# 加载后端的 .env 文件
load_dotenv('../backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:jinchun123@localhost:3306/energy_station')
```

### 2. 配置验证
在爬虫启动前验证数据库连接：

```python
def validate_database_connection():
    try:
        conn = pymysql.connect(...)
        conn.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False
```

### 3. 文档更新
在环境切换文档中明确说明需要修改爬虫配置。

---

## 📝 相关文件

### 修改的文件
- `crawler/energy_crawler/settings.py` - 爬虫配置文件

### 相关配置文件
- `backend/.env` - 后端环境变量
- `backend/config.py` - 后端配置
- `crawler/energy_crawler/pipelines.py` - 数据库管道（使用settings.py的配置）

---

## ✅ 修复确认

### 修复前
- ❌ 爬虫启动失败
- ❌ 数据库连接被拒绝
- ❌ 无法保存爬取的数据

### 修复后
- ✅ 爬虫启动成功
- ✅ 数据库连接正常
- ✅ 数据保存成功
- ✅ 日志无错误

---

## 🎯 后续操作

### 已完成
- [x] 修复爬虫数据库配置
- [x] 测试爬虫启动
- [x] 验证数据保存
- [x] 检查运行日志

### 建议测试
- [ ] 测试其他爬虫（如 xinhua_real, chinapower 等）
- [ ] 测试批量启动爬虫
- [ ] 测试长时间运行的爬虫
- [ ] 测试爬虫停止功能

---

## 📚 参考文档

- [本地环境配置指南](LOCAL_SETUP.md)
- [爬虫功能说明](CRAWLER_UI_ENHANCEMENT.md)
- [快速启动指南](QUICK_START_LOCAL.md)

---

**修复完成时间**: 2026-04-13 16:07:33  
**测试状态**: ✅ 全部通过  
**问题状态**: 🟢 已解决
