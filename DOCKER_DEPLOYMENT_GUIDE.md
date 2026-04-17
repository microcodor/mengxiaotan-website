# Docker 部署指南

## 概述

本文档说明如何使用 Docker 和 Docker Compose 部署蒙小碳·能源站。

## 前置要求

### 必需软件
- Docker 20.10+
- Docker Compose 2.0+（或 docker-compose 1.29+）

### 系统要求
- CPU: 2核+
- 内存: 4GB+
- 磁盘: 20GB+

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd mengxiaotan-website
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑环境变量（必须修改密钥和API配置）
vim .env
```

**重要配置项**：
```bash
# 生产环境必须修改这些密钥
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-random-jwt-secret-key-here

# MiniMax AI配置（用于生成简报）
MINIMAX_API_KEY=your-minimax-api-key
MINIMAX_GROUP_ID=your-minimax-group-id

# 企业微信推送配置（用于消息推送）
WECHAT_WORK_CORPID=your-corp-id
WECHAT_WORK_CORPSECRET=your-corp-secret
WECHAT_WORK_AGENTID=your-agent-id
```

### 3. 启动服务

```bash
# 使用 docker compose（Docker Compose V2）
docker compose up -d

# 或使用 docker-compose（Docker Compose V1）
docker-compose up -d
```

### 4. 初始化数据库

```bash
# 进入后端容器
docker exec -it mengxiaotan_backend bash

# 运行数据库初始化脚本
python init_db.py

# 退出容器
exit
```

### 5. 访问应用

- **前端**: http://localhost:5173
- **后端API**: http://localhost:5001
- **管理后台**: http://localhost:5173/admin

**默认账号**：
- 管理员: 13800138000 / admin123
- 测试用户: 13900139000 / test123

## 服务说明

### 服务列表

| 服务 | 容器名 | 端口映射 | 说明 |
|------|--------|----------|------|
| MySQL | mengxiaotan_mysql | 3307:3306 | 数据库服务 |
| Redis | mengxiaotan_redis | 6380:6379 | 缓存服务 |
| Backend | mengxiaotan_backend | 5001:5000 | 后端API服务 |
| Frontend | mengxiaotan_frontend | 5173:80 | 前端Web服务 |
| Crawler | mengxiaotan_crawler | - | 爬虫服务（可选） |

### 服务依赖关系

```
Frontend → Backend → MySQL
                  → Redis
Crawler → MySQL
```

## 常用命令

### 查看服务状态

```bash
docker compose ps
```

### 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart backend
docker compose restart frontend
```

### 停止服务

```bash
# 停止所有服务
docker compose stop

# 停止并删除容器
docker compose down

# 停止并删除容器和数据卷（危险！会删除数据）
docker compose down -v
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build

# 或分步执行
docker compose build
docker compose up -d
```

### 进入容器

```bash
# 进入后端容器
docker exec -it mengxiaotan_backend bash

# 进入MySQL容器
docker exec -it mengxiaotan_mysql bash

# 在MySQL容器中连接数据库
docker exec -it mengxiaotan_mysql mysql -uroot -ppassword mengxiaotan
```

### 备份数据

```bash
# 备份MySQL数据
docker exec mengxiaotan_mysql mysqldump -uroot -ppassword mengxiaotan > backup_$(date +%Y%m%d).sql

# 备份Redis数据
docker exec mengxiaotan_redis redis-cli SAVE
docker cp mengxiaotan_redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

### 恢复数据

```bash
# 恢复MySQL数据
docker exec -i mengxiaotan_mysql mysql -uroot -ppassword mengxiaotan < backup_20260417.sql

# 恢复Redis数据
docker cp redis_backup_20260417.rdb mengxiaotan_redis:/data/dump.rdb
docker compose restart redis
```

## 爬虫服务

爬虫服务默认不启动，需要手动触发。

### 启动爬虫服务

```bash
# 使用 profile 启动爬虫
docker compose --profile crawler up -d crawler
```

### 运行特定爬虫

```bash
# 进入爬虫容器
docker exec -it mengxiaotan_crawler bash

# 运行特定爬虫
cd /app
scrapy crawl xinhua_real

# 或直接执行
docker exec mengxiaotan_crawler scrapy crawl xinhua_real
```

### 查看可用爬虫

```bash
docker exec mengxiaotan_crawler scrapy list
```

## 健康检查

### 检查服务健康状态

```bash
# 检查后端健康
curl http://localhost:5001/api/health

