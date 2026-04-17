# Implementation Plan: 订阅系统完善 (Subscription Enhancement)

## Overview

本实现计划将订阅系统完善功能分解为可执行的编码任务。实现基于Flask + SQLAlchemy + MySQL后端架构，包括支付凭证管理、退款流程、关键词推送、AI简报生成、权限控制和多渠道推送等核心功能。

## Tasks

- [x] 1. 数据库模型扩展和迁移
  - 扩展 Order 表，添加 payment_info, refund_reason, refund_status, refund_applied_at, refund_processed_at, refund_processed_by 字段
  - 创建 RefundApplication 表，包含所有必需字段和索引
  - 创建数据库迁移脚本
  - _Requirements: 需求2.3, 需求2.4, 需求2.7, 需求2.10_

- [x] 2. 支付凭证管理器实现
  - [x] 2.1 实现文件上传和验证功能
    - 创建 PaymentProofManager 类
    - 实现 upload_proof() 方法，支持 JPG, PNG, PDF 格式
    - 实现 validate_file() 方法，验证文件格式和大小（最大5MB）
    - 实现文件名 sanitization 和安全存储
    - 存储路径: uploads/payment_proofs/{year}/{month}/{order_id}_{timestamp}.{ext}
    - _Requirements: 需求1.1, 需求1.2, 需求1.3, 需求1.7_
  
  - [x] 2.2 编写支付凭证上传的单元测试
    - 测试支持的文件格式 (JPG, PNG, PDF)
    - 测试不支持的文件格式
    - 测试文件大小边界 (4.9MB, 5MB, 5.1MB)
    - 测试文件名 sanitization
    - _Requirements: 需求1.2, 需求1.7_
  
  - [x] 2.3 实现 OCR 支付信息提取功能
    - 实现 extract_payment_info() 方法
    - 集成百度OCR API或腾讯云OCR API
    - 提取金额、交易流水号、时间戳
    - 实现静默失败机制（OCR失败不影响上传）
    - 将OCR结果存储到 Order.payment_info JSON字段
    - _Requirements: 需求7.1, 需求7.2, 需求7.4, 需求7.5_
  
  - [x] 2.4 编写 OCR 功能的单元测试
    - 测试 OCR 成功场景
    - 测试 OCR 失败场景（静默失败）
    - 测试金额不一致警告
    - 测试低置信度处理
    - _Requirements: 需求7.3, 需求7.4_
  
  - [x] 2.5 实现支付凭证查看和下载功能
    - 实现 get_proof_url() 方法
    - 创建文件访问路由
    - 实现权限验证（仅订单所有者和管理员可访问）
    - _Requirements: 需求1.4, 需求1.5, 需求1.6_

- [x] 3. 退款处理器实现
  - [x] 3.1 实现退款申请创建功能
    - 创建 RefundProcessor 类
    - 实现 create_refund_application() 方法
    - 验证订单状态为 paid
    - 检查是否已有待处理的退款申请
    - 创建 RefundApplication 记录
    - 更新订单状态为 refund_pending
    - _Requirements: 需求2.1, 需求2.2, 需求2.3, 需求2.4_
  
  - [x] 3.2 实现退款审批功能
    - 实现 approve_refund() 方法
    - 实现 reject_refund() 方法
    - 验证管理员权限
    - 更新订单和订阅状态
    - 记录处理人和处理时间
    - _Requirements: 需求2.6, 需求2.7, 需求2.8, 需求2.10_
  
  - [x] 3.3 编写退款状态机的属性测试
    - **Property 1: 退款状态机转换正确性**
    - **Validates: Requirements 2.4, 2.7, 2.8**
    - 测试订单状态从 paid → refund_pending → refunded 的转换
    - 测试订单状态从 paid → refund_pending → paid 的转换（拒绝）
    - 测试订阅状态在退款批准后转换为 cancelled
    - 使用 hypothesis 生成随机订单和用户数据
  
  - [x] 3.4 实现退款通知功能
    - 实现 notify_user() 方法
    - 集成 MultiChannelPusher 发送通知
    - 通知内容包含申请状态、处理结果、拒绝原因（如有）
    - _Requirements: 需求2.9_
  
  - [x] 3.5 实现待处理退款申请查询
    - 实现 get_pending_applications() 方法
    - 支持分页和排序
    - 返回申请详情和关联订单信息
    - _Requirements: 需求2.5_

