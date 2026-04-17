# 快速开始指南

## 5 分钟快速启动

### 1️⃣ 选择你的操作系统

<table>
<tr>
<td width="33%">

#### 🍎 macOS
```bash
chmod +x start.sh
./start.sh
```

</td>
<td width="33%">

#### 🐧 Linux
```bash
chmod +x start.sh
./start.sh
```

</td>
<td width="33%">

#### 🪟 Windows
双击 `start.bat`
或
```cmd
start.bat
```

</td>
</tr>
</table>

### 2️⃣ 等待启动完成

启动脚本会自动：
- ✅ 检查系统环境
- ✅ 启动 Docker 容器
- ✅ 初始化数据库
- ✅ 安装依赖
- ✅ 启动前后端服务

⏱️ 首次启动约需 3-5 分钟

### 3️⃣ 访问应用

| 服务 | 地址 | 说明 |
|------|------|------|
| 🎨 前端门户 | http://localhost:5173 | 用户访问入口 |
| 📊 管理后台 | http://localhost:5173/admin | 管理员后台 |
| 📈 数据看板 | http://localhost:5173/dashboard | 数据可视化 |
| 🔌 后端 API | http://localhost:5000 | API 接口 |

### 4️⃣ 登录系统

#### 管理员账号
- 📱 手机号：`13800138000`
- 🔑 密码：`admin123`

#### 测试用户
- 📱 手机号：`13900139000`
- 🔑 密码：`test123`

---

## 常用操作

### 停止服务

<table>
<tr>
<td width="50%">

#### macOS / Linux
```bash
./stop.sh
```

</td>
<td width="50%">

#### Windows
双击 `stop.bat`
或
```cmd
stop.bat
```

</td>
</tr>
</table>

### 查看日志

```bash
# Docker Compose v2
docker compose logs -f backend
docker compose logs -f mysql

# Docker Compose v1
docker-compose logs -f backend
docker-compose logs -f mysql
```

### 重启服务

```bash
# 停止
./stop.sh  # 或 stop.bat

# 启动
./start.sh  # 或 start.bat
```

### 运行爬虫

```bash
cd crawler

# 抓取发改委数据
scrapy crawl ndrc

# 抓取煤炭数据
scrapy crawl coal

# 抓取电力数据
scrapy crawl power

# 抓取新能源数据
scrapy crawl newenergy

# 抓取国家能源局数据
scrapy crawl nea
```

---

## 功能演示

### 1. 查看首页
访问 http://localhost:5173
- 焦点资讯轮播
- 今日 AI 建议
- 分类快捷入口
- 最新资讯列表

### 2. 查看数据看板
访问 http://localhost:5173/dashboard
- 能源核心指标
- 价格走势图表
- 分类统计分析

### 3. 管理后台
访问 http://localhost:5173/admin
- 数据仪表盘
- 文章管理
- 用户管理
- 生成每日简报

### 4. 生成 AI 简报
1. 登录管理后台
2. 点击"生成简报"按钮
3. 查看 AI 生成的每日简报

---

## 故障排查

## 故障排查

### ❌ Python 依赖安装失败

**症状**: 
```
ERROR: Could not find a version that satisfies the requirement Flask==3.0.0
ModuleNotFoundError: No module named 'flask'
```

**原因**: 
- 网络连接问题
- pip 源访问慢或不可用
- Python 版本不兼容

**解决**:

#### 🔧 方案1: 使用依赖修复脚本（推荐）
```bash
# macOS/Linux
chmod +x fix-dependencies.sh
./fix-dependencies.sh

# Windows
fix-dependencies.bat
```

#### 🔧 方案2: 手动安装
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 升级 pip
pip install --upgrade pip

# 使用国内镜像源安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 🔧 方案3: 配置 pip 镜像源
```bash
# macOS/Linux
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
EOF

# Windows
# 创建 %APPDATA%\pip\pip.ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 🔧 方案4: 检查 Python 版本
```bash
python --version  # 需要 3.9 或更高版本

# 如果版本过低，升级 Python
# macOS: brew install python@3.11
# Windows: 从 python.org 下载安装
```

### ❌ 端口被占用（最常见）

**症状**: 
```
Error: ports are not available: listen tcp 0.0.0.0:3306: bind: address already in use
```

**原因**: 本地已经运行了 MySQL 或其他服务占用了端口

**解决**:

#### 🔍 步骤1: 检查端口占用
```bash
# macOS/Linux
chmod +x check-ports.sh
./check-ports.sh

# Windows
check-ports.bat
```

#### 🛠️ 步骤2: 选择解决方案

**方案A: 使用项目配置的 3307 端口（推荐）**
```bash
# 项目已配置使用 3307 端口，直接启动即可
./start.sh  # 或 start.bat
```

**方案B: 停止本地 MySQL**
```bash
# macOS
brew services stop mysql

# Linux
sudo systemctl stop mysql

# Windows
net stop MySQL80
```

**方案C: 修改为其他端口**
编辑 `docker-compose.yml`:
```yaml
mysql:
  ports:
    - "3308:3306"  # 改为 3308 或其他未占用端口
```

然后更新 `backend/config.py` 和 `crawler/energy_crawler/settings.py` 中的端口号。

### ❌ Docker 未启动
**症状**：提示 Docker 未安装或未运行

**解决**：
- macOS/Windows: 启动 Docker Desktop 应用
- Linux: `sudo systemctl start docker`

### ❌ 端口被占用
**症状**：提示端口 5000 或 5173 已被占用

**解决**：
```bash
# macOS/Linux
lsof -i :5000
lsof -i :5173
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### ❌ 数据库连接失败
**症状**：后端无法连接数据库

**解决**：
```bash
# 检查 MySQL 容器状态
docker ps | grep mysql

# 查看 MySQL 日志
docker compose logs mysql

# 重启 MySQL
docker compose restart mysql
```

### ❌ 前端无法访问后端
**症状**：前端页面显示网络错误

**解决**：
1. 检查后端是否正常运行
2. 检查浏览器控制台错误信息
3. 确认 API 地址配置正确

---

## 下一步

### 📚 深入学习
- [README.md](README.md) - 完整项目文档
- [DEVELOPMENT.md](DEVELOPMENT.md) - 开发指南
- [PLATFORM.md](PLATFORM.md) - 跨平台部署指南
- [PROGRESS.md](PROGRESS.md) - 开发进度报告

### 🔧 开发定制
- 添加新的数据源爬虫
- 自定义 AI 简报模板
- 扩展数据看板指标
- 开发新的功能模块

### 🚀 生产部署
- 配置生产环境变量
- 设置 Nginx 反向代理
- 配置 SSL 证书
- 设置定时备份

---

## 获取帮助

- 📖 查看文档：[README.md](README.md)
- 🐛 报告问题：提交 GitHub Issue
- 💬 技术交流：查看项目讨论区

---

**祝你使用愉快！** 🎉
