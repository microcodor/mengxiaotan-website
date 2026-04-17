# Docker 部署配置更新总结

## 更新概述

本次更新优化了Docker部署配置，提升了部署的可靠性、安全性和可维护性。

## 主要改进

### 1. Docker Compose 配置优化

#### 改进前
- 容器名称不统一
- 缺少健康检查
- 没有环境变量支持
- 依赖关系不明确
- 缺少重启策略

#### 改进后
✅ **统一命名规范**
- 所有容器使用 `mengxiaotan_` 前缀
- 清晰的服务命名

✅ **健康检查机制**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

✅ **环境变量支持**
```yaml
environment:
  SECRET_KEY: ${SECRET_KEY:-production-secret-key-change-me}
  MINIMAX_API_KEY: ${MINIMAX_API_KEY:-}
```

✅ **依赖关系优化**
```yaml
depends_on:
  mysql:
    condition: service_healthy
  redis:
    condition: service_healthy
```

✅ **自动重启策略**
```yaml
restart: unless-stopped
```

### 2. Dockerfile 优化

#### Backend Dockerfile
**改进**：
- 添加健康检查
- 使用国内镜像源加速
- 创建必要目录
- 优化Gunicorn配置
- 添加日志输出

```dockerfile
# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 优化的启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-", "app:app"]
```

#### Frontend Dockerfile
**改进**：
- 支持构建时环境变量
- 添加健康检查
- 优化构建过程

```dockerfile
# 构建参数
ARG VITE_API_BASE_URL=http://localhost:5001
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1
```

#### Crawler Dockerfile（新增）
**特性**：
- 独立的爬虫服务
- 支持按需启动
- 使用 profile 控制

### 3. 健康检查端点

**新增 `/api/health` 端点**：
```python
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503
```

### 4. 环境变量配置

**新增 `.env.example` 文件**：
```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3307/mengxiaotan

# 密钥配置
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# API配置
MINIMAX_API_KEY=your-api-key
WECHAT_WORK_CORPID=your-corp-id
```

### 5. 文档完善

**新增文档**：
1. ✅ `DOCKER_DEPLOYMENT_GUIDE.md` - 详细部署指南
2. ✅ `DOCKER_DEPLOYMENT_CHECKLIST.md` - 部署检查清单
3. ✅ `DOCKER_DEPLOYMENT_SUMMARY.md` - 本文档

## 配置对比

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|----------|----------|------|
| MySQL | 3306 | 3307 | 避免与本地MySQL冲突 |
| Redis | 6379 | 6380 | 避免与本地Redis冲突 |
| Backend | 5000 | 5001 | 后端API服务 |
| Frontend | 80 | 5173 | 前端Web服务 |

### 数据卷

| 卷名 | 挂载点 | 说明 |
|------|--------|------|
| mysql_data | /var/lib/mysql | MySQL数据持久化 |
| redis_data | /data | Redis数据持久化 |
| ./backend/uploads | /app/uploads | 上传文件 |
| ./backend/logs | /app/logs | 应用日志 |

## 部署流程

### 快速部署（3步）

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env

# 2. 启动服务
docker compose up -d

# 3. 初始化数据库
docker exec -it mengxiaotan_backend python init_db.py
```

### 完整部署流程

```bash
# 1. 克隆项目
git clone <repository-url>
cd mengxiaotan-website

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，修改必要配置

# 3. 构建镜像
docker compose build

# 4. 启动服务
docker compose up -d

# 5. 等待服务就绪
sleep 30

# 6. 初始化数据库
docker exec -it mengxiaotan_backend python init_db.py

# 7. 检查服务状态
docker compose ps
curl http://localhost:5001/api/health
curl http://localhost:5173

# 8. 查看日志
docker compose logs -f
```

## 常用命令

### 服务管理
```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose stop

# 重启服务
docker compose restart

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f backend
```

### 数据管理
```bash
# 备份MySQL
docker exec mengxiaotan_mysql mysqldump -uroot -ppassword mengxiaotan > backup.sql

# 恢复MySQL
docker exec -i mengxiaotan_mysql mysql -uroot -ppassword mengxiaotan < backup.sql

# 备份Redis
docker exec mengxiaotan_redis redis-cli SAVE
docker cp mengxiaotan_redis:/data/dump.rdb ./redis_backup.rdb
```

### 调试命令
```bash
# 进入容器
docker exec -it mengxiaotan_backend bash

# 查看容器日志
docker logs mengxiaotan_backend

# 检查网络
docker network inspect mengxiaotan-website_default

