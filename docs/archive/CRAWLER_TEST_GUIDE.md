# 爬虫功能测试指南

## 🎯 测试目标

验证爬虫管理系统的完整功能，包括：
1. 爬虫能否正常运行并抓取数据
2. 管理界面能否正常显示和控制爬虫
3. API接口是否正常工作
4. 自动调度是否正常

## 📋 前置条件

### 1. 确保依赖已安装

```bash
# 检查 Scrapy 是否已安装
cd backend
source venv/bin/activate
python -c "import scrapy; print(scrapy.__version__)"
# 应该输出: 2.15.0 或更高版本

# 如果未安装，执行：
pip install "Scrapy>=2.11.0" "itemadapter>=0.8.0"
```

### 2. 确保数据库运行

```bash
# 检查 MySQL 容器
docker ps | grep energy_mysql

# 如果未运行，启动：
docker-compose up -d mysql

# 等待几秒后测试连接
docker exec energy_mysql mysql -uroot -ppassword -e "USE energy_station; SHOW TABLES;"
```

## 🧪 测试步骤

### 步骤1：运行自动化测试脚本

```bash
# 在项目根目录执行
./test-crawler.sh
```

**预期结果：**
- ✅ 8个爬虫文件存在
- ✅ Scrapy 已安装（可能显示未安装，因为脚本检查的是系统Python）
- ✅ 数据库连接正常
- ✅ 爬虫配置存在
- ✅ 爬虫 API 可访问
- ✅ 前端页面存在

### 步骤2：手动测试单个爬虫

```bash
# 进入爬虫目录
cd crawler

# 列出所有可用的爬虫
../backend/venv/bin/scrapy list
# 应该输出：
# cnenergy
# coal
# ndrc
# nea
# newenergy
# peopledaily
# power
# xinhua

# 测试运行 ndrc 爬虫（限制抓取5篇文章）
../backend/venv/bin/scrapy crawl ndrc -s CLOSESPIDER_ITEMCOUNT=5

# 测试运行 coal 爬虫
../backend/venv/bin/scrapy crawl coal -s CLOSESPIDER_ITEMCOUNT=5
```

**预期结果：**
- 爬虫启动成功
- 显示爬取进度
- 保存文章到数据库
- 无严重错误

### 步骤3：验证数据已保存

```bash
# 查看文章总数
docker exec energy_mysql mysql -uroot -ppassword -e \
  "USE energy_station; SELECT COUNT(*) as total FROM articles;"

# 按来源统计文章数
docker exec energy_mysql mysql -uroot -ppassword -e \
  "USE energy_station; SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC;"

# 查看最新的10篇文章
docker exec energy_mysql mysql -uroot -ppassword -e \
  "USE energy_station; SELECT id, title, source, category, published_at FROM articles ORDER BY created_at DESC LIMIT 10;"
```

**预期结果：**
- 文章总数应该增加
- 能看到不同来源的文章
- 文章标题、来源、分类等信息完整

### 步骤4：启动后端服务

```bash
# 在新终端窗口启动后端
cd backend
source venv/bin/activate
python app.py
```

**预期输出：**
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### 步骤5：测试爬虫管理API

