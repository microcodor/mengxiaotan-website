# 爬虫内容提取优化 - 快速开始

## 🎯 问题解决

**问题**: 爬虫抓取的内容包含导航栏、侧边栏、广告等无关内容

**解决**: 使用trafilatura智能提取库,自动识别和提取正文

**状态**: ✅ 已完成核心功能,可以部署使用

## 🚀 快速部署

### 1. 安装依赖

```bash
cd backend
source venv/bin/activate
pip install trafilatura==1.12.2
```

### 2. 测试爬虫

```bash
cd ../crawler

# 测试新华网爬虫
../backend/venv/bin/scrapy crawl xinhua_real -s LOG_LEVEL=INFO

# 测试中国电力网爬虫
../backend/venv/bin/scrapy crawl chinapower -s LOG_LEVEL=INFO
```

### 3. 通过API运行

```bash
# 启动后端服务
cd backend
python run_production.py

# 在另一个终端运行爬虫
curl -X POST http://localhost:5001/api/crawler/spiders/xinhua_real/run \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json"
```

## 📊 效果对比

### 优化前
```
首页 | 关于我们 | 联系我们
热门文章
- 推荐1
- 推荐2
这是文章的正文内容...
版权所有 © 2024
备案号: 京ICP备12345678号
```

### 优化后
```
这是文章的正文内容...
```

## ✅ 已优化的爬虫

1. **xinhua_real** - 新华网能源 ✅
2. **chinapower** - 中国电力网 ✅

## ⏳ 待优化的爬虫

3. power - 北极星电力网
4. ndrc - 国家发改委
5. energy_news - 综合能源新闻
6. peopledaily - 人民网能源
7. coal - 中国煤炭网
8. newenergy - 中国新能源网
9. cnenergy - 中国能源网
10. ccer - CCER碳交易
11. mysteel - 我的钢铁网
12. cnmn_paper - 中国有色金属报
13. smm_metal - 上海有色金属网
14. nea - 国家能源局(测试版)
15. real_nea - 国家能源局(真实)

## 📖 详细文档

- **CRAWLER_CONTENT_EXTRACTION_UPGRADE.md** - 技术实现详解
- **CRAWLER_OPTIMIZATION_SUMMARY.md** - 优化方案总览
- **CRAWLER_CONTENT_EXTRACTION_COMPLETE.md** - 完成报告

## 🔍 验证方法

### 检查内容质量

```sql
-- 查看最近抓取的文章
SELECT id, title, source, LENGTH(content) as len, created_at
FROM articles
WHERE source IN ('新华网', '中国电力网')
ORDER BY created_at DESC
LIMIT 10;

-- 检查是否包含无关内容
SELECT id, title, source
FROM articles
WHERE source IN ('新华网', '中国电力网')
  AND (content LIKE '%首页%' OR content LIKE '%返回%')
ORDER BY created_at DESC;
```

### 预期结果

- ✅ 内容长度在 500-10000 字之间
- ✅ 不包含"首页"、"返回"、"版权所有"等导航文本
- ✅ 文章段落完整,没有被截断

## 💡 使用建议

1. **先测试**: 在生产环境部署前,先在测试环境运行
2. **监控日志**: 关注爬虫日志,确保提取成功
3. **抽查内容**: 人工抽查几篇文章,确认质量
4. **逐步推广**: 先部署2个已优化的爬虫,稳定后再优化其他

## 🆘 遇到问题?

### 提取失败

**检查**:
1. 网页是否需要JavaScript渲染?
2. CSS选择器是否正确?
3. 内容是否在iframe中?

**解决**:
- 查看日志中的错误信息
- 检查网页源代码
- 调整CSS选择器

### 内容不完整

**检查**:
1. 是否有分页?
2. 是否需要点击"展开"?
3. 是否有反爬虫限制?

**解决**:
- 处理分页逻辑
- 使用Playwright模拟点击
- 调整请求延迟

## 📞 联系方式

如有问题,请查看详细文档或联系开发团队。

---

**更新时间**: 2026-04-16
**状态**: ✅ 可以部署使用
