# IM推送快速开始指南

## 🚀 5分钟快速配置

### 第一步: 配置环境变量

编辑 `backend/.env` 文件,添加IM平台配置:

```bash
# 企业微信配置
ENTERPRISE_WECHAT_CORP_ID=ww1234567890abcdef
ENTERPRISE_WECHAT_AGENT_ID=1000002
ENTERPRISE_WECHAT_SECRET=your-secret-here

# 钉钉配置
DINGTALK_APP_KEY=dingxxxxxxxx
DINGTALK_APP_SECRET=your-secret-here
DINGTALK_AGENT_ID=123456789

# 飞书配置
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=your-secret-here
```

### 第二步: 重启后端服务

```bash
cd backend
source venv/bin/activate
flask run --port=5001
```

### 第三步: 访问推送设置

#### 用户端
1. 登录系统: `http://localhost:5173/login`
2. 进入推送设置: `http://localhost:5173/dashboard/push`
3. 配置推送渠道并保存

#### 管理端
1. 以管理员身份登录
2. 进入推送配置: `http://localhost:5173/admin/push`
3. 搜索用户并配置推送

### 第四步: 测试推送

点击"测试推送"按钮,检查是否收到消息。

---

## 📱 获取用户ID指南

### 企业微信用户ID

**方法1: 通过管理后台查看**
1. 登录[企业微信管理后台](https://work.weixin.qq.com/)
2. 进入"通讯录"
3. 点击成员,查看"账号"字段 (如: zhangsan)

**方法2: 通过API获取**
```python
# 调用企业微信API获取部门成员列表
GET https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=TOKEN&department_id=1
```

### 钉钉用户ID

**方法1: 通过管理后台查看**
1. 登录[钉钉管理后台](https://oa.dingtalk.com/)
2. 进入"通讯录"
3. 点击成员,查看"工号"或"UserID"

**方法2: 通过API获取**
```python
# 调用钉钉API获取用户详情
GET https://oapi.dingtalk.com/topapi/v2/user/get?access_token=TOKEN&userid=xxx
```

### 飞书用户ID

**方法1: 通过管理后台查看**
1. 登录[飞书管理后台](https://www.feishu.cn/admin)
2. 进入"通讯录"
3. 点击成员,查看"Open ID" (如: ou_xxx)

**方法2: 通过API获取**
```python
# 调用飞书API获取用户信息
GET https://open.feishu.cn/open-apis/contact/v3/users/:user_id
```

---

## 🧪 测试示例

### 使用curl测试API

#### 1. 获取用户推送配置
```bash
curl -X GET http://localhost:5001/api/push-settings/user/channels \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2. 更新推送配置
```bash
curl -X POST http://localhost:5001/api/push-settings/user/channels \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channels": {
      "enterprise_wechat": {
        "enabled": true,
        "user_id": "zhangsan"
      },
      "dingtalk": {
        "enabled": true,
        "user_id": "manager123"
      },
      "feishu": {
        "enabled": true,
        "user_id": "ou_xxx"
      }
    }
  }'
```

#### 3. 测试推送
```bash
curl -X POST http://localhost:5001/api/push-settings/user/test \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channels": ["enterprise_wechat", "dingtalk", "feishu"]
  }'
```

---

## 🔍 常见问题

### Q1: 推送失败,提示"invalid user_id"
**A**: 检查用户ID是否正确,确保是对应平台的真实用户ID。

### Q2: 推送失败,提示"access_token invalid"
**A**: 检查环境变量中的配置是否正确,特别是AppID和Secret。

### Q3: 看不到某些推送渠道
**A**: 检查用户的订阅等级,不同等级可用的渠道不同:
- 免费: 企业微信、钉钉、飞书
- 基础版: 企业微信、钉钉、飞书、邮件
- 高级版: 全部渠道

### Q4: 如何查看推送日志?
**A**: 查看后端日志文件或控制台输出,搜索"推送"关键字。

### Q5: 可以同时推送到多个渠道吗?
**A**: 可以,启用多个渠道后,系统会自动向所有启用的渠道推送。

---

## 📊 推送配置示例

### 示例1: 只使用企业微信
```json
{
  "channels": {
    "enterprise_wechat": {
      "enabled": true,
      "user_id": "zhangsan"
    }
  }
}
```

### 示例2: 使用多个IM平台
```json
{
  "channels": {
    "enterprise_wechat": {
      "enabled": true,
      "user_id": "zhangsan"
    },
    "dingtalk": {
      "enabled": true,
      "user_id": "manager123"
    },
    "feishu": {
      "enabled": true,
      "user_id": "ou_xxx"
    }
  }
}
```

### 示例3: 完整配置(高级版用户)
```json
{
  "channels": {
    "enterprise_wechat": {
      "enabled": true,
      "user_id": "zhangsan"
    },
    "dingtalk": {
      "enabled": true,
      "user_id": "manager123"
    },
    "feishu": {
      "enabled": true,
      "user_id": "ou_xxx"
    },
    "email": {
      "enabled": true,
      "address": "user@example.com"
    },
    "sms": {
      "enabled": true,
      "phone": "13800138000"
    }
  }
}
```

---

## 🎯 推送场景示例

### 场景1: 新文章推送
当有新文章发布时,系统会自动推送到用户配置的渠道:

**企业微信消息**:
```
【新文章推送】
标题: 2026年能源行业发展趋势
分类: 行业动态
摘要: 本文分析了2026年能源行业的主要发展趋势...
查看详情: http://localhost:5173/articles/123
```

**钉钉消息**:
```markdown
## 新文章推送