- [ ] 4. Checkpoint - 确保支付和退款功能测试通过
  - 确保所有测试通过，如有问题请询问用户

- [ ] 5. 关键词推送引擎实现
  - [x] 5.1 实现关键词匹配算法
    - 创建 KeywordPushEngine 类
    - 实现 calculate_relevance_score() 方法
    - 实现精确匹配和模糊匹配（使用 jieba 分词）
    - 实现权重计算：标题(3.0)、摘要(2.0)、标签(1.5)、内容(1.0)
    - 实现相关度分数归一化（0.0-1.0）
    - _Requirements: 需求3.3, 需求3.5_
  
  - [x] 5.2 编写关键词匹配的属性测试
    - **Property 2: 关键词匹配正确性**
    - **Validates: Requirements 3.3, 3.5**
    - 测试关键词在标题、摘要、标签中的匹配
    - 测试相关度分数范围（0.0-1.0）
    - 测试权重计算正确性
    - 使用 hypothesis 生成随机关键词和文章
  
  - [x] 5.3 实现文章匹配和排序功能
    - 实现 match_articles() 方法
    - 按相关度分数降序排序
    - 相同分数按发布时间降序排序
    - 限制返回前50篇文章
    - _Requirements: 需求3.4, 需求3.9_
  
  - [x] 5.4 编写文章排序和截断的属性测试
    - **Property 3: 文章排序和截断正确性**
    - **Validates: Requirements 3.9**
    - 测试排序逻辑（相关度 + 时间）
    - 测试截断逻辑（最多50篇）
    - 使用 hypothesis 生成随机文章列表
  
  - [x] 5.5 实现关键词推送功能
    - 实现 push_matched_articles() 方法
    - 每日汇总匹配文章
    - 在用户设定时间推送
    - 未设置关键词时推送热门文章
    - _Requirements: 需求3.6, 需求3.7_
  
  - [x] 5.6 实现关键词管理接口
    - 创建关键词查询、更新 API 端点
    - 验证关键词数量限制（最多20个）
    - 验证用户订阅等级（仅高级版）
    - 存储到 Subscription.custom_keywords JSON字段
    - _Requirements: 需求3.1, 需求3.2, 需求3.8_

- [ ] 6. AI简报生成器实现
  - [x] 6.1 实现文章收集功能
    - 创建 AIBriefGenerator 类
    - 实现 collect_articles() 方法
    - 查询前一天发布的文章
    - 按浏览量和点赞数排序，选取前30篇
    - _Requirements: 需求4.3_
  
  - [x] 6.2 实现 MiniMax API 调用
    - 实现 call_minimax_api() 方法
    - 配置 API key 和 group ID
    - 构造 Prompt（包含文章标题、摘要、分类）
    - 处理 API 响应
    - 实现重试机制（1小时后重试，最多3次）
    - _Requirements: 需求4.4, 需求4.9_
  
  - [x] 6.3 实现简报内容格式化
    - 实现 format_brief_content() 方法
    - 格式化为 JSON 结构（按分类组织）
    - 包含行业热点、政策解读、市场趋势
    - 高级版用户包含决策建议
    - 限制总字数1000字以内
    - _Requirements: 需求4.5, 需求4.6_
  
  - [x] 6.4 实现简报生成和存储
    - 实现 generate_daily_brief() 方法
    - 存储到 DailyBrief 表
    - 记录生成时间和AI建议
    - _Requirements: 需求4.7_
  
  - [x] 6.5 实现简报推送功能
    - 集成 MultiChannelPusher
    - 推送给标准版和高级版用户
    - 根据用户订阅等级推送不同内容
    - _Requirements: 需求4.1, 需求4.8_
  
  - [x] 6.6 编写 MiniMax API 集成测试
    - 测试 API 调用成功
    - 测试 API 调用失败和重试
    - 测试生成内容格式化
    - 使用 mock 避免实际 API 调用
    - _Requirements: 需求4.9_
  
  - [x] 6.7 实现定时任务调度
    - 使用 APScheduler 配置每日7:00执行
    - 实现任务失败恢复机制
    - 记录任务执行日志
    - _Requirements: 需求4.2_
  
  - [x] 6.8 实现管理后台简报功能
    - 创建简报预览 API 端点
    - 创建手动生成简报 API 端点
    - 实现简报列表查询
    - _Requirements: 需求4.10_

