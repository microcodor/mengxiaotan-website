# Docker 状态说明

## 当前情况

Docker Desktop 正在重启和初始化中。这个过程通常需要 1-2 分钟。

## 为什么需要 Docker？

Docker 用于运行以下服务：
- **MySQL 数据库**（端口 3307）- 存储文章、用户、订阅等数据
- **Redis 缓存**（端口 6380）- 用于缓存和会话管理

## 当前系统状态

### ✅ 正常运行的服务
- **后端 API**（端口 5001）- 运行中，但需要数据库连接
- **前端服务**（端口 5173）- 运行中，不依赖 Docker

### ⏳ 等待启动的服务
- **Docker Desktop** - 正在初始化
- **MySQL 容器** - 等待 Docker 就绪后启动
- **Redis 容器** - 等待 Docker 就绪后启动

## 手动操作步骤

### 1. 检查 Docker Desktop 状态

**方法 1**: 查看菜单栏
- 点击菜单栏右上角的 Docker 图标
- 如果显示 "Docker Desktop is running"，说明已就绪
- 如果显示 "Docker Desktop is starting..."，需要继续等待

**方法 2**: 使用命令行
```bash
docker ps
```
- 如果显示容器列表（即使为空），说明 Docker 已就绪
- 如果显示错误信息，说明还在初始化

### 2. 启动数据库容器

当 Docker 就绪后，运行：
```bash
docker-compose up -d mysql redis
```

预期输出：
```
[+] Running 2/2
 ✔ Container energy_mysql  Started
 ✔ Container energy_redis  Started
```

### 3. 验证容器状态

```bash
docker ps
```

应该看到两个容器：
- `energy_mysql` - MySQL 数据库
- `energy_redis` - Redis 缓存

### 4. 测试后端 API

```bash
./test_backend.sh
```

所有测试应该通过。

## 如果 Docker 无法启动

### 临时解决方案：使用本地数据库

如果 Docker Desktop 持续无法启动，可以使用本地安装的 MySQL：

1. **安装 MySQL**（如果未安装）
   ```bash
   brew install mysql
   brew services start mysql
   ```

2. **创建数据库**
   ```bash
   mysql -uroot -e "CREATE DATABASE IF NOT EXISTS energy_station"
   ```

3. **修改后端配置**
   编辑 `backend/.env` 或 `backend/config.py`：
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost:3306/energy_station'
   ```

4. **重启后端服务**
   ```bash
   pkill -f "python.*app.py"
   ./backend/venv/bin/python3 backend/app.py > backend.log 2>&1 &
   ```

## 常见问题

### Q: Docker Desktop 一直显示 "Starting..."
**A**: 
1. 完全退出 Docker Desktop
2. 等待 10 秒
3. 重新打开 Docker Desktop
4. 等待 1-2 分钟

### Q: 容器启动失败
**A**: 检查端口是否被占用：
```bash
lsof -ti:3307  # MySQL
lsof -ti:6380  # Redis
```

如果有进程占用，先停止它们：
```bash
lsof -ti:3307 | xargs kill -9
lsof -ti:6380 | xargs kill -9
```

### Q: 数据会丢失吗？
**A**: 不会。数据存储在 Docker volumes 中：
```bash
docker volume ls | grep energy
```

即使容器停止或删除，数据仍然保留。

## 下一步

1. **等待 Docker Desktop 完全启动**（查看菜单栏图标）
2. **运行启动脚本**：
   ```bash
   ./start.sh
   ```
3. **或者手动启动容器**：
   ```bash
   docker-compose up -d mysql redis
   ```
4. **测试系统**：
   ```bash
   ./test_backend.sh
   ```

## 当前可用功能

即使 Docker 未启动，以下功能仍然可用：
- ✅ 前端页面浏览（http://localhost:5173）
- ✅ 前端静态资源
- ⚠️ 后端 API（需要数据库连接才能正常工作）

## 需要帮助？

如果遇到问题，请查看：
1. `fix_docker.md` - Docker 问题详细诊断和修复指南
2. `STATUS_REPORT.md` - 系统整体状态报告
3. `backend.log` - 后端服务日志
