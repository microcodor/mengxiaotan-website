# IM推送集成 - 使用指南

## 🎉 欢迎使用IM推送集成服务!

本项目已成功集成企业微信、钉钉、飞书三大IM平台的推送服务。

---

## 📚 文档导航

### 快速开始
👉 **[快速开始指南](./PUSH_QUICK_START.md)** - 5分钟快速配置和使用

### 完整文档
📖 **[完整实现文档](./IM_PUSH_INTEGRATION_COMPLETE.md)** - 详细的功能说明和API文档

### 项目总结
📊 **[项目总结](./IM_PUSH_INTEGRATION_SUMMARY.md)** - 项目概览和交付清单

### 测试报告
✅ **[测试报告](./IM_PUSH_TEST_REPORT.md)** - 详细的测试结果和验证

### 完成状态
🎯 **[最终状态](./IM_PUSH_FINAL_STATUS.md)** - 项目完成状态和下一步操作

---

## 🚀 快速开始 (3步)

### 第1步: 配置IM平台凭证

编辑 `backend/.env` 文件,添加你的IM平台配置:

```bash
# 企业微信
ENTERPRISE_WECHAT_CORP_ID=ww1234567890abcdef
ENTERPRISE_WECHAT_AGENT_ID=1000002
ENTERPRISE_WECHAT_SECRET=your-secret-here

# 钉钉
DINGTALK_APP_KEY=dingxxxxxxxx
DINGTALK_APP_SECRET=your-secret-here
DINGTALK_AGENT_ID=123456789

# 飞书
FEISHU_APP_ID=cli_xxxxxxxx
FEISHU_APP_SECRET=your-secret-here
```

**如何获取配置?** 查看 [快速开始指南](./PUSH_QUICK_START.md#获取用户id指南)

### 第2步: 启动服务

```bash
# 启动后端 (如果还没启动)
cd backend
./venv/bin/python app.py

# 启动前端 (新终端)
cd frontend
npm run dev
```

### 第3步: 访问测试

- **用户端**: http://localhost:5173/dashboard/push
- **管理端**: http://localhost:5173/admin/push

---

## 📱 功能概览

### 用户端功能
- ✅ 查看可用推送渠道(根据订阅等级)
- ✅ 配置推送渠道(企业微信、钉钉、飞书、邮件、短信)
- ✅ 测试推送功能
- ✅ 实时保存配置

### 管理端功能
- ✅ 搜索用户
- ✅ 查看用户订阅等级和可用渠道
- ✅ 为用户配置推送渠道
- ✅ 测试推送功能

### 权限控制
- **免费订阅**: 企业微信、钉钉、飞书
- **基础版**: 企业微信、钉钉、飞书、邮件
- **高级版**: 全部渠道

---

## 🎯 使用场景

### 场景1: 新文章推送
当有新文章发布时,系统自动推送到用户配置的所有渠道。

### 场景2: 订阅到期提醒
订阅即将到期时,自动发送提醒消息。

### 场景3: 定制报告通知
定制报告生成完成后,通知用户查看。

### 场景4: 系统通知
重要系统通知通过多渠道推送,确保用户及时收到。

---

## 🔧 配置说明

### 订阅等级与渠道权限

| 订阅等级 | 可用渠道 |
|---------|---------|
| 免费 | 企业微信、钉钉、飞书 |
| 基础版 | 企业微信、钉钉、飞书、邮件 |
| 高级版 | 企业微信、钉钉、飞书、邮件、短信 |

### 用户ID说明

- **企业微信**: 成员UserID (如: zhangsan)
- **钉钉**: 员工工号或UserID (如: manager123)
- **飞书**: 用户OpenID (如: ou_xxx)

详细获取方法请查看 [快速开始指南](./PUSH_QUICK_START.md#获取用户id指南)

---

## 📖 API文档

### 用户端API

#### 获取推送配置
```http
GET /api/push-settings/user/channels
Authorization: Bearer <token>
```

#### 更新推送配置
```http
POST /api/push-settings/user/channels
Authorization: Bearer <token>
Content-Type: application/json

{
  "channels": {
    "enterprise_wechat": {
      "enabled": true,
      "user_id": "zhangsan"
    }
  }
}
```

#### 测试推送
```http
POST /api/push-settings/user/test
Authorization: Bearer <token>
Content-Type: application/json

{
  "channels": ["enterprise_wechat"]
}
```

### 管理员API

详细API文档请查看 [完整实现文档](./IM_PUSH_INTEGRATION_COMPLETE.md#api接口详情)

---

## ❓ 常见问题

### Q1: 推送失败,提示"invalid user_id"
**A**: 检查用户ID是否正确,确保是对应平台的真实用户ID。

### Q2: 推送失败,提示"access_token invalid"
**A**: 检查环境变量中的配置是否正确,特别是AppID和Secret。

### Q3: 看不到某些推送渠道
**A**: 检查用户的订阅等级,不同等级可用的渠道不同。

### Q4: 如何查看推送日志?
**A**: 查看后端日志文件或控制台输出,搜索"推送"关键字。

### Q5: 可以同时推送到多个渠道吗?
**A**: 可以,启用多个渠道后,系统会自动向所有启用的渠道推送。

更多问题请查看 [快速开始指南](./PUSH_QUICK_START.md#常见问题)

---

## 🎓 技术支持

### 文档资源
1. [快速开始指南](./PUSH_QUICK_START.md) - 快速上手
2. [完整实现文档](./IM_PUSH_INTEGRATION_COMPLETE.md) - 详细说明
3. [测试报告](./IM_PUSH_TEST_REPORT.md) - 测试结果
4. [项目总结](./IM_PUSH_INTEGRATION_SUMMARY.md) - 项目概览

### 平台文档
- [企业微信API文档](https://developer.work.weixin.qq.com/document/)
- [钉钉开放平台文档](https://open.dingtalk.com/document/)
- [飞书开放平台文档](https://open.feishu.cn/document/)

---

## ✅ 项目状态

- **完成度**: 100%
- **测试状态**: ✅ 全部通过
- **可用性**: ✅ 可立即使用
- **文档完整性**: ✅ 100%

---

## 🎊 开始使用

1. 📖 阅读 [快速开始指南](./PUSH_QUICK_START.md)
2. 🔧 配置IM平台凭证
3. 🚀 启动服务
4. 🎯 开始使用推送功能

**祝您使用愉快!** 🎉

---

**文档版本**: 1.0  
**最后更新**: 2026-04-16  
**维护者**: AI Assistant
