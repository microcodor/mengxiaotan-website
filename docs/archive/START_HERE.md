# 🚀 快速启动指南

## ⚠️ 当前问题：SSL 证书错误

您遇到的错误是 macOS Python 的 SSL 证书验证问题。

---

## ✅ 解决方案（3 步搞定）

### 第 1 步：运行安装脚本

```bash
./install-backend.sh
```

这个脚本会：
- 清理旧的虚拟环境
- 创建新的虚拟环境
- 使用清华大学镜像源（跳过 SSL 验证）
- 安装所有依赖包
- 验证安装是否成功

### 第 2 步：启动项目

```bash
./start.sh
```

### 第 3 步：访问应用

- 前端：http://localhost:5173
- 后端：http://localhost:5000
- 管理后台：http://localhost:5173/admin

---

## 🔑 登录信息

- **管理员**：13800138000 / admin123
- **测试用户**：13900139000 / test123

---

## 📝 为什么会出现 SSL 错误？

macOS 上的 Python 默认不包含 SSL 证书。有两种解决方案：

1. **安装证书**（永久解决）：
   ```bash
   "/Applications/Python 3.12/Install Certificates.command"
   ```

2. **使用国内镜像**（推荐，更快）：
   - 清华镜像：`https://pypi.tuna.tsinghua.edu.cn/simple`
   - 阿里云镜像：`https://mirrors.aliyun.com/pypi/simple/`
   - 使用 `--trusted-host` 参数跳过 SSL 验证

我们的脚本使用方案 2，既快速又可靠。

---

## 🛠️ 如果还有问题

### 检查 Python 版本
```bash
python3 --version
```
需要 Python 3.9 或更高版本。

### 检查 Docker
```bash
docker --version
docker compose version
```

### 手动安装依赖
```bash
cd backend
source venv/bin/activate
python -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended Flask-CORS Flask-Smorest python-dotenv PyMySQL cryptography redis APScheduler requests marshmallow apispec gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
cd ..
```

---

## 📚 更多文档

- `FIX_SSL.md` - SSL 问题详细解决方案
- `QUICKSTART.md` - 快速启动指南
- `PORT_CONFIG.md` - 端口配置说明
- `TROUBLESHOOTING.md` - 故障排除指南

---

**最后更新**：2026-04-10
