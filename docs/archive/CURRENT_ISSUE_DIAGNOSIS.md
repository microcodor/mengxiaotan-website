# 当前问题诊断

## 问题现象
前端显示 500 Internal Server Error，分类和内容无法加载。

## 问题分析

### 1. 错误类型变化
- **之前**: 403 Forbidden（macOS AirPlay占用5000端口）
- **现在**: 500 Internal Server Error（后端服务未启动）

### 2. 根本原因
后端服务（Flask应用）没有运行在5001端口。

### 3. 验证方法
```bash
# 检查5001端口是否有服务
lsof -i:5001

# 测试后端API
curl http://localhost:5001/api/categories

# 检查Python进程
ps aux | grep "python.*app.py"
```

## 解决方案

### 方案 1: 使用快速启动脚本（推荐）

```bash
# 在项目根目录执行
./quick-start-backend.sh
```

这个脚本会：
1. 激活Python虚拟环境
2. 检查并清理5001端口
3. 启动Flask后端服务

### 方案 2: 手动启动后端

```bash
# 1. 进入后端目录
cd backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development

# 4. 启动服务
python app.py
```

### 方案 3: 使用完整启动脚本

```bash
# 停止所有服务
./stop.sh

# 重新启动所有服务
./start.sh
```

**注意**: `start.sh` 会启动 Docker 容器、初始化数据库、启动后端和前端。

## 启动后验证

### 1. 检查后端服务
```bash
# 应该看到Flask进程
ps aux | grep "python.*app.py"

# 应该看到5001端口被占用
lsof -i:5001

# 测试API（应该返回JSON数据）
curl http://localhost:5001/api/categories
```

### 2. 检查前端
访问 http://localhost:5173，应该能看到：
- 分类导航正常显示
- 文章列表正常加载
- 浏览器控制台没有错误

## 常见问题

### Q1: 虚拟环境不存在
**错误**: `❌ 虚拟环境不存在`

**解决**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Q2: 数据库连接失败
**错误**: `sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")`

**解决**:
```bash
# 启动MySQL容器
docker-compose up -d mysql

# 等待MySQL启动
sleep 10

# 初始化数据库
cd backend
source venv/bin/activate
python init_db.py
```

### Q3: 端口被占用
**错误**: `OSError: [Errno 48] Address already in use`

**解决**:
```bash
# 查找占用进程
lsof -ti:5001

# 终止进程
kill -9 $(lsof -ti:5001)
```

### Q4: 模块导入错误
**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## 服务架构

```
┌─────────────────┐
│   浏览器        │
│ localhost:5173  │
└────────┬────────┘
         │
         │ HTTP请求
         ▼
┌─────────────────┐
│  Vite Dev Server│
│  (前端)         │
│  Port: 5173     │
└────────┬────────┘
         │
         │ /api/* 代理到
         │ http://localhost:5001
         ▼
┌─────────────────┐
│  Flask Backend  │
│  (后端API)      │
│  Port: 5001     │
└────────┬────────┘
         │
         │ 数据库连接
         ▼
┌─────────────────┐
│  MySQL (Docker) │
│  Port: 3307     │
└─────────────────┘
```

## 下一步

1. **启动后端服务**
   ```bash
   ./quick-start-backend.sh
   ```

2. **保持后端运行**，在新终端启动前端
   ```bash
   cd frontend
   npm run dev
   ```

3. **访问应用**
   - 前端: http://localhost:5173
   - 后端API: http://localhost:5001

4. **查看日志**
   - 后端日志会直接显示在终端
   - 前端日志在浏览器控制台

## 完整启动流程

如果要从头开始：

```bash
# 1. 停止所有服务
./stop.sh

# 2. 启动Docker服务
docker-compose up -d mysql redis

# 3. 等待数据库启动
sleep 10

# 4. 初始化数据库（如果需要）
cd backend
source venv/bin/activate
python init_db.py
python init_categories.py
cd ..

# 5. 启动后端（在一个终端）
./quick-start-backend.sh

# 6. 启动前端（在另一个终端）
cd frontend
npm run dev
```

## 监控和调试

### 查看后端日志
后端日志会直接输出到启动后端的终端。

### 查看前端日志
打开浏览器开发者工具 (F12)，查看 Console 和 Network 标签。

### 测试API端点
```bash
# 测试分类API
curl http://localhost:5001/api/categories

# 测试文章API
curl http://localhost:5001/api/articles?page=1&per_page=12

# 测试轮播文章
curl http://localhost:5001/api/articles/carousel
```

## 总结

当前问题的核心是**后端服务未启动**。使用 `./quick-start-backend.sh` 快速启动后端，然后在浏览器中刷新页面即可解决问题。
