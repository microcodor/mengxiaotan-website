# IM推送集成 V2.0 更新说明

## 🎯 重大变更

### 设计变更
从**全局配置**改为**用户级配置**,每个用户可以配置自己企业的IM应用。

### 变更前 (V1.0)
- IM应用配置(AppID、Secret)存储在环境变量
- 所有用户共用一套IM应用
- 适用于单一企业场景

### 变更后 (V2.0) ✅
- IM应用配置存储在用户表(`users.im_app_config`)
- 每个用户配置自己企业的IM应用
- 适用于多租户/多企业场景
- Secret加密存储,安全性更高

---

## 📊 数据结构

### 1. 用户表新增字段
```sql
ALTER TABLE users ADD COLUMN im_app_config JSON COMMENT 'IM应用配置';
```

**数据格式**:
```json
{
  "enterprise_wechat": {
    "enabled": true,
    "corp_id": "ww1234567890abcdef",
    "agent_id": "1000002",
    "secret": "encrypted_secret"  // 加密存储
  },
  "dingtalk": {
    "enabled": true,
    "app_key": "dingxxxxxxxx",
    "app_secret": "encrypted_secret",
    "agent_id": "123456789"
  },
  "feishu": {
    "enabled": true,
    "app_id": "cli_xxxxxxxx",
    "app_secret": "encrypted_secret"
  }
}
```

### 2. 订阅表(无变更)
```python
push_channels = Column(JSON)  # 接收人配置
```

---

## 🔧 新增功能

### 后端

#### 1. 加密工具 (`app/utils/crypto.py`)
- `encrypt_im_app_config()` - 加密IM应用配置
- `decrypt_im_app_config()` - 解密IM应用配置
- `mask_im_app_config()` - 脱敏显示配置

#### 2. 新增API接口

**IM应用配置API**:
- `GET /api/push-settings/im-apps` - 获取IM应用配置(脱敏)
- `POST /api/push-settings/im-apps` - 更新IM应用配置
- `POST /api/push-settings/im-apps/test` - 测试IM应用连接

**推送渠道配置API**(接收人):
- `GET /api/push-settings/channels` - 获取推送渠道配置
- `POST /api/push-settings/channels` - 更新推送渠道配置
- `POST /api/push-settings/test` - 测试推送

### 前端

#### 1. Tab页面结构
- **Tab 1: IM应用配置** - 配置企业微信/钉钉/飞书应用
- **Tab 2: 接收人配置** - 配置推送接收人UserID

#### 2. 功能特性
- ✅ 启用/禁用各个IM平台
- ✅ 配置应用凭证(AppID、Secret等)
- ✅ 测试连接功能
- ✅ Secret密码输入框
- ✅ 配置保存和加载
- ✅ 接收人配置
- ✅ 测试推送功能

---

## 📁 文件变更

### 新增文件
1. `backend/app/utils/crypto.py` - 加密工具
2. `backend/migrations/add_im_app_config.sql` - 数据库迁移
3. `IM_PUSH_NEW_DESIGN.md` - 新设计文档
4. `IM_PUSH_V2_UPDATE.md` - 本文档

### 修改文件
1. `backend/app/models.py` - 添加`im_app_config`字段
2. `backend/app/api/push_settings.py` - 重构API接口
3. `frontend/src/pages/PushSettings.tsx` - 重构为Tab页面

---

## 🚀 部署步骤

### 第1步: 数据库迁移
```bash
cd backend
mysql -u root -p energy_station < migrations/add_im_app_config.sql
```

### 第2步: 安装依赖
```bash
# 后端需要cryptography库
cd backend
./venv/bin/pip install cryptography
```

### 第3步: 配置加密密钥(可选)
在 `backend/.env` 中添加:
```bash
CRYPTO_SECRET_KEY=your-secret-key-for-encryption
```

### 第4步: 重启服务
```bash
# 后端
cd backend
./venv/bin/python app.py

# 前端
cd frontend
npm run dev
```

### 第5步: 测试功能
1. 访问 http://localhost:5173/dashboard/push
2. 切换到"IM应用配置"Tab
3. 配置企业微信/钉钉/飞书应用
4. 测试连接
5. 切换到"接收人配置"Tab
6. 配置接收人UserID
7. 测试推送

---

## 🔐 安全特性

### 1. Secret加密存储
- 使用AES加密算法
- 基于PBKDF2密钥派生
- 加密后存储到数据库

### 2. Secret脱敏显示
- 前端显示时只显示前4个字符
- 其余字符显示为`****`
- 例如: `abcd****`

### 3. 权限控制
- 用户只能查看和修改自己的配置
- Secret在传输时使用HTTPS加密

