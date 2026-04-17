# 爬虫内容提取优化报告

## 📋 问题描述

**用户反馈**: 爬虫抓取的数据包含整个页面HTML,包括导航栏、侧边栏、广告等无关内容,而不是只有文章正文。

**问题示例**:
- 抓取的内容包含"首页"、"返回"、"关于我们"等导航链接
- 包含侧边栏的"热门文章"、"推荐阅读"等内容
- 包含页脚的版权信息、备案号等
- 包含广告和其他无关的页面元素

## 🎯 解决方案

### 1. 引入智能内容提取库

使用 **trafilatura** 库进行智能内容提取:
- trafilatura 是一个专门用于网页正文提取的Python库
- 能够自动识别和提取网页的主要内容
- 自动过滤导航栏、侧边栏、广告、评论等干扰信息
- 支持多种网页结构和框架

### 2. 实现内容提取工具类

创建了 `crawler/energy_crawler/content_extractor.py`:

**核心功能**:
- `extract_content()`: 从HTML中提取正文内容
- `extract_with_fallback()`: 使用trafilatura提取,失败时回退到CSS选择器
- `_clean_content()`: 清理提取的内容,移除多余空行和无关文本

**提取配置**:
```python
trafilatura.extract(
    html_text,
    url=url,
    include_comments=False,    # 不包含评论
    include_tables=True,       # 包含表格(可能包含重要数据)
    no_fallback=False,         # 如果主要方法失败,使用备用方法
    output_format='txt',       # 纯文本输出
    with_metadata=True,        # 包含元数据(标题、作者、日期)
)
```

**内容清理规则**:
- 移除多余的空行
- 过滤太短的行(可能是导航或无关内容)
- 过滤常见的导航和无关文本:
  - 首页、返回、上一页、下一页、更多
  - 关于我们、联系我们、版权所有、备案号
  - 分享到、收藏、打印、字号
  - Copyright、©、ICP

### 3. 更新爬虫实现

已更新的爬虫:
- ✅ `xinhua_real_spider.py` - 新华网能源
- ✅ `chinapower_spider.py` - 中国电力网

**更新方式**:
```python
# 旧方式: 使用CSS选择器
content_parts = response.css('div.content p::text').getall()
content = '\n\n'.join(content_parts)

# 新方式: 使用智能提取器
from energy_crawler.content_extractor import extractor

extraction_result = extractor.extract_with_fallback(response, css_selectors)
if extraction_result['success']:
    content = extraction_result['content']
```

**优势**:
1. **智能识别**: 自动识别正文区域,无需手动编写复杂的CSS选择器
2. **通用性强**: 适用于各种网页结构,不需要为每个网站定制选择器
3. **容错性好**: 如果trafilatura失败,自动回退到CSS选择器方案
4. **提取元数据**: 可以提取标题、作者、发布日期等元数据

## 📊 测试结果

### 测试用例

使用包含导航栏、侧边栏、正文、页脚的完整HTML页面进行测试:

**测试结果**:
```
内容质量检查:
  ✅ 已过滤: 首页
  ✅ 已过滤: 关于我们
  ✅ 已过滤: 热门文章
  ✅ 已过滤: 版权所有
  ✅ 已过滤: 备案号

正文内容检查:
  ✅ 包含正文: 第一段内容
  ✅ 包含正文: 第二段内容
  ✅ 包含正文: 第三段内容
  ✅ 包含正文: 第四段内容
```

**结论**: 智能提取器成功过滤了所有无关内容,只保留了正文部分。

## 📦 依赖更新

### 新增依赖

在 `crawler/requirements.txt` 中添加:
```
trafilatura==1.12.2
```

### 安装依赖

```bash
cd backend
source venv/bin/activate
pip install trafilatura==1.12.2
```

## 🔄 待完成工作

### 需要更新的爬虫

以下爬虫还需要更新为使用智能内容提取器:

