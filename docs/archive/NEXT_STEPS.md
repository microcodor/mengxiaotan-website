# 下一步工作计划

**更新时间**: 2026-04-10 23:25  
**当前状态**: 已完成测试，3个爬虫正常工作

---

## ✅ 已完成工作

### 1. 系统测试
- ✅ 测试了所有12个爬虫
- ✅ 验证了3个爬虫正常工作
- ✅ 识别了6个需要修复的爬虫
- ✅ 创建了详细的测试报告

### 2. 正常工作的爬虫（3个）
1. **xinhua_real** - 新华网能源（17篇/次）
2. **chinapower** - 中国电力网（30+篇/次）
3. **nea** - 国家能源局测试版（3篇/次）

**当前能力**:
- 单次抓取：50+篇
- 每日3次：150+篇
- 总字数：约450,000-600,000字/天

### 3. 文档完善
- ✅ CRAWLER_SITES_CONFIG.md - 网站配置清单
- ✅ CRAWLER_TECH_SUMMARY.md - 技术方案总结
- ✅ TEST_ALL_CRAWLERS.md - 测试指南
- ✅ CRAWLER_STATUS_FINAL.md - 最终状态报告
- ✅ CRAWLER_TEST_RESULTS.md - 测试结果报告
- ✅ NEXT_STEPS.md - 下一步计划（本文档）

---

## 🔧 需要修复的爬虫（6个）

### 问题诊断

所有6个爬虫都是因为**选择器失效**或**URL配置错误**导致无法抓取数据。

| 爬虫 | 网站 | 问题 | 优先级 |
|------|------|------|--------|
| power | 北极星电力网 | 选择器失效 | ⭐⭐⭐ 高 |
| ndrc | 国家发改委 | 选择器失效 | ⭐⭐⭐ 高 |
| peopledaily | 人民网能源 | 选择器失效 | ⭐⭐⭐ 高 |
| coal | 中国煤炭网 | URL 404错误 | ⭐⭐ 中 |
| newenergy | 中国新能源网 | 选择器失效 | ⭐⭐ 中 |
| cnenergy | 中国能源网 | 选择器失效 | ⭐⭐ 中 |

### 修复方法

#### 方法1：手动修复（推荐）

对每个爬虫：
1. 访问目标网站
2. 使用浏览器开发者工具（F12）
3. 找到文章列表的HTML结构
4. 更新CSS选择器
5. 测试验证

#### 方法2：使用Playwright（备选）

如果网站使用JavaScript渲染，考虑：
1. 将爬虫改为Playwright版本
2. 参考`real_nea_spider.py`的实现
3. 测试验证

---

## 📋 详细修复计划

### 第一优先级：高价值爬虫（本周）

#### 1. power - 北极星电力网

**网站**: https://news.bjx.com.cn/list/power.html  
**问题**: 选择器失效  
**预期数量**: 20-30篇/次

**修复步骤**:
```bash
# 1. 访问网站，查看HTML结构
curl https://news.bjx.com.cn/list/power.html | head -200

# 2. 使用浏览器开发者工具找到正确的选择器

# 3. 更新爬虫文件
# crawler/energy_crawler/spiders/power_spider.py

# 4. 测试
scrapy crawl power -s LOG_LEVEL=INFO
```

**预计耗时**: 30分钟

---

#### 2. ndrc - 国家发改委

**网站**: https://www.ndrc.gov.cn/fggz/fgzy/  
**问题**: 选择器失效  
**预期数量**: 10-15篇/次

**修复步骤**:
```bash
# 1. 访问网站
curl https://www.ndrc.gov.cn/fggz/fgzy/ | head -200

# 2. 找到正确的选择器

# 3. 更新爬虫文件
# crawler/energy_crawler/spiders/ndrc_spider.py

# 4. 测试
scrapy crawl ndrc -s LOG_LEVEL=INFO
```

**预计耗时**: 30分钟

---

#### 3. peopledaily - 人民网能源

