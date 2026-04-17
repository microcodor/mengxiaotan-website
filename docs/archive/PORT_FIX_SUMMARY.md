# 端口配置修复总结

## 问题描述
前端首页分类和内容无法显示，浏览器控制台显示大量 `ERR_CONNECTION_REFUSED` 和 500 错误。

## 根本原因
1. **Vite代理配置错误**：`frontend/vite.config.ts` 中的代理目标最初指向 `http://localhost:5000`
2. **macOS端口冲突**：macOS Monterey及以上版本的AirPlay Receiver默认占用5000端口
3. **实际后端端口**：后端服务配置为运行在 `http://localhost:5001`
4. **端口占用问题**：启动脚本没有检查和清理已占用的端口

## 修复内容

### 1. 修复 Vite 代理配置
**文件**: `frontend/vite.config.ts`

```typescript
// 修改前
proxy: {
  '/api': {
    target: 'http://localhost:5000',  // ❌ 被macOS AirPlay占用
    changeOrigin: true,
  },
}

// 修改后
proxy: {
  '/api': {
    target: 'http://localhost:5001',  // ✅ 正确端口
    changeOrigin: true,
  },
}
```

### 2. 增强 start.sh 脚本
**文件**: `start.sh`

**新增功能**：
- ✅ 启动前自动检测端口占用（5001, 5173, 3307, 6380）
- ✅ 自动终止占用端口的进程
- ✅ 跨平台支持（Mac/Linux/Windows）
- ✅ 显示更详细的端口和数据库信息

**检测逻辑**：
- Mac/Linux: 使用 `lsof -ti:PORT` 查找进程
- Windows: 使用 `netstat -ano` 查找进程

### 3. 增强 stop.sh 脚本
**文件**: `stop.sh`

**新增功能**：
- ✅ 智能检测并停止占用端口的进程
- ✅ 跨平台支持（Mac/Linux/Windows）
- ✅ 清理残留进程
- ✅ 更友好的输出信息

## 端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端开发服务器 | 5173 | Vite dev server |
| 后端API服务 | 5001 | Flask application (避免与macOS AirPlay冲突) |
| MySQL数据库 | 3307 | 映射到容器的3306 |
| Redis缓存 | 6380 | 映射到容器的6379 |

**注意**: macOS Monterey及以上版本的AirPlay Receiver默认占用5000端口，因此后端使用5001端口。

## 使用方法

### 启动服务
```bash
./start.sh
```

启动脚本会自动：
1. 检测并清理端口占用
2. 启动 Docker 容器（MySQL, Redis）
3. 初始化数据库
4. 启动后端服务（端口 5001）
5. 启动前端服务（端口 5173）

### 停止服务
```bash
./stop.sh
```

停止脚本会自动：
1. 停止 Docker 容器
2. 清理占用端口的进程
3. 清理残留进程

### 访问地址
- 前端: http://localhost:5173
- 后端API: http://localhost:5001
- 管理后台: http://localhost:5173/admin
- 数据看板: http://localhost:5173/dashboard

## 验证修复

1. 运行 `./stop.sh` 停止所有服务
2. 运行 `./start.sh` 重新启动
3. 访问 http://localhost:5173
4. 检查浏览器控制台，应该没有连接错误
5. 首页应该正常显示分类导航和文章列表

## 注意事项

1. **首次启动**：需要等待数据库初始化完成（约10秒）
2. **端口冲突**：如果脚本无法自动清理端口，请手动检查并停止占用进程
3. **权限问题**：在某些系统上可能需要 sudo 权限来终止进程
4. **Windows环境**：确保在 Git Bash 或 WSL 中运行脚本

## 故障排查

### 问题：端口仍然被占用
```bash
# Mac/Linux
lsof -ti:5001
kill -9 <PID>

# Windows (PowerShell)
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

### 问题：前端无法连接后端
1. 检查后端是否启动：`curl http://localhost:5001/api/categories`
2. 检查 Vite 配置：确认代理目标是 `http://localhost:5001`
3. 重启前端服务：`cd frontend && npm run dev`

### 问题：macOS上5000端口被占用
macOS Monterey及以上版本的AirPlay Receiver默认占用5000端口。解决方案：
1. 使用5001端口（已在配置中设置）
2. 或者关闭AirPlay Receiver：系统偏好设置 → 共享 → 取消勾选"隔空播放接收器"

### 问题：数据库连接失败
```bash
# 检查 MySQL 容器状态
docker ps | grep mysql

# 查看 MySQL 日志
docker logs energy_mysql

# 重启 MySQL
docker-compose restart mysql
```
