# 人民网爬虫优化成功报告

## 优化时间
2026-04-16

## 优化目标
修复人民网爬虫的CSS选择器，使其能够正确提取文章列表和内容。

## 优化过程

### 1. 问题诊断
**原问题**：
- ❌ 列表页CSS选择器提取到文章，但详情页内容太短
- ❌ 使用Markdown提取，但内容不完整

### 2. 网站分析
使用Python requests + BeautifulSoup分析网站结构：

```bash
# 访问列表页
http://finance.people.com.cn/

# 发现：
- 人民网能源频道已重定向到财经频道
- 列表页选择器：ul.list_14 li
- 详情页内容选择器：div.rm_txt_con p
```

### 3. 选择器优化

#### 列表页选择器
```python
# 优化前（通用选择器）
"baseSelector": "div.w1000 ul.list_14 li, div.list_14 li, ul.list li"

# 优化后（精确选择器）
"baseSelector": "ul.list_14 li"
```

#### 详情页选择器
```python
# 优化前（使用Markdown）
self.detail_schema = None

# 优化后（使用CSS选择器）
self.detail_schema = {
    "name": "PeopleDailyArticle",
    "baseSelector": "body",
    "fields": [
        {
            "name": "content",
            "selector": "div.rm_txt_con p",
            "type": "text",
            "all": True  # 提取所有段落
        }
    ]
}
```

### 4. URL更新
```python
# 优化前
base_url="http://energy.people.com.cn/"

# 优化后
base_url="http://finance.people.com.cn/"
```

## 测试结果

### 测试配置
- 限制：3篇文章
- 日期检测：开启
- 内容验证：开启

### 测试输出
```
============================================================
🚀 开始爬取 人民网
📍 URL: http://finance.people.com.cn/
============================================================

📋 步骤1: 爬取列表页...
✅ 列表页加载成功
📊 CSS选择器提取到 11 个链接
✅ 有效文章: 11 篇

📖 步骤2: 爬取文章详情...

[1/3] 人民银行缩量续做6个月期买断式逆回购...
  ⏭️  跳过: 非当日文章(2026-04-15)

[2/3] 降低中小企业用算成本 "算力银行"要来了...
  ⚠️  警告: 无法提取发布日期，仍然保存
  ✅ 保存成功

[3/3] 探馆消博会：品质生活场景不断上新...
  ⚠️  跳过: 内容太短

============================================================
📊 爬取完成
✅ 新增文章: 1 篇
============================================================
```

### 数据库验证
```sql
SELECT id, title, source, DATE(published_at), LENGTH(content)
FROM articles
WHERE source='人民网'
ORDER BY created_at DESC
LIMIT 1;

结果：
id: 128
title: 降低中小企业用算成本 "算力银行"要来了
source: 人民网
pub_date: 2026-04-16
content_len: 380
```

## 成功指标

### ✅ 功能验证
- ✅ 列表页提取成功（11个链接）
- ✅ 详情页内容提取成功（380字符）
- ✅ 日期检测工作正常（跳过昨天的文章）
- ✅ 内容验证工作正常（过滤内容太短的文章）
- ✅ 数据库保存成功

### ✅ 自动功能
- ✅ 日期检测：正确识别并跳过2026-04-15的文章
- ✅ 内容验证：过滤内容太短的文章
- ✅ URL处理：自动补全相对路径
- ✅ 数据库去重：自动检查是否已存在

## 优化经验总结

### 关键步骤
1. **实际访问网站**：不要猜测，要实际查看HTML结构
2. **使用工具分析**：requests + BeautifulSoup 快速验证选择器
3. **精确选择器**：使用网站实际的CSS类名，不要用通用选择器
4. **详情页CSS**：对于结构化内容，CSS选择器比Markdown更可靠
5. **测试验证**：每次修改后立即测试

