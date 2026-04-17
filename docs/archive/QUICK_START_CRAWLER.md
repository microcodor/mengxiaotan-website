# 爬虫管理快速启动指南

## 问题：403 Forbidden

当访问 `http://localhost:5173/api/crawler/spiders` 时出现 403 错误，原因是：

1. **后端服务未启动** - 爬虫管理API需要后端服务运行
2. **端口冲突** - 5000端口可能被其他程序占用（如ControlCenter）
3. **未登录或无权限** - 需要管理员账号登录

## 解决方案

### 方案1：使用备用端口启动后端（推荐）

```bash
# 1. 进入后端目录
cd backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 使用5001端口启动（避免冲突）
python -c "
from app import create_app
from app.scheduler import init_scheduler
app = create_app()
init_scheduler()
app.run(host='0.0.0.0', port=5001, debug=True)
"
```

然后修改前端代理配置：

```bash
# 编辑 frontend/vite.config.ts
# 将 target: 'http://localhost:5000' 改为 target: 'http://localhost:5001'
```

### 方案2：停止占用5000端口的程序

```bash
# 1. 查看占用5000端口的进程
lsof -i :5000

# 2. 停止ControlCenter（如果是它占用的）
# 在macOS上，ControlCenter是系统进程，建议使用方案1

# 3. 或者杀死进程（替换<PID>为实际进程ID）
kill <PID>
```

### 方案3：使用Docker启动（最简单）

```bash
# 在项目根目录
docker-compose up -d

# 这会启动：
# - MySQL (3307端口)
# - Redis (6379端口)
# - Backend (5000端口，在容器内)
# - Frontend (80端口)
```

## 完整启动步骤

### 步骤1：启动数据库

```bash
# 启动MySQL和Redis
docker-compose up -d mysql redis

# 等待几秒让数据库启动
sleep 5

# 验证数据库运行
docker ps | grep energy_mysql
```

### 步骤2：启动后端（选择一种方式）

**方式A：直接启动（使用5001端口）**

```bash
# 新终端窗口
cd backend
source venv/bin/activate

# 创建临时启动脚本
cat > run_backend.py << 'EOF'
from app import create_app
from app.scheduler import init_scheduler

app = create_app()
init_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
EOF

# 运行
python run_backend.py
```

**方式B：使用Docker**

```bash
docker-compose up -d backend
```

### 步骤3：更新前端代理配置

如果使用5001端口，需要修改前端配置：

```bash
# 编辑 frontend/vite.config.ts
```

将以下内容：
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  },
},
```

改为：
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:5001',
    changeOrigin: true,
  },
},
```

### 步骤4：启动前端

```bash
# 新终端窗口
cd frontend
npm run dev
```

### 步骤5：登录管理员账号

1. 打开浏览器：http://localhost:5173
2. 点击"登录"
3. 使用管理员账号：
   - 手机号：`admin`
   - 密码：`admin123`

### 步骤6：访问爬虫管理

登录后，访问：http://localhost:5173/admin/crawler

## 验证步骤

### 1. 检查后端是否运行

```bash
# 测试后端健康状态（根据实际端口）
curl http://localhost:5001/api/articles

# 应该返回文章列表JSON
```

### 2. 检查前端代理

```bash
# 在浏览器开发者工具的Network标签中
# 查看API请求是否正确代理到后端
```

### 3. 测试爬虫API（需要登录）

```bash
# 1. 获取token
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"admin","password":"admin123"}' | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. 测试爬虫列表API
curl -s http://localhost:5001/api/crawler/spiders \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 应该返回8个爬虫的信息
```

## 常见问题

### Q1: 403 Forbidden

**原因：** 未登录或没有管理员权限

**解决：**
1. 确保已登录管理员账号（admin / admin123）
2. 检查浏览器localStorage中是否有access_token
3. Token可能已过期，重新登录

### Q2: Network Error / ERR_CONNECTION_REFUSED

**原因：** 后端服务未启动

**解决：**
1. 检查后端进程是否运行
2. 检查端口是否正确（5000或5001）
3. 查看后端终端是否有错误信息

### Q3: 端口被占用

**原因：** 5000端口被其他程序占用

**解决：**
```bash
# 查看占用端口的进程
lsof -i :5000

# 使用其他端口（如5001）
# 或停止占用端口的程序
```

### Q4: 前端显示空白页面

**原因：** API请求失败或权限不足

**解决：**
1. 打开浏览器开发者工具（F12）
2. 查看Console标签的错误信息
3. 查看Network标签的API请求状态
4. 确保已登录管理员账号

## 一键启动脚本

创建一个启动脚本 `start-crawler.sh`：

```bash
#!/bin/bash

echo "🚀 启动爬虫管理系统"
echo "================================"

# 1. 启动数据库
echo "📦 启动数据库..."
docker-compose up -d mysql redis
sleep 5

# 2. 启动后端（使用5001端口）
echo "🔧 启动后端服务..."
cd backend
source venv/bin/activate

# 创建临时启动脚本
cat > run_backend.py << 'EOF'
from app import create_app
from app.scheduler import init_scheduler

app = create_app()
init_scheduler()

if __name__ == '__main__':
    print("🚀 后端服务启动在 http://0.0.0.0:5001")
    print("📝 管理员账号: admin / admin123")
    app.run(host='0.0.0.0', port=5001, debug=True)
EOF

# 后台运行
nohup python run_backend.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID, 端口: 5001)"

cd ..

# 3. 提示前端配置
echo ""
echo "⚠️  请确保前端代理配置正确："
echo "   frontend/vite.config.ts 中的 target 应为 'http://localhost:5001'"
echo ""
echo "📱 启动前端："
echo "   cd frontend && npm run dev"
echo ""
echo "🌐 访问地址："
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:5001"
echo "   爬虫管理: http://localhost:5173/admin/crawler"
echo ""
echo "👤 管理员账号："
echo "   手机号: admin"
echo "   密码: admin123"
echo ""
echo "📋 查看后端日志："
echo "   tail -f backend.log"
```

使用方法：

```bash
# 赋予执行权限
chmod +x start-crawler.sh

# 运行
./start-crawler.sh

# 然后在新终端启动前端
cd frontend
npm run dev
```

## 停止服务

```bash
# 停止后端
pkill -f "python run_backend.py"

# 停止前端（在前端终端按 Ctrl+C）

# 停止数据库
docker-compose down
```

## 测试爬虫功能

登录后台后，可以：

1. **查看爬虫列表**
   - 访问：http://localhost:5173/admin/crawler
   - 应该看到8个爬虫卡片

2. **手动运行爬虫**
   - 点击任意爬虫的"运行"按钮
   - 观察状态变化

3. **查看爬取日志**
   - 切换到"爬取日志"标签
   - 查看历史记录

4. **查看统计信息**
   - 切换到"统计信息"标签
   - 查看文章统计

## 需要帮助？

如果仍然遇到问题：

1. 查看后端日志：`tail -f backend.log`
2. 查看浏览器控制台错误
3. 检查网络请求状态
4. 参考 `CRAWLER_TEST_GUIDE.md` 进行详细测试
