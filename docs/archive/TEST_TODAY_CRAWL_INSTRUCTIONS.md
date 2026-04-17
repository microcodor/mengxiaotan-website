# 当日文章爬取功能测试说明

## 测试目标
验证爬虫是否能正确识别和过滤非当日文章，只保存今天发布的文章。

## 测试准备

### 1. 确保服务正在运行
```bash
# 如果服务未运行，先启动
./start_local.sh
```

### 2. 激活后端虚拟环境
```bash
cd backend
source venv/bin/activate
```

### 3. 检查crawl4ai是否安装
```bash
python -c "import crawl4ai; print('crawl4ai installed')"
```

如果未安装，运行：
```bash
pip install crawl4ai
```

## 测试步骤

### 测试1: 人民网爬虫（3篇文章）

```bash
cd ../crawler
python crawl4ai_peopledaily.py
```

**预期结果**：
- ✅ 显示找到的文章总数
- ✅ 对每篇文章进行日期检测
- ✅ 显示 `✓ 当日文章(2026-04-16)` 或 `⏭️ 跳过: 非当日文章(日期)`
- ✅ 只保存今天的文章到数据库
- ✅ 显示最终保存的文章数量

### 测试2: 中国能源网爬虫（3篇文章）

修改 `crawl4ai_cnenergy.py`，将 `max_articles=10` 改为 `max_articles=3`

```bash
python crawl4ai_cnenergy.py
```

### 测试3: 中国能源报爬虫（3篇文章）

修改 `crawl4ai_cnenergynews.py`，将 `max_articles=10` 改为 `max_articles=3`

```bash
python crawl4ai_cnenergynews.py
```

## 验证结果

### 1. 查看爬虫日志

日志中应该包含：
```
[1/3] 文章标题...
  ✓ 当日文章(2026-04-16)
  ✅ 保存成功

[2/3] 文章标题...
  ⏭️ 跳过: 非当日文章(2026-04-15)

[3/3] 文章标题...
  ⚠️ 警告: 无法提取发布日期，仍然保存
  ✅ 保存成功
```

### 2. 查询数据库

```bash
# 在MySQL中查询今天保存的文章
mysql -h localhost -P 3306 -u root -pjinchun123 energy_station

# 查询今天的文章
SELECT id, title, source, DATE(published_at) as pub_date, DATE(created_at) as create_date
FROM articles
WHERE DATE(created_at) = CURDATE()
ORDER BY created_at DESC
LIMIT 10;

# 查询各来源今天的文章数量
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source;
```

### 3. 检查日期分布

```sql
# 查看最近保存的文章的发布日期分布
SELECT DATE(published_at) as pub_date, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY DATE(published_at)
ORDER BY pub_date DESC;
```

**预期结果**：
- 大部分文章的 `published_at` 应该是今天（2026-04-16）
- 少数无法提取日期的文章可能显示为当前时间

## 测试检查清单

- [ ] 爬虫能正确提取文章日期
- [ ] 爬虫能识别今天的文章（显示 `✓ 当日文章`）
- [ ] 爬虫能识别非今天的文章（显示 `⏭️ 跳过: 非当日文章`）
- [ ] 非当日文章不会保存到数据库
- [ ] 无法提取日期的文章会给出警告但仍然保存
- [ ] 数据库中的文章主要是今天发布的

## 常见问题

### Q1: 所有文章都显示"无法提取发布日期"
**原因**: 网站的日期格式可能不在支持的格式列表中
**解决**: 
1. 查看文章内容，找到日期格式
2. 在 `crawl4ai_base.py` 的 `extract_date_from_content` 方法中添加新的日期格式

### Q2: 爬虫跳过了所有文章
**原因**: 可能爬取的都是历史文章
**解决**: 
1. 检查网站列表页是否显示最新文章
2. 尝试访问网站的"最新"或"今日"栏目

### Q3: crawl4ai导入失败
**原因**: crawl4ai未安装或虚拟环境未激活
**解决**:
```bash
source backend/venv/bin/activate
pip install crawl4ai
```

## 下一步

测试通过后：
1. 恢复所有爬虫的 `max_articles` 为10或更多
2. 运行完整的爬虫测试
3. 设置定时任务，每天自动运行爬虫
4. 监控日期提取失败率，优化日期格式支持
