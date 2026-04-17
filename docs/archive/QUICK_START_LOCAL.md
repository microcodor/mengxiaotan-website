# 本地环境快速启动指南

## 🚀 一键启动

```bash
./start_local.sh
```

等待30秒，然后访问：http://localhost:5173

---

## 📱 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端首页 | http://localhost:5173 | 用户端界面 |
| 管理后台 | http://localhost:5173/admin | 管理员界面 |
| 数据看板 | http://localhost:5173/dashboard | 数据统计 |
| 后端API | http://localhost:5001/api | REST API |
| API文档 | http://localhost:5001/swagger-ui | Swagger文档 |

---

## 👤 测试账号

### 管理员账号
- 手机号: `13800138000`
- 密码: `admin123`
- 权限: 完整管理权限

### 普通用户
- 手机号: `13900139000`
- 密码: `test123`
- 权限: 普通用户权限

---

## 🛑 停止服务

```bash
# 方式1: 按 Ctrl+C（如果在前台运行）

# 方式2: 运行停止脚本
./stop_local.sh
```

---

## 🔍 检查服务状态

```bash
# 检查后端服务
curl http://localhost:5001/api/auth/login

# 检查前端服务
curl http://localhost:5173

# 查看进程
ps aux | grep -E "(python|node)" | grep -v grep

# 查看端口占用
lsof -i :5001  # 后端
lsof -i :5173  # 前端
```

---

## 🗄️ 数据库信息

### MySQL
- Host: `localhost`
- Port: `3306`
- User: `root`
- Password: `jinchun123`
- Database: `energy_station`

### Redis
- Host: `localhost`
- Port: `6379`
- Password: `123456`
- Database: `0`

---

## 📝 查看日志

```bash
# 后端日志
tail -f backend/logs/app.log

# 实时查看所有日志
tail -f backend/logs/*.log
```

---

## 🐛 常见问题

### 1. 端口被占用
```bash
# 查看占用端口的进程
lsof -i :5001
lsof -i :5173

# 终止进程
kill -9 <PID>

# 或使用停止脚本
./stop_local.sh
```

### 2. MySQL连接失败
```bash
# 检查MySQL是否运行
mysql -h localhost -P 3306 -u root -pjinchun123 -e "SELECT 1"

# 启动MySQL（macOS Homebrew）
brew services start mysql

# 或使用系统偏好设置启动MySQL
```

### 3. Redis连接失败
```bash
# 检查Redis是否运行
redis-cli -h localhost -p 6379 -a 123456 PING

# 启动Redis（macOS Homebrew）
brew services start redis
```

### 4. 前端无法访问
```bash
# 检查前端服务是否运行
lsof -i :5173

# 如果没有运行，手动启动
cd frontend
npm run dev
```

### 5. 后端API报错
```bash
# 检查后端服务是否运行
lsof -i :5001

# 查看后端日志
tail -f backend/logs/app.log

# 如果没有运行，手动启动
cd backend
source venv/bin/activate
python app.py
```

---

## 🧪 测试API

### 登录测试
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}'
```

### 爬虫测试
```bash
# 先登录获取token
TOKEN=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 测试爬虫
curl -X POST http://localhost:5001/api/crawler/test-run \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📚 更多文档

- [完整配置指南](LOCAL_SETUP.md)
- [测试报告](LOCAL_ENV_TEST_REPORT.md)
- [爬虫功能说明](CRAWLER_UI_ENHANCEMENT.md)
- [项目README](README.md)

---

## ✅ 环境检查清单

启动前确认：
- [ ] MySQL正在运行（端口3306）
- [ ] Redis正在运行（端口6379）
- [ ] Python 3.8+已安装
- [ ] Node.js 16+已安装
- [ ] 端口5001和5173未被占用

---

**最后更新**: 2026-04-13  
**版本**: v1.0  
**状态**: ✅ 测试通过
