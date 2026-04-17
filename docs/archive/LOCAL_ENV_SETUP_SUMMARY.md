# 本地开发环境配置完成总结

**配置日期**: 2026-04-13  
**状态**: ✅ 已完成

---

## 配置内容

已将开发环境从Docker切换到本地运行，使用本地MySQL和Redis。

### 数据库配置

#### MySQL
- **Host**: localhost
- **Port**: 3306
- **User**: root
- **Password**: jinchun123
- **Database**: energy_station

#### Redis
- **Host**: localhost
- **Port**: 6379
- **Password**: 123456
- **Database**: 0

---

## 修改的文件

### 1. 后端配置
- ✅ `backend/.env` - 创建本地环境变量文件
- ✅ `backend/config.py` - 更新默认数据库连接
- ✅ `backend/app/__init__.py` - 更新Redis连接配置
- ✅ `backend/requirements.txt` - 保持PyMySQL驱动

### 2. 启动脚本
- ✅ `start_local.sh` - 创建本地启动脚本
- ✅ `stop_local.sh` - 创建本地停止脚本

### 3. 文档
- ✅ `LOCAL_SETUP.md` - 创建详细的配置指南
- ✅ `LOCAL_ENV_SETUP_SUMMARY.md` - 本文档

---

## 配置详情

### backend/.env
```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:jinchun123@localhost:3306/energy_station

# Redis配置
REDIS_URL=redis://:123456@localhost:6379/0

# 其他配置
FLASK_ENV=development
PORT=5001
SECRET_KEY=dev-secret-key-for-local-development
JWT_SECRET_KEY=jwt-secret-key-for-local-development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### backend/config.py
```python
# 默认数据库连接
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://root:jinchun123@localhost:3306/energy_station'
)

# 默认Redis连接
REDIS_URL = os.getenv(
    'REDIS_URL', 
    'redis://:123456@localhost:6379/0'
)
```

### backend/app/__init__.py
```python
# Redis连接（支持密码）
from urllib.parse import urlparse
redis_url = app.config['REDIS_URL']
parsed = urlparse(redis_url)

redis_client = Redis(
    host=parsed.hostname or 'localhost',
    port=parsed.port or 6379,
    db=int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 0,
    password=parsed.password,
    decode_responses=True
)
```

---

## 使用方法

### 快速启动
```bash
# 1. 给脚本添加执行权限
chmod +x start_local.sh stop_local.sh

# 2. 启动服务
./start_local.sh
```

### 启动脚本功能
`start_local.sh` 会自动执行以下操作：

1. **环境检查**
   - ✅ 检测操作系统（Mac/Linux）
   - ✅ 检查Python、Node.js版本
   - ✅ 检查MySQL连接（localhost:3306）
   - ✅ 检查Redis连接（localhost:6379）
   - ✅ 检查端口占用（5001、5173）

2. **后端服务**
   - ✅ 创建Python虚拟环境（如果不存在）
   - ✅ 安装Python依赖
   - ✅ 创建MySQL数据库（如果不存在）
   - ✅ 运行数据库迁移
   - ✅ 初始化测试数据
   - ✅ 启动Flask服务（端口5001）

3. **前端服务**
   - ✅ 安装Node.js依赖
   - ✅ 启动Vite开发服务器（端口5173）

### 停止服务
```bash
# 方式1: 按 Ctrl+C（如果在前台运行）

# 方式2: 运行停止脚本
./stop_local.sh
```

### 访问应用
- **前端**: http://localhost:5173
- **后端API**: http://localhost:5001/api
- **管理后台**: http://localhost:5173/admin
- **API文档**: http://localhost:5001/swagger-ui

### 登录账号
- **管理员**: 13800138000 / admin123
- **测试用户**: 13900139000 / test123

---

## 前置条件

### 必需服务
在启动前，请确保以下服务正在运行：

#### 1. MySQL
```bash
# 检查MySQL是否运行
mysql -h localhost -P 3306 -u root -pjinchun123 -e "SELECT 1"

# macOS启动MySQL
brew services start mysql

# Linux启动MySQL
sudo systemctl start mysql
```

#### 2. Redis
```bash
# 检查Redis是否运行
redis-cli -h localhost -p 6379 -a 123456 PING

# macOS启动Redis
brew services start redis

