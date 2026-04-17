# 最简单的安装步骤

## 🎯 5 个命令搞定

打开终端，复制粘贴以下命令（一次一行）：

### 1️⃣ 进入后端目录
```bash
cd backend
```

### 2️⃣ 重新创建虚拟环境
```bash
rm -rf venv && python3 -m venv venv
```

### 3️⃣ 激活虚拟环境
```bash
source venv/bin/activate
```

**检查**: 命令提示符前面应该出现 `(venv)`

### 4️⃣ 安装依赖
```bash
python -m pip install --upgrade pip && python -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended Flask-CORS Flask-Smorest python-dotenv PyMySQL cryptography redis APScheduler requests marshmallow apispec gunicorn
```

### 5️⃣ 验证并返回
```bash
python -c "import flask; print(f'✅ Flask {flask.__version__}')" && cd ..
```

---

## ✅ 如果看到 `✅ Flask 3.1.3`

恭喜！安装成功，现在启动项目：

```bash
./start.sh
```

---

## ❌ 如果还是失败

尝试使用国内镜像：

```bash
cd backend
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended Flask-CORS Flask-Smorest python-dotenv PyMySQL cryptography redis APScheduler requests marshmallow apispec gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
cd ..
```

---

## 🔍 调试命令

如果需要调试，运行这些命令查看状态：

```bash
# 检查虚拟环境
which python  # 应该显示 venv/bin/python

# 检查 pip
which pip     # 应该显示 venv/bin/pip

# 测试网络
python -m pip install Flask --dry-run

# 查看已安装的包
python -m pip list
```

---

**提示**: 如果命令太长，可以分开执行，但要确保在同一个终端窗口中，保持虚拟环境激活状态。
