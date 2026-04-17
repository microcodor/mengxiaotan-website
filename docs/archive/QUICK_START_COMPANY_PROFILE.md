# 企业画像功能快速启动指南

**版本**: 1.0  
**更新时间**: 2026-04-16

---

## 🚀 快速启动

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 确保已安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

后端服务将在 `http://localhost:5000` 启动

---

### 2. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 确保已安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

---

## 🔑 访问企业画像

### 方式1：通过导航菜单

1. 打开浏览器访问 `http://localhost:5173`
2. 登录系统（使用已注册的账号）
3. 进入用户工作台
4. 在左侧导航菜单中点击"企业画像"

### 方式2：直接访问URL

```
http://localhost:5173/dashboard/company/profile
```

---

## 📋 前置条件

### 必须满足以下条件才能查看企业画像：

1. ✅ **已登录** - 需要有效的用户账号
2. ✅ **已绑定企业** - 在个人中心绑定企业信息
3. ✅ **有效订阅** - 基础版订阅或试用期内

### 如何满足条件：

#### 1. 注册和登录
```bash
# 访问注册页面
http://localhost:5173/register

# 或访问登录页面
http://localhost:5173/login
```

#### 2. 绑定企业信息
```bash
# 登录后访问个人中心
http://localhost:5173/dashboard/profile

# 或访问企业信息页面
http://localhost:5173/dashboard/company
```

填写企业信息：
- 企业名称
- 统一社会信用代码
- 企业类型
- 所在地区
- 等等...

#### 3. 开通订阅
```bash
# 访问订阅页面
http://localhost:5173/dashboard/subscription
```

选择订阅方式：
- **免费试用** - 7天试用期（每用户限一次）
- **基础版** - ¥39/月 或 ¥468/年

---

## 🧪 快速测试

### 测试脚本

后端提供了测试脚本，可以快速验证功能：

```bash
cd backend
python test_company_profile.py
```

测试脚本会：
1. 创建测试企业数据
2. 生成企业画像
3. 显示分析结果
4. 验证API接口

---

## 📊 查看画像内容

企业画像包含以下内容：

### 1. 综合评分
- 0-100分的综合评分
- 评级：优秀/良好/一般/较差

### 2. 关键指标
- **竞争力得分** - 企业竞争力评估
- **风险等级** - 整体风险水平
- **机会等级** - 发展机会评估

### 3. 详细分析
- **核心竞争力** - 优势和能力分析
- **风险识别** - 4类风险详细分析
- **发展机会** - 3类机会详细分析

### 4. 其他功能
- **画像摘要** - AI生成的总结
- **数据来源** - 分析数据来源
- **JSON导出** - 导出完整数据

---

## 🔍 API测试

### 使用curl测试API

#### 1. 获取访问令牌

```bash
# 登录获取token
curl -X POST "http://localhost:5000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "password": "your_password"
  }'
```

响应示例：
```json
{
  "code": 200,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {...}
  }
}
```

#### 2. 获取企业画像

```bash
# 替换 YOUR_TOKEN 和 COMPANY_ID
curl -X GET "http://localhost:5000/api/company-profile/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. 获取画像摘要

```bash
curl -X GET "http://localhost:5000/api/company-profile/1/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4. 导出画像数据

```bash
curl -X GET "http://localhost:5000/api/company-profile/1/export?format=json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 常见问题

### 问题1：页面显示"未绑定企业"

**原因**: 用户未绑定企业信息

**解决方案**:
1. 访问 `/dashboard/company`
2. 填写企业基本信息
3. 保存后返回企业画像页面

---

### 问题2：页面显示"权限不足"

**原因**: 用户没有基础版订阅

**解决方案**:
1. 访问 `/dashboard/subscription`
2. 开通免费试用或购买基础版
3. 返回企业画像页面

---

### 问题3：页面一直显示"正在生成..."

**原因**: 
- 后端服务未启动
- 网络请求失败
- 数据库连接问题

**解决方案**:
1. 检查后端服务是否正常运行
2. 打开浏览器控制台查看错误信息
3. 检查数据库连接配置

---

### 问题4：导出功能不工作

**原因**: 
- API请求失败
- 浏览器阻止下载

**解决方案**:
1. 检查浏览器控制台错误
2. 检查浏览器下载设置
3. 尝试使用其他浏览器

---

## 📱 浏览器兼容性

### 推荐浏览器
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### 不支持的浏览器
- ❌ IE 11 及以下
- ❌ 旧版本移动浏览器

---

## 🔧 开发调试

### 前端调试

#### 1. 启用React DevTools
安装Chrome扩展：React Developer Tools

#### 2. 查看网络请求
打开浏览器开发者工具 → Network标签

#### 3. 查看控制台日志
打开浏览器开发者工具 → Console标签

### 后端调试

#### 1. 启用调试模式
```python
# app.py
app.run(debug=True)
```

#### 2. 查看日志
```bash
# 后端会输出详细的请求日志
[2026-04-16 16:00:00] INFO: GET /api/company-profile/1
[2026-04-16 16:00:01] INFO: Response: 200
```

#### 3. 使用Python调试器
```python
# 在代码中添加断点
import pdb; pdb.set_trace()
```

---

## 📚 相关文档

- [企业画像功能完成报告](./SUBSCRIPTION_PHASE3_FRONTEND_COMPLETE.md)
- [企业画像测试指南](./COMPANY_PROFILE_TEST_GUIDE.md)
- [第三阶段完成总结](./PHASE3_COMPLETE_SUMMARY.md)
- [开发进度文档](./SUBSCRIPTION_DEVELOPMENT_PROGRESS.md)

---

## 💬 获取帮助

### 查看日志
- 前端日志：浏览器控制台
- 后端日志：终端输出

### 检查配置
- 数据库配置：`backend/config.py`
- API配置：`frontend/src/lib/api.ts`

### 重启服务
```bash
# 重启后端
cd backend
python app.py

# 重启前端
cd frontend
npm run dev
```

---

## ✅ 快速检查清单

启动前检查：
- [ ] MySQL服务已启动
- [ ] Redis服务已启动（如需要）
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装
- [ ] 数据库已初始化

访问前检查：
- [ ] 用户已注册
- [ ] 用户已登录
- [ ] 企业信息已绑定
- [ ] 订阅状态有效

功能检查：
- [ ] 页面可正常访问
- [ ] 数据可正常加载
- [ ] 导出功能正常
- [ ] 无控制台错误

---

**祝您使用愉快！** 🎉

如有问题，请查看相关文档或联系技术支持。