---

## 💡 使用流程

### 用户配置流程
```
1. 登录系统
   ↓
2. 进入推送设置
   ↓
3. Tab 1: IM应用配置
   ├─ 启用企业微信
   ├─ 填写CorpID、AgentID、Secret
   ├─ 测试连接
   └─ 保存配置
   ↓
4. Tab 2: 接收人配置
   ├─ 填写企业微信UserID
   ├─ 测试推送
   └─ 保存配置
   ↓
5. 完成配置,开始接收推送
```

### 推送执行流程
```
触发推送
   ↓
获取用户IM应用配置
   ↓
解密Secret
   ↓
使用用户配置获取Token
   ↓
获取接收人配置
   ↓
发送推送消息
   ↓
返回推送结果
```

---

## 🎨 界面预览

### Tab 1: IM应用配置
```
┌─────────────────────────────────────────┐
│ 推送设置                                 │
├─────────────────────────────────────────┤
│ [IM应用配置] [接收人配置]                │
├─────────────────────────────────────────┤
│                                         │
│ 企业微信应用配置          [✓] 启用       │
│ ┌─────────────────────────────────────┐ │
│ │ 企业ID (CorpID)                     │ │
│ │ [ww1234567890abcdef____________]    │ │
│ │                                     │ │
│ │ 应用ID (AgentID)                    │ │
│ │ [1000002_______________________]    │ │
│ │                                     │ │
│ │ 应用Secret                          │ │
│ │ [●●●●●●●●●●●●●●●●●●●●●●●●●●]        │ │
│ │                                     │ │
│ │ [测试连接]                           │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [保存配置]                               │
└─────────────────────────────────────────┘
```

### Tab 2: 接收人配置
```
┌─────────────────────────────────────────┐
│ 推送设置                                 │
├─────────────────────────────────────────┤
│ [IM应用配置] [接收人配置]                │
├─────────────────────────────────────────┤
│                                         │
│ 当前订阅: 基础版                         │
│ 可用渠道: 企业微信、钉钉、飞书、邮件      │
│                                         │
│ 企业微信                                │
│ ┌─────────────────────────────────────┐ │
│ │ 用户ID (UserID)                     │ │
│ │ [zhangsan__________________]        │ │
│ │ 💡 在企业微信通讯录中查看成员账号     │ │
│ │                                     │ │
│ │ [测试推送]                           │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [保存配置]                               │
└─────────────────────────────────────────┘
```

---

## ✅ 测试清单

### 后端测试
- [ ] 数据库字段添加成功
- [ ] 加密/解密功能正常
- [ ] IM应用配置API正常
- [ ] 推送渠道配置API正常
- [ ] 测试连接功能正常
- [ ] 测试推送功能正常

### 前端测试
- [ ] Tab切换正常
- [ ] IM应用配置表单正常
- [ ] 接收人配置表单正常
- [ ] 测试连接按钮正常
- [ ] 测试推送按钮正常
- [ ] 保存配置正常
- [ ] 加载配置正常

### 集成测试
- [ ] 配置企业微信应用
- [ ] 测试企业微信连接
- [ ] 配置企业微信接收人
- [ ] 测试企业微信推送
- [ ] 配置钉钉应用
- [ ] 测试钉钉推送
- [ ] 配置飞书应用
- [ ] 测试飞书推送

---

## 🎯 优势对比

### V1.0 (全局配置)
- ❌ 所有用户共用一套IM应用
- ❌ 只适用于单一企业
- ❌ Secret明文存储在环境变量
- ✅ 配置简单

### V2.0 (用户级配置)
- ✅ 每个用户使用自己的IM应用
- ✅ 适用于多租户场景
- ✅ Secret加密存储
- ✅ 更高的安全性
- ✅ 更大的灵活性
- ⚠️ 配置稍复杂(但更安全)

---

## 📝 注意事项

### 1. 数据迁移
- 现有用户需要重新配置IM应用
- 旧的环境变量配置不再使用

### 2. 加密密钥
- 生产环境必须设置`CRYPTO_SECRET_KEY`
- 密钥丢失将无法解密已存储的Secret

### 3. 依赖安装
- 需要安装`cryptography`库
- `pip install cryptography`

### 4. 兼容性
- 与V1.0不兼容
- 需要执行数据库迁移

---

## 🔄 回滚方案

如需回滚到V1.0:
1. 恢复旧版本代码
2. 删除`im_app_config`字段
3. 恢复环境变量配置

---

**版本**: 2.0  
**更新时间**: 2026-04-16  
**状态**: ✅ 已完成  
**兼容性**: 不兼容V1.0