- [ ] 7. Checkpoint - 确保关键词推送和AI简报功能测试通过
  - 确保所有测试通过，如有问题请询问用户

- [x] 8. 权限控制中间件实现
  - [x] 8.1 实现权限检查核心逻辑
    - 创建 PermissionController 类
    - 实现 get_user_subscription_level() 方法
    - 实现 get_available_features() 方法
    - 定义权限矩阵（免费版、标准版、高级版）
    - _Requirements: 需求5.1_
  
  - [x] 8.2 实现权限检查方法
    - 实现 check_permission() 方法
    - 验证用户订阅等级和功能要求
    - 检查订阅是否过期
    - _Requirements: 需求5.2, 需求5.3, 需求5.4, 需求5.7_
  
  - [x] 8.3 编写权限控制的属性测试
    - **Property 4: 权限控制正确性**
    - **Validates: Requirements 5.1, 5.5, 5.7**
    - 测试不同订阅等级的权限范围
    - 测试订阅升级和降级时的权限变化
    - 测试权限不足时的错误响应
    - 使用 hypothesis 生成随机订阅等级和功能
  
  - [x] 8.4 实现 Flask 装饰器
    - 实现 @require_subscription 装饰器
    - 集成 JWT 认证
    - 返回权限不足错误（403）
    - 包含当前等级和所需等级信息
    - _Requirements: 需求5.5_
  
  - [x] 8.5 实现前端权限控制
    - 创建权限查询 API 端点
    - 返回用户可用功能列表
    - 支持功能权限检查
    - _Requirements: 需求5.6_
  
  - [x] 8.6 实现权限访问日志
    - 记录用户访问数据看板的日志
    - 包含访问时间、模块、订阅等级
    - _Requirements: 需求5.8_

- [ ] 9. 多渠道推送器实现
  - [x] 9.1 实现推送器核心框架
    - 创建 MultiChannelPusher 类
    - 实现 get_user_channels() 方法
    - 实现渠道配置验证
    - _Requirements: 需求6.2, 需求6.3_
  
  - [x] 9.2 实现邮件推送服务
    - 创建 EmailPushService 类
    - 实现 SMTP 邮件发送
    - 支持 HTML 和纯文本格式
    - 实现重试机制（3次，间隔5分钟）
    - _Requirements: 需求6.4, 需求6.10_
  
  - [x] 9.3 实现短信推送服务
    - 创建 SMSPushService 类
    - 集成阿里云或腾讯云短信API
    - 实现内容截断（70字限制）
    - 超长内容附带链接
    - 实现重试机制（1次）
    - _Requirements: 需求6.5, 需求6.11, 需求6.13_
  
  - [x] 9.4 编写短信内容截断的属性测试
    - **Property 6: 短信内容截断正确性**
    - **Validates: Requirements 6.13**
    - 测试内容长度 ≤70字时发送完整内容
    - 测试内容长度 >70字时截断并附带链接
    - 使用 hypothesis 生成随机长度的内容
  
  - [ ] 9.5 实现多渠道并行推送
    - 实现 push() 方法
    - 并行发送到多个渠道
    - 实现渠道失败隔离
    - 记录每个渠道的推送状态
    - _Requirements: 需求6.6, 需求6.7, 需求6.8_
  
  - [ ] 9.6 编写推送渠道错误隔离的属性测试
    - **Property 5: 推送渠道错误隔离**
    - **Validates: Requirements 6.7**
    - 测试某个渠道失败时其他渠道继续执行
    - 测试失败渠道被记录到日志
    - 测试推送任务的整体状态反映部分成功
    - 使用 hypothesis 生成随机渠道失败场景
  
  - [ ] 9.7 实现批量推送功能
    - 实现 push_batch() 方法
    - 支持批量用户推送
    - 记录每个用户的推送状态
    - 生成推送报告
    - _Requirements: 需求6.6_
  
  - [ ] 9.8 实现推送设置管理接口
    - 创建推送设置查询、更新 API 端点
    - 验证邮箱和手机号格式
    - 验证订阅等级和渠道限制
    - 存储到 Subscription.push_channels JSON字段
    - _Requirements: 需求6.9, 需求6.10, 需求6.11_
  
  - [ ] 9.9 实现推送频率设置
    - 支持用户选择推送时间
    - 存储到 Subscription.push_time 字段
    - 在定时任务中使用用户设定时间
    - _Requirements: 需求6.12_
  
  - [ ] 9.10 编写推送服务集成测试
    - 测试企业微信推送
    - 测试邮件推送
    - 测试短信推送
    - 测试多渠道并行推送
    - 使用 mock 避免实际推送
    - _Requirements: 需求6.1, 需求6.6_