**网站**: http://energy.people.com.cn/  
**问题**: 选择器失效  
**预期数量**: 15-20篇/次

**修复步骤**:
```bash
# 1. 访问网站
curl http://energy.people.com.cn/ | head -200

# 2. 找到正确的选择器

# 3. 更新爬虫文件
# crawler/energy_crawler/spiders/peopledaily_spider.py

# 4. 测试
scrapy crawl peopledaily -s LOG_LEVEL=INFO
```

**预计耗时**: 30分钟

---

### 第二优先级：行业网站（本周）

#### 4. coal - 中国煤炭网

**网站**: https://www.cctd.com.cn/  
**问题**: URL 404错误  
**预期数量**: 10-15篇/次

**修复步骤**:
```bash
# 1. 找到正确的新闻列表URL
# 主页: https://www.cctd.com.cn/
# 可能的URL:
# - https://www.cctd.com.cn/news/
# - https://www.cctd.com.cn/article/

# 2. 更新start_urls

# 3. 测试
scrapy crawl coal -s LOG_LEVEL=INFO
```

**预计耗时**: 20分钟

---

#### 5. newenergy - 中国新能源网

**网站**: https://www.china-nengyuan.com/  
**问题**: 选择器失效  
**预期数量**: 10-15篇/次

**修复步骤**:
```bash
# 1. 访问网站
curl https://www.china-nengyuan.com/ | head -200

# 2. 找到正确的选择器

# 3. 更新爬虫文件
# crawler/energy_crawler/spiders/newenergy_spider.py

# 4. 测试
scrapy crawl newenergy -s LOG_LEVEL=INFO
```

**预计耗时**: 20分钟

---

#### 6. cnenergy - 中国能源网

**网站**: http://www.cnenergy.org/  
**问题**: 选择器失效或网站不可用  
**预期数量**: 10-15篇/次

**修复步骤**:
```bash
# 1. 检查网站是否可访问
curl -I http://www.cnenergy.org/

# 2. 如果404，寻找新的URL或替代网站

# 3. 更新爬虫配置

# 4. 测试
scrapy crawl cnenergy -s LOG_LEVEL=INFO
```

**预计耗时**: 20分钟

---

## 📅 时间计划

### 本周（2026-04-10 至 2026-04-16）

**Day 1-2**: 修复高优先级爬虫
- [ ] power - 北极星电力网
- [ ] ndrc - 国家发改委
- [ ] peopledaily - 人民网能源

**Day 3-4**: 修复中优先级爬虫
- [ ] coal - 中国煤炭网
- [ ] newenergy - 中国新能源网
- [ ] cnenergy - 中国能源网

**Day 5**: 测试和验证
- [ ] 测试所有修复的爬虫
- [ ] 验证数据质量
- [ ] 更新文档

**Day 6-7**: 配置定时任务
- [ ] 设置每天3次自动运行
- [ ] 配置运行时间（6:00, 12:00, 18:00）
- [ ] 测试定时任务

---

## 🎯 预期成果

### 修复完成后的系统能力

**数据源**: 9个正常工作的爬虫

**单次运行**:
- 抓取数量：150-200篇
- 总字数：300,000-400,000字
- 耗时：20-30分钟

**每日运行3次**:
- 抓取数量：450-600篇
- 总字数：900,000-1,200,000字
- 总耗时：约1-1.5小时

**每月累计**:
- 抓取数量：13,500-18,000篇
- 总字数：27,000,000-36,000,000字

---

## 🔍 修复示例

### 示例：修复power爬虫

#### 1. 访问网站，查看HTML结构

```bash
# 使用curl获取HTML
curl https://news.bjx.com.cn/list/power.html > power_page.html

# 或使用浏览器开发者工具（推荐）
# 1. 打开 https://news.bjx.com.cn/list/power.html
# 2. 按F12打开开发者工具
# 3. 点击Elements标签
# 4. 找到文章列表的HTML结构
```

#### 2. 找到正确的选择器

