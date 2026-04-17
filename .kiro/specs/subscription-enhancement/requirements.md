# 需求文档 - 订阅系统完善

## 简介

本文档定义了蒙小碳能源站订阅系统的完善需求，包括支付凭证管理、退款流程、关键词定制推送、AI每日简报生成、数据看板权限控制和多渠道推送扩展等功能。这些功能将提升订阅系统的完整性和用户体验。

## 术语表

- **Subscription_System**: 订阅系统，管理用户订阅套餐、订单和推送服务的系统
- **Payment_Proof_Manager**: 支付凭证管理器，处理支付凭证上传、存储和审核的模块
- **Refund_Processor**: 退款处理器，处理退款申请和审批流程的模块
- **Keyword_Push_Engine**: 关键词推送引擎，根据用户定制关键词推送相关文章的模块
- **AI_Brief_Generator**: AI简报生成器，使用MiniMax API生成每日简报的模块
- **Permission_Controller**: 权限控制器，根据订阅等级控制功能访问权限的模块
- **Multi_Channel_Pusher**: 多渠道推送器，支持企业微信、邮件、短信等多种推送渠道的模块
- **Admin**: 管理员，具有审核订单、处理退款等权限的用户
- **Subscriber**: 订阅用户，购买了订阅套餐的用户
- **Order**: 订单，用户购买订阅套餐产生的订单记录
- **Subscription**: 订阅记录，用户当前的订阅状态和配置

## 需求

### 需求 1: 支付凭证存储和管理

**用户故事:** 作为订阅用户，我想上传支付凭证并由管理员审核，以便完成线下支付的订单确认。

#### 验收标准

1. WHEN 用户创建线下支付订单时，THE Subscription_System SHALL 允许用户上传支付凭证图片
2. THE Payment_Proof_Manager SHALL 支持上传 JPG、PNG、PDF 格式的文件，单个文件大小不超过 5MB
3. WHEN 用户上传支付凭证后，THE Subscription_System SHALL 将文件存储到服务器并记录文件URL到订单的 payment_proof 字段
4. THE Subscription_System SHALL 在订单列表中显示支付凭证的缩略图或下载链接
5. WHEN 管理员审核订单时，THE Payment_Proof_Manager SHALL 提供查看支付凭证的功能
6. THE Admin SHALL 能够下载支付凭证进行核对
7. WHEN 支付凭证上传失败时，THE Subscription_System SHALL 返回明确的错误信息（如文件格式不支持、文件过大等）

### 需求 2: 退款流程

**用户故事:** 作为订阅用户，我想申请退款，以便在不满意服务时取回费用。

#### 验收标准

1. WHEN 订单状态为已支付时，THE Subscription_System SHALL 允许用户申请退款
2. WHEN 用户申请退款时，THE Refund_Processor SHALL 要求用户填写退款原因
3. THE Refund_Processor SHALL 创建退款申请记录，包含订单号、申请时间、退款原因和申请状态
4. WHEN 退款申请创建后，THE Subscription_System SHALL 将订单的 payment_status 更新为 refund_pending
5. THE Admin SHALL 能够查看所有待处理的退款申请列表
6. WHEN 管理员审批退款申请时，THE Refund_Processor SHALL 允许管理员选择批准或拒绝
7. WHEN 管理员批准退款时，THE Refund_Processor SHALL 将订单的 payment_status 更新为 refunded，并将关联的订阅状态更新为 cancelled
8. WHEN 管理员拒绝退款时，THE Refund_Processor SHALL 将订单的 payment_status 恢复为 paid，并记录拒绝原因
9. WHEN 退款申请状态变更时，THE Subscription_System SHALL 通过企业微信或邮件通知用户
10. THE Refund_Processor SHALL 记录退款处理的完整日志，包括处理人、处理时间和处理结果

### 需求 3: 关键词定制推送逻辑

**用户故事:** 作为高级版订阅用户，我想设置关键词，以便接收与我关注领域相关的文章推送。

#### 验收标准

1. WHERE 用户订阅了高级版套餐，THE Subscription_System SHALL 允许用户设置最多 20 个自定义关键词
2. THE Keyword_Push_Engine SHALL 将用户设置的关键词存储到订阅记录的 custom_keywords 字段
3. WHEN 新文章发布时，THE Keyword_Push_Engine SHALL 检查文章标题、摘要和标签是否包含用户的自定义关键词
4. WHEN 文章匹配用户关键词时，THE Keyword_Push_Engine SHALL 将该文章添加到用户的推送队列
5. THE Keyword_Push_Engine SHALL 支持关键词的模糊匹配（如"光伏"可以匹配"光伏发电"、"光伏产业"）
6. THE Keyword_Push_Engine SHALL 每天汇总匹配的文章，在用户设定的推送时间发送
7. WHERE 用户未设置关键词，THE Keyword_Push_Engine SHALL 推送所有分类的热门文章
8. THE Subscription_System SHALL 提供关键词管理界面，允许用户添加、删除和修改关键词
9. WHEN 关键词匹配的文章数量超过 50 篇时，THE Keyword_Push_Engine SHALL 按文章发布时间和热度排序，推送前 50 篇

