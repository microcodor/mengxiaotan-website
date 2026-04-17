# Crawl4AI 输出格式详解

**测试日期**: 2026-04-15  
**测试URL**: https://www.nbcnews.com/business

---

## 📊 Crawl4AI 输出的数据结构

### 1. 基本信息
```python
result.url              # 最终URL（处理重定向后）
result.status_code      # HTTP状态码: 200
result.success          # 是否成功: True/False
result.error_message    # 错误信息（如果有）
```

---

### 2. HTML内容
```python
result.html             # 完整的HTML源代码
```

**特点**:
- 完整的页面HTML
- 包含所有JavaScript渲染后的内容
- 长度: 2,402,504 字符（本次测试）

**示例**:
```html
<!DOCTYPE html><html lang="en"><head>
<script async="" src="https://sb.scorecardresearch.com/beacon.js"></script>
...
```

---

### 3. Markdown内容 ⭐⭐⭐

这是Crawl4AI的核心功能！自动将HTML转换为干净的Markdown。

```python
result.markdown.raw_markdown              # 原始Markdown
result.markdown.fit_markdown              # 过滤后的Markdown（去除噪音）
result.markdown.markdown_with_citations   # 带引用的Markdown
```

#### 3.1 Raw Markdown（原始）
- 长度: 32,462 字符
- 包含所有内容（导航、文章、链接等）
- 格式化良好，保留结构

**示例**:
```markdown
## LATEST BUSINESS NEWS

### [Iran war](https://www.nbcnews.com/world/iran-war)
## [U.S. military turns back ships amid hope for new peace talks](...)

### [Personal Finance](https://www.nbcnews.com/business/personal-finance)
## [5 smart ways to spend your tax refund](...)

## BUSINESS VIDEO
* [How to Give Back Without Spending: Donate Time, Skills, More](...)
* [It's Tax Day! Here Are Some Last-Minute Tips for Procrastinators](...)
```

#### 3.2 Fit Markdown（过滤后）
- 使用BM25算法过滤噪音
- 只保留核心内容
- 适合LLM处理

#### 3.3 Markdown with Citations（带引用）
- 长度: 17,176 字符
- 将链接转换为引用格式
- 更适合学术或正式文档

---

### 4. 链接信息 🔗

```python
result.links = {
    'internal': [...],  # 内部链接
    'external': [...]   # 外部链接
}
```

**统计**:
- 内部链接: 114个
- 外部链接: 21个

**链接格式**:
```json
{
  "text": "Politics",
  "href": "https://www.nbcnews.com/politics",
  "title": null
}
```

**示例**:
```python
# 前5个内部链接
1. NBC News Logo -> https://www.nbcnews.com
2. Politics -> https://www.nbcnews.com/politics
3. U.S. News -> https://www.nbcnews.com/us-news
4. World -> https://www.nbcnews.com/world
5. New York -> https://www.nbcnews.com/new-york
```

---

### 5. 媒体信息 🖼️

```python
result.media = {
    'images': [...],
    'videos': [...],
    'audios': [...]
}
```

**统计**:
- 图片: 333张
- 视频: 0个
- 音频: 0个

**图片格式**:
```json
{
  "src": "https://media-cldnry.s-nbcnews.com/image/upload/...",
  "alt": "Federal Reserve construction.",
  "width": null,
  "height": null
}
```

---

### 6. 元数据 📋

```python
result.metadata  # 字典格式
```

**包含的元数据**:
```json
{
  "title": "Business News: Reports and Video...",
  "description": "Find the latest news, videos...",
  "keywords": null,
  "author": null,
  
  // Open Graph
  "og:site_name": "NBC News",
  "og:locale": "en_US",
  "og:url": "https://www.nbcnews.com/business",
  "og:title": "Business News: Reports and Video...",
  "og:description": "Find the latest news...",
  "og:image": "https://media3.s-nbcnews.com/...",
  "og:type": "website",
  
  // Twitter Card
  "twitter:creator": "NBCNews",
  "twitter:site": "NBCNews",
  "twitter:title": "Business News: Reports...",
  "twitter:card": "summary_large_image",
  "twitter:image": "https://media3.s-nbcnews.com/..."
}
```

**用途**:
- 文章标题和描述
- SEO信息
- 社交媒体分享信息
- 作者和发布信息

---

### 7. 提取的内容 📦

```python
result.extracted_content  # 根据提取策略返回
```

**两种提取方式**:

#### 方式1: CSS选择器提取
```python
from crawl4ai import JsonCssExtractionStrategy

schema = {
    "name": "Articles",
    "baseSelector": "article",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "content", "selector": ".content", "type": "text"}
    ]
}

strategy = JsonCssExtractionStrategy(schema)
```

**返回格式**:
```json
[
  {
    "title": "Article Title 1",
    "content": "Article content..."
  },
  {
    "title": "Article Title 2",
    "content": "Article content..."
  }
]
```