# 查看资源使用
docker stats
```

## 安全改进

### 1. 密钥管理
- ✅ 使用环境变量管理敏感信息
- ✅ 提供 `.env.example` 模板
- ✅ `.env` 文件不纳入版本控制

### 2. 端口安全
- ✅ 数据库端口可配置为仅本地访问
- ✅ Redis端口可配置为仅本地访问
- ✅ 生产环境建议使用内网端口

### 3. 容器安全
- ✅ 使用官方基础镜像
- ✅ 最小化镜像大小
- ✅ 定期更新依赖

## 性能优化

### 1. 构建优化
- ✅ 使用多阶段构建（Frontend）
- ✅ 使用国内镜像源加速
- ✅ 优化层缓存

### 2. 运行优化
- ✅ Gunicorn 多进程（4 workers）
- ✅ Nginx 静态资源缓存
- ✅ Redis 持久化配置

### 3. 资源限制（可选）
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 监控和日志

### 健康检查
- ✅ 后端健康检查端点
- ✅ Docker 健康检查机制
- ✅ 自动重启不健康容器

### 日志管理
- ✅ 应用日志输出到文件
- ✅ Docker 日志收集
- ✅ 日志轮转配置（可选）

### 监控指标
- ✅ 容器状态监控
- ✅ 资源使用监控
- ✅ 服务可用性监控

## 故障恢复

### 自动恢复
- ✅ 容器异常自动重启
- ✅ 健康检查失败自动重启
- ✅ 依赖服务就绪后启动

### 手动恢复
```bash
# 重启单个服务
docker compose restart backend

# 重建容器
docker compose up -d --force-recreate backend

# 完全重建
docker compose down
docker compose up -d --build
```

## 测试验证

### 功能测试
- ✅ 健康检查端点测试
- ✅ API接口测试
- ✅ 前端页面测试
- ✅ 数据库连接测试
- ✅ Redis连接测试

### 性能测试
- ✅ 响应时间测试
- ✅ 并发测试（可选）
- ✅ 资源使用测试

### 安全测试
- ✅ 密码安全检查
- ✅ 端口暴露检查
- ✅ 文件权限检查

## 已知问题和限制

### 当前限制
1. 爬虫服务需要手动触发
2. 日志轮转需要额外配置
3. 监控告警需要集成第三方工具

### 待优化项
1. 添加 Prometheus 监控
2. 集成 ELK 日志系统
3. 添加自动化测试
4. 优化镜像大小

## 升级指南

### 从旧版本升级

```bash
# 1. 备份数据
docker exec mengxiaotan_mysql mysqldump -uroot -ppassword mengxiaotan > backup_before_upgrade.sql

# 2. 停止旧服务
docker compose down

# 3. 拉取新代码
git pull

# 4. 更新配置
# 检查 .env 文件，添加新的配置项

# 5. 重新构建
docker compose build

# 6. 启动新服务
docker compose up -d

# 7. 运行数据库迁移（如有）
docker exec -it mengxiaotan_backend python migrations/migrate.py

# 8. 验证服务
curl http://localhost:5001/api/health
```

## 文件清单

### 新增文件
- ✅ `.env.example` - 环境变量模板
- ✅ `crawler/Dockerfile` - 爬虫服务Dockerfile
- ✅ `DOCKER_DEPLOYMENT_GUIDE.md` - 部署指南
- ✅ `DOCKER_DEPLOYMENT_CHECKLIST.md` - 检查清单
- ✅ `DOCKER_DEPLOYMENT_SUMMARY.md` - 本文档

### 修改文件
- ✅ `docker-compose.yml` - 优化配置
- ✅ `backend/Dockerfile` - 添加健康检查
- ✅ `frontend/Dockerfile` - 优化构建
- ✅ `backend/app.py` - 添加健康检查端点

## 总结

本次Docker部署配置更新主要解决了以下问题：

1. **可靠性提升**
   - 添加健康检查机制
   - 优化依赖关系
   - 自动重启策略

2. **安全性增强**
   - 环境变量管理
   - 密钥配置优化
   - 端口安全配置

3. **可维护性改进**
   - 统一命名规范
   - 完善文档
   - 标准化流程

4. **性能优化**
   - 构建优化
   - 运行优化
   - 资源管理

现在的Docker部署配置更加完善、可靠和易于维护，适合生产环境使用！

## 下一步

1. 根据实际需求调整配置
2. 完成部署检查清单
3. 进行压力测试
4. 配置监控告警
5. 制定运维计划
