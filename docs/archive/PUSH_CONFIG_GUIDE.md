# 推送配置完整指南

## 📋 概述

蒙小碳的推送系统分为两个层面的配置：
1. **IM应用配置**（用户端）- 配置企业微信/钉钉/飞书的应用信息
2. **推送渠道配置**（管理端）- 配置具体的接收人ID

## 🔧 配置流程

### 第一步：用户配置IM应用（必需）

用户需要先在个人设置中配置IM应用信息，这是推送功能的基础。

**配置位置**：用户个人设置 → IM应用配置

**需要配置的信息**：

#### 企业微信
- `corp_id`: 企业ID
- `agent_id`: 应用AgentId
- `secret`: 应用Secret

#### 钉钉
- `app_key`: 应用AppKey
- `app_secret`: 应用AppSecret
- `agent_id`: 应用AgentId

#### 飞书
- `app_id`: 应用App ID
- `app_secret`: 应用App Secret

**API端点**：
```
POST /api/push-settings/im-apps
GET /api/push-settings/im-apps
POST /api/push-settings/im-apps/test
```

### 第二步：管理员配置推送渠道（必需）

管理员在后台为用户配置具体的接收人ID。

**配置位置**：管理后台 → 推送配置 (`/admin/push`)

**需要配置的信息**：
- `enterprise_wechat`: 企业微信UserID（如：zhangsan）
- `dingtalk`: 钉钉UserID（如：manager123）
- `feishu`: 飞书Open ID（如：ou_xxx）
- `email`: 邮箱地址
- `sms`: 手机号码

**API端点**：
```
GET /api/push-settings/admin/user/{user_id}
PUT /api/push-settings/admin/user/{user_id}
POST /api/push-settings/admin/user/{user_id}/test
```

## 🧪 测试推送

### 测试前提条件

1. ✅ 用户已配置IM应用信息
2. ✅ 管理员已配置推送渠道接收人
3. ✅ 用户有活跃的订阅

### 测试方法

#### 方法1：管理后台测试
1. 进入 `/admin/push` 页面
2. 输入用户ID查询
3. 点击对应渠道的"测试"按钮
4. 系统会发送测试消息到配置的接收人

#### 方法2：API测试
```bash
# 管理员测试用户推送
curl -X POST http://localhost:5001/api/push-settings/admin/user/1/test \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "enterprise_wechat",
    "message": "这是一条测试消息"
  }'
```

## ❌ 常见问题

### 1. 测试推送失败

**可能原因**：
- ❌ 用户未配置IM应用信息
- ❌ IM应用配置错误（Corp ID、Secret等）
- ❌ 接收人ID配置错误
- ❌ 用户没有活跃订阅

**解决方法**：
1. 确认用户已在个人设置中配置IM应用
2. 使用 `/api/push-settings/im-apps/test` 测试IM应用连接
3. 检查接收人ID格式是否正确
4. 确认用户有活跃订阅

### 2. 企业微信配置不完整提示

**原因**：后端启动时检测到系统级企业微信配置不完整

**说明**：这是正常的，因为推送系统使用的是用户级配置，不是系统级配置

**解决**：忽略此提示，确保用户在个人设置中配置了IM应用即可

### 3. 无法找到IM应用配置入口

**用户端配置位置**：
- 登录后 → 个人中心 → 设置 → IM应用配置
- 或访问 `/settings/im-apps`（需要实现此页面）

## 📊 配置状态检查

### 检查用户配置完整性

```bash
# 查询用户推送设置
curl -X GET http://localhost:5001/api/push-settings/admin/user/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**返回示例**：
```json
{
  "user_id": 1,
  "username": "admin",
  "company_name": "测试企业",
  "subscription_level": "premium",
  "allowed_channels": ["enterprise_wechat", "dingtalk", "feishu", "email", "sms"],
  "configured_channels": {
    "enterprise_wechat": "zhangsan",
    "dingtalk": "manager123",
    "feishu": null,
    "email": "user@example.com",
    "sms": null
  }
}
```

## 🎨 页面优化说明

### 已完成的优化

1. ✅ **主色调统一**：使用绿色主题（primary-500/600）
2. ✅ **渐变效果**：按钮和图标使用渐变背景
3. ✅ **圆角优化**：使用 `rounded-xl` 替代 `rounded-lg`
4. ✅ **阴影效果**：添加 `shadow-sm` 提升层次感
5. ✅ **配置说明**：添加蓝色提示框说明配置流程
6. ✅ **状态标识**：使用彩色徽章标识订阅等级
7. ✅ **渠道图标**：每个渠道使用独特的渐变色
8. ✅ **空状态优化**：美化空状态提示

### 样式特点

- **主色调**：绿色 (`from-primary-500 to-primary-600`)
- **辅助色**：蓝色（说明）、红色（错误）、灰色（禁用）
- **圆角**：`rounded-xl` (12px)
- **间距**：统一使用 `gap-3`、`p-6` 等
- **过渡**：所有交互元素添加 `transition-colors` 或 `transition-all`

## 🔐 权限说明

### 用户权限
- ✅ 配置自己的IM应用信息
- ✅ 查看自己的推送渠道配置
- ✅ 测试自己的推送渠道

### 管理员权限
- ✅ 查询任意用户的推送设置
- ✅ 为任意用户配置推送渠道
- ✅ 测试任意用户的推送功能
- ⚠️ 注意：管理员不能查看用户的IM应用Secret

## 📝 开发建议

### 待实现功能

1. **用户端IM应用配置页面**
   - 路径：`/settings/im-apps`
   - 功能：用户自助配置企业微信/钉钉/飞书应用信息

2. **批量配置功能**
   - 支持CSV导入批量配置用户推送渠道

3. **推送日志查看**
   - 查看历史推送记录和状态

4. **权限验证增强**
   - 在管理员API中添加真正的权限验证
   - 目前只有 `# TODO: 添加管理员权限验证` 注释

## 🚀 快速测试

### 完整测试流程

```bash
# 1. 用户配置IM应用（需要用户登录）
curl -X POST http://localhost:5001/api/push-settings/im-apps \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_wechat": {
      "enabled": true,
      "corp_id": "ww1234567890abcdef",
      "agent_id": "1000002",
      "secret": "your-secret-here"
    }
  }'

# 2. 测试IM应用连接
curl -X POST http://localhost:5001/api/push-settings/im-apps/test \
  -H "Authorization: Bearer USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"platform": "enterprise_wechat"}'

# 3. 管理员配置推送渠道
curl -X PUT http://localhost:5001/api/push-settings/admin/user/1 \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_wechat": "zhangsan"
  }'

# 4. 管理员测试推送
curl -X POST http://localhost:5001/api/push-settings/admin/user/1/test \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "enterprise_wechat",
    "message": "测试消息"
  }'
```

## 📞 技术支持

如有问题，请检查：
1. 后端日志：`backend/logs/app.log`
2. 浏览器控制台
3. 网络请求响应

---

**最后更新**：2026-04-17
**版本**：v1.0
