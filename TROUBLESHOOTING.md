# 故障排查指南

本文档提供常见问题的详细解决方案。

---

## 目录
- [Python 依赖问题](#python-依赖问题)
- [端口冲突问题](#端口冲突问题)
- [Docker 问题](#docker-问题)
- [数据库问题](#数据库问题)
- [网络问题](#网络问题)
- [其他问题](#其他问题)

---

## Python 依赖问题

### 问题 1: Flask 安装失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement Flask==3.0.0
ERROR: No matching distribution found for Flask==3.0.0
```

**原因**:
- PyPI 官方源访问慢或不可用
- 网络连接问题
- pip 版本过旧

**解决方案**:

#### 方案 A: 使用修复脚本（最简单）
```bash
# macOS/Linux
chmod +x fix-dependencies.sh
./fix-dependencies.sh

# Windows
fix-dependencies.bat
```

#### 方案 B: 使用国内镜像源
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 清华大学镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或中科大镜像
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
```

#### 方案 C: 永久配置镜像源

**macOS/Linux**:
```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

**Windows**:
```cmd
# 创建文件 %APPDATA%\pip\pip.ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

#### 方案 D: 升级 pip
```bash
python -m pip install --upgrade pip
```

### 问题 2: ModuleNotFoundError

**症状**:
```
ModuleNotFoundError: No module named 'flask'
```

**原因**:
- 虚拟环境未激活
- 依赖未安装

**解决方案**:
```bash
cd backend

# 确保虚拟环境已创建
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 3: Python 版本不兼容

**症状**:
```
ERROR: Package 'xxx' requires a different Python: 3.8.0 not in '>=3.9'
```

**解决方案**:

检查 Python 版本:
```bash
python --version
python3 --version
```

需要 Python 3.9 或更高版本。

**升级 Python**:

**macOS**:
```bash
brew install python@3.11
```

**Linux (Ubuntu)**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

**Windows**:
从 https://www.python.org/downloads/ 下载安装

---

## 端口冲突问题

### 问题 1: MySQL 端口 3306 被占用

**症状**:
```
Error: ports are not available: listen tcp 0.0.0.0:3306: bind: address already in use
```

**解决方案**:

#### 方案 A: 使用端口检查工具
```bash
# macOS/Linux
chmod +x check-ports.sh
./check-ports.sh

# Windows
check-ports.bat
```

#### 方案 B: 使用项目配置的 3307 端口
项目已配置使用 3307 端口，直接启动即可：
```bash
./start.sh  # 或 start.bat
```

#### 方案 C: 停止本地 MySQL
```bash
# macOS
brew services stop mysql

# Linux
sudo systemctl stop mysql

# Windows
net stop MySQL80
```

#### 方案 D: 查找并停止占用进程
```bash
# macOS/Linux
lsof -i :3306
kill -9 $(lsof -t -i:3306)

# Windows
netstat -ano | findstr :3306
taskkill /PID [PID] /F
```

### 问题 2: 其他端口被占用

参考 [PORT_CONFIG.md](PORT_CONFIG.md) 获取详细的端口配置说明。

---

## Docker 问题

### 问题 1: Docker 未运行

**症状**:
```
Cannot connect to the Docker daemon
```

**解决方案**:

**macOS/Windows**:
1. 打开 Docker Desktop 应用
2. 等待 Docker 引擎启动完成
3. 重新运行启动脚本

**Linux**:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 问题 2: Docker Compose 命令不存在

**症状**:
```
docker-compose: command not found
```

**解决方案**:

检查 Docker Compose 版本:
```bash
# 新版本
docker compose version

# 旧版本
docker-compose --version
```

如果都不存在，安装 Docker Compose:

**macOS/Windows**: 更新 Docker Desktop

**Linux**:
```bash
# 安装 Docker Compose 插件
sudo apt install docker-compose-plugin

# 或安装独立版本
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 问题 3: 容器启动失败

**症状**:
```
Error response from daemon: driver failed programming external connectivity
```

**解决方案**:

1. 停止所有容器:
```bash
docker compose down
```

2. 清理网络:
```bash
docker network prune
```

3. 重启 Docker:
```bash
# macOS/Windows: 重启 Docker Desktop

# Linux
sudo systemctl restart docker
```

4. 重新启动:
```bash
./start.sh
```

---

## 数据库问题

### 问题 1: 数据库连接失败

**症状**:
```
Can't connect to MySQL server on 'localhost'
```

**解决方案**:

1. 检查 MySQL 容器状态:
```bash
docker ps | grep mysql
```

2. 查看 MySQL 日志:
```bash
docker compose logs mysql
```

3. 等待 MySQL 完全启动:
```bash
# MySQL 需要 10-15 秒启动时间
sleep 15
```

4. 测试连接:
```bash
mysql -h 127.0.0.1 -P 3307 -u root -p
# 密码: password
```

### 问题 2: 数据库初始化失败

**症状**:
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError)
```

**解决方案**:

1. 确保 MySQL 容器正在运行
2. 检查端口配置是否正确
3. 手动初始化:
```bash
cd backend
source venv/bin/activate
python init_db.py
```

### 问题 3: 表已存在错误

**症状**:
```
Table 'xxx' already exists
```

**解决方案**:

重置数据库:
```bash
# 停止服务
./stop.sh

# 删除数据卷
docker compose down -v

# 重新启动
./start.sh
```

---

## 网络问题

### 问题 1: 前端无法访问后端

**症状**:
- 前端页面显示网络错误
- API 请求失败

**解决方案**:

1. 检查后端是否运行:
```bash
curl http://localhost:5000
```

2. 检查 CORS 配置:
```python
# backend/config.py
CORS_ORIGINS = 'http://localhost:5173'
```

3. 检查浏览器控制台错误信息

4. 确认 API 地址配置:
```typescript
// frontend/src/lib/api.ts
baseURL: '/api'  // 或 'http://localhost:5000/api'
```

### 问题 2: npm 安装慢

**解决方案**:

使用国内镜像:
```bash
# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 或永久配置
npm config set registry https://registry.npmmirror.com
```

---

## 其他问题

### 问题 1: 权限被拒绝

**症状**:
```
Permission denied
```

**解决方案**:

给脚本添加执行权限:
```bash
chmod +x start.sh stop.sh check-ports.sh fix-dependencies.sh
```

### 问题 2: 虚拟环境激活失败

**症状**:
```
venv/bin/activate: No such file or directory
```

**解决方案**:

重新创建虚拟环境:
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 3: 爬虫运行失败

**症状**:
```
ImportError: No module named 'scrapy'
```

**解决方案**:

安装爬虫依赖:
```bash
cd crawler
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 完整重置流程

如果遇到无法解决的问题，可以尝试完整重置:

```bash
# 1. 停止所有服务
./stop.sh  # 或 stop.bat

# 2. 清理 Docker
docker compose down -v
docker system prune -f

# 3. 删除虚拟环境
rm -rf backend/venv
rm -rf frontend/node_modules

# 4. 重新启动
./start.sh  # 或 start.bat
```

---

## 获取帮助

如果以上方案都无法解决问题:

1. 查看完整错误日志
2. 检查系统环境:
   - Python 版本
   - Node.js 版本
   - Docker 版本
   - 操作系统版本
3. 提交 Issue 并附上:
   - 错误信息
   - 系统环境
   - 已尝试的解决方案

---

## 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [PORT_CONFIG.md](PORT_CONFIG.md) - 端口配置说明
- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南
- [README.md](README.md) - 主文档

---

**最后更新**: 2026-04-10
