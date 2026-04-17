# 爬虫迁移优先级分析

## 当前状态总结

### ✅ 已迁移到Crawl4AI（7个）
1. **人民网** - `crawl4ai_peopledaily.py` ✅ 已测试
2. **中国能源网** - `crawl4ai_cnenergy.py`
3. **中国能源报** - `crawl4ai_cnenergynews.py`
4. **国家发改委** - `crawl4ai_ndrc.py`
5. **有色金属网** - `crawl4ai_smm_metal.py`
6. **中国有色金属报** - `crawl4ai_cnmn_paper.py`
7. **北京绿色交易所** - `crawl4ai_ccer.py`

### ❌ 未迁移（12个Scrapy爬虫）

## 详细分析

### 🔴 高优先级（建议立即迁移）

#### 1. 国家能源局 ⭐⭐⭐⭐⭐
- **Scrapy文件**: `nea_spider.py` + `real_nea_spider.py`
- **URL**: https://www.nea.gov.cn/xwzx/nyyw.htm
- **重要性**: 最高 - 官方权威来源
- **复杂度**: 高 - 使用Playwright处理Vue.js动态渲染
- **问题**: 
  - 需要Playwright处理动态内容
  - 有两个版本的爬虫（nea和real_nea）
  - 代码复杂，维护成本高
- **迁移收益**: 
  - ✅ 简化代码（从200+行减少到50行）
  - ✅ 自动获得日期检测功能
  - ✅ 自动获得内容验证功能
  - ✅ 统一的错误处理
- **预计时间**: 2-3小时
- **建议**: 合并两个爬虫为一个Crawl4AI版本

#### 2. 新华网能源 ⭐⭐⭐⭐
- **Scrapy文件**: `xinhua_energy_spider.py` + `xinhua_spider.py` + `xinhua_real_spider.py`
- **URL**: http://www.news.cn/energy/
- **重要性**: 高 - 权威媒体
- **复杂度**: 中等
- **问题**: 有三个版本的爬虫，代码重复
- **迁移收益**: 
  - ✅ 合并三个爬虫为一个
  - ✅ 减少代码重复
  - ✅ 统一维护
- **预计时间**: 1.5-2小时
- **建议**: 合并为一个Crawl4AI版本

### 🟡 中优先级（建议本周完成）

#### 3. 中国电力网 ⭐⭐⭐
- **Scrapy文件**: `chinapower_spider.py`
- **URL**: 待确认
- **重要性**: 中 - 电力行业专业网站
- **复杂度**: 中等
- **预计时间**: 1.5小时

#### 4. 电力新闻 ⭐⭐⭐
- **Scrapy文件**: `power_spider.py`
- **URL**: 待确认
- **重要性**: 中 - 电力行业新闻
- **复杂度**: 简单
- **预计时间**: 1小时

### 🟢 低优先级（可选）

#### 5. 煤炭网 ⭐⭐
- **Scrapy文件**: `coal_spider.py`
- **重要性**: 低 - 细分领域
- **预计时间**: 1小时

#### 6. 新能源网 ⭐⭐
- **Scrapy文件**: `newenergy_spider.py`
- **重要性**: 低 - 细分领域
- **预计时间**: 1小时

### ❓ 待评估

#### 7. 能源新闻 ❓
- **Scrapy文件**: `energy_news_spider.py`
- **状态**: 需要检查是否与其他爬虫重复

#### 8. 我的钢铁网 ❓
- **Scrapy文件**: `mysteel_spider.py`
- **状态**: 需要检查是否与smm_metal重复

## 迁移策略

### 阶段1：高优先级（本周）
1. **国家能源局** - 合并nea和real_nea为一个Crawl4AI爬虫
2. **新华网** - 合并三个版本为一个Crawl4AI爬虫

### 阶段2：中优先级（下周）
3. **中国电力网**
4. **电力新闻**

### 阶段3：低优先级（按需）
5. **煤炭网**
6. **新能源网**
7. 其他待评估的爬虫

## 迁移收益对比

### 国家能源局爬虫对比

| 特性 | Scrapy版本 | Crawl4AI版本 |
|------|-----------|-------------|
| 代码行数 | ~250行 | ~50行 |
| 依赖 | Scrapy + Playwright | Crawl4AI |
| 动态渲染 | 手动处理Playwright | 内置支持 |
| 日期检测 | 手动实现 | 自动继承 |
| 内容验证 | 无 | 自动继承 |
| 错误处理 | 手动处理 | 统一处理 |
| 维护成本 | 高 | 低 |