# Linux启动Redis
sudo systemctl start redis
```

---

## 与Docker环境的区别

### Docker环境（原配置）
- MySQL: localhost:3307 (Docker映射)
- Redis: localhost:6380 (Docker映射)
- 数据库密码: password
- Redis无密码
- 需要Docker Desktop运行

### 本地环境（新配置）
- MySQL: localhost:3306 (本地MySQL)
- Redis: localhost:6379 (本地Redis)
- 数据库密码: jinchun123
- Redis密码: 123456
- 不需要Docker

---

## 环境切换

### 从Docker切换到本地
```bash
# 1. 停止Docker服务
./stop.sh
# 或
docker compose down

# 2. 启动本地服务
./start_local.sh
```

### 从本地切换到Docker
```bash
# 1. 停止本地服务
./stop_local.sh
# 或按 Ctrl+C

# 2. 启动Docker服务
./start.sh
# 或
docker compose up -d
```

---

## 数据迁移（可选）

如果需要从Docker MySQL迁移数据到本地MySQL：

```bash
# 1. 确保Docker MySQL正在运行
docker compose up -d mysql

# 2. 导出Docker MySQL数据
docker exec energy_mysql mysqldump -u root -ppassword energy_station > backup.sql

# 3. 导入到本地MySQL
mysql -h localhost -P 3306 -u root -pjinchun123 energy_station < backup.sql

# 4. 清理备份文件
rm backup.sql
```

---

## 常见问题

### 1. MySQL连接失败
**错误**: `Can't connect to MySQL server`

**检查**:
```bash
# 测试连接
mysql -h localhost -P 3306 -u root -pjinchun123 -e "SELECT 1"

# 检查MySQL服务
brew services list | grep mysql  # macOS
sudo systemctl status mysql      # Linux
```

### 2. Redis连接失败
**错误**: `Error connecting to Redis`

**检查**:
```bash
# 测试连接
redis-cli -h localhost -p 6379 -a 123456 PING

# 检查Redis服务
brew services list | grep redis  # macOS
sudo systemctl status redis      # Linux
```

### 3. 端口被占用
**错误**: `Address already in use`

**解决**:
```bash
# 查看占用端口的进程
lsof -i :5001  # 后端
lsof -i :5173  # 前端

# 使用停止脚本清理
./stop_local.sh
```

### 4. 数据库不存在
**错误**: `Unknown database 'energy_station'`

**解决**:
```bash
# 手动创建数据库
mysql -h localhost -P 3306 -u root -pjinchun123 -e "CREATE DATABASE energy_station CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 或重新运行启动脚本（会自动创建）
./start_local.sh
```

---

## 测试验证

### 1. 测试后端API
```bash
# 测试登录
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}'

# 测试爬虫列表
curl http://localhost:5001/api/crawler/spiders \
  -H "Authorization: Bearer <token>"
```

### 2. 测试前端
- 打开浏览器访问 http://localhost:5173
- 使用管理员账号登录
- 访问管理后台 http://localhost:5173/admin

### 3. 测试爬虫功能
```bash
# 运行爬虫API测试
bash test_crawler_apis.sh
```

---

## 下一步

1. **启动服务**
   ```bash
   ./start_local.sh
   ```

2. **访问应用**
   - 前端: http://localhost:5173
   - 管理后台: http://localhost:5173/admin

3. **开始开发**
   - 后端代码: `backend/app/`
   - 前端代码: `frontend/src/`

4. **查看文档**
   - 详细配置: [LOCAL_SETUP.md](LOCAL_SETUP.md)
   - 项目说明: [README.md](README.md)
   - 爬虫功能: [CRAWLER_UI_ENHANCEMENT.md](CRAWLER_UI_ENHANCEMENT.md)

---

## 技术栈

### 后端
- **框架**: Flask 3.0+
- **数据库**: MySQL 8.0 + PyMySQL
- **缓存**: Redis 5.0+
- **ORM**: SQLAlchemy
- **认证**: JWT (Flask-JWT-Extended)
- **API**: Flask-Smorest (OpenAPI 3.0)
- **爬虫**: Scrapy 2.11+

### 前端
- **框架**: React 18
- **语言**: TypeScript
- **构建**: Vite 5
- **路由**: React Router
- **状态**: React Query
- **UI**: Tailwind CSS

---

## 总结

✅ **本地开发环境配置完成！**

现在你可以：
- 使用本地MySQL（localhost:3306）
- 使用本地Redis（localhost:6379）
- 不依赖Docker运行开发环境
- 快速启动和停止服务
- 方便调试和开发

如有问题，请查看 [LOCAL_SETUP.md](LOCAL_SETUP.md) 或提交Issue。

---

**配置完成时间**: 2026-04-13 19:30  
**版本**: v1.0  
**状态**: ✅ 就绪
