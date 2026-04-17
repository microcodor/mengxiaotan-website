-- 为 daily_briefs 表添加分享和版本相关字段

-- 添加唯一分享token字段
ALTER TABLE daily_briefs ADD COLUMN share_token VARCHAR(32) UNIQUE;
CREATE INDEX idx_daily_briefs_share_token ON daily_briefs(share_token);

-- 添加标准版内容字段
ALTER TABLE daily_briefs ADD COLUMN standard_content JSON;

-- 添加高级版内容字段
ALTER TABLE daily_briefs ADD COLUMN premium_content JSON;

-- 添加浏览次数字段
ALTER TABLE daily_briefs ADD COLUMN view_count INT DEFAULT 0;

-- 添加分享次数字段
ALTER TABLE daily_briefs ADD COLUMN share_count INT DEFAULT 0;

-- 为已存在的简报生成share_token
UPDATE daily_briefs 
SET share_token = MD5(CONCAT(brief_date, UUID()))
WHERE share_token IS NULL;

-- 为已存在的简报复制内容到standard_content和premium_content
UPDATE daily_briefs 
SET standard_content = content,
    premium_content = content
WHERE standard_content IS NULL;

-- 设置share_token为NOT NULL
ALTER TABLE daily_briefs MODIFY COLUMN share_token VARCHAR(32) NOT NULL;