1. ⏳ `power_spider.py` - 北极星电力网
2. ⏳ `ndrc_spider.py` - 国家发改委
3. ⏳ `peopledaily_spider.py` - 人民网能源
4. ⏳ `coal_spider.py` - 中国煤炭网
5. ⏳ `newenergy_spider.py` - 中国新能源网
6. ⏳ `cnenergy_spider.py` - 中国能源网
7. ⏳ `energy_news_spider.py` - 综合能源新闻
8. ⏳ `ccer_spider.py` - CCER碳交易
9. ⏳ `mysteel_spider.py` - 我的钢铁网
10. ⏳ `cnmn_paper_spider.py` - 中国有色金属报
11. ⏳ `smm_metal_spider.py` - 上海有色金属网

### 更新步骤

对于每个爬虫文件:

1. **添加导入**:
```python
from energy_crawler.content_extractor import extractor
```

2. **更新 parse_article 方法**:
```python
def parse_article(self, response):
    # ... 前面的代码 ...
    
    # 定义备用的CSS选择器
    css_selectors = [
        'div.content p::text',
        'div.article p::text',
        # ... 其他选择器 ...
    ]
    
    # 使用智能提取器
    extraction_result = extractor.extract_with_fallback(response, css_selectors)
    
    if extraction_result['success']:
        content = extraction_result['content']
        item['content'] = content
        item['summary'] = content[:200] + '...' if len(content) > 200 else content
        
        # 如果提取到了标题,可以覆盖原标题
        if extraction_result['title'] and len(extraction_result['title']) > 5:
            item['title'] = extraction_result['title']
    else:
        item['content'] = ''
        item['summary'] = ''
    
    # ... 后面的代码 ...
```

3. **测试爬虫**:
```bash
cd crawler
../backend/venv/bin/scrapy crawl <spider_name> -s LOG_LEVEL=INFO
```

## 📈 预期效果

### 内容质量提升

- **更准确**: 只包含文章正文,不包含无关内容
- **更干净**: 自动过滤导航、广告、评论等干扰信息
- **更完整**: 保留文章的完整结构和段落

### 用户体验改善

- **阅读体验**: 用户看到的是纯净的文章内容
- **搜索准确**: 搜索时不会匹配到导航栏等无关文本
- **推送质量**: 推送的内容更有价值

### 维护成本降低

- **通用性强**: 不需要为每个网站编写复杂的CSS选择器
- **适应性好**: 网站改版后仍能正常工作
- **易于扩展**: 新增网站时更容易实现

## 🔍 监控指标

### 关键指标

1. **内容长度**: 提取的内容应该在合理范围内(500-10000字)
2. **成功率**: 内容提取成功率应该 > 90%
3. **质量评分**: 人工抽查内容质量,确保无关内容被过滤

### 告警条件

- 内容长度 < 100字 (可能提取失败)
- 内容长度 > 50000字 (可能包含了整个页面)
- 内容包含"首页"、"返回"等导航文本 (过滤不完全)

## 📝 使用建议

### 最佳实践

1. **优先使用智能提取器**: 对于新网站,先尝试使用trafilatura
2. **保留CSS选择器作为备用**: 如果trafilatura失败,回退到CSS选择器
3. **定期检查内容质量**: 人工抽查抓取的内容,确保质量
4. **记录失败案例**: 对于提取失败的页面,记录URL和原因

### 特殊情况处理

1. **JavaScript渲染的页面**: trafilatura可能无法处理,需要使用Playwright
2. **PDF文档**: 需要使用专门的PDF提取工具
3. **图片内容**: 需要OCR技术提取文字

## 🎉 总结

通过引入trafilatura智能内容提取库,我们成功解决了爬虫抓取内容包含无关信息的问题。新的提取方案具有以下优势:

1. ✅ **智能识别**: 自动识别正文区域
2. ✅ **过滤干扰**: 自动过滤导航、广告等无关内容
3. ✅ **通用性强**: 适用于各种网页结构
4. ✅ **容错性好**: 失败时自动回退到备用方案
5. ✅ **易于维护**: 减少了手动编写CSS选择器的工作量

**下一步**: 将智能内容提取器应用到所有爬虫,并进行全面测试。

---

**更新时间**: 2026-04-16
**更新人员**: AI Assistant
**文档版本**: v1.0
