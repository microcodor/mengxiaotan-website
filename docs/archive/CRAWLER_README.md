# 爬虫系统使用说明

## 快速开始

### 运行单个爬虫

#### Crawl4AI爬虫（推荐用于简单网站）
```bash
cd backend && source venv/bin/activate
cd ../crawler
python crawl4ai_peopledaily.py
```

#### Scrapy爬虫（推荐用于复杂网站）
```bash
cd crawler
scrapy crawl nea
```

### 批量运行
```bash
cd crawler
./daily_crawl.sh
```

## 可用的爬虫

### Crawl4AI爬虫（1个）
- ✅ **人民网** - 自动日期检测，自动内容验证

### Scrapy爬虫（12个）
- 国家能源局、新华网、中国能源网、国家发改委等

详见：`CRAWLER_USAGE_GUIDE.md`

## 核心功能

### 自动日期检测
- 只抓取当日文章
- 使用中国时区
- 支持6种日期格式

### 自动内容验证
- 过滤404页面
- 过滤反爬验证页面
- 过滤非详情页
- 过滤内容太短的文章

### 统一日志
- 清晰的爬取进度
- 详细的错误信息
- 保存结果统计

## 设置定时任务

```bash
# 编辑crontab
crontab -e

# 每天早上8点运行
0 8 * * * /path/to/mengxiaotan-website/crawler/daily_crawl.sh
```

## 查看结果

```bash
# 连接数据库
/usr/local/mysql-8.0.33-macos13-arm64/bin/mysql -h localhost -P 3306 -u root -pjinchun123 energy_station

# 查询今天的文章
SELECT source, COUNT(*) as count
FROM articles
WHERE DATE(created_at) = CURDATE()
GROUP BY source;
```

## 文档

- `CRAWLER_USAGE_GUIDE.md` - 详细使用指南
- `CRAWLER_PROJECT_SUMMARY.md` - 项目总结
- `CRAWLER_FINAL_STATUS.md` - 最终状态报告

## 工具

- `analyze_website.py` - 网站结构分析工具
- `run_all_scrapy.sh` - 批量运行Scrapy爬虫
- `daily_crawl.sh` - 每日爬取脚本

## 支持

如有问题，请查看相关文档或联系开发人员。

---

**更新时间**: 2026-04-16  
**状态**: ✅ 可投入使用
