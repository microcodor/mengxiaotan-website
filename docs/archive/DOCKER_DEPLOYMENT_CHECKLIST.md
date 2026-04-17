# Docker 部署检查清单

## 部署前检查

### 环境准备
- [ ] Docker 已安装（版本 20.10+）
- [ ] Docker Compose 已安装（版本 2.0+）
- [ ] 服务器满足最低配置要求（2核CPU, 4GB内存, 20GB磁盘）
- [ ] 必要端口未被占用（5001, 5173, 3307, 6380）

### 配置文件
- [ ] `.env` 文件已创建并配置
- [ ] `SECRET_KEY` 已修改为随机值
- [ ] `JWT_SECRET_KEY` 已修改为随机值
- [ ] `MINIMAX_API_KEY` 已配置（如需AI功能）
- [ ] `WECHAT_WORK_*` 已配置（如需推送功能）
- [ ] 数据库密码已修改（生产环境）

### 文件检查
- [ ] `docker-compose.yml` 存在
- [ ] `backend/Dockerfile` 存在
- [ ] `frontend/Dockerfile` 存在
- [ ] `crawler/Dockerfile` 存在
- [ ] `frontend/nginx.conf` 存在
- [ ] `backend/requirements.txt` 存在
- [ ] `frontend/package.json` 存在

## 部署步骤

### 1. 构建镜像
```bash
docker compose build
```
- [ ] MySQL 镜像拉取成功
- [ ] Redis 镜像拉取成功
- [ ] Backend 镜像构建成功
- [ ] Frontend 镜像构建成功

### 2. 启动服务
```bash
docker compose up -d
```
- [ ] MySQL 容器启动成功
- [ ] Redis 容器启动成功
- [ ] Backend 容器启动成功
- [ ] Frontend 容器启动成功

### 3. 检查服务状态
```bash
docker compose ps
```
- [ ] 所有容器状态为 "Up"
- [ ] 没有容器处于 "Restarting" 状态

### 4. 初始化数据库
```bash
docker exec -it mengxiaotan_backend python init_db.py
```
- [ ] 数据库表创建成功
- [ ] 初始数据插入成功
- [ ] 没有错误信息

## 功能测试

### 健康检查
```bash
# 后端健康检查
curl http://localhost:5001/api/health
```
- [ ] 返回状态码 200
- [ ] 返回 JSON 包含 `"status": "healthy"`
- [ ] 数据库连接正常

```bash
# 前端访问测试
curl http://localhost:5173
```
- [ ] 返回状态码 200
- [ ] 返回 HTML 内容

### 数据库连接
```bash
docker exec mengxiaotan_mysql mysql -uroot -ppassword -e "SELECT 1"
```
- [ ] 连接成功
- [ ] 返回结果 "1"

```bash
# 检查数据库
docker exec mengxiaotan_mysql mysql -uroot -ppassword mengxiaotan -e "SHOW TABLES"
```
- [ ] 显示所有表
- [ ] 包含核心表（users, articles, subscriptions等）

### Redis连接
```bash
docker exec mengxiaotan_redis redis-cli ping
```
- [ ] 返回 "PONG"

### API测试
```bash
# 测试登录接口
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}'
```
- [ ] 返回状态码 200
- [ ] 返回包含 access_token

```bash
# 测试文章列表接口
curl http://localhost:5001/api/articles
```
- [ ] 返回状态码 200
- [ ] 返回文章列表数据

### 前端功能
在浏览器中访问 http://localhost:5173

- [ ] 首页正常显示
- [ ] 可以查看文章列表
- [ ] 可以登录（13800138000 / admin123）
- [ ] 登录后可以访问管理后台
- [ ] 管理后台功能正常

### 定时任务
```bash
# 检查定时任务
docker exec mengxiaotan_backend python -c "from app.scheduler import list_jobs; import json; print(json.dumps(list_jobs(), indent=2))"
```
- [ ] 显示定时任务列表
- [ ] 包含爬虫任务（evening_crawl）
- [ ] 包含简报生成任务（daily_brief）

## 性能测试

### 响应时间
```bash
# 测试后端响应时间
time curl http://localhost:5001/api/health
```
- [ ] 响应时间 < 1秒

```bash
# 测试前端响应时间
time curl http://localhost:5173
```
- [ ] 响应时间 < 2秒

### 并发测试（可选）
```bash
# 使用 ab 工具测试
ab -n 100 -c 10 http://localhost:5001/api/health
```
- [ ] 成功率 100%
- [ ] 平均响应时间 < 500ms

## 日志检查

### 查看日志
```bash
# 后端日志
docker compose logs backend | tail -50
```
- [ ] 没有 ERROR 级别日志
- [ ] 没有异常堆栈信息

```bash
# 前端日志
docker compose logs frontend | tail -50
```
- [ ] Nginx 正常启动
- [ ] 没有错误信息