假设HTML结构如下：
```html
<div class="news-list">
  <div class="news-item">
    <a href="/article/123.html">文章标题</a>
    <span class="date">2026-04-10</span>
  </div>
</div>
```

正确的选择器应该是：
```python
articles = response.css('div.news-item')
title = article.css('a::text').get()
url = article.css('a::attr(href)').get()
date_str = article.css('span.date::text').get()
```

#### 3. 更新爬虫文件

```python
# crawler/energy_crawler/spiders/power_spider.py

def parse(self, response):
    # 更新选择器
    articles = response.css('div.news-item')  # 新选择器
    
    for article in articles:
        title = article.css('a::text').get()
        url = article.css('a::attr(href)').get()
        date_str = article.css('span.date::text').get()
        
        # ... 其余代码保持不变
```

#### 4. 测试验证

```bash
# 运行爬虫
scrapy crawl power -s LOG_LEVEL=INFO

# 检查输出
# 应该看到类似：
# [power] INFO: 找到文章 1: xxx
# [power] INFO: 找到文章 2: xxx
# ...
# [power] INFO: ✅ 成功抓取: xxx (内容长度: xxx)
```

---

## 📊 成功标准

### 每个爬虫修复后应满足：

1. **抓取数量**: 至少5篇文章
2. **内容质量**: 
   - 标题完整（10-100字）
   - 正文完整（>100字）
   - 来源正确
3. **成功率**: >80%
4. **性能**: <5分钟

---

## 🚀 快速开始

### 立即开始修复

```bash
# 1. 进入项目目录
cd /path/to/mengxiaotan-website

# 2. 激活虚拟环境
source backend/venv/bin/activate

# 3. 进入爬虫目录
cd crawler

# 4. 选择一个爬虫开始修复
# 例如：修复power爬虫

# 5. 编辑爬虫文件
vim energy_crawler/spiders/power_spider.py

# 6. 测试
scrapy crawl power -s LOG_LEVEL=INFO

# 7. 如果成功，继续下一个
```

---

## 📝 修复记录模板

### 爬虫修复记录

**爬虫名称**: _______________  
**修复日期**: _______________  
**修复人员**: _______________

**问题描述**:
```
（描述发现的问题）
```

**解决方案**:
```
（描述如何解决）
```

**修改内容**:
```python
# 修改前
old_selector = 'div.old-class'

# 修改后
new_selector = 'div.new-class'
```

**测试结果**:
- 抓取数量: _____ 篇
- 成功率: _____ %
- 耗时: _____ 秒

**状态**: ✅ 成功 / ⚠️  部分成功 / ❌ 失败

---

## 💡 提示和技巧

### 1. 使用浏览器开发者工具

最有效的方法是使用浏览器开发者工具：
1. 打开目标网站
2. 按F12打开开发者工具
3. 点击Elements标签
4. 使用选择器工具（左上角箭头图标）
5. 点击页面上的文章标题
6. 查看HTML结构
7. 复制CSS选择器

### 2. 测试选择器

在Scrapy Shell中测试选择器：
```bash
scrapy shell "https://website.com"

# 在shell中测试
>>> response.css('div.news-item').getall()
>>> response.css('div.news-item a::text').getall()
```

### 3. 处理JavaScript渲染

如果网站使用JavaScript渲染，选择器可能找不到内容：
```bash
# 检查是否需要JavaScript
curl https://website.com | grep "文章标题"

# 如果找不到，说明需要JavaScript渲染
# 考虑使用Playwright
```

### 4. 处理编码问题

如果出现乱码：
```python
# 在parse方法开始处添加
response = response.replace(encoding='utf-8')
# 或
response = response.replace(encoding='gbk')
```

---

## 📞 需要帮助？

如果遇到问题，可以：
1. 查看文档：CRAWLER_SITES_CONFIG.md
2. 查看示例：xinhua_real_spider.py, chinapower_spider.py
3. 查看测试报告：CRAWLER_TEST_RESULTS.md

---

**文档版本**: v1.0  
**最后更新**: 2026-04-10 23:25