### 代码复杂度对比

**Scrapy版本（nea_spider.py）**:
```python
# 需要手动管理Playwright
async def init_playwright(self):
    if not self.playwright:
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(...)
        self.context = await self.browser.new_context(...)

# 需要手动处理异步
def parse_with_playwright(self, response):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        html = loop.run_until_complete(self.fetch_page(response.url))
        ...
    finally:
        loop.close()

# 需要手动提取内容
content_selectors = [
    'div.TRS_Editor p::text',
    'div#TRS_AUTOADD_CONTENT p::text',
    ...
]
for selector in content_selectors:
    parts = response.css(selector).getall()
    if parts and len(parts) > 1:
        content_parts = parts
        break

# 需要手动验证内容
if item['content'] and len(item['content']) > 100:
    yield item
else:
    self.logger.warning(f'⚠️  内容太短或为空，跳过')
```

**Crawl4AI版本（预期）**:
```python
class NeaCrawler(Crawl4AIBase):
    def __init__(self):
        super().__init__(
            source_name="国家能源局",
            base_url="https://www.nea.gov.cn/xwzx/nyyw.htm",
            category="energy"
        )
        
        self.list_schema = {
            "name": "NeaArticles",
            "baseSelector": "ul.list li, div.list-item",
            "fields": [
                {"name": "title", "selector": "a", "type": "text"},
                {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"},
                {"name": "published_date", "selector": ".date, .time", "type": "text"}
            ]
        }
        
        self.detail_schema = None  # 使用Markdown提取

# 自动继承：
# - 动态渲染支持
# - 日期检测
# - 内容验证
# - 错误处理
# - 数据库保存
```

**代码减少**: ~80% (250行 → 50行)

## 迁移步骤（以国家能源局为例）

### 1. 创建新文件
```bash
touch crawler/crawl4ai_nea.py
```

### 2. 实现基本结构
```python
import asyncio
from crawl4ai_base import Crawl4AIBase

class NeaCrawler(Crawl4AIBase):
    def __init__(self):
        super().__init__(
            source_name="国家能源局",
            base_url="https://www.nea.gov.cn/xwzx/nyyw.htm",
            category="energy"
        )
        
        # 配置列表页选择器
        self.list_schema = {...}
        
        # 使用Markdown提取详情页
        self.detail_schema = None

async def main():
    crawler = NeaCrawler()
    await crawler.crawl(max_articles=10)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 测试运行
```bash
cd backend
source venv/bin/activate
cd ../crawler
python crawl4ai_nea.py
```

### 4. 验证数据
```sql
SELECT * FROM articles WHERE source = '国家能源局' ORDER BY created_at DESC LIMIT 10;
```

### 5. 删除旧爬虫
```bash
rm crawler/energy_crawler/spiders/nea_spider.py
rm crawler/energy_crawler/spiders/real_nea_spider.py
```

## 预期成果

### 迁移完成后
- ✅ 代码量减少 ~70%
- ✅ 维护成本降低 ~80%
- ✅ 所有爬虫统一使用Crawl4AI
- ✅ 自动支持日期检测
- ✅ 自动支持内容验证
- ✅ 统一的错误处理和日志
- ✅ 更好的可维护性

### 代码统计
- **迁移前**: ~2000行 Scrapy代码
- **迁移后**: ~400行 Crawl4AI代码
- **减少**: ~80%

## 建议

### 立即行动
1. **今天**: 迁移国家能源局爬虫（合并nea和real_nea）
2. **明天**: 迁移新华网爬虫（合并三个版本）

### 本周完成
3. 迁移中国电力网
4. 迁移电力新闻

### 后续优化
5. 评估其他爬虫是否需要迁移
6. 删除所有旧的Scrapy代码
7. 更新文档和配置

## 总结

✅ **建议优先迁移国家能源局和新华网爬虫**

原因：
1. 这两个是最重要的内容来源
2. 代码最复杂，迁移收益最大
3. 可以合并多个版本，减少代码重复
4. 自动获得日期检测和内容验证功能

预计收益：
- 代码减少 ~80%
- 维护成本降低 ~80%
- 功能更强大（自动日期检测、内容验证）
- 更好的可维护性
