-- 添加IM应用配置字段到users表
-- 执行时间: 2026-04-16

ALTER TABLE users ADD COLUMN im_app_config JSON COMMENT 'IM应用配置(企业微信、钉钉、飞书)';

-- 示例数据格式:
-- {
--   "enterprise_wechat": {
--     "enabled": true,
--     "corp_id": "ww1234567890abcdef",
--     "agent_id": "1000002",
--     "secret": "encrypted_secret_here"
--   },
--   "dingtalk": {
--     "enabled": true,
--     "app_key": "dingxxxxxxxx",
--     "app_secret": "encrypted_secret_here",
--     "agent_id": "123456789"
--   },
--   "feishu": {
--     "enabled": true,
--     "app_id": "cli_xxxxxxxx",
--     "app_secret": "encrypted_secret_here"
--   }
-- }
