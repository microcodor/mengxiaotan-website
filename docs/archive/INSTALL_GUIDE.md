# 安装指南

## 快速解决依赖问题

### 问题现象
```
ERROR: No matching distribution found for Flask==X.X.X
ModuleNotFoundError: No module named 'flask'
```

---

## 解决方案（按顺序尝试）

### 🎯 方案 1: 使用修复脚本（推荐）

```bash
# macOS/Linux
chmod +x fix-dependencies.sh
./fix-dependencies.sh

# Windows
fix-dependencies.bat
```

**说明**: 脚本会自动：
- 重新创建虚拟环境
- 升级 pip
- 尝试多个镜像源
- 逐个安装核心包

⏱️ **预计时间**: 3-5 分钟

---

### 🎯 方案 2: 手动安装（最可靠）

#### 步骤 1: 进入后端目录
```bash
cd backend
```

#### 步骤 2: 删除旧环境（如果存在）
```bash
# macOS/Linux
rm -rf venv

# Windows
rmdir /s /q venv
```

#### 步骤 3: 创建新的虚拟环境
```bash
python3 -m venv venv  # macOS/Linux
python -m venv venv   # Windows
```

#### 步骤 4: 激活虚拟环境
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 步骤 5: 升级 pip
```bash
python -m pip install --upgrade pip setuptools wheel
```

#### 步骤 6: 安装依赖（选择一个镜像源）

> 💡 **重要**: 使用 `python -m pip` 而不是 `pip`，确保使用虚拟环境中的 pip

**选项 A: 使用默认源**
```bash
python -m pip install -r requirements.txt
```

**选项 B: 使用清华镜像（推荐，国内用户）**
```bash
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**选项 C: 使用阿里云镜像**
```bash
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

**选项 D: 逐个安装核心包**
```bash
python -m pip install Flask
python -m pip install Flask-SQLAlchemy
python -m pip install Flask-Migrate
python -m pip install Flask-JWT-Extended
python -m pip install Flask-CORS
python -m pip install Flask-Smorest
python -m pip install python-dotenv
python -m pip install PyMySQL
python -m pip install cryptography
python -m pip install redis
python -m pip install APScheduler
python -m pip install requests
python -m pip install marshmallow
python -m pip install apispec
python -m pip install gunicorn
```

#### 步骤 7: 验证安装
```bash
python -m pip list | grep Flask
```

应该看到类似输出：
```
Flask                3.1.3
Flask-CORS           4.0.0
Flask-JWT-Extended   4.6.0
Flask-Migrate        4.0.7
Flask-Smorest        0.44.0
Flask-SQLAlchemy     3.1.1
```

#### 步骤 8: 返回项目根目录
```bash
cd ..
```

---

### 🎯 方案 3: 配置永久镜像源

如果经常遇到安装慢的问题，可以永久配置镜像源：

#### macOS/Linux
```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

#### Windows
创建文件 `%APPDATA%\pip\pip.ini`:
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

然后重新运行安装：
```bash
cd backend
source venv/bin/activate  # 或 venv\Scripts\activate
python -m pip install -r requirements.txt
```

---

## 常见问题

### Q1: 虚拟环境激活失败
**症状**: `venv/bin/activate: No such file or directory`

**解决**:
```bash
# 确保在 backend 目录
cd backend

# 重新创建虚拟环境
python3 -m venv venv

# 激活
source venv/bin/activate
```

### Q2: pip 命令不存在
**症状**: `pip: command not found`

**解决**:
```bash
# 使用 python -m pip 代替 pip
python -m pip install -r requirements.txt
```

### Q3: 权限错误
**症状**: `Permission denied`

**解决**:
```bash
# 不要使用 sudo
# 确保在虚拟环境中
source venv/bin/activate
pip install -r requirements.txt
```

### Q4: 网络超时
**症状**: `ReadTimeoutError`

**解决**:
```bash
# 增加超时时间
pip install -r requirements.txt --timeout=100

# 或使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q5: SSL 证书错误
**症状**: `SSL: CERTIFICATE_VERIFY_FAILED`

**解决**:
```bash
# 临时禁用 SSL 验证（不推荐）
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

# 或使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 验证安装成功

安装完成后，运行以下命令验证：

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 检查 Flask
python -c "import flask; print(f'Flask {flask.__version__}')"

# 检查所有核心包
python -c "
import flask
import flask_sqlalchemy
import flask_migrate
import flask_jwt_extended
import redis
import apscheduler
print('✅ 所有核心包导入成功')
"
```

如果没有错误，说明安装成功！

---

## 下一步

安装成功后，返回项目根目录并启动：

```bash
cd ..
./start.sh  # 或 start.bat
```

---

## 获取帮助

如果以上方案都无法解决问题：

1. 检查 Python 版本: `python --version` (需要 3.9+)
2. 检查网络连接
3. 查看完整错误日志
4. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
5. 提交 Issue

---

**最后更新**: 2026-04-10
