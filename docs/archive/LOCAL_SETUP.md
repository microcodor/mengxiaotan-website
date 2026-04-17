# 本地开发环境配置指南

## 环境要求

### 必需软件
- **Python**: 3.8+ (推荐 3.12)
- **Node.js**: 16+ (推荐 24.x)
- **MySQL**: 5.7+ 或 8.0+
- **Redis**: 5.0+

### 可选软件
- **Git**: 版本控制
- **VS Code**: 推荐的IDE

---

## 数据库配置

### MySQL
- **Host**: localhost
- **Port**: 3306
- **User**: root
- **Password**: jinchun123
- **Database**: energy_station

### Redis
- **Host**: localhost
- **Port**: 6379
- **Password**: 123456
- **Database**: 0

---

## 快速启动

### 1. 克隆项目（如果还没有）
```bash
git clone <repository-url>
cd mengxiaotan-website
```

### 2. 配置环境变量
项目已经包含了 `backend/.env` 文件，配置如下：
```env
DATABASE_URL=mysql+pymysql://root:jinchun123@localhost:3306/energy_station
REDIS_URL=redis://:123456@localhost:6379/0
```

如需修改，请编辑 `backend/.env` 文件。

### 3. 启动服务
```bash
# 给脚本添加执行权限
chmod +x start_local.sh stop_local.sh

# 启动所有服务
./start_local.sh
```

启动脚本会自动：
1. ✅ 检查Python、Node.js、MySQL、Redis
2. ✅ 检查端口占用（5001、5173）
3. ✅ 安装Python依赖
4. ✅ 创建MySQL数据库（如果不存在）
5. ✅ 运行数据库迁移
6. ✅ 初始化测试数据
7. ✅ 启动后端服务（端口5001）
8. ✅ 安装Node.js依赖
9. ✅ 启动前端服务（端口5173）

### 4. 访问应用
- **前端**: http://localhost:5173
- **后端API**: http://localhost:5001/api
- **管理后台**: http://localhost:5173/admin
- **API文档**: http://localhost:5001/swagger-ui

### 5. 登录账号
- **管理员**: 13800138000 / admin123
- **测试用户**: 13900139000 / test123

### 6. 停止服务
```bash
# 方式1: 按 Ctrl+C（如果在前台运行）

# 方式2: 运行停止脚本
./stop_local.sh
```

---

## 手动启动（如果自动脚本失败）

### 后端服务
```bash
cd backend

# 创建虚拟环境（首次）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建数据库
mysql -h localhost -P 3306 -u root -pjinchun123 -e "CREATE DATABASE IF NOT EXISTS energy_station CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 初始化数据库
python init_db.py

# 启动服务
python app.py
```

### 前端服务
```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

---

## 常见问题

### 1. MySQL连接失败
**错误**: `Can't connect to MySQL server`

**解决方案**:
```bash
# 检查MySQL是否运行
mysql -h localhost -P 3306 -u root -pjinchun123 -e "SELECT 1"

# 如果失败，启动MySQL服务
# macOS (Homebrew)
brew services start mysql

# Linux (systemd)
sudo systemctl start mysql

# 或检查密码是否正确
```

### 2. Redis连接失败
**错误**: `Error connecting to Redis`

**解决方案**:
```bash
# 检查Redis是否运行
redis-cli -h localhost -p 6379 -a 123456 PING

# 如果失败，启动Redis服务
# macOS (Homebrew)
brew services start redis

# Linux (systemd)
sudo systemctl start redis

# 或检查密码是否正确
```

### 3. 端口被占用
**错误**: `Address already in use`

**解决方案**:
```bash
# 查看占用端口的进程
lsof -i :5001  # 后端
lsof -i :5173  # 前端

# 终止进程
kill -9 <PID>

# 或使用停止脚本
./stop_local.sh
```

### 4. Python依赖安装失败
**错误**: `pip install` 失败

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果是M1/M2 Mac，某些包可能需要特殊处理
arch -arm64 pip install -r requirements.txt
```

### 5. 数据库迁移失败
**错误**: `alembic.util.exc.CommandError`

**解决方案**:
```bash
cd backend
source venv/bin/activate

# 删除旧的迁移
rm -rf migrations/

# 重新初始化
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 或直接运行初始化脚本
python init_db.py
```

---

## 开发工具

### VS Code推荐插件
- **Python**: Python语言支持
- **Pylance**: Python智能提示
- **ESLint**: JavaScript/TypeScript代码检查
- **Prettier**: 代码格式化
- **Volar**: Vue 3支持（如果使用Vue）
- **Thunder Client**: API测试

### 数据库管理工具
- **MySQL Workbench**: 官方GUI工具
- **DBeaver**: 跨平台数据库工具
- **TablePlus**: macOS推荐
- **Navicat**: 商业工具

### Redis管理工具
- **RedisInsight**: 官方GUI工具
- **Another Redis Desktop Manager**: 开源工具
- **Medis**: macOS推荐

---

## 项目结构

```
mengxiaotan-website/
├── backend/                 # 后端服务
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── __init__.py    # 应用初始化
│   ├── migrations/         # 数据库迁移
│   ├── logs/              # 日志文件
│   ├── uploads/           # 上传文件
│   ├── venv/              # Python虚拟环境
│   ├── .env               # 环境变量
│   ├── config.py          # 配置文件
│   ├── app.py             # 应用入口
│   ├── init_db.py         # 数据库初始化
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端服务
│   ├── src/               # 源代码
│   │   ├── pages/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   ├── lib/          # 工具库
│   │   └── main.tsx      # 应用入口
│   ├── public/            # 静态资源
│   ├── node_modules/      # Node.js依赖
│   ├── package.json       # 项目配置
│   └── vite.config.ts     # Vite配置
├── crawler/                # 爬虫服务
│   └── energy_crawler/    # Scrapy爬虫
├── start_local.sh         # 本地启动脚本
├── stop_local.sh          # 本地停止脚本
└── LOCAL_SETUP.md         # 本文档
```

---

## 环境切换

### 从Docker切换到本地
1. 停止Docker服务：`./stop.sh` 或 `docker compose down`
2. 启动本地服务：`./start_local.sh`

### 从本地切换到Docker
1. 停止本地服务：`./stop_local.sh` 或 `Ctrl+C`
2. 启动Docker服务：`./start.sh` 或 `docker compose up -d`

---

## 下一步

- 📖 阅读 [README.md](README.md) 了解项目详情
- 🐛 查看 [CRAWLER_UI_ENHANCEMENT.md](CRAWLER_UI_ENHANCEMENT.md) 了解爬虫功能
- 📝 查看 [API文档](http://localhost:5001/swagger-ui) 了解接口
- 🧪 运行测试：`bash test_crawler_apis.sh`

---

## 技术支持

如遇到问题，请：
1. 查看本文档的"常见问题"部分
2. 检查日志文件：`backend/logs/app.log`
3. 查看控制台输出
4. 提交Issue到项目仓库

---

**最后更新**: 2026-04-13  
**版本**: v1.0