### 需求 4: AI每日简报生成

**用户故事:** 作为标准版或高级版订阅用户，我想接收AI生成的每日简报，以便快速了解能源行业动态。

#### 验收标准

1. WHERE 用户订阅了标准版或高级版套餐，THE AI_Brief_Generator SHALL 每天生成一份AI简报
2. THE AI_Brief_Generator SHALL 在每天早上 7:00 自动运行
3. THE AI_Brief_Generator SHALL 收集前一天发布的所有文章（按浏览量和点赞数排序，选取前 30 篇）
4. THE AI_Brief_Generator SHALL 调用 MiniMax API，生成不超过 1000 字的简报内容
5. THE AI_Brief_Generator SHALL 在简报中包含以下内容：行业热点总结、重要政策解读、市场趋势分析
6. WHERE 用户订阅了高级版套餐，THE AI_Brief_Generator SHALL 在简报中额外包含决策建议
7. THE AI_Brief_Generator SHALL 将生成的简报存储到 daily_briefs 表
8. WHEN 简报生成完成后，THE Multi_Channel_Pusher SHALL 通过用户选择的推送渠道发送简报
9. WHEN MiniMax API 调用失败时，THE AI_Brief_Generator SHALL 记录错误日志，并在 1 小时后重试，最多重试 3 次
10. THE AI_Brief_Generator SHALL 在管理后台提供简报预览和手动生成功能

### 需求 5: 数据看板权限控制

**用户故事:** 作为订阅用户，我想根据我的订阅等级访问相应的数据看板功能，以便获得与我付费相匹配的服务。

#### 验收标准

1. THE Permission_Controller SHALL 根据用户的订阅套餐等级控制数据看板的访问权限
2. WHERE 用户订阅了免费版，THE Permission_Controller SHALL 仅允许访问基础数据（文章总数、分类统计）
3. WHERE 用户订阅了标准版，THE Permission_Controller SHALL 允许访问完整数据（包括浏览趋势、热门文章、来源分布）
4. WHERE 用户订阅了高级版，THE Permission_Controller SHALL 允许访问完整数据和趋势分析（包括行业趋势预测、关键词热度分析）
5. WHEN 用户尝试访问超出其订阅等级的功能时，THE Permission_Controller SHALL 返回权限不足的提示，并引导用户升级订阅
6. THE Permission_Controller SHALL 在前端界面中根据用户订阅等级动态显示或隐藏相应的数据看板模块
7. WHEN 用户订阅状态变更时，THE Permission_Controller SHALL 实时更新用户的访问权限
8. THE Permission_Controller SHALL 记录用户访问数据看板的日志，包括访问时间、访问模块和订阅等级

### 需求 6: 多渠道推送扩展

**用户故事:** 作为订阅用户，我想选择多种推送渠道，以便通过我偏好的方式接收资讯。

#### 验收标准

1. THE Multi_Channel_Pusher SHALL 支持企业微信、邮件和短信三种推送渠道
2. THE Subscription_System SHALL 允许用户在订阅设置中选择一个或多个推送渠道
3. THE Multi_Channel_Pusher SHALL 将用户选择的推送渠道存储到订阅记录的 push_channels 字段
4. WHERE 用户选择邮件推送，THE Multi_Channel_Pusher SHALL 要求用户提供有效的邮箱地址
5. WHERE 用户选择短信推送，THE Multi_Channel_Pusher SHALL 要求用户提供有效的手机号码
6. WHEN 推送任务触发时，THE Multi_Channel_Pusher SHALL 根据用户选择的渠道并行发送推送消息
7. WHEN 某个推送渠道发送失败时，THE Multi_Channel_Pusher SHALL 记录失败日志，但不影响其他渠道的推送
8. THE Multi_Channel_Pusher SHALL 在推送日志中记录每个渠道的发送状态（成功、失败、待发送）
9. WHERE 用户订阅了免费版，THE Multi_Channel_Pusher SHALL 仅支持企业微信推送
10. WHERE 用户订阅了标准版，THE Multi_Channel_Pusher SHALL 支持企业微信和邮件推送
11. WHERE 用户订阅了高级版，THE Multi_Channel_Pusher SHALL 支持所有三种推送渠道
12. THE Multi_Channel_Pusher SHALL 提供推送频率设置，允许用户选择每天推送的时间（如早上 8:00、中午 12:00、晚上 18:00）
13. WHEN 推送内容超过短信字数限制（70字）时，THE Multi_Channel_Pusher SHALL 发送摘要并附带完整内容的链接

### 需求 7: 支付凭证解析器

**用户故事:** 作为管理员，我想系统能够自动识别支付凭证中的关键信息，以便提高审核效率。

#### 验收标准

