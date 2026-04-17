# 爬虫使用指南

## 当前可用的爬虫

### Crawl4AI爬虫（1个）

#### 人民网 ✅
```bash
cd backend && source venv/bin/activate
cd ../crawler
python crawl4ai_peopledaily.py
```

**特点**：
- ✅ 自动日期检测（只抓取当日文章）
- ✅ 自动内容验证（过滤404、反爬、非详情页）
- ✅ 代码简洁（50行）
- ✅ 统一的日志输出

### Scrapy爬虫（12个）

#### 运行单个Scrapy爬虫
```bash
cd crawler
scrapy crawl <爬虫名称>
```

#### 可用的Scrapy爬虫列表

| 爬虫名称 | 网站 | 命令 |
|---------|------|------|
| `peopledaily` | 人民网 | `scrapy crawl peopledaily` |
| `nea` | 国家能源局 | `scrapy crawl nea` |
| `real_nea` | 国家能源局（真实） | `scrapy crawl real_nea` |
| `xinhua` | 新华网 | `scrapy crawl xinhua` |
| `xinhua_energy` | 新华网能源 | `scrapy crawl xinhua_energy` |
| `xinhua_real` | 新华网（真实） | `scrapy crawl xinhua_real` |
| `cnenergy` | 中国能源网 | `scrapy crawl cnenergy` |
| `ndrc` | 国家发改委 | `scrapy crawl ndrc` |
| `smm_metal` | 有色金属网 | `scrapy crawl smm_metal` |
| `cnmn_paper` | 中国有色金属报 | `scrapy crawl cnmn_paper` |
| `ccer` | 北京绿色交易所 | `scrapy crawl ccer` |
| `chinapower` | 中国电力网 | `scrapy crawl chinapower` |
| `power` | 北极星电力网 | `scrapy crawl power` |
| `coal` | 中国煤炭市场网 | `scrapy crawl coal` |
| `newenergy` | 中国新能源网 | `scrapy crawl newenergy` |

## 推荐使用方案

### 方案1：混合使用（推荐）

**简单网站** → Crawl4AI：
- 人民网：`python crawl4ai_peopledaily.py`

**复杂网站** → Scrapy：
- 国家能源局：`scrapy crawl nea`
- 新华网：`scrapy crawl xinhua_energy`
- 其他网站：使用对应的Scrapy爬虫

### 方案2：批量运行Scrapy爬虫

创建批量运行脚本 `crawler/run_all_scrapy.sh`：

```bash
#!/bin/bash

echo "开始批量运行Scrapy爬虫"

# 重要的爬虫
scrapy crawl nea
scrapy crawl xinhua_energy
scrapy crawl cnenergy
scrapy crawl ndrc

# 其他爬虫
scrapy crawl smm_metal
scrapy crawl cnmn_paper
scrapy crawl chinapower
scrapy crawl power
scrapy crawl coal
scrapy crawl newenergy

echo "批量运行完成"
```

使用方法：
```bash
cd crawler
chmod +x run_all_scrapy.sh
./run_all_scrapy.sh
```

## 日常使用

### 每日爬取流程

#### 1. 运行Crawl4AI爬虫（快速）
```bash
cd backend && source venv/bin/activate
cd ../crawler

# 人民网（自动过滤非当日文章）
python crawl4ai_peopledaily.py
```

#### 2. 运行重要的Scrapy爬虫
```bash
cd crawler

# 国家能源局（官方权威）
scrapy crawl nea

# 新华网（权威媒体）
scrapy crawl xinhua_energy

# 中国能源网（行业网站）
scrapy crawl cnenergy
```

#### 3. 查看爬取结果
```bash
# 使用MySQL命令行
/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql -h localhost -P 3306 -u root -pjinchun123 energy_station

# 查询今天的文章
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source
ORDER BY count DESC;

# 查看最新文章
SELECT id, title, source, DATE(published_at) as pub_date
FROM articles
ORDER BY created_at DESC
LIMIT 20;
```

## 定时任务设置

### 使用crontab设置每日自动爬取

```bash
# 编辑crontab
crontab -e

# 添加以下内容（每天早上8点运行）
0 8 * * * cd /path/to/mengxiaotan-website/backend && source venv/bin/activate && cd ../crawler && python crawl4ai_peopledaily.py >> /tmp/crawler.log 2>&1

# 每天早上8:30运行Scrapy爬虫
30 8 * * * cd /path/to/mengxiaotan-website/crawler && scrapy crawl nea >> /tmp/scrapy.log 2>&1
30 8 * * * cd /path/to/mengxiaotan-website/crawler && scrapy crawl xinhua_energy >> /tmp/scrapy.log 2>&1
```

