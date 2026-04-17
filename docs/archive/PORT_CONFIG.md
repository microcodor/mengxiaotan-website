# 端口配置说明

## 默认端口配置

| 服务 | 默认端口 | 备用端口 | 说明 |
|------|---------|---------|------|
| MySQL | ~~3306~~ | **3307** | 避免与本地 MySQL 冲突 |
| Redis | 6379 | 6380 | 缓存服务 |
| 后端 API | 5000 | 5001 | Flask 应用 |
| 前端开发 | 5173 | 5174 | Vite 开发服务器 |

> 💡 **注意**: 项目默认使用 **3307** 端口运行 MySQL，避免与本地 MySQL 服务冲突。

---

## 端口冲突检查

### 快速检查工具

#### macOS / Linux
```bash
chmod +x check-ports.sh
./check-ports.sh
```

#### Windows
```cmd
check-ports.bat
```

### 手动检查

#### macOS
```bash
# 检查 MySQL 端口
lsof -i :3306
lsof -i :3307

# 检查其他端口
lsof -i :6379  # Redis
lsof -i :5000  # 后端
lsof -i :5173  # 前端
```

#### Linux
```bash
# 检查端口占用
ss -ltn | grep :3306
netstat -ltn | grep :3306

# 查看进程
ss -ltnp | grep :3306
```

#### Windows
```cmd
# 检查端口占用
netstat -ano | findstr :3306
netstat -ano | findstr :3307

# 查看进程详情
tasklist /FI "PID eq [PID]"
```

---

## 修改端口配置

### 1. 修改 MySQL 端口

#### 步骤 1: 修改 docker-compose.yml
```yaml
mysql:
  ports:
    - "3308:3306"  # 改为你想要的端口
```

#### 步骤 2: 修改 backend/config.py
```python
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://root:password@localhost:3308/energy_station'  # 改为对应端口
)
```

#### 步骤 3: 修改 crawler/energy_crawler/settings.py
```python
DATABASE_URL = 'mysql+pymysql://root:password@localhost:3308/energy_station'  # 改为对应端口
```

#### 步骤 4: 创建 backend/.env（可选）
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3308/energy_station
```

### 2. 修改 Redis 端口

#### docker-compose.yml
```yaml
redis:
  ports:
    - "6380:6379"  # 改为你想要的端口
```

#### backend/config.py
```python
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6380/0')
```

### 3. 修改后端 API 端口

#### 修改启动命令
```bash
# start.sh 中修改
flask run --host=0.0.0.0 --port=5001

# 或在 app.py 中修改
app.run(host='0.0.0.0', port=5001)
```

#### 更新前端 API 地址
```typescript
// frontend/src/lib/api.ts
const api = axios.create({
  baseURL: '/api',  // 如果使用代理
  // 或
  baseURL: 'http://localhost:5001/api',  // 直接指定
})
```

### 4. 修改前端开发端口

#### vite.config.ts
```typescript
export default defineConfig({
  server: {
    port: 5174,  // 改为你想要的端口
  }
})
```

---

## 常见端口冲突解决方案

### MySQL 端口冲突 (3306)

**原因**: 本地已安装 MySQL 服务

**解决方案**:

#### 方案 1: 使用项目配置的 3307 端口（推荐）
```bash
# 无需修改，直接启动
./start.sh
```

#### 方案 2: 停止本地 MySQL
```bash
# macOS (Homebrew)
brew services stop mysql

# macOS (手动安装)
sudo /usr/local/mysql/support-files/mysql.server stop

# Linux (systemd)
sudo systemctl stop mysql

# Linux (service)
sudo service mysql stop

# Windows
net stop MySQL80
# 或在服务管理器中停止 MySQL 服务
```

#### 方案 3: 修改为其他端口
参考上面的"修改 MySQL 端口"部分

### Redis 端口冲突 (6379)

**解决方案**:

```bash
# macOS
brew services stop redis
# 或
redis-cli shutdown

# Linux
sudo systemctl stop redis
# 或
redis-cli shutdown

# Windows
# 在服务管理器中停止 Redis 服务
```

### 后端端口冲突 (5000)

**解决方案**:

```bash
# macOS/Linux - 查找并停止进程
lsof -i :5000
kill -9 $(lsof -t -i:5000)

# Windows
netstat -ano | findstr :5000
taskkill /PID [PID] /F
```

### 前端端口冲突 (5173)

**解决方案**:

```bash
# macOS/Linux
lsof -i :5173
kill -9 $(lsof -t -i:5173)

# Windows
netstat -ano | findstr :5173
taskkill /PID [PID] /F
```

---

## 环境变量配置

创建 `backend/.env` 文件来覆盖默认配置:

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3307/energy_station

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 其他配置...
```

---

## Docker 内部端口 vs 外部端口

### 理解端口映射

```yaml
ports:
  - "3307:3306"
    ↑     ↑
    |     └─ 容器内部端口（固定为 3306）
    └─ 主机外部端口（可以修改）
```

**重要**: 
- 容器内部端口始终是 **3306**（MySQL 默认）
- 主机外部端口可以是 **3307** 或其他任意端口
- 应用连接时使用**外部端口**（3307）

### 示例

```yaml
# docker-compose.yml
mysql:
  ports:
    - "3307:3306"  # 主机:容器
```

```python
# backend/config.py
# 连接时使用主机端口 3307
DATABASE_URL = 'mysql+pymysql://root:password@localhost:3307/energy_station'
```

---

## 生产环境建议

### 1. 使用标准端口
生产环境建议使用标准端口（3306, 6379），通过防火墙和网络隔离保证安全。

### 2. 不暴露数据库端口
```yaml
mysql:
  # 不映射到主机端口，只在 Docker 网络内访问
  expose:
    - "3306"
  # 移除 ports 配置
```

### 3. 使用环境变量
```bash
# 生产环境使用环境变量
export DATABASE_URL="mysql+pymysql://user:pass@db-host:3306/dbname"
```

---

## 故障排查清单

- [ ] 运行端口检查工具
- [ ] 确认 Docker 容器正常启动
- [ ] 检查配置文件中的端口号是否一致
- [ ] 查看 Docker 日志: `docker compose logs mysql`
- [ ] 测试数据库连接: `mysql -h 127.0.0.1 -P 3307 -u root -p`
- [ ] 检查防火墙设置

---

## 获取帮助

如果仍然遇到端口问题:

1. 运行 `./check-ports.sh` 或 `check-ports.bat`
2. 查看完整错误日志
3. 检查 [QUICKSTART.md](QUICKSTART.md) 故障排查部分
4. 提交 Issue 并附上错误信息

---

**最后更新**: 2026-04-10