1. WHEN 用户上传支付凭证时，THE Payment_Proof_Manager SHALL 尝试使用OCR技术提取凭证中的金额、时间和交易流水号
2. WHEN OCR提取成功时，THE Payment_Proof_Manager SHALL 将提取的信息显示在订单详情页供管理员参考
3. WHEN OCR提取的金额与订单金额不一致时，THE Payment_Proof_Manager SHALL 在管理后台显示警告提示
4. WHEN OCR提取失败时，THE Payment_Proof_Manager SHALL 静默失败，不影响正常的上传流程
5. THE Payment_Proof_Manager SHALL 将OCR提取的信息存储到订单的 payment_info 字段（JSON格式）

### 需求 8: 订阅续费提醒

**用户故事:** 作为订阅用户，我想在订阅即将到期时收到提醒，以便及时续费避免服务中断。

#### 验收标准

1. THE Subscription_System SHALL 每天检查所有即将到期的订阅（到期时间在 7 天内）
2. WHEN 订阅距离到期还有 7 天时，THE Subscription_System SHALL 发送第一次续费提醒
3. WHEN 订阅距离到期还有 3 天时，THE Subscription_System SHALL 发送第二次续费提醒
4. WHEN 订阅距离到期还有 1 天时，THE Subscription_System SHALL 发送第三次续费提醒
5. THE Subscription_System SHALL 通过用户选择的推送渠道发送续费提醒
6. THE Subscription_System SHALL 在续费提醒中包含订阅到期时间、套餐名称和续费链接
7. WHERE 用户开启了自动续费，THE Subscription_System SHALL 不发送续费提醒
8. WHEN 订阅到期后，THE Subscription_System SHALL 将订阅状态更新为 expired

### 需求 9: 订阅数据统计

**用户故事:** 作为管理员，我想查看订阅系统的统计数据，以便了解业务运营情况。

#### 验收标准

1. THE Subscription_System SHALL 在管理后台提供订阅数据统计页面
2. THE Subscription_System SHALL 显示以下统计数据：总订阅数、活跃订阅数、即将到期订阅数、本月新增订阅数
3. THE Subscription_System SHALL 显示各套餐的订阅分布（饼图或柱状图）
4. THE Subscription_System SHALL 显示订阅趋势图（按月统计）
5. THE Subscription_System SHALL 显示订单统计数据：总订单数、待审核订单数、已完成订单数、退款订单数
6. THE Subscription_System SHALL 显示收入统计数据：总收入、本月收入、各套餐收入占比
7. THE Subscription_System SHALL 支持按时间范围筛选统计数据（本周、本月、本季度、本年度、自定义）
8. THE Subscription_System SHALL 支持导出统计数据为 Excel 或 CSV 格式

## 数据模型扩展

### Order 表新增字段
- `payment_info`: JSON 类型，存储OCR提取的支付信息
- `refund_reason`: TEXT 类型，存储退款原因
- `refund_status`: VARCHAR(20)，退款状态（null, pending, approved, rejected）
- `refund_applied_at`: DATETIME，退款申请时间
- `refund_processed_at`: DATETIME，退款处理时间
- `refund_processed_by`: INT，退款处理人ID

### Subscription 表字段说明
- `push_channels`: JSON 类型，存储推送渠道配置，格式如 `{"enterprise_wechat": true, "email": "user@example.com", "sms": "13800138000"}`
- `custom_keywords`: JSON 类型，存储用户自定义关键词，格式如 `["光伏", "风电", "储能"]`
- `push_time`: VARCHAR(20)，推送时间设置，格式如 `"08:00,12:00,18:00"`

### 新增 RefundApplication 表
- `id`: INT，主键
- `order_id`: INT，关联订单ID
- `user_id`: INT，申请用户ID
- `reason`: TEXT，退款原因
- `status`: VARCHAR(20)，状态（pending, approved, rejected）
- `applied_at`: DATETIME，申请时间
- `processed_by`: INT，处理人ID
- `processed_at`: DATETIME，处理时间
- `reject_reason`: TEXT，拒绝原因
- `created_at`: DATETIME，创建时间

## 技术约束

1. 文件上传使用 Flask 的 `werkzeug.utils.secure_filename` 确保文件名安全
2. 支付凭证存储在服务器的 `uploads/payment_proofs/` 目录
3. MiniMax API 调用需要配置 `MINIMAX_API_KEY` 和 `MINIMAX_GROUP_ID`
4. 邮件推送使用 SMTP 协议，需要配置 `SMTP_SERVER`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASSWORD`
5. 短信推送需要集成第三方短信服务商API（如阿里云短信、腾讯云短信）
6. OCR功能可选使用百度OCR API或腾讯云OCR API
7. 定时任务使用 APScheduler 调度
8. 推送日志记录到 `broadcast_logs` 表

## 非功能性需求

1. **性能**: AI简报生成应在 30 秒内完成
2. **可靠性**: 推送失败时应有重试机制，最多重试 3 次
3. **安全性**: 支付凭证文件应进行病毒扫描，防止恶意文件上传
4. **可用性**: 系统应提供友好的错误提示，引导用户正确操作
5. **可维护性**: 所有关键操作应记录日志，便于问题排查