```bash
# MySQL日志
docker compose logs mysql | tail -50
```
- [ ] MySQL 正常启动
- [ ] 没有错误信息

```bash
# Redis日志
docker compose logs redis | tail -50
```
- [ ] Redis 正常启动
- [ ] 没有错误信息

## 安全检查

### 密码安全
- [ ] MySQL root 密码已修改（生产环境）
- [ ] SECRET_KEY 不是默认值
- [ ] JWT_SECRET_KEY 不是默认值
- [ ] 敏感信息不在代码中硬编码

### 端口安全
- [ ] 生产环境只暴露必要端口
- [ ] MySQL 端口不对外暴露（或限制IP）
- [ ] Redis 端口不对外暴露（或限制IP）

### 文件权限
```bash
# 检查敏感文件权限
ls -la .env
```
- [ ] .env 文件权限为 600 或 644
- [ ] 不在版本控制中（.gitignore）

## 备份检查

### 数据备份
```bash
# 测试MySQL备份
docker exec mengxiaotan_mysql mysqldump -uroot -ppassword mengxiaotan > test_backup.sql
```
- [ ] 备份文件创建成功
- [ ] 备份文件大小 > 0

```bash
# 测试Redis备份
docker exec mengxiaotan_redis redis-cli SAVE
docker cp mengxiaotan_redis:/data/dump.rdb test_redis_backup.rdb
```
- [ ] 备份文件创建成功
- [ ] 备份文件大小 > 0

### 恢复测试（可选）
- [ ] 可以从备份恢复MySQL数据
- [ ] 可以从备份恢复Redis数据

## 监控配置

### 健康检查配置
```bash
# 检查健康检查配置
docker inspect mengxiaotan_backend | grep -A 10 Healthcheck
```
- [ ] 健康检查已配置
- [ ] 健康检查正常工作

### 日志配置
```bash
# 检查日志配置
docker inspect mengxiaotan_backend | grep -A 5 LogConfig
```
- [ ] 日志驱动已配置
- [ ] 日志轮转已配置（生产环境）

## 文档检查

### 文档完整性
- [ ] README.md 存在并更新
- [ ] DOCKER_DEPLOYMENT_GUIDE.md 存在
- [ ] API文档存在
- [ ] 运维文档存在

### 文档准确性
- [ ] 端口号正确
- [ ] 默认账号密码正确
- [ ] 命令可以正常执行

## 生产环境额外检查

### SSL/TLS
- [ ] SSL证书已配置
- [ ] HTTPS 正常工作
- [ ] HTTP 自动跳转到 HTTPS

### 域名配置
- [ ] 域名解析正确
- [ ] 可以通过域名访问
- [ ] 子域名配置正确（如有）

### 反向代理
- [ ] Nginx 反向代理配置正确
- [ ] 负载均衡配置正确（如有）
- [ ] 静态资源缓存配置正确

### 自动重启
```bash
# 检查重启策略
docker inspect mengxiaotan_backend | grep RestartPolicy
```
- [ ] 重启策略为 "always" 或 "unless-stopped"

### 资源限制
```bash
# 检查资源限制
docker stats --no-stream
```
- [ ] CPU 使用率 < 80%
- [ ] 内存使用率 < 80%
- [ ] 磁盘使用率 < 80%

## 故障恢复测试

### 容器重启测试
```bash
# 重启后端容器
docker compose restart backend
```
- [ ] 容器成功重启
- [ ] 服务自动恢复
- [ ] 数据没有丢失

### 数据库故障恢复
```bash
# 停止MySQL
docker compose stop mysql
# 等待10秒
sleep 10
# 启动MySQL
docker compose start mysql
```
- [ ] MySQL 成功重启
- [ ] 后端自动重连
- [ ] 数据完整性正常

## 部署完成确认

### 最终检查
- [ ] 所有容器正常运行
- [ ] 所有功能测试通过
- [ ] 日志没有错误
- [ ] 性能满足要求
- [ ] 安全检查通过
- [ ] 备份机制正常
- [ ] 监控配置完成
- [ ] 文档已更新

### 交付清单
- [ ] 部署文档已交付
- [ ] 管理员账号已交付
- [ ] 数据库连接信息已交付
- [ ] API文档已交付
- [ ] 运维手册已交付

## 问题记录

### 部署过程中遇到的问题
1. 问题描述：
   解决方案：
   
2. 问题描述：
   解决方案：

### 待优化项
1. 
2. 
3. 

## 签字确认

- 部署人员：__________ 日期：__________
- 测试人员：__________ 日期：__________
- 项目负责人：__________ 日期：__________

---

**注意事项**：
1. 本检查清单适用于Docker部署方式
2. 生产环境部署前必须完成所有检查项
3. 测试环境可以跳过部分安全和性能检查
4. 遇到问题及时记录并解决
5. 部署完成后保留此清单作为交付文档
