# Docker 问题诊断和修复指南

## 问题描述
Docker daemon 无法连接，导致 MySQL 和 Redis 容器无法启动。

## 诊断结果
1. ✅ Docker Desktop 应用程序正在运行
2. ❌ Docker daemon 无法通过 socket 连接
3. ❌ MySQL 端口 3307 无法访问
4. ❌ 容器已停止

## 解决方案

### 方案 1: 重启 Docker Desktop（推荐）

1. **完全退出 Docker Desktop**
   ```bash
   # 方法 1: 通过菜单栏
   点击菜单栏的 Docker 图标 → Quit Docker Desktop
   
   # 方法 2: 通过命令行
   osascript -e 'quit app "Docker"'
   ```

2. **等待 5-10 秒**

3. **重新启动 Docker Desktop**
   ```bash
   open -a Docker
   ```

4. **等待 Docker 完全启动**（约 30-60 秒）
   - 菜单栏 Docker 图标变为绿色
   - 或者运行以下命令检查：
   ```bash
   docker ps
   ```

5. **启动容器**
   ```bash
   docker-compose up -d mysql redis
   ```

---

### 方案 2: 使用本地 MySQL 和 Redis（临时方案）

如果 Docker 问题无法快速解决，可以使用本地安装的 MySQL 和 Redis：

#### 安装 MySQL（如果未安装）
```bash
brew install mysql
brew services start mysql
```

#### 安装 Redis（如果未安装）
```bash
brew install redis
brew services start redis
```

#### 修改后端配置
编辑 `backend/config.py`，将数据库连接改为：
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/energy_station'
REDIS_URL = 'redis://localhost:6379/0'
```

---

### 方案 3: 检查 Docker Desktop 设置

1. **打开 Docker Desktop**
2. **点击设置图标（齿轮）**
3. **检查以下设置**：
   - General → "Use Docker Compose V2" 应该启用
   - Resources → 确保有足够的 CPU 和内存分配
   - Advanced → 确保 "Enable default Docker socket" 已启用

4. **应用更改并重启 Docker Desktop**

---

## 验证步骤

### 1. 检查 Docker 是否运行
```bash
docker ps
```
**预期输出**: 显示容器列表（可能为空）

### 2. 检查容器状态
```bash
docker ps -a | grep -E "mysql|redis"
```
**预期输出**: 显示 energy_mysql 和 energy_redis 容器

### 3. 启动容器
```bash
docker-compose up -d mysql redis
```
**预期输出**: 
```
[+] Running 2/2
 ✔ Container energy_mysql  Started
 ✔ Container energy_redis  Started
```

### 4. 检查端口
```bash
nc -zv localhost 3307  # MySQL
nc -zv localhost 6380  # Redis
```
**预期输出**: Connection succeeded

### 5. 测试数据库连接
```bash
docker exec energy_mysql mysql -uroot -ppassword -e "SELECT 1"
```
**预期输出**: 
```
+---+
| 1 |
+---+
| 1 |
+---+
```

---

## 当前系统状态

### 后端服务
- ✅ 运行中（PID: 98002）
- ✅ 端口 5001 正常
- ⚠️ 需要数据库连接

### 前端服务
- ✅ 运行中
- ✅ 端口 5173 正常
- ✅ 不依赖 Docker

### 数据库
- ❌ MySQL 容器未运行
- ❌ 端口 3307 无法访问
- ⚠️ 后端 API 可能会失败

---

## 快速修复命令

```bash
# 1. 重启 Docker Desktop
osascript -e 'quit app "Docker"'
sleep 5
open -a Docker
sleep 30

# 2. 检查 Docker 是否可用
docker ps

# 3. 启动容器
docker-compose up -d mysql redis

# 4. 等待容器启动
sleep 10

# 5. 验证
docker ps
nc -zv localhost 3307
nc -zv localhost 6380

# 6. 测试后端 API
./test_backend.sh
```

---

## 常见问题

### Q: Docker Desktop 启动很慢
**A**: 这是正常的，特别是在 macOS 上。通常需要 30-60 秒。

### Q: 容器启动后立即停止
**A**: 检查日志：
```bash
docker logs energy_mysql
docker logs energy_redis
```

### Q: 端口被占用
**A**: 检查并清理：
```bash
lsof -ti:3307 | xargs kill -9  # MySQL
lsof -ti:6380 | xargs kill -9  # Redis
```

### Q: 数据丢失
**A**: Docker volumes 保存了数据：
```bash
docker volume ls | grep energy
```

---

## 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. Docker Desktop 版本
   ```bash
   docker --version
   ```

2. macOS 版本
   ```bash
   sw_vers
   ```

3. Docker 日志
   ```bash
   docker info
   ```

4. 容器日志
   ```bash
   docker logs energy_mysql
   docker logs energy_redis
   ```
