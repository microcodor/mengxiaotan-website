# 推送系统使用指南

## 📱 功能概述

蒙小碳·能源站支持企业微信推送功能，可以将每日简报、重要文章等信息实时推送到用户的企业微信。

---

## 🔧 配置步骤

### 1. 获取企业微信配置

#### 步骤 1：登录企业微信管理后台
访问：https://work.weixin.qq.com/

#### 步骤 2：获取企业 ID (CorpID)
- 进入「我的企业」
- 在「企业信息」中找到「企业 ID」
- 复制保存

#### 步骤 3：创建应用
- 进入「应用管理」→「应用」→「创建应用」
- 填写应用名称：蒙小碳·能源站
- 上传应用 Logo
- 选择可见范围（选择需要接收推送的部门/成员）
- 创建完成后，记录「AgentId」和「Secret」

#### 步骤 4：配置环境变量
编辑 `backend/.env` 文件，添加以下配置：

```env
# 企业微信推送配置
WECHAT_WORK_CORPID=your-corp-id
WECHAT_WORK_CORPSECRET=your-corp-secret
WECHAT_WORK_AGENTID=your-agent-id
```

### 2. 重启后端服务

```bash
# 停止服务
./stop.sh

# 启动服务
./start.sh
```

---

## 👤 用户配置

### 1. 获取企业微信用户 ID

用户的企业微信 ID 通常是：
- 工号
- 邮箱前缀
- 手机号

可以在企业微信管理后台的「通讯录」中查看。

### 2. 配置推送设置

1. 登录蒙小碳·能源站
2. 访问「推送设置」页面：http://localhost:5173/push-settings
3. 填写企业微信用户 ID
4. 点击「发送测试消息」验证配置
5. 设置关键词订阅（可选）
6. 保存设置

---

## 📨 推送类型

### 1. 每日简报推送

**推送时间**：每天 9:30

**推送内容**：
- 发改委动态摘要
- 煤炭行业要闻
- 电力行业动态
- 新能源资讯
- AI 决策建议

**推送对象**：所有活跃订阅用户

### 2. 重要文章推送

**推送时机**：文章发布后实时推送

**推送内容**：
- 文章标题
- 文章摘要
- 文章分类和来源
- 查看详情链接

**推送对象**：
- 所有订阅用户
- 或管理员指定的用户

### 3. 关键词匹配推送

**推送时机**：文章包含用户关注的关键词时

**推送内容**：
- 匹配的关键词
- 文章标题和摘要
- 查看详情链接

**推送对象**：设置了该关键词的用户

### 4. 自定义推送

**推送时机**：管理员手动创建推送任务

**推送内容**：自定义标题和内容

**推送对象**：
- 所有订阅用户
- 指定套餐用户
- 自定义用户列表

---

## 🎛️ 管理员功能

### 1. 推送管理

访问：http://localhost:5173/admin/broadcast

功能：
- 创建推送任务
- 查看推送历史
- 推送今日简报
- 查看推送统计

### 2. 创建推送任务

1. 点击「创建推送」
2. 填写标题和内容
3. 选择推送对象
4. 点击「立即发送」

### 3. 推送今日简报

1. 确保今日简报已生成
2. 点击「推送今日简报」
3. 系统自动推送给所有订阅用户

---

## 📊 API 接口

### 用户端接口

#### 获取推送设置
```http
GET /api/push/settings
Authorization: Bearer <token>
```

#### 更新推送设置
```http
PUT /api/push/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "push_channels": {
    "enterprise_wechat": "user_id"
  },
  "custom_keywords": ["煤炭", "电力", "新能源"]
}
```

#### 发送测试消息
```http
POST /api/push/test
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "测试消息内容",
  "message_type": "text"
}
```

### 管理员接口

#### 创建推送任务
```http
POST /api/push/broadcast
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "推送标题",
  "content": "推送内容",
  "target_type": "all",
  "channel": "enterprise_wechat"
}
```

#### 推送每日简报
```http
POST /api/push/daily-brief
Authorization: Bearer <token>
```

#### 推送文章
```http
POST /api/push/article/{article_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_ids": [1, 2, 3]  // 可选，不指定则发送给所有用户
}
```

---

## 🔍 消息类型

### 1. 文本消息 (text)
```json
{
  "message_type": "text",
  "content": "这是一条文本消息"
}
```

### 2. Markdown 消息 (markdown)
```json
{
  "message_type": "markdown",
  "content": "# 标题\n\n**粗体** *斜体*\n\n- 列表项1\n- 列表项2"
}
```

### 3. 文本卡片 (textcard)
```json
{
  "message_type": "textcard",
  "title": "卡片标题",
  "content": "卡片内容",
  "url": "https://example.com",
  "btntxt": "查看详情"
}
```

---

## 🐛 常见问题

### 1. 推送失败

**可能原因**：
- 企业微信配置错误
- 用户 ID 不正确
- 应用可见范围未包含该用户
- Access Token 过期

**解决方法**：
- 检查 `.env` 配置是否正确
- 确认用户 ID 是否正确
- 在企业微信后台检查应用可见范围
- 重启后端服务刷新 Token

### 2. 收不到推送

**可能原因**：
- 未配置企业微信用户 ID
- 订阅已过期
- 企业微信未关注应用

**解决方法**：
- 在推送设置页面配置用户 ID
- 检查订阅状态
- 在企业微信中关注应用

### 3. 测试消息发送失败

**可能原因**：
- 企业微信配置错误
- 用户 ID 格式不正确
- 网络连接问题

**解决方法**：
- 检查配置是否正确
- 联系管理员确认用户 ID
- 检查服务器网络连接

---

## 📈 推送统计

### 查看推送记录

访问：http://localhost:5173/admin/broadcast

可以查看：
- 推送任务列表
- 推送状态（待发送/发送中/已完成/失败）
- 推送时间
- 推送对象

### 推送日志

推送日志存储在数据库 `broadcast_logs` 表中，包含：
- 用户 ID
- 推送状态
- 发送时间
- 阅读时间
- 错误信息

---

## 🔐 安全建议

1. **保护配置信息**
   - 不要将 `.env` 文件提交到版本控制
   - 定期更换 Secret

2. **限制推送频率**
   - 避免频繁推送打扰用户
   - 合理设置推送时间

3. **用户隐私**
   - 不要在推送中包含敏感信息
   - 遵守用户隐私政策

---

## 📞 技术支持

如有问题，请：
1. 查看本文档
2. 查看企业微信官方文档：https://developer.work.weixin.qq.com/
3. 联系技术支持

---

**最后更新**：2026-04-10
