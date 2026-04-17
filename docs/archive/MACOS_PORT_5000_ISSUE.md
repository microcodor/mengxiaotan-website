# macOS 端口 5000 冲突问题解决方案

## 问题描述

在 macOS Monterey (12.0) 及以上版本中，系统的 **AirPlay Receiver** 服务默认占用 5000 端口，导致 Flask 等 Web 应用无法使用该端口。

## 症状

1. 后端服务启动失败或无法访问
2. 访问 `http://localhost:5000` 返回 403 Forbidden
3. 响应头显示 `Server: AirTunes/xxx`
4. `lsof -i:5000` 显示 `ControlCenter` 进程占用端口

## 解决方案

### 方案 1: 使用其他端口（推荐）

将后端服务改为使用 5001 端口（本项目已采用此方案）：

**后端配置** (`backend/config.py`):
```python
PORT = int(os.getenv('PORT', 5001))
```

**后端启动** (`backend/app.py`):
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

**前端代理配置** (`frontend/vite.config.ts`):
```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',  // 使用 5001 端口
        changeOrigin: true,
      },
    },
  },
})
```

### 方案 2: 关闭 AirPlay Receiver

如果确实需要使用 5000 端口，可以关闭 AirPlay Receiver：

1. 打开 **系统偏好设置** (System Preferences)
2. 选择 **共享** (Sharing)
3. 取消勾选 **隔空播放接收器** (AirPlay Receiver)

**注意**: 关闭后将无法使用 AirPlay 功能接收其他设备的投屏。

### 方案 3: 临时终止进程（不推荐）

```bash
# 查找占用 5000 端口的进程
lsof -ti:5000

# 终止进程（需要 sudo）
sudo kill -9 $(lsof -ti:5000)
```

**注意**: 系统会自动重启 ControlCenter 进程，此方法只是临时解决。

## 本项目的配置

本项目已采用**方案 1**，使用 5001 端口作为后端服务端口：

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端开发服务器 | 5173 | Vite dev server |
| 后端API服务 | 5001 | Flask application |
| MySQL数据库 | 3307 | Docker 映射端口 |
| Redis缓存 | 6380 | Docker 映射端口 |

## 验证配置

### 1. 检查端口占用
```bash
# 检查 5000 端口（应该被 ControlCenter 占用）
lsof -i:5000

# 检查 5001 端口（应该是空闲或被 Flask 占用）
lsof -i:5001
```

### 2. 测试后端服务
```bash
# 测试后端 API
curl http://localhost:5001/api/categories

# 应该返回分类列表 JSON 数据
```

### 3. 测试前端代理
```bash
# 启动前端服务
cd frontend
npm run dev

# 访问 http://localhost:5173
# 前端应该能正常调用后端 API
```

## 相关资源

- [Apple Developer Forums - Port 5000 already in use](https://developer.apple.com/forums/thread/682332)
- [Stack Overflow - macOS Monterey AirPlay Receiver using port 5000](https://stackoverflow.com/questions/69818376)
- [GitHub Issue - Flask port 5000 conflict on macOS](https://github.com/pallets/flask/issues/4170)

## 其他受影响的端口

macOS 系统服务可能占用的其他常用端口：

| 端口 | 服务 | 说明 |
|------|------|------|
| 5000 | AirPlay Receiver | macOS Monterey+ |
| 7000 | AirPlay | 旧版 macOS |
| 8000 | 某些系统服务 | 偶尔冲突 |

建议开发时避免使用这些端口，或在启动脚本中添加端口检测和清理逻辑。

## 启动脚本改进

本项目的 `start.sh` 已添加自动端口检测和清理功能：

```bash
# 定义需要检查的端口
PORTS=(5001 5173 3307 6380)
PORT_NAMES=("后端服务" "前端服务" "MySQL" "Redis")

# 自动检测并清理占用的端口
for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "⚠️  端口 $PORT ($NAME) 被占用，PID: $PID"
        echo "   正在终止进程..."
        kill -9 $PID 2>/dev/null
        echo "✓ 端口 $PORT 已释放"
    fi
done
```

这样可以确保每次启动时端口都是可用的。
