# Docker 快速参考

## 一键启动

```bash
# 1. 配置环境
cp .env.example .env && vim .env

# 2. 启动服务
docker compose up -d

# 3. 初始化数据库
docker exec -it mengxiaotan_backend python init_db.py

# 4. 访问应用
open http://localhost:5173
```

## 常用命令速查

### 服务管理
| 命令 | 说明 |
|------|------|
| `docker compose up -d` | 启动所有服务 |
| `docker compose down` | 停止并删除容器 |
| `docker compose restart` | 重启所有服务 |
| `docker compose ps` | 查看服务状态 |
| `docker compose logs -f` | 查看实时日志 |

### 单个服务操作
| 命令 | 说明 |
|------|------|
| `docker compose restart backend` | 重启后端 |
| `docker compose logs -f backend` | 查看后端日志 |
| `docker compose exec backend bash` | 进入后端容器 |

### 数据库操作
| 命令 | 说明 |
|------|------|
| `docker exec -it mengxiaotan_mysql mysql -uroot -ppassword mengxiaotan` | 连接数据库 |
| `docker exec mengxiaotan_mysql mysqldump -uroot -ppassword mengxiaotan > backup.sql` | 备份数据库 |
| `docker exec -i mengxiaotan_mysql mysql -uroot -ppassword mengxiaotan < backup.sql` | 恢复数据库 |

### 健康检查
| 命令 | 说明 |
|------|------|
| `curl http://localhost:5001/api/health` | 检查后端健康 |
| `curl http://localhost:5173` | 检查前端 |
| `docker exec mengxiaotan_mysql mysqladmin ping -uroot -ppassword` | 检查MySQL |
| `docker exec mengxiaotan_redis redis-cli ping` | 检查Redis |

## 端口映射

| 服务 | 容器端口 | 主机端口 | 访问地址 |
|------|----------|----------|----------|
| Frontend | 80 | 5173 | http://localhost:5173 |
| Backend | 5000 | 5001 | http://localhost:5001 |
| MySQL | 3306 | 3307 | localhost:3307 |
| Redis | 6379 | 6380 | localhost:6380 |

## 默认账号

| 类型 | 账号 | 密码 |
|------|------|------|
| 管理员 | 13800138000 | admin123 |
| 测试用户 | 13900139000 | test123 |
| MySQL | root | password |

## 故障排查

### 容器无法启动
```bash
# 查看日志
docker compose logs backend

# 重新构建
docker compose down
docker compose up -d --build
```

### 数据库连接失败
```bash
# 检查MySQL状态
docker compose ps mysql

# 测试连接
docker exec mengxiaotan_mysql mysql -uroot -ppassword -e "SELECT 1"

# 等待MySQL启动
sleep 30 && docker compose restart backend
```

### 端口被占用
```bash
# Mac/Linux
lsof -ti:5001 | xargs kill -9

# 或修改 docker-compose.yml 中的端口映射
```

## 环境变量

必须配置的环境变量（`.env`文件）：

```bash
# 密钥（必须修改）
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-random-jwt-secret-key

# AI功能（可选）
MINIMAX_API_KEY=your-api-key
MINIMAX_GROUP_ID=your-group-id

# 推送功能（可选）
WECHAT_WORK_CORPID=your-corp-id
WECHAT_WORK_CORPSECRET=your-secret
WECHAT_WORK_AGENTID=your-agent-id
```

## 更新部署

```bash
# 1. 备份数据
docker exec mengxiaotan_mysql mysqldump -uroot -ppassword mengxiaotan > backup.sql

# 2. 拉取代码
git pull

# 3. 重新构建
docker compose build

# 4. 重启服务
docker compose up -d

# 5. 验证
curl http://localhost:5001/api/health
```

## 完全清理

```bash
# 停止并删除所有容器和数据卷（危险！）
docker compose down -v

# 删除镜像
docker rmi mengxiaotan-website-backend
docker rmi mengxiaotan-website-frontend
```

## 性能监控

```bash
# 查看资源使用
docker stats

# 查看容器详情
docker inspect mengxiaotan_backend

# 查看网络
docker network inspect mengxiaotan-website_default
```

## 文档链接

- 📖 [完整部署指南](DOCKER_DEPLOYMENT_GUIDE.md)
- ✅ [部署检查清单](DOCKER_DEPLOYMENT_CHECKLIST.md)
- 📝 [更新总结](DOCKER_DEPLOYMENT_SUMMARY.md)