```bash
# 在另一个终端执行以下命令

# 1. 登录获取token（使用管理员账号）
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"admin","password":"admin123"}' | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. 获取爬虫列表
curl -s http://localhost:5000/api/crawler/spiders \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 3. 手动运行 ndrc 爬虫
curl -s -X POST http://localhost:5000/api/crawler/spiders/ndrc/run \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 4. 查看爬取日志
curl -s http://localhost:5000/api/crawler/logs \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 5. 查看统计信息
curl -s http://localhost:5000/api/crawler/stats \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**预期结果：**
- 能成功获取token
- 爬虫列表返回8个爬虫信息
- 手动运行返回成功消息和进程ID
- 日志列表显示历史爬取记录
- 统计信息显示文章数量和分布

### 步骤6：启动前端服务

```bash
# 在新终端窗口启动前端
cd frontend
npm run dev
```

**预期输出：**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### 步骤7：测试管理界面

1. **访问管理后台**
   - 打开浏览器访问：http://localhost:5173/admin
   - 如果未登录，会跳转到登录页
   - 使用管理员账号登录：admin / admin123

2. **进入爬虫管理页面**
   - 点击左侧菜单的"爬虫管理"
   - 或直接访问：http://localhost:5173/admin/crawler

3. **测试爬虫列表标签页**
   - ✅ 应该看到8个爬虫卡片
   - ✅ 每个卡片显示：名称、状态、描述、调度时间
   - ✅ 状态徽章正确显示（正常/运行中/错误）
   - ✅ 显示最后运行时间
   - ✅ 显示最后执行记录（状态、文章数、耗时）
   - ✅ 有"运行"按钮

4. **测试手动运行功能**
   - 点击任意爬虫的"运行"按钮
   - ✅ 应该弹出提示"爬虫已启动"
   - ✅ 爬虫状态变为"运行中"
   - ✅ 页面每10秒自动刷新状态
   - ✅ 运行完成后状态变回"正常"
   - ✅ 显示新的执行记录

5. **测试爬取日志标签页**
   - 切换到"爬取日志"标签
   - ✅ 应该看到表格显示所有爬取记录
   - ✅ 显示：数据源、状态、文章数、开始时间、结束时间、耗时
   - ✅ 最新的记录在最上面
   - ✅ 支持分页（如果记录超过20条）

6. **测试统计信息标签页**
   - 切换到"统计信息"标签
   - ✅ 应该看到4个概览卡片：
     - 总文章数
     - 今日抓取
     - 活跃爬虫
     - 错误爬虫
   - ✅ 应该看到分类统计列表
   - ✅ 应该看到来源统计列表

### 步骤8：测试自动调度

```bash
# 查看调度任务
curl -s http://localhost:5000/api/crawler/schedule \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**预期结果：**
- 返回所有定时任务列表
- 每个任务显示：ID、名称、下次运行时间、触发器

**注意：** 自动调度需要等到设定的时间才会执行，可以通过修改 `backend/app/scheduler.py` 中的时间来测试。

## 🐛 常见问题排查

### 问题1：Scrapy 未安装

**症状：** 运行爬虫时提示 `scrapy: command not found`

**解决：**
```bash
cd backend
source venv/bin/activate
pip install "Scrapy>=2.11.0" "itemadapter>=0.8.0"
```

### 问题2：数据库连接失败

**症状：** 爬虫运行时报错 `Can't connect to MySQL server`

**解决：**
```bash
# 检查 MySQL 容器状态
docker ps | grep energy_mysql

# 重启 MySQL
docker-compose restart mysql

# 检查端口配置（应该是3307）
grep DATABASE_URL crawler/energy_crawler/settings.py
```

### 问题3：爬虫不抓取数据

**症状：** 爬虫运行完成但没有新文章

**可能原因：**
1. CSS选择器不匹配（网站结构变化）
2. 数据已存在（source_url唯一约束）
3. 网站反爬虫限制

**排查：**
```bash
# 查看详细日志
cd crawler
../backend/venv/bin/scrapy crawl ndrc -L DEBUG

# 检查是否有重复数据
docker exec energy_mysql mysql -uroot -ppassword -e \
  "USE energy_station; SELECT source_url FROM articles WHERE source='国家发改委' LIMIT 5;"
```

### 问题4：API返回401错误

**症状：** 调用API时返回 `Unauthorized`

**解决：**
```bash
# 重新获取token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"admin","password":"admin123"}' | jq -r '.access_token')

# 确保请求头包含token
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/crawler/spiders
```

### 问题5：前端页面空白

**症状：** 访问爬虫管理页面显示空白