### 或者创建定时脚本

创建 `crawler/daily_crawl.sh`：

```bash
#!/bin/bash

# 每日爬取脚本
LOG_FILE="/tmp/daily_crawl_$(date +%Y%m%d).log"

echo "开始每日爬取 - $(date)" >> $LOG_FILE

# 激活虚拟环境
cd /path/to/mengxiaotan-website/backend
source venv/bin/activate

# 运行Crawl4AI爬虫
cd ../crawler
echo "运行人民网爬虫..." >> $LOG_FILE
python crawl4ai_peopledaily.py >> $LOG_FILE 2>&1

# 运行Scrapy爬虫
echo "运行国家能源局爬虫..." >> $LOG_FILE
scrapy crawl nea >> $LOG_FILE 2>&1

echo "运行新华网爬虫..." >> $LOG_FILE
scrapy crawl xinhua_energy >> $LOG_FILE 2>&1

echo "运行中国能源网爬虫..." >> $LOG_FILE
scrapy crawl cnenergy >> $LOG_FILE 2>&1

echo "每日爬取完成 - $(date)" >> $LOG_FILE
```

然后在crontab中添加：
```bash
0 8 * * * /path/to/mengxiaotan-website/crawler/daily_crawl.sh
```

## 监控和维护

### 查看爬取日志
```bash
# Crawl4AI日志（输出到终端）
cd crawler
python crawl4ai_peopledaily.py

# Scrapy日志
cd crawler
scrapy crawl nea 2>&1 | tee scrapy_nea.log
```

### 检查数据库
```sql
-- 查看今天各来源的文章数量
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source
ORDER BY count DESC;

-- 查看最近7天的文章数量趋势
SELECT DATE(created_at) as date, COUNT(*) as count
FROM articles
WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 查看各来源的总文章数
SELECT source, COUNT(*) as total
FROM articles
GROUP BY source
ORDER BY total DESC;
```

### 常见问题

#### 1. Crawl4AI导入失败
```bash
cd backend
source venv/bin/activate
pip install crawl4ai pytz
```

#### 2. Scrapy爬虫失败
```bash
cd crawler
pip install -r requirements.txt
```

#### 3. 数据库连接失败
检查MySQL是否运行：
```bash
/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql -h localhost -P 3306 -u root -pjinchun123 -e "SELECT 1"
```

#### 4. 爬虫没有抓取到文章
- 检查网站是否可访问
- 查看爬虫日志中的错误信息
- 网站结构可能已变化，需要更新选择器

## 性能优化

### Crawl4AI优化
```python
# 在crawl4ai_base.py中调整并发数
# 目前每个爬虫串行执行，可以考虑并发
```

### Scrapy优化
```python
# 在crawler/energy_crawler/settings.py中调整
CONCURRENT_REQUESTS = 16  # 并发请求数
DOWNLOAD_DELAY = 1  # 下载延迟（秒）
```

## 添加新爬虫

### 添加Crawl4AI爬虫

1. 使用分析工具查看网站结构：
```bash
cd crawler
python analyze_website.py <网站URL>
```

2. 创建新爬虫文件：
```python
# crawler/crawl4ai_newsite.py
from crawl4ai_base import Crawl4AIBase

class NewSiteCrawler(Crawl4AIBase):
    def __init__(self):
        super().__init__(
            source_name="网站名称",
            base_url="网站URL",
            category="分类"
        )
        
        self.list_schema = {
            "baseSelector": "实际的选择器",
            "fields": [...]
        }
        
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

3. 测试：
```bash
python crawl4ai_newsite.py
```

### 添加Scrapy爬虫

参考现有的Scrapy爬虫，在 `crawler/energy_crawler/spiders/` 目录下创建新文件。

## 总结

### 推荐的日常流程

1. **每天早上8点** - 自动运行定时任务
2. **查看结果** - 检查数据库中的新文章
3. **手动补充** - 如果某个爬虫失败，手动运行
4. **定期维护** - 每周检查爬虫状态，更新失效的选择器

### 优先级

**高优先级**（每天必跑）：
- 人民网（Crawl4AI）
- 国家能源局（Scrapy）
- 新华网（Scrapy）

**中优先级**（每周2-3次）：
- 中国能源网
- 国家发改委
- 有色金属网

**低优先级**（按需运行）：
- 其他行业网站

---

**更新时间**: 2026-04-16  
**可用爬虫**: 1个Crawl4AI + 12个Scrapy  
**推荐方案**: 混合使用
