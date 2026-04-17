# IM推送集成 V2.0 - 快速启动指南

## 🚀 快速启动

### 方式1: 使用启动脚本(推荐)

#### 启动后端
```bash
cd backend
./venv/bin/python run_production.py
```

#### 启动前端(新终端)
```bash
./start_frontend.sh
```

或者:
```bash
cd frontend
npm run dev
```

### 方式2: 使用统一启动脚本
```bash
./start.sh
```

---

## 📊 服务状态检查

### 检查后端
```bash
# 检查端口
lsof -i:5001

# 测试API
curl http://localhost:5001/api/categories/
```

### 检查前端
```bash
# 检查端口
lsof -i:5173

# 浏览器访问
open http://localhost:5173
```

---

## 🎯 访问地址

### 用户端
- **首页**: http://localhost:5173
- **登录**: http://localhost:5173/login
- **推送设置**: http://localhost:5173/dashboard/push

### 管理端
- **管理后台**: http://localhost:5173/admin
- **推送配置**: http://localhost:5173/admin/push

### 后端API
- **API文档**: http://localhost:5001/api/spec.json
- **分类API**: http://localhost:5001/api/categories/
- **推送设置API**: http://localhost:5001/api/push-settings/im-apps

---

## 👤 测试账号

### 管理员账号
- **手机号**: 13800138000
- **密码**: admin123

### 测试用户
- **手机号**: 13900139000
- **密码**: test123

---

## 🔧 常见问题

### Q1: 后端启动失败,提示端口被占用
```bash
# 释放5001端口
lsof -ti:5001 | xargs kill -9

# 重新启动
cd backend
./venv/bin/python run_production.py
```

### Q2: 前端启动失败,提示端口被占用
```bash
# 释放5173端口
lsof -ti:5173 | xargs kill -9

# 重新启动
cd frontend
npm run dev
```

### Q3: 前端加载超时
**原因**: 后端服务未启动或不稳定

**解决**:
1. 检查后端是否运行: `lsof -i:5001`
2. 查看后端日志
3. 使用生产模式启动: `./venv/bin/python run_production.py`

### Q4: API返回502错误
**原因**: 后端服务崩溃

**解决**:
1. 重启后端服务
2. 查看错误日志
3. 检查数据库连接

---

## 📝 测试流程

### 1. 登录系统
1. 访问 http://localhost:5173/login
2. 输入手机号: 13800138000
3. 输入密码: admin123
4. 点击登录

### 2. 进入推送设置
1. 登录后自动跳转到工作台
2. 点击左侧菜单"推送设置"
3. 或直接访问: http://localhost:5173/dashboard/push

### 3. 配置IM应用(Tab 1)
1. 点击"IM应用配置"Tab
2. 启用企业微信
3. 填写配置:
   - 企业ID: ww_test_corp_id
   - 应用ID: 1000002
   - Secret: test_secret_123
4. 点击"测试连接"
5. 点击"保存配置"

### 4. 配置接收人(Tab 2)
1. 点击"接收人配置"Tab
2. 查看订阅等级和可用渠道
3. 填写企业微信UserID: test_user
4. 点击"测试推送"
5. 点击"保存配置"

---

## 🎨 界面预览

### 推送设置页面
```
┌─────────────────────────────────────────┐
│ 推送设置                                 │
├─────────────────────────────────────────┤
│ [IM应用配置] [接收人配置]                │
├─────────────────────────────────────────┤
│                                         │
│ Tab 1: IM应用配置                        │
│ - 企业微信应用配置                       │
│ - 钉钉应用配置                          │
│ - 飞书应用配置                          │
│                                         │
│ Tab 2: 接收人配置                        │
│ - 当前订阅等级                          │
│ - 可用推送渠道                          │
│ - 配置接收人UserID                      │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📚 相关文档

1. **[IM_PUSH_NEW_DESIGN.md](./IM_PUSH_NEW_DESIGN.md)** - 设计方案
2. **[IM_PUSH_V2_UPDATE.md](./IM_PUSH_V2_UPDATE.md)** - 更新说明
3. **[IM_PUSH_V2_COMPLETE.md](./IM_PUSH_V2_COMPLETE.md)** - 完成报告
4. **[IM_PUSH_V2_FINAL_TEST.md](./IM_PUSH_V2_FINAL_TEST.md)** - 测试报告
5. **[QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)** - 快速指南(本文档)

---

## 🎯 核心功能

### 已实现
- ✅ 用户级IM应用配置
- ✅ Secret加密存储
- ✅ 脱敏显示
- ✅ 测试连接功能
- ✅ 接收人配置
- ✅ 测试推送功能
- ✅ Tab页面结构
- ✅ 实时状态反馈

### 支持的平台
- ✅ 企业微信
- ✅ 钉钉
- ✅ 飞书
- ✅ 邮件
- ✅ 短信

---

## 💡 使用提示

1. **首次使用**
   - 先配置IM应用(Tab 1)
   - 再配置接收人(Tab 2)
   - 测试连接和推送

2. **配置建议**
   - 使用真实的应用凭证
   - 确保UserID正确
   - 先测试连接再配置接收人

3. **安全建议**
   - Secret会加密存储
   - 定期更换Secret
   - 不要分享配置信息

---

## 🎊 开始使用

现在你可以:

1. **启动服务**
   ```bash
   # 后端
   cd backend
   ./venv/bin/python run_production.py
   
   # 前端(新终端)
   cd frontend
   npm run dev
   ```

2. **访问系统**
   - 打开浏览器
   - 访问 http://localhost:5173
   - 登录并开始配置

3. **配置推送**
   - 进入推送设置
   - 配置IM应用
   - 配置接收人
   - 测试推送

**祝使用愉快!** 🎉

---

**文档版本**: 1.0  
**最后更新**: 2026-04-16  
**维护者**: AI Assistant
