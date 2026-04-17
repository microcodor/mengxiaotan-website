-- 创建权限访问日志表
-- Validates: Requirements 5.8

CREATE TABLE IF NOT EXISTS permission_access_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    feature VARCHAR(100) NOT NULL,
    subscription_level VARCHAR(20) NOT NULL,
    allowed BOOLEAN NOT NULL,
    ip_address VARCHAR(50),
    accessed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_feature (feature),
    INDEX idx_accessed_at (accessed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限访问日志表';
