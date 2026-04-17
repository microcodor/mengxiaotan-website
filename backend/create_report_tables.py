"""
创建定制报告相关数据表
"""
import mysql.connector
from mysql.connector import Error

def create_report_tables():
    """创建定制报告相关的数据表"""
    try:
        # 连接数据库
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
            
            # 创建 report_requests 表
            create_requests_table = """
            CREATE TABLE IF NOT EXISTS report_requests (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                company_id INT NOT NULL,
                report_type VARCHAR(50) NOT NULL COMMENT '报告类型',
                title VARCHAR(200) NOT NULL COMMENT '报告标题',
                description TEXT NOT NULL COMMENT '需求描述',
                expected_delivery_date DATE COMMENT '期望交付时间',
                additional_notes TEXT COMMENT '附加说明',
                status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, assigned, in_progress, completed, rejected',
                assigned_to INT COMMENT '分配给谁',
                assigned_at DATETIME COMMENT '分配时间',
                completed_at DATETIME COMMENT '完成时间',
                rejected_reason TEXT COMMENT '拒绝原因',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_company_id (company_id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告申请表';
            """
            
            cursor.execute(create_requests_table)
            print("✓ 创建 report_requests 表成功")
            
            # 创建 report_files 表
            create_files_table = """
            CREATE TABLE IF NOT EXISTS report_files (
                id INT PRIMARY KEY AUTO_INCREMENT,
                request_id INT NOT NULL,
                file_name VARCHAR(255) NOT NULL COMMENT '文件名',
                file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
                file_type VARCHAR(20) NOT NULL COMMENT '文件类型(pdf, docx, etc)',
                file_size INT NOT NULL COMMENT '文件大小(字节)',
                uploaded_by INT NOT NULL COMMENT '上传人',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES report_requests(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_request_id (request_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告文件表';
            """
            
            cursor.execute(create_files_table)
            print("✓ 创建 report_files 表成功")
            
            # 创建 report_quota_usage 表
            create_quota_table = """
            CREATE TABLE IF NOT EXISTS report_quota_usage (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                year INT NOT NULL COMMENT '年份',
                month INT NOT NULL COMMENT '月份',
                used_quota INT DEFAULT 0 COMMENT '已使用配额',
                total_quota INT DEFAULT 2 COMMENT '总配额',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY uk_user_year_month (user_id, year, month),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告配额使用记录表';
            """
            
            cursor.execute(create_quota_table)
            print("✓ 创建 report_quota_usage 表成功")
            
            # 提交更改
            connection.commit()
            print("\n✅ 所有表创建成功！")
            
            # 显示表结构
            print("\n" + "="*60)
            print("report_requests 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE report_requests")
            for row in cursor.fetchall():
                print(f"  {row[0]:<25} {row[1]:<20} {row[2]:<10} {row[3]:<10}")
            
            print("\n" + "="*60)
            print("report_files 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE report_files")
            for row in cursor.fetchall():
                print(f"  {row[0]:<25} {row[1]:<20} {row[2]:<10} {row[3]:<10}")
            
            print("\n" + "="*60)
            print("report_quota_usage 表结构:")
            print("="*60)
            cursor.execute("DESCRIBE report_quota_usage")
            for row in cursor.fetchall():
                print(f"  {row[0]:<25} {row[1]:<20} {row[2]:<10} {row[3]:<10}")
            
    except Error as e:
        print(f"❌ 错误: {e}")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")


if __name__ == '__main__':
    print("开始创建定制报告数据表...")
    print("="*60)
    create_report_tables()