**标题**: 2026年能源行业发展趋势  
**分类**: 行业动态  
**摘要**: 本文分析了2026年能源行业的主要发展趋势...

[查看详情](http://localhost:5173/articles/123)
```

**飞书消息**:
```
新文章推送
━━━━━━━━━━━━━━━━
标题: 2026年能源行业发展趋势
分类: 行业动态
摘要: 本文分析了2026年能源行业的主要发展趋势...

👉 查看详情: http://localhost:5173/articles/123
```

### 场景2: 订阅到期提醒
```
【订阅到期提醒】
您的基础版订阅将于3天后到期
到期时间: 2026-04-19
续费可继续享受推送服务
立即续费: http://localhost:5173/subscription
```

### 场景3: 系统通知
```
【系统通知】
您有一条新的定制报告已生成
报告名称: 企业能源消耗分析报告
生成时间: 2026-04-16 14:30
查看报告: http://localhost:5173/dashboard/reports/456
```

---

## 🔧 高级配置

### 自定义推送内容

编辑 `backend/app/services/multi_channel_pusher.py`:

```python
def push(self, user_id: int, title: str, content: str, **kwargs):
    """
    自定义推送内容
    
    kwargs可选参数:
    - url: 跳转链接
    - image_url: 图片链接
    - action_text: 按钮文字
    - priority: 优先级 (high/normal/low)
    """
    # 实现自定义逻辑
```

### 推送失败重试

```python
# 在配置文件中添加重试设置
PUSH_RETRY_TIMES = 3
PUSH_RETRY_DELAY = 5  # 秒
```

### 推送频率限制

```python
# 防止推送过于频繁
PUSH_RATE_LIMIT = {
    'max_per_hour': 10,
    'max_per_day': 50
}
```

---

## 📈 监控和日志

### 查看推送日志
```bash
# 查看最近的推送日志
tail -f backend/logs/push.log

# 搜索特定用户的推送记录
grep "user_id=123" backend/logs/push.log
```

### 推送统计
```python
# 获取推送统计信息
GET /api/push-settings/stats
```

返回:
```json
{
  "total_pushes": 1000,
  "success_rate": 0.95,
  "channel_stats": {
    "enterprise_wechat": {
      "total": 400,
      "success": 380,
      "failed": 20
    },
    "dingtalk": {
      "total": 350,
      "success": 340,
      "failed": 10
    },
    "feishu": {
      "total": 250,
      "success": 245,
      "failed": 5
    }
  }
}
```

---

## 🎓 最佳实践

### 1. 用户ID管理
- 建议在用户注册时就收集各平台的用户ID
- 提供用户ID验证功能
- 定期检查用户ID的有效性

### 2. 推送内容优化
- 标题简洁明了,不超过50字
- 内容重点突出,使用Markdown格式
- 提供明确的操作链接
- 避免推送过于频繁

### 3. 错误处理
- 记录详细的错误日志
- 推送失败时发送邮件通知
- 定期检查推送成功率
- 及时处理失败的推送

### 4. 性能优化
- 使用异步推送
- 批量推送时分批处理
- 缓存access_token
- 使用消息队列

---

## 📚 相关文档

- [IM推送集成完整文档](./IM_PUSH_INTEGRATION_COMPLETE.md)
- [企业微信API文档](https://developer.work.weixin.qq.com/document/)
- [钉钉开放平台文档](https://open.dingtalk.com/document/)
- [飞书开放平台文档](https://open.feishu.cn/document/)

---

## 💡 提示

- 首次配置建议先测试一个渠道,确认成功后再配置其他渠道
- 用户ID错误是最常见的问题,请仔细核对
- 推送失败时查看后端日志获取详细错误信息
- 建议为重要用户配置多个推送渠道,提高消息到达率

---

**快速开始指南版本**: 1.0  
**最后更新**: 2026-04-16
