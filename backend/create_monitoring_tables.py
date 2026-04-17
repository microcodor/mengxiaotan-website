"""
创建动态监测预警相关数据表
"""
import mysql.connector
from mysql.connector import Error

def create_monitoring_tables():
    """创建监测预警相关的数据表"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='jinchun123',
            database='energy_station'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("成功连接到MySQL数据库")
            
            # 创建 monitoring_rules 表
            create_rules_table = """
            CREATE TABLE IF NOT EXISTS monitoring_rules (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                company_id INT NOT NULL,
                name VARCHAR(100) NOT NULL COMMENT '规则名称',
                type VARCHAR(20) NOT NULL COMMENT '监测类型: policy, price, industry',
                keywords JSON NOT NULL COMMENT '关键词列表',
                threshold DECIMAL(10,2) COMMENT '预警阈值',
                level VARCHAR(20) DEFAULT 'medium' COMMENT '预警等级: high, medium, low',
                channels JSON NOT NULL COMMENT '推送渠道',
                enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_company_id (company_id),
                INDEX idx_enabled (enabled)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监测规则表';
            """
            
            cursor.execute(create_rules_table)
            print("✓ 创建 monitoring_rules 表成功")
            
            # 创建 monitoring_alerts 表
            create_alerts_table = """
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id INT PRIMARY KEY AUTO_INCREMENT,
                rule_id INT NOT NULL,
                user_id INT NOT NULL,
                company_id INT NOT NULL,
                title VARCHAR(200) NOT NULL COMMENT '预警标题',
                content TEXT NOT NULL COMMENT '预警内容',
                level VARCHAR(20) NOT NULL COMMENT '预警等级',
                source_type VARCHAR(50) COMMENT '来源类型',
                source_id INT COMMENT '来源ID',
                status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, sent, read',
                sent_at DATETIME COMMENT '发送时间',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rule_id) REFERENCES monitoring_rules(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_status (status),
                INDEX idx_level (level),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预警记录表';
            """
            
            cursor.execute(create_alerts_table)
            print("✓ 创建 monitoring_alerts 表成功")
            
            connection.commit()
            print("\n✅ 所有表创建成功！")
            
            # 显示表结构
            print("\n" + "="*60)
            print("monitoring_rules 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE monitoring_rules")
            for row in cursor.fetchall():
                print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<10}")
            
            print("\n" + "="*60)
            print("monitoring_alerts 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE monitoring_alerts")
            for row in cursor.fetchall():
                print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<10}")
            
    except Error as e:
        print(f"❌ 错误: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")


if __name__ == '__main__':
    print("开始创建动态监测预警数据表...")
    print("="*60)
    create_monitoring_tables()
