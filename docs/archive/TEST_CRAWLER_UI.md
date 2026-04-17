# 爬虫UI优化测试指南

## 快速测试步骤

### 1. 启动服务
```bash
# 启动后端
cd backend
source venv/bin/activate
python app.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 2. 访问爬虫管理页面
```
http://localhost:5173/admin/crawler
```

### 3. 测试一键爬取功能

#### 步骤：
1. 点击右上角"🚀 一键爬取所有平台"按钮
2. 观察Toast通知显示启动结果
3. 检查右下角是否自动显示进度面板

#### 预期结果：
- ✅ 按钮显示"启动中..."
- ✅ 1-2秒后显示成功通知
- ✅ 通知显示启动统计（如"已启动: 12 个"）
- ✅ 右下角自动弹出进度面板

### 4. 测试实时进度显示

#### 步骤：
1. 观察右下角进度面板
2. 检查是否每2秒更新数据
3. 点击"实时进度"标签页

#### 预期结果：
- ✅ 显示运行中的爬虫列表
- ✅ 每个爬虫显示：
  - 已抓取文章数（动态增加）
  - 请求数（动态增加）
  - 运行时长（动态增加）
  - 最新日志行
- ✅ 数据每2秒自动刷新

### 5. 测试进度面板交互

#### 步骤：
1. 点击进度面板右上角的"✕"按钮
2. 等待5秒
3. 观察面板是否重新显示

#### 预期结果：
- ✅ 点击"✕"后面板隐藏
- ✅ 如果有爬虫运行，面板不会重新显示（手动关闭）
- ✅ 启动新爬虫后，面板重新显示

### 6. 测试实时进度标签页

#### 步骤：
1. 切换到"实时进度"标签页
2. 观察详细进度卡片
3. 等待爬虫完成

#### 预期结果：
- ✅ 显示详细的进度指标卡片
- ✅ 显示最新日志内容
- ✅ 爬虫完成后从列表中消失
- ✅ 所有爬虫完成后显示"当前没有运行中的爬虫"

## API测试

### 测试一键爬取API
```bash
# 获取token（先登录）
TOKEN="your_jwt_token"

# 调用一键爬取API
curl -X POST http://localhost:5001/api/crawler/spiders/run-all \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**预期响应**:
```json
{
  "message": "成功启动 12 个爬虫",
  "started_count": 12,
  "failed_count": 0,
  "running_count": 0,
  "started_spiders": [
    {
      "name": "mysteel",
      "display_name": "我的钢铁网",
      "log_id": 123,
      "pid": 12345
    },
    ...
  ],
  "failed_spiders": [],
  "running_spiders": []
}
```

### 测试实时进度API
```bash
# 获取实时进度
curl -X GET http://localhost:5001/api/crawler/progress \
  -H "Authorization: Bearer $TOKEN"
```

**预期响应**:
```json
{
  "items": [
    {
      "spider_name": "mysteel",
      "display_name": "我的钢铁网",
      "log_id": 123,
      "status": "running",
      "started_at": "2026-04-12T10:00:00",
      "duration": 45.5,
      "items_scraped": 15,
      "pages_crawled": 3,
      "requests_count": 25,
      "last_log_line": "[mysteel] INFO: 正在抓取第3页..."
    },
    ...
  ],
  "total_running": 12
}
```

## 浏览器控制台测试

### 1. 检查API调用
打开浏览器开发者工具（F12），切换到Network标签：

- 查找 `/api/crawler/progress` 请求
- 检查是否每2秒调用一次
- 查看响应数据是否正确

### 2. 检查React Query缓存
在Console中输入：
```javascript
// 查看爬虫列表缓存
window.__REACT_QUERY_DEVTOOLS__

// 或者查看具体的query
queryClient.getQueryData(['crawler-progress'])
```

## 性能测试

### 1. 测试批量启动性能
```bash
# 记录启动时间
time curl -X POST http://localhost:5001/api/crawler/spiders/run-all \
  -H "Authorization: Bearer $TOKEN"
```

**预期**: 启动12个爬虫应在2秒内完成

### 2. 测试进度查询性能
```bash
# 测试100次查询的平均时间
for i in {1..100}; do
  time curl -s http://localhost:5001/api/crawler/progress \
    -H "Authorization: Bearer $TOKEN" > /dev/null
done
```

**预期**: 每次查询应在100ms内完成

## 常见问题排查

### 问题1：一键启动按钮无响应
**检查**:
```bash
# 检查后端日志
tail -f backend/logs/app.log

# 检查是否有权限
# 确保登录用户是管理员
```

### 问题2：进度不更新
**检查**:
```bash
# 检查Redis连接
docker exec energy_redis redis-cli PING

# 检查日志文件是否存在
ls -la logs/crawler/

# 检查Redis中的日志路径
docker exec energy_redis redis-cli KEYS "crawler:*:log_file"
```

### 问题3：前端报错
**检查**:
```bash
# 查看浏览器控制台错误
# 检查API响应状态码
# 确认token是否有效
```

## 压力测试

### 测试并发启动
```bash
# 同时启动多个爬虫
for spider in mysteel chinapower xinhua_real; do
  curl -X POST http://localhost:5001/api/crawler/spiders/$spider/run \
    -H "Authorization: Bearer $TOKEN" &
done
wait
```

### 测试高频查询
```bash
# 模拟多个用户同时查询进度
for i in {1..10}; do
  (
    for j in {1..100}; do
      curl -s http://localhost:5001/api/crawler/progress \
        -H "Authorization: Bearer $TOKEN" > /dev/null
    done
  ) &
done
wait
```

## 验收标准

### 功能验收
- ✅ 一键启动按钮正常工作
- ✅ 批量启动成功率 > 95%
- ✅ 实时进度每2秒更新
- ✅ 进度数据准确（文章数、请求数等）
- ✅ 浮动面板自动显示/隐藏
- ✅ Toast通知正常显示

### 性能验收
- ✅ 批量启动响应时间 < 2秒
- ✅ 进度查询响应时间 < 100ms
- ✅ 前端刷新无卡顿
- ✅ 内存占用正常（< 500MB）

### 用户体验验收
- ✅ 界面美观，动画流畅
- ✅ 操作直观，无需说明
- ✅ 反馈及时，信息清晰
- ✅ 错误提示友好

## 测试报告模板

```markdown
# 爬虫UI优化测试报告

## 测试环境
- 浏览器: Chrome 120
- 操作系统: macOS 14
- 后端版本: v1.0
- 前端版本: v1.0

## 测试结果

### 1. 一键爬取功能
- [ ] 按钮点击响应
- [ ] Toast通知显示
- [ ] 批量启动成功
- [ ] 错误处理正确

### 2. 实时进度显示
- [ ] 浮动面板显示
- [ ] 数据实时更新
- [ ] 进度标签页正常
- [ ] 自动刷新工作

### 3. 性能测试
- 批量启动时间: ___ 秒
- 进度查询时间: ___ ms
- 内存占用: ___ MB

### 4. 问题记录
1. 问题描述...
2. 问题描述...

### 5. 总体评价
- 功能完整性: ⭐⭐⭐⭐⭐
- 性能表现: ⭐⭐⭐⭐⭐
- 用户体验: ⭐⭐⭐⭐⭐

## 建议
1. ...
2. ...
```

---

**测试时间**: 2026-04-12
**测试人**: ___
**状态**: 待测试
