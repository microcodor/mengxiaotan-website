# IM推送集成 - 新设计方案

## 🎯 设计变更

### 原设计
- IM应用配置(AppID、Secret)存储在环境变量
- 所有用户共用一套IM应用

### 新设计 ✅
- **IM应用配置存储在用户后台**
- 每个用户可以配置自己的IM应用
- 用户可以使用自己企业的企业微信/钉钉/飞书应用

---

## 📊 数据结构设计

### 1. 用户表 (users)
添加字段存储IM应用配置:

```python
im_app_config = Column(JSON, comment='IM应用配置')
```

**数据格式**:
```json
{
  "enterprise_wechat": {
    "enabled": true,
    "corp_id": "ww1234567890abcdef",
    "agent_id": "1000002",
    "secret": "your-secret-here"
  },
  "dingtalk": {
    "enabled": true,
    "app_key": "dingxxxxxxxx",
    "app_secret": "your-secret-here",
    "agent_id": "123456789"
  },
  "feishu": {
    "enabled": true,
    "app_id": "cli_xxxxxxxx",
    "app_secret": "your-secret-here"
  }
}
```

### 2. 订阅表 (subscriptions)
已有字段存储接收人配置:

```python
push_channels = Column(JSON, comment='推送渠道配置')
```

**数据格式**:
```json
{
  "enterprise_wechat": "zhangsan",  // 企业微信UserID
  "dingtalk": "manager123",         // 钉钉UserID
  "feishu": "ou_xxx",               // 飞书OpenID
  "email": "user@example.com",
  "sms": "13800138000"
}
```

---

## 🔧 API设计

### 用户端API

#### 1. 获取IM应用配置
```http
GET /api/push-settings/im-apps
Authorization: Bearer <token>
```

**响应**:
```json
{
  "enterprise_wechat": {
    "enabled": true,
    "corp_id": "ww1234567890abcdef",
    "agent_id": "1000002",
    "secret": "***" // 脱敏显示
  },
  "dingtalk": {
    "enabled": false
  },
  "feishu": {
    "enabled": false
  }
}
```

#### 2. 更新IM应用配置
```http
POST /api/push-settings/im-apps
Authorization: Bearer <token>
Content-Type: application/json

{
  "enterprise_wechat": {
    "enabled": true,
    "corp_id": "ww1234567890abcdef",
    "agent_id": "1000002",
    "secret": "your-secret-here"
  }
}
```

#### 3. 获取推送渠道配置(接收人)
```http
GET /api/push-settings/channels
Authorization: Bearer <token>
```

**响应**:
```json
{
  "subscription_level": "基础版",
  "allowed_channels": ["enterprise_wechat", "dingtalk", "feishu", "email"],
  "channels": {
    "enterprise_wechat": "zhangsan",
    "dingtalk": "",
    "feishu": "",
    "email": "user@example.com"
  }
}
```

#### 4. 更新推送渠道配置(接收人)
```http
POST /api/push-settings/channels
Authorization: Bearer <token>
Content-Type: application/json

{
  "enterprise_wechat": "zhangsan",
  "dingtalk": "manager123",
  "email": "user@example.com"
}
```

#### 5. 测试推送
```http
POST /api/push-settings/test
Authorization: Bearer <token>
Content-Type: application/json

{
  "channel": "enterprise_wechat"
}
```

---

## 🎨 前端界面设计

### 用户推送设置页面

#### Tab 1: IM应用配置
```
┌─────────────────────────────────────────┐
│ IM应用配置                               │
├─────────────────────────────────────────┤
│                                         │
│ 企业微信应用配置                         │
│ ┌─────────────────────────────────────┐ │
│ │ ☑ 启用企业微信推送                   │ │
│ │                                     │ │
│ │ 企业ID (CorpID)                     │ │
│ │ [ww1234567890abcdef____________]    │ │
│ │                                     │ │
│ │ 应用ID (AgentID)                    │ │
│ │ [1000002_______________________]    │ │
│ │                                     │ │
│ │ 应用Secret                          │ │
│ │ [**************************]  [显示] │ │
│ │                                     │ │
│ │ [测试连接]  [保存配置]               │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 钉钉应用配置                            │
│ ┌─────────────────────────────────────┐ │
│ │ ☐ 启用钉钉推送                       │ │
│ │ (展开后显示配置项)                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 飞书应用配置                            │
│ ┌─────────────────────────────────────┐ │
│ │ ☐ 启用飞书推送                       │ │
│ │ (展开后显示配置项)                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

#### Tab 2: 接收人配置
```
┌─────────────────────────────────────────┐
│ 推送接收人配置                           │
├─────────────────────────────────────────┤
│                                         │
│ 当前订阅: 基础版                         │
│ 可用渠道: 企业微信、钉钉、飞书、邮件      │
│                                         │
│ 企业微信                                │
│ ┌─────────────────────────────────────┐ │
│ │ ☑ 启用  (需要先配置应用)             │ │
│ │                                     │ │
│ │ 用户ID (UserID)                     │ │
│ │ [zhangsan__________________]        │ │
│ │                                     │ │
│ │ 💡 在企业微信通讯录中查看成员账号     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 钉钉                                    │
│ ┌─────────────────────────────────────┐ │
│ │ ☐ 启用  (需要先配置应用)             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [保存配置]  [测试推送]                   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔄 推送流程