**排查：**
1. 检查浏览器控制台是否有错误
2. 检查是否已登录管理员账号
3. 检查后端API是否正常响应

```bash
# 测试API
curl http://localhost:5000/api/crawler/spiders
```

### 问题6：爬虫无法停止

**症状：** 点击停止按钮后爬虫仍在运行

**解决：**
```bash
# 手动查找并停止爬虫进程
ps aux | grep "scrapy crawl"

# 停止进程（替换 <PID> 为实际进程ID）
kill <PID>
```

## 📊 测试检查清单

### 后端功能
- [ ] Scrapy 已安装在 backend/venv
- [ ] 8个爬虫文件存在
- [ ] 数据库连接正常
- [ ] 可以手动运行爬虫
- [ ] 爬虫能抓取并保存数据
- [ ] API接口正常响应
- [ ] 管理员权限验证正常
- [ ] 日志记录功能正常

### 前端功能
- [ ] 爬虫管理页面可访问
- [ ] 爬虫列表正确显示
- [ ] 状态实时更新
- [ ] 手动运行按钮可用
- [ ] 停止按钮可用（运行时）
- [ ] 日志列表正确显示
- [ ] 统计信息正确显示
- [ ] 页面自动刷新

### 数据完整性
- [ ] 文章保存到数据库
- [ ] Source记录正确创建
- [ ] CrawlLog记录正确创建
- [ ] 文章字段完整（标题、内容、来源等）
- [ ] 时间字段正确
- [ ] 分类标签正确

## 🎉 测试成功标准

完成以上所有测试步骤后，应该达到以下标准：

1. ✅ 所有8个爬虫都能正常运行
2. ✅ 数据库中有来自不同来源的文章
3. ✅ 管理界面能正确显示爬虫状态
4. ✅ 可以通过界面手动控制爬虫
5. ✅ 日志和统计信息正确显示
6. ✅ API接口全部正常工作
7. ✅ 无严重错误或异常

## 📝 测试报告模板

```
爬虫功能测试报告
==================

测试时间：2026-04-10
测试人员：[姓名]

测试环境：
- 操作系统：macOS
- Python版本：3.12.7
- Scrapy版本：2.15.0
- MySQL版本：8.0

测试结果：
1. 爬虫运行测试：[通过/失败]
   - ndrc: [通过/失败] - 抓取 X 篇
   - coal: [通过/失败] - 抓取 X 篇
   - power: [通过/失败] - 抓取 X 篇
   - ...

2. API接口测试：[通过/失败]
   - 爬虫列表：[通过/失败]
   - 手动运行：[通过/失败]
   - 日志查询：[通过/失败]
   - 统计信息：[通过/失败]

3. 管理界面测试：[通过/失败]
   - 页面加载：[通过/失败]
   - 状态显示：[通过/失败]
   - 手动控制：[通过/失败]
   - 日志查看：[通过/失败]

问题记录：
1. [问题描述]
   - 严重程度：[高/中/低]
   - 解决方案：[描述]

总体评价：
[通过/需要改进]

备注：
[其他说明]
```

## 🚀 快速测试命令集合

```bash
# 一键测试所有爬虫（每个抓取3篇）
cd crawler
for spider in ndrc nea coal power newenergy peopledaily xinhua cnenergy; do
  echo "Testing $spider..."
  ../backend/venv/bin/scrapy crawl $spider -s CLOSESPIDER_ITEMCOUNT=3
done

# 查看结果
docker exec energy_mysql mysql -uroot -ppassword -e \
  "USE energy_station; SELECT source, COUNT(*) as count FROM articles GROUP BY source;"
```

## 📞 需要帮助？

如果测试过程中遇到问题：
1. 查看本文档的"常见问题排查"部分
2. 查看 `UPDATE_SUMMARY_爬虫管理.md` 了解系统架构
3. 查看爬虫日志：`/tmp/crawler_test.log`
4. 查看后端日志：backend终端输出
5. 查看前端日志：浏览器控制台
