-- 订阅系统完善 - 数据库迁移脚本
-- 功能: 扩展订单表字段，创建退款申请表
-- 日期: 2024

-- ============================================
-- 1. 扩展 orders 表 - 添加支付信息和退款相关字段
-- ============================================

-- 添加 payment_info 字段 (OCR提取的支付信息)
ALTER TABLE orders 
ADD COLUMN payment_info JSON COMMENT 'OCR提取的支付信息';

-- 添加退款相关字段
ALTER TABLE orders 
ADD COLUMN refund_reason TEXT COMMENT '退款原因',
ADD COLUMN refund_status VARCHAR(20) COMMENT '退款状态: null, pending, approved, rejected',
ADD COLUMN refund_applied_at DATETIME COMMENT '退款申请时间',
ADD COLUMN refund_processed_at DATETIME COMMENT '退款处理时间',
ADD COLUMN refund_processed_by INT COMMENT '退款处理人ID';

-- 添加索引以提高查询性能
ALTER TABLE orders 
ADD INDEX idx_refund_status (refund_status),
ADD INDEX idx_refund_applied_at (refund_applied_at);

-- 添加外键约束
ALTER TABLE orders 
ADD CONSTRAINT fk_orders_refund_processor 
FOREIGN KEY (refund_processed_by) REFERENCES users(id);

-- 更新 payment_status 字段注释，添加 refund_pending 状态
ALTER TABLE orders 
MODIFY COLUMN payment_status VARCHAR(20) DEFAULT 'pending' 
COMMENT '支付状态: pending, paid, cancelled, refunded, refund_pending';

-- ============================================
-- 2. 创建 refund_applications 表
-- ============================================

CREATE TABLE IF NOT EXISTS refund_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL COMMENT '订单ID',
    user_id INT NOT NULL COMMENT '申请用户ID',
    reason TEXT NOT NULL COMMENT '退款原因',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态: pending, approved, rejected',
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
    processed_by INT COMMENT '处理人ID',
    processed_at DATETIME COMMENT '处理时间',
    reject_reason TEXT COMMENT '拒绝原因',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (processed_by) REFERENCES users(id),
    
    -- 索引
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_applied_at (applied_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='退款申请表';

-- ============================================
-- 3. 验证迁移结果
-- ============================================

-- 显示 orders 表结构
SELECT 'Orders table structure:' AS message;
DESCRIBE orders;

-- 显示 refund_applications 表结构
SELECT 'RefundApplications table structure:' AS message;
DESCRIBE refund_applications;

-- 显示成功消息
SELECT 'Migration completed successfully!' AS message;