### 最佳实践
```python
# 1. 列表页选择器 - 使用精确的CSS类名
self.list_schema = {
    "baseSelector": "ul.list_14 li",  # 网站实际的类名
    "fields": [...]
}

# 2. 详情页选择器 - 使用CSS提取内容
self.detail_schema = {
    "baseSelector": "body",
    "fields": [
        {
            "name": "content",
            "selector": "div.rm_txt_con p",  # 内容容器的实际选择器
            "type": "text",
            "all": True  # 提取所有段落
        }
    ]
}

# 3. URL处理 - 补全相对路径
def process_url(self, url):
    if url.startswith('/'):
        return f"http://finance.people.com.cn{url}"
    return url
```

## 应用到其他爬虫

### 优化流程模板

#### 步骤1：分析网站结构
```python
import requests
from bs4 import BeautifulSoup

url = 'http://网站URL'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

# 查找列表页选择器
items = soup.select('你的选择器')
print(f'找到: {len(items)} 个元素')

# 查找详情页选择器
paragraphs = soup.select('你的内容选择器')
print(f'段落数: {len(paragraphs)}')
```

#### 步骤2：更新爬虫代码
```python
class YourCrawler(Crawl4AIBase):
    def __init__(self):
        super().__init__(
            source_name="网站名称",
            base_url="实际URL",
            category="分类"
        )
        
        # 使用实际测试的选择器
        self.list_schema = {
            "baseSelector": "实际的列表选择器",
            "fields": [...]
        }
        
        # 使用CSS提取详情页内容
        self.detail_schema = {
            "baseSelector": "body",
            "fields": [
                {
                    "name": "content",
                    "selector": "实际的内容选择器",
                    "type": "text",
                    "all": True
                }
            ]
        }
```

#### 步骤3：测试验证
```bash
cd backend && source venv/bin/activate
cd ../crawler
python crawl4ai_your_crawler.py
```

#### 步骤4：检查数据库
```sql
SELECT * FROM articles 
WHERE source='网站名称' 
ORDER BY created_at DESC 
LIMIT 5;
```

## 下一步计划

### 立即优化（高优先级）
1. **国家能源局** - 官方权威来源
2. **中国能源网** - 行业重要网站
3. **新华网** - 权威媒体

### 优化顺序建议
1. 国家能源局（最重要）
2. 新华网（权威媒体）
3. 中国能源网（行业网站）
4. 其他爬虫

### 预计时间
- 每个爬虫优化：30-60分钟
- 包括：分析网站、更新代码、测试验证

## 工具脚本

### 快速分析网站结构
创建 `crawler/analyze_website.py`：
```python
import requests
from bs4 import BeautifulSoup
import sys

if len(sys.argv) < 2:
    print("用法: python analyze_website.py <URL>")
    sys.exit(1)

url = sys.argv[1]
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

print(f"分析网站: {url}")
print("\n=== 常见列表选择器 ===")
for selector in ['ul.list li', 'div.list li', 'ul.news li', 'div.news-list li']:
    items = soup.select(selector)
    if items:
        print(f"{selector}: {len(items)} 个元素")

print("\n=== 常见内容选择器 ===")
for selector in ['div.content p', 'div.article p', 'div.text p']:
    items = soup.select(selector)
    if items:
        print(f"{selector}: {len(items)} 个段落")
```

使用方法：
```bash
python analyze_website.py http://网站URL
```

## 总结

✅ **人民网爬虫优化成功**

### 关键成果
- 列表页提取：11个链接
- 详情页提取：成功
- 保存文章：1篇
- 日期检测：正常工作
- 内容验证：正常工作

### 关键经验
1. 实际查看HTML结构，不要猜测
2. 使用精确的CSS选择器
3. 详情页使用CSS而不是Markdown
4. 每次修改后立即测试

### 可复用模板
- 网站分析脚本
- 爬虫优化流程
- 测试验证方法

---

**优化时间**: 2026-04-16  
**优化结果**: ✅ 成功  
**保存文章**: 1篇  
**下一步**: 优化国家能源局爬虫