#### 方式2: LLM驱动提取 ⭐
```python
from crawl4ai import LLMExtractionStrategy, LLMConfig
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    summary: str
    content: str
    published_at: str

strategy = LLMExtractionStrategy(
    llm_config=LLMConfig(provider="openai/gpt-4o-mini"),
    schema=Article.schema(),
    instruction="提取所有文章..."
)
```

**返回格式**:
```json
[
  {
    "title": "Article Title",
    "summary": "Article summary...",
    "content": "Full article content...",
    "published_at": "2026-04-15"
  }
]
```

---

### 8. 截图 📸

```python
result.screenshot  # Base64编码的图片数据
```

**启用方式**:
```python
config = CrawlerRunConfig(
    screenshot=True,
    screenshot_wait_for=2.0  # 等待2秒后截图
)
```

---

## 🎯 实际应用示例

### 示例1: 提取新闻列表

**输入**: 新闻网站首页  
**输出**: Markdown格式的新闻列表

```markdown
## LATEST BUSINESS NEWS

### Iran war
## U.S. military turns back ships amid hope for new peace talks

### Personal Finance
## 5 smart ways to spend your tax refund

### Iran war
## Oil prices might be starting to come down for a worrisome reason
```

**优点**:
- ✅ 自动格式化
- ✅ 保留标题层级
- ✅ 保留链接
- ✅ 去除广告和导航

---

### 示例2: 提取文章详情

**使用LLM提取**:
```python
class Article(BaseModel):
    title: str
    author: str
    published_date: str
    content: str
    tags: list[str]

# LLM自动理解页面结构，提取所需字段
```

**输出**:
```json
{
  "title": "5 smart ways to spend your tax refund",
  "author": "John Doe",
  "published_date": "2026-04-15",
  "content": "Full article text...",
  "tags": ["finance", "tax", "savings"]
}
```

**优点**:
- ✅ 不需要CSS选择器
- ✅ 自动适应网站变化
- ✅ 智能提取相关信息

---

## 📊 数据格式对比

### Scrapy vs Crawl4AI

| 数据类型 | Scrapy | Crawl4AI | 优势 |
|---------|--------|----------|------|
| HTML | ✅ response.text | ✅ result.html | 平手 |
| Markdown | ❌ 需要自己转换 | ✅ 自动生成 | Crawl4AI |
| 链接提取 | 🟡 需要手动提取 | ✅ 自动分类 | Crawl4AI |
| 媒体提取 | 🟡 需要手动提取 | ✅ 自动提取 | Crawl4AI |
| 元数据 | 🟡 需要手动提取 | ✅ 自动提取 | Crawl4AI |
| LLM提取 | ❌ 需要自己实现 | ✅ 原生支持 | Crawl4AI |

---

## 💡 最佳实践

### 1. 列表页爬取
**推荐**: 使用Markdown + 链接提取

```python
result = await crawler.arun(url)

# 方式1: 从Markdown提取
markdown = result.markdown.raw_markdown
# 解析Markdown中的标题和链接

# 方式2: 从links提取
for link in result.links['internal']:
    if 'article' in link['href']:
        article_urls.append(link['href'])
```

---

### 2. 详情页爬取
**推荐**: 使用LLM提取

```python
strategy = LLMExtractionStrategy(
    llm_config=LLMConfig(provider="openai/gpt-4o-mini"),
    schema=Article.schema(),
    instruction="提取文章的标题、作者、内容、发布时间"
)

result = await crawler.arun(url, config=CrawlerRunConfig(
    extraction_strategy=strategy
))

article = json.loads(result.extracted_content)
```

---

### 3. 混合方案（最佳）
**列表页**: Markdown + 链接  
**详情页**: LLM提取

```python
# 第1步: 爬取列表页
list_result = await crawler.arun(list_url)
article_urls = extract_urls_from_markdown(list_result.markdown)

# 第2步: 爬取详情页
for url in article_urls:
    detail_result = await crawler.arun(url, config=CrawlerRunConfig(
        extraction_strategy=llm_strategy
    ))
    save_article(detail_result.extracted_content)
```

---

## 🎉 总结

### Crawl4AI输出的核心优势

1. **✅ Markdown格式**
   - 自动转换HTML为Markdown
   - 保留结构和格式
   - 适合LLM处理

2. **✅ 结构化数据**
   - 自动提取链接、媒体、元数据
   - 分类清晰（内部/外部链接）
   - JSON格式，易于处理

3. **✅ LLM友好**
   - 原生支持LLM提取
   - 智能理解页面结构
   - 无需维护选择器

4. **✅ 完整信息**
   - HTML、Markdown、元数据一应俱全
   - 支持截图
   - 支持自定义提取

---

## 📁 测试文件

本次测试生成的文件：
- `crawler/test_output/raw_markdown.md` - 原始Markdown（32KB）
- `crawler/test_output/fit_markdown.md` - 过滤后的Markdown
- `crawler/test_output/page.html` - 完整HTML（2.4MB）
- `crawler/test_output/metadata.json` - 元数据
- `crawler/test_output/links.json` - 链接信息

---

**文档生成时间**: 2026-04-15 22:45  
**测试状态**: ✅ 成功  
**推荐使用**: ⭐⭐⭐⭐⭐