- [ ] 10. Checkpoint - 确保权限控制和多渠道推送功能测试通过
  - 确保所有测试通过，如有问题请询问用户

- [ ] 11. 订阅续费提醒实现
  - [ ] 11.1 实现续费提醒检查逻辑
    - 创建续费提醒定时任务
    - 查询即将到期的订阅（7天内）
    - 检查自动续费标志
    - 计算提醒时机（7天、3天、1天）
    - _Requirements: 需求8.1, 需求8.2, 需求8.3, 需求8.4, 需求8.7_
  
  - [ ] 11.2 编写续费提醒时机的属性测试
    - **Property 8: 续费提醒时机正确性**
    - **Validates: Requirements 8.2, 8.3, 8.4**
    - 测试距离到期7天、3天、1天时发送提醒
    - 测试其他天数不发送提醒
    - 测试时区处理（Asia/Shanghai）
    - 使用 hypothesis 生成随机订阅和日期
  
  - [ ] 11.3 编写自动续费不发送提醒的属性测试
    - **Property 9: 自动续费不发送提醒**
    - **Validates: Requirements 8.7**
    - 测试开启自动续费时不发送提醒
    - 测试自动续费标志正确存储
    - 使用 hypothesis 生成随机订阅数据
  
  - [ ] 11.4 实现续费提醒内容生成
    - 生成提醒消息
    - 包含到期时间、套餐名称、续费链接
    - 集成 MultiChannelPusher 发送
    - _Requirements: 需求8.5, 需求8.6_
  
  - [ ] 11.5 实现订阅到期状态更新
    - 创建每日检查任务
    - 更新过期订阅状态为 expired
    - _Requirements: 需求8.8_
  
  - [ ] 11.6 编写订阅到期状态更新的属性测试
    - **Property 10: 订阅到期状态更新**
    - **Validates: Requirements 8.8**
    - 测试 end_date < 当前时间时状态更新为 expired
    - 测试已过期的订阅不再次更新
    - 使用 hypothesis 生成随机订阅数据

- [ ] 12. 订阅数据统计实现
  - [ ] 12.1 实现统计数据计算
    - 实现订阅统计：总数、活跃数、即将到期数、本月新增数
    - 实现订单统计：总数、待审核数、已完成数、退款数
    - 实现收入统计：总收入、本月收入、各套餐收入占比
    - _Requirements: 需求9.2, 需求9.5, 需求9.6_
  
  - [ ] 12.2 编写统计计算的属性测试
    - **Property 11: 统计计算正确性**
    - **Validates: Requirements 9.2, 9.5, 9.6**
    - 测试所有统计指标的计算正确性
    - 使用 hypothesis 生成随机订阅和订单数据
  
  - [ ] 12.3 实现时间范围过滤
    - 支持按时间范围筛选（本周、本月、本季度、本年度、自定义）
    - 实现日期范围验证
    - _Requirements: 需求9.7_
  
  - [ ] 12.4 编写时间范围过滤的属性测试
    - **Property 12: 时间范围过滤正确性**
    - **Validates: Requirements 9.7**
    - 测试闭区间过滤
    - 测试边界值处理
    - 测试 start_date > end_date 的错误处理
    - 使用 hypothesis 生成随机时间范围
  
  - [ ] 12.5 实现统计数据可视化接口
    - 创建统计数据查询 API 端点
    - 返回各套餐订阅分布数据（饼图/柱状图）
    - 返回订阅趋势数据（按月统计）
    - _Requirements: 需求9.1, 需求9.3, 需求9.4_
  
  - [ ] 12.6 实现统计数据导出
    - 支持导出为 Excel 格式
    - 支持导出为 CSV 格式
    - 包含所有统计指标
    - _Requirements: 需求9.8_

