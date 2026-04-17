# 新爬虫快速开始指南

## 🚀 快速测试

### 方法1：批量测试所有新爬虫
```bash
# 1. 激活虚拟环境
cd backend
source venv/bin/activate

# 2. 运行批量测试（每个爬虫3篇文章）
cd ../crawler
python test_all_new_crawlers.py
```

### 方法2：单独测试每个爬虫
```bash
# 1. 激活虚拟环境
cd backend
source venv/bin/activate
cd ../crawler

# 2. 测试国家能源局（最重要）
python crawl4ai_nea.py

# 3. 测试新华网
python crawl4ai_xinhua.py

# 4. 测试中国电力网
python crawl4ai_chinapower.py

# 5. 测试北极星电力网
python crawl4ai_bjx_power.py

# 6. 测试中国煤炭市场网
python crawl4ai_coal.py

# 7. 测试中国新能源网
python crawl4ai_newenergy.py
```

## 📊 验证结果

### 查看爬虫日志
日志会显示：
```
============================================================
🚀 开始爬取 国家能源局
📍 URL: https://www.nea.gov.cn/xwzx/nyyw.htm
============================================================

📋 步骤1: 爬取列表页...
✅ 列表页加载成功
📊 CSS选择器提取到 15 个链接
✅ 有效文章: 15 篇

📖 步骤2: 爬取文章详情...

[1/10] 文章标题...
  ✓ 当日文章(2026-04-16)
  ✅ 保存成功

[2/10] 文章标题...
  ⏭️  跳过: 非当日文章(2026-04-15)

[3/10] 文章标题...
  ⚠️  警告: 无法提取发布日期，仍然保存
  ✅ 保存成功

============================================================
📊 爬取完成
✅ 新增文章: 8 篇
============================================================
```

### 查询数据库
```bash
# 连接数据库
mysql -h localhost -P 3306 -u root -pjinchun123 energy_station
```

```sql
-- 1. 查询今天各来源的文章数量
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source
ORDER BY count DESC;

-- 2. 查询最新的文章
SELECT id, title, source, DATE(published_at) as pub_date
FROM articles
WHERE DATE(created_at) = CURDATE()
ORDER BY created_at DESC
LIMIT 20;

-- 3. 查询各来源的文章日期分布
SELECT source, DATE(published_at) as pub_date, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source, DATE(published_at)
ORDER BY source, pub_date DESC;
```

## ✅ 预期结果

### 成功标志
- ✅ 爬虫能找到文章链接
- ✅ 能提取文章内容
- ✅ 能识别今天的文章（显示 `✓ 当日文章`）
- ✅ 能过滤非今天的文章（显示 `⏭️ 跳过: 非当日文章`）
- ✅ 文章保存到数据库
- ✅ 数据库中的文章主要是今天发布的

### 常见输出
```
✓ 当日文章(2026-04-16)          # 是今天的文章，会保存
⏭️ 跳过: 非当日文章(2026-04-15)  # 不是今天的文章，跳过
⚠️ 警告: 无法提取发布日期        # 无法确定日期，仍然保存
⚠️ 跳过: 404页面                # 无效页面，跳过
⚠️ 跳过: 反爬验证页面            # 反爬页面，跳过
⚠️ 跳过: 非详情页                # 不是文章页面，跳过
```

## 🔧 调试技巧

### 如果爬虫没有找到文章
1. 检查网站是否可访问
2. 检查CSS选择器是否正确
3. 查看爬虫日志中的错误信息

### 如果所有文章都被跳过
1. 检查是否都是历史文章（非今天发布）
2. 检查日期提取是否正常工作
3. 尝试访问网站，查看文章的实际发布日期

### 如果内容提取失败
1. 爬虫会自动使用Markdown提取作为备用方案
2. 检查网站是否有反爬措施
3. 查看爬虫日志中的详细错误信息

## 📈 性能监控

### 查看爬取速度
```bash
# 查看爬虫运行时间
time python crawl4ai_nea.py
```

### 查看数据库增长
```sql
-- 查询今天新增的文章数量
SELECT COUNT(*) as today_count
FROM articles
WHERE DATE(created_at) = CURDATE();

-- 查询最近1小时新增的文章
SELECT COUNT(*) as recent_count
FROM articles
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
```

## 🎯 下一步

### 测试通过后
1. 运行完整的爬虫（不限制文章数量）
2. 设置定时任务，每天自动运行
3. 监控爬虫运行情况

### 如果测试失败
1. 查看错误日志
2. 检查网站是否可访问
3. 调整CSS选择器
4. 联系开发人员

## 📞 获取帮助

### 查看详细文档
- `CRAWLER_MIGRATION_COMPLETE.md` - 迁移完成报告
- `CRAWLER_MIGRATION_SUMMARY.md` - 迁移总结
- `TODAY_ARTICLE_DETECTION_SUMMARY.md` - 日期检测功能说明

### 常见问题
1. **crawl4ai导入失败**: 确保虚拟环境已激活，运行 `pip install crawl4ai`
2. **数据库连接失败**: 检查MySQL是否运行，密码是否正确
3. **所有文章都被跳过**: 可能都是历史文章，检查网站的文章日期

---

**快速开始**: `python test_all_new_crawlers.py`  
**单独测试**: `python crawl4ai_nea.py`  
**查看数据**: 连接MySQL查询 `articles` 表
