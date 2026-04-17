# SSL 证书问题解决方案

## 🔐 问题现象

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

这是 macOS 上 Python 的常见问题，Python 无法验证 HTTPS 证书。

---

## ✅ 解决方案（按顺序尝试）

### 方案 1: 运行 Python 证书安装脚本（最简单）

打开 **Finder**，找到并双击运行：

```
/Applications/Python 3.12/Install Certificates.command
```

或在终端运行：

```bash
"/Applications/Python 3.12/Install Certificates.command"
```

**说明**: 这会安装 Python 需要的 SSL 证书。

运行后，重新尝试安装依赖。

---

### 方案 2: 使用国内镜像源（最可靠）

国内镜像源通常不需要严格的 SSL 验证：

```bash
cd backend
source venv/bin/activate
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

**一键命令**:
```bash
cd backend && source venv/bin/activate && python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn && cd ..
```

---

### 方案 3: 使用 certifi 包

```bash
cd backend
source venv/bin/activate

# 1. 先安装 certifi（跳过 SSL 验证）
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org certifi

# 2. 设置证书路径
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")

# 3. 安装其他依赖
python -m pip install -r requirements.txt

cd ..
```

---

### 方案 4: 临时禁用 SSL 验证（不推荐，仅用于测试）

```bash
cd backend
source venv/bin/activate
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
cd ..
```

---

## 🚀 推荐的完整流程

### 步骤 1: 安装证书
```bash
"/Applications/Python 3.12/Install Certificates.command"
```

### 步骤 2: 重新创建虚拟环境
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### 步骤 3: 使用国内镜像安装
```bash
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 步骤 4: 验证
```bash
python -c "import flask; print(f'✅ Flask {flask.__version__}')"
```

### 步骤 5: 返回并启动
```bash
cd ..
./start.sh
```

---

## 📋 一键复制命令

### 完整安装（使用清华镜像）

```bash
cd backend && \
rm -rf venv && \
python3 -m venv venv && \
source venv/bin/activate && \
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn && \
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn && \
python -c "import flask; print(f'✅ Flask {flask.__version__}')" && \
cd ..
```

### 完整安装（使用阿里云镜像）

```bash
cd backend && \
rm -rf venv && \
python3 -m venv venv && \
source venv/bin/activate && \
python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && \
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && \
python -c "import flask; print(f'✅ Flask {flask.__version__}')" && \
cd ..
```

---

## 🔍 验证 SSL 是否正常

```bash
python3 -c "import ssl; print(ssl.get_default_verify_paths())"
```

应该显示证书路径。

---

## 💡 为什么会出现这个问题？

macOS 上的 Python 默认不包含 SSL 证书，需要手动安装。这是 Python 官方的设计，不是 bug。

---

## 🎯 最快的解决方案

**直接使用国内镜像 + 跳过 SSL 验证**:

```bash
cd backend
source venv/bin/activate
python -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended Flask-CORS Flask-Smorest python-dotenv PyMySQL cryptography redis APScheduler requests marshmallow apispec gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
cd ..
```

---

**最后更新**: 2026-04-10