- [ ] 13. API 端点集成和路由配置
  - [ ] 13.1 创建支付凭证相关 API 端点
    - POST /api/orders/{order_id}/payment-proof
    - GET /api/orders/{order_id}/payment-proof
    - DELETE /api/orders/{order_id}/payment-proof
    - 应用权限验证和错误处理
  
  - [ ] 13.2 创建退款相关 API 端点
    - POST /api/refunds
    - GET /api/refunds
    - GET /api/refunds/{id}
    - PUT /api/refunds/{id}/approve
    - PUT /api/refunds/{id}/reject
    - 应用管理员权限验证
  
  - [ ] 13.3 创建关键词推送相关 API 端点
    - GET /api/subscriptions/keywords
    - PUT /api/subscriptions/keywords
    - POST /api/subscriptions/test-keywords
    - 应用订阅等级验证
  
  - [ ] 13.4 创建 AI 简报相关 API 端点
    - GET /api/briefs
    - GET /api/briefs/{date}
    - POST /api/admin/briefs/generate
    - 应用权限验证
  
  - [ ] 13.5 创建推送设置相关 API 端点
    - GET /api/subscriptions/push-settings
    - PUT /api/subscriptions/push-settings
    - POST /api/subscriptions/test-push
    - 应用订阅等级验证
  
  - [ ] 13.6 创建权限相关 API 端点
    - GET /api/permissions/features
    - GET /api/permissions/check/{feature}
  
  - [ ] 13.7 创建统计数据相关 API 端点
    - GET /api/admin/statistics/subscriptions
    - GET /api/admin/statistics/orders
    - GET /api/admin/statistics/revenue
    - GET /api/admin/statistics/export
    - 应用管理员权限验证

- [ ] 14. 错误处理和日志记录
  - [ ] 14.1 实现统一错误处理
    - 创建自定义异常类
    - 实现 Flask 错误处理器
    - 返回标准化错误响应
  
  - [ ] 14.2 实现日志记录
    - 配置日志级别和格式
    - 记录关键操作日志（退款、推送、简报生成）
    - 记录错误堆栈和上下文信息
  
  - [ ] 14.3 实现告警通知
    - MiniMax API 连续失败3次后发送告警
    - 定时任务执行失败后发送告警
    - 短信余额不足时发送告警

- [ ] 15. 配置管理和环境变量
  - [ ] 15.1 配置外部服务参数
    - MINIMAX_API_KEY, MINIMAX_GROUP_ID
    - SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
    - SMS_PROVIDER, SMS_API_KEY, SMS_API_SECRET
    - OCR_PROVIDER, OCR_API_KEY, OCR_API_SECRET
  
  - [ ] 15.2 配置文件上传参数
    - UPLOAD_FOLDER, MAX_FILE_SIZE
    - ALLOWED_EXTENSIONS
  
  - [ ] 15.3 配置定时任务参数
    - BRIEF_GENERATION_TIME (默认 07:00)
    - RENEWAL_REMINDER_TIME (默认 09:00)

- [ ] 16. Final Checkpoint - 运行完整测试套件
  - 运行所有单元测试
  - 运行所有属性测试
  - 运行所有集成测试
  - 确保代码覆盖率 > 80%
  - 确保所有测试通过，如有问题请询问用户

## Notes

- 任务标记 `*` 的为可选测试任务，可跳过以加快 MVP 开发
- 每个任务引用具体需求以确保可追溯性
- Checkpoint 任务确保增量验证
- 属性测试验证核心业务逻辑的通用正确性
- 单元测试验证具体示例和边界条件
- 集成测试验证外部服务集成和端到端流程