### 1. 用户配置流程
```
用户登录
    ↓
进入推送设置
    ↓
Tab 1: 配置IM应用
    ├─→ 填写企业微信应用信息
    ├─→ 填写钉钉应用信息
    └─→ 填写飞书应用信息
    ↓
测试连接(验证配置是否正确)
    ↓
保存配置
    ↓
Tab 2: 配置接收人
    ├─→ 填写企业微信UserID
    ├─→ 填写钉钉UserID
    └─→ 填写飞书OpenID
    ↓
测试推送
    ↓
完成配置
```

### 2. 推送执行流程
```
触发推送
    ↓
获取用户IM应用配置
    ↓
获取用户接收人配置
    ↓
使用用户的应用配置获取Token
    ↓
向用户的接收人发送消息
    ↓
返回推送结果
```

---

## 📝 数据库迁移

### 添加字段
```python
# migrations/versions/xxx_add_im_app_config.py

def upgrade():
    op.add_column('users', 
        sa.Column('im_app_config', sa.JSON(), nullable=True, comment='IM应用配置')
    )

def downgrade():
    op.drop_column('users', 'im_app_config')
```

---

## 🔐 安全考虑

### 1. Secret加密存储
- 使用AES加密存储Secret
- 只在推送时解密使用
- 前端显示时脱敏(显示为***)

### 2. 权限控制
- 用户只能查看和修改自己的配置
- 管理员可以查看所有用户配置(Secret脱敏)

### 3. 配置验证
- 保存前验证配置格式
- 测试连接验证配置有效性
- 推送失败时记录详细日志

---

## 💡 优势

### 1. 灵活性
- 每个用户使用自己企业的IM应用
- 不同用户可以使用不同的IM平台

### 2. 安全性
- 用户数据隔离
- Secret加密存储
- 不依赖全局配置

### 3. 可扩展性
- 易于添加新的IM平台
- 支持企业级多租户场景

---

## 🚀 实施步骤

### 第1步: 数据库迁移
- [ ] 添加 `im_app_config` 字段到users表

### 第2步: 后端API实现
- [ ] 实现IM应用配置API (GET/POST /api/push-settings/im-apps)
- [ ] 更新推送渠道配置API
- [ ] 修改推送服务使用用户配置
- [ ] 添加Secret加密/解密功能

### 第3步: 前端界面实现
- [ ] 更新PushSettings页面,添加Tab切换
- [ ] 实现IM应用配置表单
- [ ] 实现接收人配置表单
- [ ] 添加测试连接功能

### 第4步: 测试
- [ ] 测试IM应用配置
- [ ] 测试接收人配置
- [ ] 测试推送功能
- [ ] 测试Secret加密

---

## 📋 需要修改的文件

### 后端
1. `backend/app/models.py` - 添加im_app_config字段
2. `backend/app/api/push_settings.py` - 添加IM应用配置API
3. `backend/app/services/enterprise_wechat_push_service.py` - 使用用户配置
4. `backend/app/services/dingtalk_push_service.py` - 使用用户配置
5. `backend/app/services/feishu_push_service.py` - 使用用户配置
6. `backend/app/services/multi_channel_pusher.py` - 传递用户配置
7. `backend/app/utils/crypto.py` - 新增,Secret加密工具

### 前端
1. `frontend/src/pages/PushSettings.tsx` - 重构为Tab页面
2. `frontend/src/components/IMAppConfig.tsx` - 新增,IM应用配置组件
3. `frontend/src/components/ChannelConfig.tsx` - 新增,接收人配置组件

### 数据库
1. 新增迁移文件

---

**设计版本**: 2.0  
**更新时间**: 2026-04-16  
**状态**: 待实施
