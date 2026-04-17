# 分类和内容不显示问题诊断

## 问题描述
前端首页的分类导航和文章内容都没有显示。

## 可能的原因

### 1. 数据库中没有分类数据
**检查方法：**
```bash
# 进入后端容器
docker-compose exec backend bash

# 运行初始化脚本
python init_categories.py
```

### 2. 数据库中没有文章数据
**检查方法：**
```bash
# 检查文章数量
docker-compose exec backend python -c "
from app import create_app, db
from app.models import Article, Category
app = create_app()
with app.app_context():
    print(f'分类数量: {Category.query.count()}')
    print(f'文章数量: {Article.query.count()}')
    print(f'已审核文章: {Article.query.filter_by(is_reviewed=True).count()}')
"
```

### 3. 后端服务未启动或API端点有问题
**检查方法：**
```bash
# 检查容器状态
docker-compose ps

# 测试API端点
curl http://localhost:5000/api/categories
curl http://localhost:5000/api/articles?page=1&per_page=12
```

### 4. 前端代理配置问题
**检查方法：**
- 打开浏览器开发者工具 (F12)
- 查看 Network 标签
- 刷新页面，查看 `/api/categories` 和 `/api/articles` 请求
- 检查请求状态码和响应内容

## 解决步骤

### 步骤 1: 初始化分类数据
```bash
docker-compose exec backend python init_categories.py
```

### 步骤 2: 检查是否有文章数据
如果没有文章，需要运行爬虫：
```bash
# 查看爬虫配置
cat CRAWLER_SITES_CONFIG.md

# 运行爬虫（如果已配置）
docker-compose exec backend python -m app.crawler.main
```

### 步骤 3: 重启服务
```bash
docker-compose restart backend frontend
```

### 步骤 4: 验证前端
1. 打开浏览器访问 http://localhost:3000
2. 打开开发者工具 (F12)
3. 查看 Console 是否有错误
4. 查看 Network 标签，检查 API 请求

## 前端代码分析

### Home.tsx 组件加载流程
1. 使用 `useQuery` 加载分类：`api.get('/categories')`
2. 期望返回格式：`{items: [{code, name, icon, article_count, ...}]}`
3. 取前8个分类显示在"分类导航"区域
4. 如果 `categoriesData?.items` 为空或未定义，分类区域不显示

### 可能的前端问题
- API 请求失败（网络错误、CORS、认证问题）
- 返回数据格式不匹配
- React Query 缓存问题

## 快速修复命令

```bash
# 一键修复（按顺序执行）
docker-compose exec backend python init_categories.py
docker-compose restart backend
```

## 验证修复

访问以下URL验证：
- 后端分类API: http://localhost:5000/api/categories
- 后端文章API: http://localhost:5000/api/articles?page=1&per_page=12
- 前端首页: http://localhost:3000
