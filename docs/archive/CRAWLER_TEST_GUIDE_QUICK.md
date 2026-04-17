# 爬虫功能快速测试指南

## ✅ 已完成的改进

1. **创建测试爬虫** - `test` 爬虫，确保能抓取到数据
2. **优化轮询频率** - 运行时2秒刷新，空闲时10秒刷新
3. **改进进程管理** - 使用Redis保存PID，停止功能更可靠
4. **防止重复运行** - 检查爬虫是否已在运行

## 🚀 测试步骤

### 1. 重启后端
```bash
# 停止当前后端（Ctrl+C）
cd backend
source venv/bin/activate
python app.py
```

### 2. 测试命令行爬虫
```bash
# 测试test爬虫（应该能抓取3篇文章）
cd crawler
../backend/venv/bin/scrapy crawl test

# 查看数据库
docker exec energy_mysql mysql -uroot -ppassword -e \
  "USE energy_station; SELECT title, source FROM articles WHERE source='测试数据源';" 2>&1 | grep -v "Using a password"
```

### 3. 测试管理界面

#### 3.1 访问爬虫管理
- 地址：http://localhost:5173/admin/crawler
- 登录：`13800138000 / admin123`

#### 3.2 测试运行功能
1. 找到"测试爬虫"卡片
2. 点击"运行"按钮
3. 观察状态变化：
   - ✅ 状态变为"运行中"（蓝色）
   - ✅ 页面每2秒自动刷新
   - ✅ 显示最后执行记录

#### 3.3 测试停止功能
1. 在爬虫运行时
2. 点击"停止"按钮
3. 观察状态变化：
   - ✅ 状态变回"正常"（绿色）
   - ✅ 日志显示"手动停止"

#### 3.4 查看日志
1. 切换到"爬取日志"标签
2. 查看最新的日志记录
3. 应该能看到：
   - 数据源：测试数据源
   - 状态：成功/失败
   - 文章数：3（如果成功）
   - 开始/结束时间
   - 耗时

#### 3.5 查看统计
1. 切换到"统计信息"标签
2. 查看：
   - 总文章数（应该增加）
   - 今日抓取数
   - 来源统计（应该有"测试数据源"）

## 📊 预期结果

### 成功标准
- ✅ 测试爬虫能成功抓取3篇文章
- ✅ 前端能看到状态变化
- ✅ 运行时每2秒刷新
- ✅ 停止按钮能正常工作
- ✅ 日志正确记录
- ✅ 数据库中有新文章

### 测试爬虫特点
- **快速**：每篇文章1秒延迟，总共约3秒
- **可靠**：使用httpbin.org，不依赖外部网站
- **可见**：生成的文章标题包含时间戳
- **可验证**：数据源固定为"测试数据源"

## 🐛 常见问题

### Q1: 爬虫启动失败
**检查：**
```bash
# 确认scrapy路径正确
ls -la backend/venv/bin/scrapy

# 手动测试
cd crawler
../backend/venv/bin/scrapy list
```

### Q2: 看不到状态变化
**解决：**
- 打开浏览器开发者工具（F12）
- 查看Network标签，确认API请求正常
- 查看Console是否有错误

### Q3: 停止按钮无效
**检查：**
```bash
# 查看Redis中的PID
docker exec energy_redis redis-cli GET "crawler:test:pid"

# 查看进程是否存在
ps aux | grep "scrapy crawl test"
```

### Q4: 数据库中没有数据
**检查：**
```bash
# 查看爬虫日志
cd crawler
../backend/venv/bin/scrapy crawl test 2>&1 | grep -E "(ERROR|scraped|saved)"

# 检查数据库连接
docker exec energy_mysql mysql -uroot -ppassword -e "USE energy_station; SHOW TABLES;"
```

## 📝 测试检查清单

### 命令行测试
- [ ] scrapy list 能列出test爬虫
- [ ] scrapy crawl test 能成功运行
- [ ] 日志显示 "scraped 3 items"
- [ ] 数据库中有3篇新文章

### API测试
- [ ] POST /api/crawler/spiders/test/run 返回成功
- [ ] GET /api/crawler/spiders 显示test爬虫状态为running
- [ ] POST /api/crawler/spiders/test/stop 能停止爬虫
- [ ] GET /api/crawler/logs 能看到新日志

### 前端测试
- [ ] 爬虫列表显示9个爬虫（包括test）
- [ ] 点击运行后状态变为"运行中"
- [ ] 页面自动刷新（2秒间隔）
- [ ] 显示最后执行记录
- [ ] 停止按钮可用且有效
- [ ] 日志标签页显示新记录
- [ ] 统计信息正确更新

## 🎯 下一步

测试通过后，可以：
1. 修复其他爬虫的CSS选择器
2. 添加更多数据源
3. 实现WebSocket实时推送
4. 添加爬虫配置管理
5. 优化错误处理和重试机制

## 💡 提示

- 测试爬虫使用httpbin.org，需要网络连接
- 如果httpbin.org不可用，爬虫会失败但不影响系统
- 可以修改test_spider.py使用本地数据
- Redis用于存储PID，确保Redis容器运行中
