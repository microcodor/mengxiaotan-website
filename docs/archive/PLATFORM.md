# 跨平台部署指南

本项目支持在 Windows、macOS 和 Linux 系统上运行。

---

## 系统要求

### 所有平台
- **Docker Desktop**: 最新版本
- **Python**: 3.9 或更高版本
- **Node.js**: 18 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘**: 至少 5GB 可用空间

---

## macOS 部署

### 1. 安装依赖

#### 安装 Homebrew（如果未安装）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 安装 Python
```bash
brew install python@3.11
```

#### 安装 Node.js
```bash
brew install node
```

#### 安装 Docker Desktop
下载并安装：https://www.docker.com/products/docker-desktop

### 2. 启动项目
```bash
chmod +x start.sh
./start.sh
```

### 3. 停止项目
```bash
chmod +x stop.sh
./stop.sh
```

### 常见问题

**问题**: Permission denied
```bash
# 解决方案：添加执行权限
chmod +x start.sh stop.sh
```

**问题**: Docker 未运行
```bash
# 解决方案：启动 Docker Desktop 应用
open -a Docker
```

---

## Linux 部署

### 1. 安装依赖

#### Ubuntu / Debian
```bash
# 更新包列表
sudo apt update

# 安装 Python
sudo apt install python3 python3-pip python3-venv

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose-plugin
```

#### CentOS / RHEL
```bash
# 安装 Python
sudo yum install python3 python3-pip

# 安装 Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### 2. 启动项目
```bash
chmod +x start.sh
./start.sh
```

### 3. 停止项目
```bash
chmod +x stop.sh
./stop.sh
```

### 常见问题

**问题**: Docker permission denied
```bash
# 解决方案：将用户添加到 docker 组
sudo usermod -aG docker $USER
# 重新登录或运行
newgrp docker
```

**问题**: 端口被占用
```bash
# 查看端口占用
sudo lsof -i :5000
sudo lsof -i :5173

# 杀死进程
sudo kill -9 <PID>
```

---

## Windows 部署

### 1. 安装依赖

#### 安装 Python
1. 下载：https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 验证安装：
```cmd
python --version
```

#### 安装 Node.js
1. 下载：https://nodejs.org/
2. 运行安装程序
3. 验证安装：
```cmd
node --version
npm --version
```

#### 安装 Docker Desktop
1. 下载：https://www.docker.com/products/docker-desktop
2. 安装并启动 Docker Desktop
3. 确保 WSL 2 已启用（Windows 10/11）

### 2. 启动项目

#### 方式一：双击运行
直接双击 `start.bat` 文件

#### 方式二：命令行运行
```cmd
start.bat
```

### 3. 停止项目
双击 `stop.bat` 或运行：
```cmd
stop.bat
```

### 常见问题

**问题**: Docker Desktop 未启动
```
解决方案：
1. 打开 Docker Desktop 应用
2. 等待 Docker 引擎启动完成
3. 重新运行 start.bat
```

**问题**: Python 命令未找到
```cmd
# 解决方案：检查 Python 是否在 PATH 中
where python
# 如果没有输出，重新安装 Python 并勾选 "Add to PATH"
```

**问题**: 虚拟环境激活失败
```cmd
# 解决方案：允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**问题**: 端口被占用
```cmd
# 查看端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :5173

# 杀死进程
taskkill /PID <PID> /F
```

---

## Docker Compose 版本差异

### 旧版本（docker-compose）
```bash
docker-compose up -d
docker-compose down
docker-compose logs -f
```

### 新版本（docker compose）
```bash
docker compose up -d
docker compose down
docker compose logs -f
```

**说明**：
- Docker Desktop 最新版本使用 `docker compose`（空格）
- 旧版本使用 `docker-compose`（连字符）
- 启动脚本会自动检测并使用正确的命令

---

## 环境变量配置

### macOS / Linux
创建 `backend/.env` 文件：
```bash
cd backend
cat > .env << EOF
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/energy_station
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
EOF
```

### Windows
创建 `backend\.env` 文件：
```cmd
cd backend
echo DATABASE_URL=mysql+pymysql://root:password@localhost:3306/energy_station > .env
echo REDIS_URL=redis://localhost:6379/0 >> .env
echo JWT_SECRET_KEY=your-secret-key-change-in-production >> .env
echo FLASK_ENV=development >> .env
```

---

## 性能优化建议

### macOS
- 为 Docker Desktop 分配足够的资源（设置 -> Resources）
- 推荐：4 CPU、8GB 内存

### Linux
- 使用原生 Docker（性能最佳）
- 考虑使用 Docker Swarm 或 Kubernetes 进行生产部署

### Windows
- 确保使用 WSL 2 后端（性能更好）
- 为 Docker Desktop 分配足够的资源
- 推荐：4 CPU、8GB 内存
- 将项目文件放在 WSL 文件系统中以获得更好的性能

---

## 故障排查

### 检查 Docker 状态
```bash
# macOS / Linux
docker info
docker ps

# Windows
docker info
docker ps
```

### 检查服务日志
```bash
# 后端日志
docker compose logs -f backend

# 数据库日志
docker compose logs -f mysql

# Redis 日志
docker compose logs -f redis
```

### 重置环境
```bash
# 停止所有服务
./stop.sh  # 或 stop.bat

# 删除所有容器和卷
docker compose down -v

# 重新启动
./start.sh  # 或 start.bat
```

---

## 生产环境部署

### 使用 Docker Compose（推荐）
```bash
# 构建生产镜像
docker compose -f docker-compose.prod.yml build

# 启动生产服务
docker compose -f docker-compose.prod.yml up -d
```

### 使用 Kubernetes
参考 `k8s/` 目录中的配置文件（待添加）

---

## 技术支持

如遇到问题，请：
1. 查看本文档的故障排查部分
2. 查看 [DEVELOPMENT.md](DEVELOPMENT.md) 开发指南
3. 提交 Issue 到 GitHub

---

**最后更新**: 2026-04-10
