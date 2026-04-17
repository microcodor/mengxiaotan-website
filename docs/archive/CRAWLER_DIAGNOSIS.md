# 爬虫问题诊断报告

## 问题描述
用户启动了 `cnmn_paper`（中国有色金属报）爬虫任务，但没有抓取到任何文章数据。

## 问题分析

### 1. 爬虫运行状态
✅ **爬虫成功启动并运行**
- 启动时间: 2026-04-12 16:38:33
- 运行时长: 0.114秒
- 状态: 正常完成（finished）

### 2. 日志关键信息
```
[cnmn_paper] INFO: 正在解析: https://paper.cnmn.com.cn/
[cnmn_paper] INFO: 本次共找到 0 篇文章
```

### 3. 根本原因
**网站HTML结构与爬虫解析逻辑不匹配**

#### 网站实际结构：
网站使用 **图片地图（Image Map）** 来展示文章链接：
```html
<IMG src="..." useMap=#AutoMap1>
<MAP name=AutoMap1>
  <AREA href="http://paper.cnmn.com.cn/Content.aspx?id=198770&q=5269&v=1" shape=rect coords=...>
  <AREA href="http://paper.cnmn.com.cn/Content.aspx?id=198769&q=5269&v=1" shape=rect coords=...>
  ...
</MAP>
```

#### 爬虫当前逻辑：
爬虫在查找 `<a>` 标签和文本标题：
```python
links = response.css('a[href]')
for link in links:
    title = link.css('::text').get()  # 尝试获取文本
```

**问题**：`<AREA>` 标签没有文本内容，且不是 `<a>` 标签，所以爬虫找不到任何文章。

### 4. 其他爬虫运行情况
✅ **以下爬虫运行正常，已成功抓取数据：**

| 数据源 | 文章数量 | 最新抓取时间 |
|--------|---------|-------------|
| 中国电力网 | 37篇 | 2026-04-10 23:06 |
| 新华网 | 18篇 | 2026-04-11 00:12 |
| 我的钢铁网 | 15篇 | 2026-04-11 00:36 |
| 国家能源局 | 10篇 | 2026-04-10 22:44 |
| 北极星电力网 | 8篇 | 2026-04-10 23:39 |
| 中国新能源网 | 7篇 | 2026-04-10 23:39 |
| 中国煤炭市场网 | 7篇 | 2026-04-10 23:39 |

## 解决方案

### 方案1：修复 cnmn_paper 爬虫（推荐）

需要修改 `crawler/energy_crawler/spiders/cnmn_paper_spider.py`，添加对 `<AREA>` 标签的支持：

```python
def parse(self, response):
    """解析数字报首页"""
    self.logger.info(f'正在解析: {response.url}')
    
    # 查找图片地图中的文章链接
    area_links = response.css('area[href]')
    
    articles_found = 0
    for area in area_links:
        href = area.css('::attr(href)').get()
        
        # 过滤条件：只抓取 Content.aspx 页面
        if href and 'Content.aspx' in href:
            # 构建完整URL
            if not href.startswith('http'):
                href = 'https://paper.cnmn.com.cn/' + href.lstrip('/')
            
            articles_found += 1
            
            self.logger.info(f'找到文章 {articles_found}: {href}')
            
            yield scrapy.Request(
                href,
                callback=self.parse_article,
                meta={'title': f'文章{articles_found}'},  # 标题需要从详情页提取
                dont_filter=True,
                errback=self.handle_error
            )
            
            if articles_found >= 20:
                break
    
    self.logger.info(f'本次共找到 {articles_found} 篇文章')
```

### 方案2：使用其他正常工作的爬虫（临时方案）

如果需要立即获取数据，可以使用以下已验证可用的爬虫：

**推荐使用的爬虫：**
1. **mysteel** - 我的钢铁网（金属材料相关）
2. **chinapower** - 中国电力网（电力行业）
3. **xinhua_real** - 新华网（综合能源新闻）
4. **nea** - 国家能源局（政策文件）
5. **newenergy** - 中国新能源网（新能源行业）

**启动命令示例：**
```bash
cd crawler
scrapy crawl mysteel
scrapy crawl chinapower
scrapy crawl xinhua_real
```

## 建议

### 短期建议
1. **暂时停用 cnmn_paper 爬虫**，避免浪费资源
2. **使用其他正常工作的爬虫**获取数据
3. 在管理后台标记 cnmn_paper 为"维护中"状态

### 长期建议
1. **修复 cnmn_paper 爬虫**的解析逻辑
2. **添加爬虫健康检查机制**：
   - 如果爬虫连续3次抓取0篇文章，自动标记为异常
   - 发送告警通知管理员
3. **定期检查网站结构变化**：
   - 网站改版可能导致爬虫失效
   - 建议每月检查一次爬虫运行状态

## 测试验证

修复后，可以通过以下方式验证：

```bash
# 1. 测试爬虫
cd crawler
scrapy crawl cnmn_paper

# 2. 查看日志
tail -f logs/crawler/cnmn_paper_*.log

# 3. 检查数据库
docker exec energy_mysql mysql -u root -ppassword energy_station --default-character-set=utf8mb4 -e "SELECT COUNT(*) FROM articles WHERE source='中国有色金属报';"
```

## 总结

- ✅ 爬虫系统整体运行正常
- ✅ 大部分爬虫工作正常，已抓取108篇文章
- ❌ cnmn_paper 爬虫因网站结构特殊导致无法抓取
- 💡 建议：使用其他爬虫 + 修复 cnmn_paper

---
**诊断时间**: 2026-04-12 17:00
**诊断人**: AI Assistant
