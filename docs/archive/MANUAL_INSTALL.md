# 手动安装指南

如果自动脚本失败，请按照以下步骤手动安装。

---

## 步骤 1: 打开终端并进入项目目录

```bash
cd /Users/xuekaitian1/Documents/ai-project/mengxiaotan-website
```

---

## 步骤 2: 进入后端目录

```bash
cd backend
```

---

## 步骤 3: 删除旧的虚拟环境（如果存在）

```bash
rm -rf venv
```

---

## 步骤 4: 创建新的虚拟环境

```bash
python3 -m venv venv
```

**验证**: 应该看到创建了 `venv` 文件夹

---

## 步骤 5: 激活虚拟环境

```bash
source venv/bin/activate
```

**验证**: 命令提示符前面应该出现 `(venv)`

---

## 步骤 6: 确认使用虚拟环境

```bash
which python
```

**应该显示**: `/Users/xuekaitian1/Documents/ai-project/mengxiaotan-website/backend/venv/bin/python`

```bash
which pip
```

**应该显示**: `/Users/xuekaitian1/Documents/ai-project/mengxiaotan-website/backend/venv/bin/pip`

---

## 步骤 7: 升级 pip

```bash
python -m pip install --upgrade pip
```

**应该看到**: `Successfully installed pip-24.x.x`

---

## 步骤 8: 测试网络连接

```bash
python -m pip install Flask --dry-run
```

**应该看到**: `Collecting Flask` 和一系列依赖信息

如果这一步失败，说明网络有问题。

---

## 步骤 9: 安装依赖

### 方案 A: 使用清华镜像（推荐）

```bash
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方案 B: 使用阿里云镜像

```bash
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 方案 C: 使用官方源

```bash
python -m pip install -r requirements.txt
```

### 方案 D: 逐个安装（最可靠）

如果批量安装失败，逐个安装：

```bash
# 1. Flask 核心
python -m pip install Flask

# 2. 数据库相关
python -m pip install Flask-SQLAlchemy
python -m pip install Flask-Migrate
python -m pip install PyMySQL

# 3. 认证相关
python -m pip install Flask-JWT-Extended

# 4. API 相关
python -m pip install Flask-CORS
python -m pip install Flask-Smorest
python -m pip install marshmallow
python -m pip install apispec

# 5. 其他依赖
python -m pip install python-dotenv
python -m pip install cryptography
python -m pip install redis
python -m pip install APScheduler
python -m pip install requests
python -m pip install gunicorn
```

**每安装一个包后验证**:
```bash
python -c "import flask; print('✅ Flask OK')"
python -c "import flask_sqlalchemy; print('✅ SQLAlchemy OK')"
# ... 依此类推
```

---

## 步骤 10: 验证安装

```bash
python -m pip list | grep Flask
```

**应该看到**:
```
Flask                3.1.3
Flask-CORS           4.0.0
Flask-JWT-Extended   4.6.0
Flask-Migrate        4.0.7
Flask-Smorest        0.44.0
Flask-SQLAlchemy     3.1.1
```

---

## 步骤 11: 测试导入

```bash
python << 'EOF'
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

**应该看到**: `✅ 所有核心包导入成功！`

---

## 步骤 12: 初始化数据库

```bash
python init_db.py
```

**应该看到**:
```
✓ 数据库表创建成功
✓ 管理员账号创建成功
✓ 订阅套餐创建成功
...
✓ 数据库初始化完成！
```

---

## 步骤 13: 返回项目根目录

```bash
cd ..
```

---

## 步骤 14: 启动项目

```bash
./start.sh
```

---

## 常见问题

### Q1: `source venv/bin/activate` 没有反应

**检查**:
```bash
ls -la venv/bin/activate
```

如果文件不存在，重新创建虚拟环境：
```bash
rm -rf venv
python3 -m venv venv
```

### Q2: `which python` 显示的不是 venv 路径

**解决**:
```bash
# 退出当前虚拟环境
deactivate

# 重新激活
source venv/bin/activate

# 再次检查
which python
```

### Q3: pip 安装时提示权限错误

**不要使用 sudo！**

确保：
1. 虚拟环境已激活
2. 使用 `python -m pip` 而不是 `pip`

### Q4: 网络超时

**增加超时时间**:
```bash
python -m pip install -r requirements.txt --timeout=300 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q5: SSL 证书错误

**使用国内镜像**:
```bash
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

---

## 完整的一键命令（复制粘贴）

```bash
cd backend && \
rm -rf venv && \
python3 -m venv venv && \
source venv/bin/activate && \
python -m pip install --upgrade pip && \
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
python -m pip list | grep Flask && \
python -c "import flask; print(f'✅ Flask {flask.__version__}')" && \
cd ..
```

---

## 获取帮助

如果以上步骤都失败：

1. 检查 Python 版本: `python3 --version` (需要 3.9+)
2. 检查网络: `ping pypi.tuna.tsinghua.edu.cn`
3. 查看完整错误日志
4. 尝试在新的终端窗口中重新操作

---

**最后更新**: 2026-04-10