# 检查前端
curl http://localhost:5173

# 检查MySQL
docker exec mengxiaotan_mysql mysqladmin ping -h localhost -u root -ppassword

# 检查Redis
docker exec mengxiaotan_redis redis-cli ping
```

### 健康检查响应

**后端健康检查**：
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-17T10:00:00"
}
```

## 性能优化

### 调整Worker数量

编辑 `backend/Dockerfile`：
```dockerfile
CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:5000", "app:app"]
```

### 调整数据库连接池

编辑 `backend/config.py`：
```python
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
```

### 启用Redis缓存

```python
# 在需要缓存的地方使用
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': REDIS_URL})
```

## 监控和日志

### 日志位置

- **后端日志**: `backend/logs/`
- **Nginx日志**: 容器内 `/var/log/nginx/`
- **MySQL日志**: 容器内 `/var/log/mysql/`

### 查看实时日志

```bash
# 后端日志
docker compose logs -f backend

# 前端访问日志
docker compose logs -f frontend

# 数据库日志
docker compose logs -f mysql
```

### 日志轮转

编辑 `docker-compose.yml` 添加日志配置：
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 安全建议

### 1. 修改默认密码

```bash
# 修改MySQL root密码
docker exec -it mengxiaotan_mysql mysql -uroot -ppassword
ALTER USER 'root'@'%' IDENTIFIED BY 'new-strong-password';
FLUSH PRIVILEGES;

# 更新 docker-compose.yml 和 .env 中的密码
```

### 2. 使用强密钥

```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 更新 .env 文件
SECRET_KEY=<generated-key>
JWT_SECRET_KEY=<generated-key>
```

### 3. 限制端口暴露

生产环境建议只暴露必要端口：
```yaml
services:
  mysql:
    ports:
      - "127.0.0.1:3307:3306"  # 只允许本地访问
```

### 4. 使用HTTPS

配置Nginx SSL证书：
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ...
}
```

## 故障排查

### 问题1: 容器无法启动

**检查日志**：
```bash
docker compose logs backend
```

**常见原因**：
- 端口被占用
- 环境变量配置错误
- 依赖服务未就绪

**解决方法**：
```bash
# 检查端口占用
lsof -i :5001
lsof -i :5173
lsof -i :3307

# 重新构建
docker compose down
docker compose up -d --build
```

### 问题2: 数据库连接失败

**检查MySQL状态**：
```bash
docker compose ps mysql
docker compose logs mysql
```

**测试连接**：
```bash
docker exec -it mengxiaotan_mysql mysql -uroot -ppassword -e "SELECT 1"
```

**解决方法**：
```bash
# 等待MySQL完全启动
sleep 30

# 检查健康状态
docker inspect mengxiaotan_mysql | grep Health
```

### 问题3: 前端无法访问后端

**检查网络**：
```bash
docker network ls
docker network inspect mengxiaotan-website_default
```

**测试连接**：
```bash
# 从前端容器测试后端
docker exec mengxiaotan_frontend wget -O- http://backend:5000/api/health
```

**解决方法**：
- 检查 `nginx.conf` 中的 proxy_pass 配置
- 确保后端服务正常运行

### 问题4: 定时任务不执行

**检查调度器状态**：
```bash
docker exec mengxiaotan_backend python -c "from app.scheduler import get_scheduler; print(get_scheduler().get_jobs())"
```

**查看日志**：
```bash
docker compose logs -f backend | grep scheduler
```

**解决方法**：
- 确保 `ENABLE_SCHEDULER=true`
- 检查时区设置
- 查看错误日志

## 生产环境部署

### 1. 使用生产配置

```bash
# 设置环境变量
export FLASK_ENV=production

# 使用生产配置启动
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. 配置反向代理

使用Nginx作为反向代理：
```nginx
upstream backend {
    server localhost:5001;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5173;
    }
    
    location /api {
        proxy_pass http://backend;
    }
}
```

### 3. 配置域名和SSL

```bash
# 使用 Let's Encrypt
certbot --nginx -d yourdomain.com
```

### 4. 设置自动重启

```yaml
services:
  backend:
    restart: always
  frontend:
    restart: always
```

## 更新日志

### 2026-04-17
- ✅ 添加健康检查端点
- ✅ 优化Docker配置
- ✅ 添加环境变量支持
- ✅ 完善文档

## 参考资料

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Gunicorn文档](https://docs.gunicorn.org/)
- [Nginx文档](https://nginx.org/en/docs/)
