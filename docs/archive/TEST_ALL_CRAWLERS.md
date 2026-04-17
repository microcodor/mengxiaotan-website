# 爬虫测试指南

## 🎯 快速测试所有爬虫

**更新时间**: 2026-04-10

---

## 📋 测试清单

### ✅ 已测试通过（2个）

- [x] xinhua_real - 新华网能源（17篇，51,000字）
- [x] chinapower - 中国电力网（37篇，177,244字）

### 🔄 待测试（9个Scrapy爬虫）

- [ ] power - 北极星电力网
- [ ] ndrc - 国家发改委
- [ ] peopledaily - 人民网能源
- [ ] coal - 中国煤炭网
- [ ] newenergy - 中国新能源网
- [ ] cnenergy - 中国能源网
- [ ] energy_news - 综合能源新闻
- [ ] nea - 国家能源局（测试版）
- [ ] test - 测试爬虫

### ⚠️ 需要优化（1个Playwright爬虫）

- [ ] real_nea - 国家能源局（真实版，Playwright）

---

## 🚀 测试方法

### 方法1：通过管理后台（推荐）

1. 启动服务：
```bash
docker-compose up -d
```

2. 访问管理后台：
```
http://localhost:3000/admin/crawler
```

3. 登录管理员账号：
```
手机号：13800138000
密码：admin123
```

4. 点击每个爬虫的"运行"按钮

5. 查看日志和结果

---

### 方法2：通过命令行

```bash
# 进入爬虫目录
cd crawler

# 测试单个爬虫
scrapy crawl xinhua_real
scrapy crawl chinapower
scrapy crawl power
scrapy crawl ndrc
scrapy crawl peopledaily
scrapy crawl coal
scrapy crawl newenergy
scrapy crawl cnenergy
scrapy crawl energy_news
scrapy crawl nea
scrapy crawl test

# Playwright爬虫（需要更长时间）
scrapy crawl real_nea
```

---

### 方法3：批量测试脚本

创建测试脚本 `test_all.sh`:

```bash
#!/bin/bash

# 爬虫列表
spiders=(
    "xinhua_real"
    "chinapower"
    "power"
    "ndrc"
    "peopledaily"
    "coal"
    "newenergy"
    "cnenergy"
    "energy_news"
    "nea"
    "test"
)

# 进入爬虫目录
cd crawler

# 测试每个爬虫
for spider in "${spiders[@]}"
do
    echo "=========================================="
    echo "测试爬虫: $spider"
    echo "=========================================="
    
    scrapy crawl $spider
    
    echo ""
    echo "完成: $spider"
    echo ""
    
    # 等待5秒
    sleep 5
done

echo "=========================================="
echo "所有爬虫测试完成！"
echo "=========================================="
```

运行脚本：
```bash
chmod +x test_all.sh
./test_all.sh
```

---

## 📊 测试评估标准

### 成功标准

✅ **抓取数量**: 
- 每个爬虫至少抓取5篇文章
- 推荐：10-30篇

✅ **内容质量**:
- 标题完整（10-100字）
- 正文完整（>100字）
- 来源正确
- 时间有效

✅ **成功率**:
- 成功率 > 80%
- 错误率 < 20%

✅ **性能**:
- Scrapy爬虫：< 5分钟
- Playwright爬虫：< 15分钟

### 失败标准

❌ **抓取失败**:
- 抓取数量 = 0
- 全部请求失败

❌ **内容质量差**:
- 标题为空
- 正文太短（<100字）
- 乱码

❌ **性能差**:
- Scrapy爬虫：> 10分钟
- Playwright爬虫：> 30分钟

---

## 🔍 检查结果

### 1. 查看日志

**Docker日志**:
```bash
docker-compose logs -f backend
```

**Scrapy日志**:
```bash
cd crawler
scrapy crawl xinhua_real 2>&1 | tee xinhua_real.log
```

### 2. 查看数据库

```bash
# 进入MySQL容器
docker-compose exec mysql mysql -u root -prootpassword energy_platform

# 查询文章数量
SELECT source, COUNT(*) as count 
FROM articles 
GROUP BY source 
ORDER BY count DESC;

# 查询最新文章
SELECT id, title, source, created_at 
FROM articles 
ORDER BY created_at DESC 
LIMIT 10;

# 查询今日文章
SELECT source, COUNT(*) as count 
FROM articles 
WHERE DATE(created_at) = CURDATE() 
GROUP BY source;
```

