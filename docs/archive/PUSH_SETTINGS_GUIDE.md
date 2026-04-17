# 推送配置管理说明文档

## 概述

推送配置管理是**基于用户维度**的功能，允许管理员为每个用户配置不同推送渠道的接收人信息。

## 架构设计

### 1. 数据存储

推送配置存储在 `subscriptions` 表的 `push_channels` 字段中（JSON格式）：

```json
{
  "enterprise_wechat": "zhangsan",
  "dingtalk": "manager123",
  "feishu": "ou_xxx",
  "email": "user@example.com",
  "sms": "13800138000"
}
```

### 2. 配置层级

推送配置分为两个层级：

#### 层级1：IM应用配置（用户自己配置）
- **位置**：用户个人设置页面
- **内容**：IM应用的认证信息
  - 企业微信：Corp ID、Corp Secret、Agent ID
  - 钉钉：App Key、App Secret
  - 飞书：App ID、App Secret
- **作用**：提供推送服务的认证凭证

#### 层级2：推送渠道配置（管理员配置）
- **位置**：管理后台 → 推送配置管理
- **内容**：各渠道的接收人ID
  - 企业微信：UserID（如：zhangsan）
  - 钉钉：UserID
  - 飞书：Open ID
  - 邮件：邮箱地址
  - 短信：手机号
- **作用**：指定消息发送给谁

### 3. 工作流程

```
1. 用户在个人设置中配置IM应用信息（提供认证凭证）
   ↓
2. 管理员在推送配置管理中为用户配置接收人ID
   ↓
3. 系统发送推送时：
   - 使用用户配置的IM应用信息获取access_token
   - 使用管理员配置的接收人ID发送消息
```

## 功能说明

### 管理员功能

#### 1. 查询用户
- **路径**：`/admin/push`
- **操作**：输入用户ID查询用户信息
- **返回**：
  - 用户基本信息（ID、用户名、企业名称）
  - 订阅等级
  - 允许的推送渠道
  - 已配置的推送渠道

#### 2. 配置推送渠道
- **操作**：为用户填写各渠道的接收人ID
- **支持渠道**：
  - 企业微信（所有用户）
  - 钉钉（基础版及以上）
  - 飞书（基础版及以上）
  - 邮件（基础版及以上）
  - 短信（高级版）

#### 3. 测试推送
- **操作**：点击"测试"按钮发送测试消息
- **前提**：
  - 用户已配置IM应用信息
  - 管理员已配置接收人ID
- **结果**：显示推送是否成功

### 用户功能

#### 1. 配置IM应用（待实现）
- **路径**：`/settings/im-apps`
- **内容**：
  - 企业微信应用配置
  - 钉钉应用配置
  - 飞书应用配置

#### 2. 查看推送设置
- **路径**：`/settings/push`
- **内容**：查看管理员为自己配置的推送渠道

## API接口

### 管理员接口

#### 1. 获取用户推送设置
```http
GET /api/push-settings/admin/user/:user_id
Authorization: Bearer <admin_token>
```

**响应**：
```json
{
  "user_id": 1,
  "username": "13800138000",
  "company_name": "示例企业",
  "subscription_level": "standard",
  "allowed_channels": ["enterprise_wechat", "dingtalk", "feishu", "email"],
  "configured_channels": {
    "enterprise_wechat": "zhangsan",
    "dingtalk": "manager123"
  }
}
```

#### 2. 更新用户推送设置
```http
PUT /api/push-settings/admin/user/:user_id
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "enterprise_wechat": "zhangsan",
  "dingtalk": "manager123",
  "feishu": "ou_xxx",
  "email": "user@example.com"
}
```

#### 3. 测试用户推送
```http
POST /api/push-settings/admin/user/:user_id/test
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "channel": "enterprise_wechat",
  "message": "这是一条测试消息"
}
```

**响应**：
```json
{
  "success": true,
  "message": "测试推送已发送",
  "channel": "enterprise_wechat"
}
```

### 用户接口

#### 1. 获取自己的推送设置
```http
GET /api/push-settings
Authorization: Bearer <user_token>
```

#### 2. 更新自己的推送设置
```http
PUT /api/push-settings
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "push_channels": {
    "enterprise_wechat": "zhangsan"
  },
  "custom_keywords": ["煤炭", "电力"]
}
```

## 订阅等级与推送渠道

| 订阅等级 | 企业微信 | 钉钉 | 飞书 | 邮件 | 短信 |
|---------|---------|------|------|------|------|
| 免费订阅 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 基础版   | ✅ | ✅ | ✅ | ✅ | ❌ |
| 高级版   | ✅ | ✅ | ✅ | ✅ | ✅ |

## 常见问题

### Q1: 为什么测试推送失败？
**A**: 可能的原因：
1. 用户未配置IM应用信息（Corp ID、Secret等）
2. 接收人ID填写错误
3. IM应用权限不足
4. 网络连接问题

**解决方法**：
1. 确认用户已在个人设置中配置IM应用
2. 检查接收人ID是否正确
3. 查看后端日志获取详细错误信息

### Q2: 如何获取企业微信的UserID？
**A**: 
1. 登录企业微信管理后台
2. 进入"通讯录"
3. 点击成员，查看"账号"字段即为UserID

### Q3: 推送配置是否支持批量导入？
**A**: 当前版本不支持，需要逐个用户配置。后续版本可考虑添加批量导入功能。

### Q4: 用户可以自己修改推送配置吗？
**A**: 
- 用户可以配置自己的IM应用信息
- 接收人ID由管理员统一配置，用户只能查看

## 待实现功能

1. **用户IM应用配置页面**
   - 企业微信应用配置
   - 钉钉应用配置
   - 飞书应用配置

2. **批量配置功能**
   - Excel导入用户推送配置
   - 批量测试推送

3. **推送日志查询**
   - 查看历史推送记录
   - 推送成功率统计

4. **更多推送渠道**
   - 个人微信（服务号）
   - Slack
   - Telegram

## 技术实现

### 前端组件
- `frontend/src/pages/admin/PushManagement.tsx`

### 后端接口
- `backend/app/api/push.py`

### 推送服务
- `backend/app/services/push_service.py`
- `backend/app/services/multi_channel_pusher.py`

### 数据模型
- `Subscription.push_channels` - 推送渠道配置（JSON）
- `Subscription.custom_keywords` - 自定义关键词（JSON数组）

## 总结

推送配置管理是一个**用户维度**的功能，通过管理员为每个用户配置推送渠道接收人信息，结合用户自己配置的IM应用认证信息，实现个性化的消息推送服务。

这种设计的优势：
1. **灵活性**：每个用户可以使用不同的IM应用
2. **安全性**：认证信息由用户自己管理
3. **可扩展性**：易于添加新的推送渠道
4. **精准推送**：可以针对不同用户推送不同内容
