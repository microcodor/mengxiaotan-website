# 快速修复命令

## 🚀 最快的解决方案

### macOS/Linux

```bash
# 1. 进入后端目录
cd backend

# 2. 删除旧环境
rm -rf venv

# 3. 创建新环境
python3 -m venv venv

# 4. 激活环境
source venv/bin/activate

# 5. 确认使用虚拟环境
which python  # 应该显示 .../backend/venv/bin/python
which pip     # 应该显示 .../backend/venv/bin/pip

# 6. 升级 pip
python -m pip install --upgrade pip

# 7. 安装依赖（使用清华镜像）
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 8. 验证
python -m pip list | grep Flask

# 9. 返回根目录
cd ..

# 10. 启动项目
./start.sh
```

### Windows

```cmd
REM 1. 进入后端目录
cd backend

REM 2. 删除旧环境
rmdir /s /q venv

REM 3. 创建新环境
python -m venv venv

REM 4. 激活环境
venv\Scripts\activate

REM 5. 升级 pip
python -m pip install --upgrade pip

REM 6. 安装依赖（使用清华镜像）
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

REM 7. 验证
python -m pip list | findstr Flask

REM 8. 返回根目录
cd ..

REM 9. 启动项目
start.bat
```

---

## 🔑 关键点

### ✅ 正确的做法

```bash
# 使用 python -m pip（推荐）
python -m pip install Flask

# 或者在虚拟环境激活后使用 pip
source venv/bin/activate
pip install Flask
```

### ❌ 常见错误

```bash
# 不要在虚拟环境外使用 pip3
pip3 install Flask  # 可能安装到系统 Python

# 不要使用 sudo
sudo pip install Flask  # 危险！

# 不要混用 Python 版本
python3 -m venv venv
python -m pip install ...  # 可能使用了不同的 Python
```

---

## 📋 一键复制命令

### 完整安装（macOS/Linux）

```bash
cd backend && rm -rf venv && python3 -m venv venv && source venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && python -m pip list | grep Flask && cd ..
```

### 完整安装（Windows）

```cmd
cd backend && rmdir /s /q venv && python -m venv venv && venv\Scripts\activate && python -m pip install --upgrade pip && python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && python -m pip list | findstr Flask && cd ..
```

---

## 🔍 故障排查

### 检查虚拟环境是否激活

```bash
# macOS/Linux
which python
# 应该显示: /path/to/backend/venv/bin/python

# Windows
where python
# 应该显示: C:\path\to\backend\venv\Scripts\python.exe
```

### 检查 pip 版本

```bash
python -m pip --version
# 应该显示: pip 24.x.x from /path/to/venv/lib/python3.x/site-packages/pip (python 3.x)
```

### 测试导入

```bash
python -c "import flask; print(flask.__version__)"
# 应该显示: 3.1.3 或类似版本
```

---

## 💡 为什么使用 `python -m pip`？

1. **确保使用正确的 pip**: `python -m pip` 使用当前 Python 解释器对应的 pip
2. **避免版本混淆**: 不会意外使用系统的 pip
3. **虚拟环境安全**: 即使忘记激活虚拟环境，也能正确安装
4. **跨平台一致**: Windows 和 Unix 系统都能正常工作

---

## 🎯 验证安装成功

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 测试所有核心包
python << EOF
import flask
import flask_sqlalchemy
import flask_migrate
import flask_jwt_extended
import flask_cors
import redis
import apscheduler
print("✅ 所有核心包导入成功！")
print(f"Flask 版本: {flask.__version__}")
EOF
```

如果看到 "✅ 所有核心包导入成功！"，说明安装完成！

---

**最后更新**: 2026-04-10