### 3. 查看API

```bash
# 获取爬虫列表
curl http://localhost:5001/api/crawler/spiders

# 获取爬虫统计
curl http://localhost:5001/api/crawler/stats

# 获取爬取日志
curl http://localhost:5001/api/crawler/logs
```

---

## 📝 测试记录模板

### 爬虫测试记录

**爬虫名称**: _______________

**测试时间**: _______________

**测试结果**:
- [ ] 成功
- [ ] 失败
- [ ] 部分成功

**抓取数量**: _____ 篇

**平均长度**: _____ 字

**总字数**: _____ 字

**耗时**: _____ 分钟

**成功率**: _____ %

**问题描述**:
```
（如有问题，请详细描述）
```

**解决方案**:
```
（如有问题，请记录解决方案）
```

---

## 🐛 常见问题

### 问题1：连接超时

**症状**: `TimeoutError` 或 `Connection timeout`

**原因**:
- 网站响应慢
- 网络问题
- 反爬虫限制

**解决方案**:
```python
# 增加超时时间
custom_settings = {
    'DOWNLOAD_TIMEOUT': 30,  # 30秒
}
```

### 问题2：选择器失效

**症状**: 抓取数量为0，或内容为空

**原因**:
- 网站改版
- 选择器错误
- JavaScript渲染

**解决方案**:
1. 访问网站，检查HTML结构
2. 更新选择器
3. 如需JavaScript，考虑使用Playwright

### 问题3：编码错误

**症状**: 中文乱码

**原因**:
- 网站使用GBK/GB2312编码

**解决方案**:
```python
response = response.replace(encoding='utf-8')
```

### 问题4：反爬虫限制

**症状**: 403 Forbidden 或 429 Too Many Requests

**原因**:
- 请求频率过高
- User-Agent被识别

**解决方案**:
```python
custom_settings = {
    'DOWNLOAD_DELAY': 3,  # 增加延迟
    'CONCURRENT_REQUESTS': 2,  # 降低并发
}
```

### 问题5：Playwright失败

**症状**: Playwright爬虫无法启动

**原因**:
- Chromium未安装
- 权限问题

**解决方案**:
```bash
# 重新安装Playwright
pip install playwright
playwright install chromium

# 检查权限
chmod +x /path/to/chromium
```

---

## 📈 测试报告模板

### 爬虫系统测试报告

**测试日期**: 2026-04-10

**测试人员**: _______________

**测试环境**:
- 操作系统: macOS
- Python版本: 3.9+
- Scrapy版本: 2.11+
- Playwright版本: 1.40+

**测试结果汇总**:

| 爬虫名称 | 状态 | 数量 | 字数 | 耗时 | 成功率 |
|---------|------|------|------|------|--------|
| xinhua_real | ✅ | 17 | 51,000 | 2分钟 | 95% |
| chinapower | ✅ | 37 | 177,244 | 4分钟 | 90% |
| power | 🔄 | - | - | - | - |
| ndrc | 🔄 | - | - | - | - |
| peopledaily | 🔄 | - | - | - | - |
| coal | 🔄 | - | - | - | - |
| newenergy | 🔄 | - | - | - | - |
| cnenergy | 🔄 | - | - | - | - |
| energy_news | 🔄 | - | - | - | - |
| nea | 🔄 | - | - | - | - |
| real_nea | 🔄 | - | - | - | - |
| test | 🔄 | - | - | - | - |

**总计**:
- 测试爬虫数: 12个
- 通过数: 2个
- 失败数: 0个
- 待测试: 10个

**结论**:
```
（填写测试结论）
```

**建议**:
```
（填写改进建议）
```

---

## 🎯 下一步行动

### 立即执行

1. [ ] 测试所有Scrapy爬虫（9个）
2. [ ] 记录测试结果
3. [ ] 修复发现的问题

### 本周完成

4. [ ] 优化Playwright爬虫
5. [ ] 配置定时任务
6. [ ] 添加监控告警

### 本月完成

7. [ ] 添加更多数据源
8. [ ] 优化性能
9. [ ] 完善文档

---

**文档版本**: v1.0
**最后更新**: 2026-04-10
