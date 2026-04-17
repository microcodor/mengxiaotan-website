# 问题修复总结

**修复时间**: 2026-04-15 23:10  
**修复内容**: 首页文章显示、列表页排序、分类导航

---

## ✅ 已完成的修复

### 1. 首页焦点资讯显示最新文章 ✨

**问题**: 焦点资讯显示的是测试数据，不是最新文章

**原因**: 
- API只返回 `is_carousel=True` 的文章
- 今天爬取的文章 `is_carousel=False`

**解决方案**:
```python
# 修改前
articles = Article.query.filter_by(is_carousel=True, is_reviewed=True)\
    .order_by(desc(Article.published_at)).limit(5).all()

# 修改后
articles = Article.query.filter_by(is_reviewed=True)\
    .order_by(desc(Article.created_at)).limit(5).all()
```

**修改文件**: `backend/app/api/articles.py` - `/articles/carousel` 端点

**效果**: 
- ✅ 焦点资讯现在显示最新5篇文章
- ✅ 按创建时间倒序排列

---

### 2. 首页最新资讯显示最新文章

**问题**: 首页显示的是测试数据（ID 1-5），不是最新爬取的文章

**原因**: 
- 测试数据被设置为置顶（`is_top=True`）
- API排序逻辑：`order_by(desc(Article.is_top), desc(Article.published_at))`
- 置顶文章总是排在最前面

**解决方案**:
```python
# 修改前
query = query.order_by(desc(Article.is_top), desc(Article.published_at))

# 修改后
query = query.order_by(desc(Article.created_at))
```

**修改文件**: `backend/app/api/articles.py`

**效果**: 
- ✅ 首页现在显示最新爬取的文章
- ✅ 按创建时间倒序排列
- ✅ 最新的文章在最前面

---

### 2. 列表页文章倒序显示

**问题**: 列表页文章顺序不正确

**解决方案**: 与首页使用同一个API，已经修复

**效果**:
- ✅ 列表页按创建时间倒序
- ✅ 最新文章在最前面

---

### 3. 分类导航显示后台已有平台

**问题**: 分类导航没有显示任何分类

**原因**: 数据库 `categories` 表为空

**解决方案**:
1. 修改 `backend/init_db.py`，添加分类初始化代码
2. 运行初始化脚本创建分类

**创建的分类**:
```python
categories = [
    {'code': 'power', 'name': '电力', 'icon': 'power'},
    {'code': 'energy', 'name': '能源', 'icon': 'energy'},
    {'code': 'coal', 'name': '煤炭', 'icon': 'coal'},
    {'code': 'steel', 'name': '钢铁', 'icon': 'steel'},
    {'code': 'new_energy', 'name': '新能源', 'icon': 'renewable'},
    {'code': 'ndrc', 'name': '政策', 'icon': 'government'},
]
```

**效果**:
- ✅ 分类导航显示6个分类
- ✅ 每个分类显示文章数量
- ✅ 点击分类可以筛选文章

---

## 📊 当前数据统计

### 文章统计
- **总文章数**: 90篇
- **今日新增**: 82篇
- **已审核**: 90篇

### 分类统计
| 分类 | 文章数 |
|------|--------|
| 电力 (power) | 42篇 |
| 能源 (energy) | 21篇 |
| 钢铁 (steel) | 16篇 |
| 煤炭 (coal) | 3篇 |
| 新能源 (new_energy) | 3篇 |
| 政策 (ndrc) | 2篇 |
| 测试 (test) | 3篇 |

### 来源统计
| 来源 | 文章数 |
|------|--------|
| 中国电力网 | 39篇 |
| 新华网 | 18篇 |
| 我的钢铁网 | 16篇 |
| 国家能源局 | 4篇 |
| 北极星电力网 | 3篇 |
| 其他 | 10篇 |

---

## 🔍 验证方法

### 1. 验证首页
访问: http://localhost:5173/

**预期结果**:
- ✅ 显示最新爬取的文章
- ✅ 文章按时间倒序排列
- ✅ 最新的文章在最前面

### 2. 验证列表页
访问: http://localhost:5173/articles/

**预期结果**:
- ✅ 显示分类导航（6个分类）
- ✅ 文章按时间倒序排列
- ✅ 点击分类可以筛选

### 3. 验证API
```bash
# 测试文章列表API
curl http://localhost:5001/api/articles/ | python3 -m json.tool

# 测试分类API
curl http://localhost:5001/api/categories/ | python3 -m json.tool
```

---

## 🚀 下一步工作

### 1. 将剩余爬虫改为Crawl4AI（高优先级）

**需要迁移的爬虫**（7个失败的爬虫）:
1. ❌ CCER碳交易 (ccer)
2. ❌ 中国有色金属报 (cnmn_paper)
3. ❌ 上海有色金属网 (smm_metal)
4. ❌ 国家发改委 (ndrc) - 代码错误
5. ❌ 人民网 (peopledaily) - 代码错误
6. ❌ 中国能源网 (cnenergy) - 代码错误
7. ❌ 综合能源新闻 (energy_news) - 选择器问题

**迁移方案**:
- 使用Crawl4AI框架
- 列表页：Markdown + 链接提取
- 详情页：LLM智能提取（可选）
- 代码量减少70%

**预期效果**:
- 成功率从50%提升到90%+
- 维护成本降低80%
- 适应网站改版

### 2. 修改爬虫Pipeline（中优先级）

**问题**: 新爬取的文章 `is_reviewed` 字段为 NULL

**解决方案**:
修改 `crawler/energy_crawler/pipelines.py`，在插入文章时设置 `is_reviewed=True`

```python
# 修改前
cursor.execute("""
    INSERT INTO articles 
    (title, summary, content, source, source_url, category, published_at, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (...))

# 修改后
cursor.execute("""
    INSERT INTO articles 
    (title, summary, content, source, source_url, category, published_at, created_at, is_reviewed)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (..., True))
```

### 3. 优化数据库表结构（低优先级）

**修改**:
```sql
ALTER TABLE articles 
MODIFY COLUMN is_reviewed TINYINT(1) DEFAULT 1 COMMENT '是否已审核';
```

---

## 📝 相关文档

- `ARTICLE_DISPLAY_FIX.md` - 文章显示问题修复详情
- `CRAWLER_ISSUES_ANALYSIS.md` - 爬虫问题分析
- `CRAWLER_SITES_CONFIG.md` - 爬虫配置清单
- `CRAWL4AI_DETAILED_OUTPUT_EXAMPLE.md` - Crawl4AI输出格式
- `CRAWL4AI_EVALUATION.md` - Crawl4AI评估报告

---

**修复状态**: ✅ 完成  
**测试状态**: ⏳ 待用户验证  
**下次检查**: 用户确认后开始Crawl4AI迁移
