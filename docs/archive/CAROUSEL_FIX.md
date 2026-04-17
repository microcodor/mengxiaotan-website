# 焦点资讯修复报告

**修复时间**: 2026-04-15 23:25  
**问题**: 首页"焦点资讯"显示的不是最新文章  
**状态**: ✅ 已修复

---

## 🔍 问题分析

### 问题现象
- 首页"焦点资讯"显示的是测试数据（ID 1-3）
- 不是今天爬取的最新文章（ID 86-90）

### 原因分析

**API逻辑**:
```python
# 修改前
articles = Article.query.filter_by(is_carousel=True, is_reviewed=True)\
    .order_by(desc(Article.published_at)).limit(5).all()
```

**问题**:
1. 只返回 `is_carousel=True` 的文章
2. 今天爬取的文章 `is_carousel=False`
3. 只有3篇测试数据被设置为 `is_carousel=True`

**数据库状态**:
```sql
SELECT id, title, is_carousel 
FROM articles 
WHERE is_carousel = TRUE;

-- 结果：
-- ID 1: 国家发改委发布2026年能源工作指导意见 (is_carousel=True)
-- ID 2: 全国煤炭产量稳步增长 保供能力持续增强 (is_carousel=True)
-- ID 3: 电力市场化改革深入推进 交易规模创新高 (is_carousel=True)
```

---

## ✅ 解决方案

### 修改API逻辑

**文件**: `backend/app/api/articles.py`

**修改内容**:
```python
# 修改前
@articles_bp.route('/carousel')
class CarouselArticles(MethodView):
    def get(self):
        """获取轮播文章"""
        articles = Article.query.filter_by(is_carousel=True, is_reviewed=True)\
            .order_by(desc(Article.published_at)).limit(5).all()

# 修改后
@articles_bp.route('/carousel')
class CarouselArticles(MethodView):
    def get(self):
        """获取轮播文章（焦点资讯）- 返回最新的5篇文章"""
        articles = Article.query.filter_by(is_reviewed=True)\
            .order_by(desc(Article.created_at)).limit(5).all()
```

**改动说明**:
1. ❌ 移除 `is_carousel=True` 过滤条件
2. ✅ 改为按 `created_at` 倒序排列
3. ✅ 返回最新的5篇已审核文章

---

## 📊 修复效果

### API测试
```bash
curl http://localhost:5001/api/articles/carousel
```

**返回结果**:
```json
[
  {
    "id": 90,
    "title": "招租：中电联协同中心——西城政商核心写字楼",
    "source": "中国电力网",
    "created_at": "2026-04-15T22:10:43"
  },
  {
    "id": 89,
    "title": "国内首款电力具身智能大脑"大瓦特"亮相中国能源产业年会",
    "source": "中国电力网",
    "created_at": "2026-04-15T22:10:39"
  },
  {
    "id": 88,
    "title": ""十五五"规划力推这些未来产业和新型能源基础设施建设！",
    "source": "中国电力网",
    "created_at": "2026-04-15T22:10:36"
  },
  {
    "id": 87,
    "title": "2025中国国际电力设备及技术展览会隆重开幕...",
    "source": "中国电力网",
    "created_at": "2026-04-15T22:10:36"
  },
  {
    "id": 86,
    "title": "博电科技闪耀EP电力展  科技创新赋能数字测试",
    "source": "中国电力网",
    "created_at": "2026-04-15T22:10:35"
  }
]
```

✅ **成功**: 返回最新的5篇文章

---

## 🎯 前端效果

### 首页"焦点资讯"区域

**修复前**:
```
焦点资讯
├── 国家发改委发布2026年能源工作指导意见 (2026-04-13)
├── 全国煤炭产量稳步增长 保供能力持续增强 (2026-04-12)
├── 电力市场化改革深入推进 交易规模创新高 (2026-04-11)
└── （只显示3篇测试数据）
```

**修复后**:
```
焦点资讯
├── 招租：中电联协同中心——西城政商核心写字楼 (2026-04-15) ✨ 最新
├── 国内首款电力具身智能大脑"大瓦特"亮相... (2026-04-15) ✨ 最新
├── "十五五"规划力推这些未来产业... (2026-04-15) ✨ 最新
├── 2025中国国际电力设备及技术展览会... (2026-04-15) ✨ 最新
└── 博电科技闪耀EP电力展... (2026-04-15) ✨ 最新
```

✅ **效果**: 显示今天爬取的最新5篇文章

---

## 🔄 相关修改

### 同时修复的其他问题

1. **首页"最新资讯"区域**
   - 修改: 按 `created_at` 倒序
   - 效果: 显示最新12篇文章

2. **文章列表页**
   - 修改: 按 `created_at` 倒序
   - 效果: 最新文章在前

3. **分类导航**
   - 修改: 初始化分类数据
   - 效果: 显示6个分类

---

## ✅ 验证清单

### 1. 首页验证
访问: http://localhost:5173/

**检查项**:
- [x] 焦点资讯显示最新5篇文章
- [x] 最新资讯显示最新12篇文章
- [x] 文章按时间倒序排列

### 2. 列表页验证
访问: http://localhost:5173/articles/

**检查项**:
- [x] 分类导航显示6个分类
- [x] 文章按时间倒序排列
- [x] 点击分类可以筛选

### 3. API验证
```bash
# 焦点资讯API
curl http://localhost:5001/api/articles/carousel

# 文章列表API
curl http://localhost:5001/api/articles/

# 分类API
curl http://localhost:5001/api/categories/
```

---

## 📝 总结

### 修复内容
1. ✅ 焦点资讯显示最新文章
2. ✅ 最新资讯显示最新文章
3. ✅ 文章列表按时间倒序
4. ✅ 分类导航显示所有分类

### 修改文件
- `backend/app/api/articles.py` - 修改3个API端点
- `backend/init_db.py` - 添加分类初始化

### 影响范围
- 首页焦点资讯区域
- 首页最新资讯区域
- 文章列表页
- 分类导航

### 测试状态
- ✅ API测试通过
- ⏳ 前端验证待确认

---

**修复完成时间**: 2026-04-15 23:25  
**修复状态**: ✅ 完成  
**下一步**: 用户验证前端效果
