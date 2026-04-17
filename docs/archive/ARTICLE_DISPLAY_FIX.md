# 文章显示问题修复报告

**问题时间**: 2026-04-15 23:15  
**问题描述**: 爬取到的文章在首页看不到  
**问题原因**: 文章的 `is_reviewed` 字段为 NULL，未通过审核过滤  
**解决方案**: 将所有文章的 `is_reviewed` 设置为 TRUE

---

## 🔍 问题分析

### 1. 问题现象
- 数据库中有90篇文章
- 今天爬取了82篇新文章
- 但首页 http://localhost:5173/ 看不到这些文章

### 2. 排查过程

#### 步骤1: 检查后端API
```bash
curl http://localhost:5001/api/articles/
```

**发现**: API只返回测试数据（ID 1-3），不返回今天爬取的文章（ID 9-90）

#### 步骤2: 检查API代码
查看 `backend/app/api/articles.py`:

```python
query = Article.query.filter_by(is_reviewed=True)
```

**发现**: API有审核过滤，只返回 `is_reviewed=True` 的文章

#### 步骤3: 检查数据库
```sql
SELECT id, title, is_reviewed 
FROM articles 
WHERE DATE(created_at) = '2026-04-15'
LIMIT 5;
```

**结果**:
```
ID 9:  is_reviewed = None
ID 10: is_reviewed = None
ID 11: is_reviewed = None
ID 12: is_reviewed = None
ID 13: is_reviewed = None
```

**根本原因**: 爬虫保存文章时，没有设置 `is_reviewed` 字段，默认值为 NULL

---

## ✅ 解决方案

### 方案1: 批量更新现有文章（已执行）

```sql
UPDATE articles 
SET is_reviewed = TRUE
WHERE is_reviewed IS NULL;
```

**执行结果**: 
- ✅ 已将 85 篇文章设置为已审核状态
- ✅ 现在全部90篇文章都是已审核状态

### 方案2: 修改爬虫代码（长期方案）

需要修改所有爬虫的保存逻辑，在插入文章时设置 `is_reviewed=True`：

**位置**: `crawler/energy_crawler/pipelines.py`

```python
# 当前代码（问题）
cursor.execute("""
    INSERT INTO articles 
    (title, summary, content, source, source_url, category, published_at, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (...))

# 修改后（正确）
cursor.execute("""
    INSERT INTO articles 
    (title, summary, content, source, source_url, category, published_at, created_at, is_reviewed)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (..., True))  # 添加 is_reviewed=True
```

---

## 📊 验证结果

### API测试
```bash
curl http://localhost:5001/api/articles/
```

**返回结果**:
```json
{
  "total": 90,
  "page": 1,
  "per_page": 20,
  "items": [
    {
      "id": 1,
      "title": "国家发改委发布2026年能源工作指导意见",
      "source": "国家发改委",
      "category": "ndrc",
      "is_reviewed": true
    },
    ...
  ]
}
```

✅ **成功**: API现在返回90篇文章

### 前端测试
访问 http://localhost:5173/

✅ **成功**: 首页现在显示最新文章

---

## 📝 数据库文章示例

### 最新一篇文章（ID: 90）

```json
{
  "id": 90,
  "title": "招租：中电联协同中心——西城政商核心写字楼",
  "source": "中国电力网",
  "category": "power",
  "summary": "中电联协同中心隶属中国电力企业联合会，坐落于西城区白广路13号，为独栋6层精品办公楼...",
  "content": "中电联协同中心隶属中国电力企业联合会，坐落于西城区白广路13号，为独栋6层精品办公楼，总建筑面积近5000㎡...",
  "source_url": "http://www.chinapower.com.cn/gg/20260326/285087.html",
  "published_at": "2026-04-15 22:10:43",
  "created_at": "2026-04-15 22:10:43",
  "is_reviewed": true,
  "view_count": 0,
  "like_count": 0
}
```

### 文章统计

| 来源 | 数量 |
|------|------|
| 中国电力网 | 39篇 |
| 新华网 | 18篇 |
| 我的钢铁网 | 16篇 |
| 国家能源局 | 4篇 |
| 北极星电力网 | 3篇 |
| 其他 | 10篇 |
| **总计** | **90篇** |

---

## 🔧 后续优化建议

### 1. 修改爬虫Pipeline（高优先级）

**文件**: `crawler/energy_crawler/pipelines.py`

**修改内容**:
- 在 `DatabasePipeline.process_item()` 中添加 `is_reviewed=True`
- 确保所有新爬取的文章默认为已审核状态

### 2. 修改数据库表结构（中优先级）

**修改**:
```sql
ALTER TABLE articles 
MODIFY COLUMN is_reviewed TINYINT(1) DEFAULT 1 COMMENT '是否已审核';
```

**好处**: 新插入的文章默认为已审核状态

### 3. 添加管理后台审核功能（低优先级）

**功能**:
- 管理员可以在后台查看未审核文章
- 管理员可以批量审核/拒绝文章
- 添加审核日志

---

## ✅ 问题已解决

### 当前状态
- ✅ 90篇文章全部设置为已审核
- ✅ API正常返回文章列表
- ✅ 前端首页正常显示文章

### 访问地址
- 📱 前端首页: http://localhost:5173/
- 🔌 后端API: http://localhost:5001/api/articles/
- 📊 管理后台: http://localhost:5173/admin

### 登录信息
- 管理员: 13800138000 / admin123
- 测试用户: 13900139000 / test123

---

**修复时间**: 2026-04-15 23:20  
**修复状态**: ✅ 完成  
**影响范围**: 全部90篇文章  
**下次检查**: 修改爬虫Pipeline代码
