"""
定制报告服务
Custom Report Service
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import calendar


class ReportService:
    """定制报告服务"""
    
    def __init__(self, db):
        self.db = db
    
    # ==================== 配额管理 ====================
    
    def get_quota_usage(self, user_id: int, year: int = None, month: int = None) -> Dict[str, Any]:
        """
        获取用户配额使用情况
        
        Args:
            user_id: 用户ID
            year: 年份（默认当前年）
            month: 月份（默认当前月）
            
        Returns:
            配额使用情况
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # 查询配额记录
        quota = self.db.session.execute(
            '''SELECT * FROM report_quota_usage 
               WHERE user_id = :user_id AND year = :year AND month = :month''',
            {'user_id': user_id, 'year': year, 'month': month}
        ).fetchone()
        
        if quota:
            return {
                'user_id': quota[1],
                'year': quota[2],
                'month': quota[3],
                'used_quota': quota[4],
                'total_quota': quota[5],
                'remaining_quota': quota[5] - quota[4]
            }
        else:
            # 如果没有记录，创建一个
            self.db.session.execute(
                '''INSERT INTO report_quota_usage (user_id, year, month, used_quota, total_quota)
                   VALUES (:user_id, :year, :month, 0, 2)''',
                {'user_id': user_id, 'year': year, 'month': month}
            )
            self.db.session.commit()
            
            return {
                'user_id': user_id,
                'year': year,
                'month': month,
                'used_quota': 0,
                'total_quota': 2,
                'remaining_quota': 2
            }
    
    def check_quota_available(self, user_id: int) -> bool:
        """
        检查用户是否有可用配额
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否有可用配额
        """
        quota = self.get_quota_usage(user_id)
        return quota['remaining_quota'] > 0
    
    def consume_quota(self, user_id: int) -> bool:
        """
        消耗用户配额
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功消耗
        """
        now = datetime.now()
        year = now.year
        month = now.month
        
        # 检查配额
        if not self.check_quota_available(user_id):
            return False
        
        # 更新配额
        self.db.session.execute(
            '''UPDATE report_quota_usage 
               SET used_quota = used_quota + 1 
               WHERE user_id = :user_id AND year = :year AND month = :month''',
            {'user_id': user_id, 'year': year, 'month': month}
        )
        self.db.session.commit()
        
        return True
    
    def reset_monthly_quota(self):
        """
        重置所有用户的月度配额（定时任务调用）
        """
        now = datetime.now()
        year = now.year
        month = now.month
        
        # 获取所有基础版用户
        users = self.db.session.execute(
            '''SELECT DISTINCT u.id FROM users u
               INNER JOIN subscriptions s ON u.id = s.user_id
               WHERE s.status = 'active' AND s.plan_id IN (
                   SELECT id FROM subscription_plans WHERE name LIKE '%基础版%'
               )'''
        ).fetchall()
        
        # 为每个用户创建或重置配额记录
        for user in users:
            user_id = user[0]
            
            # 检查是否已有记录
            existing = self.db.session.execute(
                '''SELECT id FROM report_quota_usage 
                   WHERE user_id = :user_id AND year = :year AND month = :month''',
                {'user_id': user_id, 'year': year, 'month': month}
            ).fetchone()
            
            if not existing:
                self.db.session.execute(
                    '''INSERT INTO report_quota_usage (user_id, year, month, used_quota, total_quota)
                       VALUES (:user_id, :year, :month, 0, 2)''',
                    {'user_id': user_id, 'year': year, 'month': month}
                )
        
        self.db.session.commit()
        print(f"✓ 已重置 {len(users)} 个用户的月度配额")
    
    # ==================== 报告申请 ====================
    
    def create_request(self, user_id: int, company_id: int, data: Dict[str, Any]) -> int:
        """
        创建报告申请
        
        Args:
            user_id: 用户ID
            company_id: 企业ID
            data: 申请数据
            
        Returns:
            申请ID
        """
        # 检查配额
        if not self.check_quota_available(user_id):
            raise ValueError('本月配额已用完')
        
        # 创建申请
        cursor = self.db.session.execute(
            '''INSERT INTO report_requests 
               (user_id, company_id, report_type, title, description, 
                expected_delivery_date, additional_notes, status)
               VALUES (:user_id, :company_id, :report_type, :title, :description,
                       :expected_delivery_date, :additional_notes, 'pending')''',
            {
                'user_id': user_id,
                'company_id': company_id,
                'report_type': data['report_type'],
                'title': data['title'],
                'description': data['description'],
                'expected_delivery_date': data.get('expected_delivery_date'),
                'additional_notes': data.get('additional_notes', '')
            }
        )
        self.db.session.commit()
        
        request_id = cursor.lastrowid
        
        # 消耗配额
        self.consume_quota(user_id)
        
        return request_id
    
    def get_user_requests(self, user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """
        获取用户的报告申请列表
        
        Args:
            user_id: 用户ID
            status: 状态筛选（可选）
            
        Returns:
            申请列表
        """
        if status:
            requests = self.db.session.execute(
                '''SELECT r.*, c.name as company_name 
                   FROM report_requests r
                   LEFT JOIN companies c ON r.company_id = c.id
                   WHERE r.user_id = :user_id AND r.status = :status
                   ORDER BY r.created_at DESC''',
                {'user_id': user_id, 'status': status}
            ).fetchall()
        else:
            requests = self.db.session.execute(
                '''SELECT r.*, c.name as company_name 
                   FROM report_requests r
                   LEFT JOIN companies c ON r.company_id = c.id
                   WHERE r.user_id = :user_id
                   ORDER BY r.created_at DESC''',
                {'user_id': user_id}
            ).fetchall()
        
        result = []
        for req in requests:
            result.append({
                'id': req[0],
                'user_id': req[1],
                'company_id': req[2],
                'company_name': req[14],
                'report_type': req[3],
                'title': req[4],
                'description': req[5],
                'expected_delivery_date': req[6].isoformat() if req[6] else None,
                'additional_notes': req[7],
                'status': req[8],
                'assigned_to': req[9],
                'assigned_at': req[10].isoformat() if req[10] else None,
                'completed_at': req[11].isoformat() if req[11] else None,
                'rejected_reason': req[12],
                'created_at': req[13].isoformat() if req[13] else None
            })
        
        return result
    
    def get_request_detail(self, request_id: int) -> Optional[Dict[str, Any]]:
        """
        获取报告申请详情
        
        Args:
            request_id: 申请ID
            
        Returns:
            申请详情
        """
        req = self.db.session.execute(
            '''SELECT r.*, c.name as company_name, u.nickname as user_name
               FROM report_requests r
               LEFT JOIN companies c ON r.company_id = c.id
               LEFT JOIN users u ON r.user_id = u.id
               WHERE r.id = :id''',
            {'id': request_id}
        ).fetchone()
        
        if not req:
            return None
        
        # 获取关联的文件
        files = self.db.session.execute(
            '''SELECT * FROM report_files WHERE request_id = :request_id''',
            {'request_id': request_id}
        ).fetchall()
        
        file_list = []
        for file in files:
            file_list.append({
                'id': file[0],
                'file_name': file[2],
                'file_path': file[3],
                'file_type': file[4],
                'file_size': file[5],
                'uploaded_by': file[6],
                'created_at': file[7].isoformat() if file[7] else None
            })
        
        return {
            'id': req[0],
            'user_id': req[1],
            'user_name': req[15],
            'company_id': req[2],
            'company_name': req[14],
            'report_type': req[3],
            'title': req[4],
            'description': req[5],
            'expected_delivery_date': req[6].isoformat() if req[6] else None,
            'additional_notes': req[7],
            'status': req[8],
            'assigned_to': req[9],
            'assigned_at': req[10].isoformat() if req[10] else None,
            'completed_at': req[11].isoformat() if req[11] else None,
            'rejected_reason': req[12],
            'created_at': req[13].isoformat() if req[13] else None,
            'files': file_list
        }
    
    def update_request_status(self, request_id: int, status: str, **kwargs) -> bool:
        """
        更新报告申请状态
        
        Args:
            request_id: 申请ID
            status: 新状态
            **kwargs: 其他更新字段
            
        Returns:
            是否成功
        """
        updates = ['status = :status']
        params = {'request_id': request_id, 'status': status}
        
        if status == 'assigned' and 'assigned_to' in kwargs:
            updates.append('assigned_to = :assigned_to')
            updates.append('assigned_at = :assigned_at')
            params['assigned_to'] = kwargs['assigned_to']
            params['assigned_at'] = datetime.now()
        
        if status == 'completed':
            updates.append('completed_at = :completed_at')
            params['completed_at'] = datetime.now()
        
        if status == 'rejected' and 'rejected_reason' in kwargs:
            updates.append('rejected_reason = :rejected_reason')
            params['rejected_reason'] = kwargs['rejected_reason']
        
        sql = f"UPDATE report_requests SET {', '.join(updates)} WHERE id = :request_id"
        self.db.session.execute(sql, params)
        self.db.session.commit()
        
        return True
    
    # ==================== 文件管理 ====================
    
    def add_report_file(self, request_id: int, file_data: Dict[str, Any]) -> int:
        """
        添加报告文件
        
        Args:
            request_id: 申请ID
            file_data: 文件数据
            
        Returns:
            文件ID
        """
        cursor = self.db.session.execute(
            '''INSERT INTO report_files 
               (request_id, file_name, file_path, file_type, file_size, uploaded_by)
               VALUES (:request_id, :file_name, :file_path, :file_type, :file_size, :uploaded_by)''',
            {
                'request_id': request_id,
                'file_name': file_data['file_name'],
                'file_path': file_data['file_path'],
                'file_type': file_data['file_type'],
                'file_size': file_data['file_size'],
                'uploaded_by': file_data['uploaded_by']
            }
        )
        self.db.session.commit()
        
        return cursor.lastrowid
    
    def get_report_files(self, request_id: int) -> List[Dict[str, Any]]:
        """
        获取报告文件列表
        
        Args:
            request_id: 申请ID
            
        Returns:
            文件列表
        """
        files = self.db.session.execute(
            '''SELECT * FROM report_files WHERE request_id = :request_id''',
            {'request_id': request_id}
        ).fetchall()
        
        result = []
        for file in files:
            result.append({
                'id': file[0],
                'request_id': file[1],
                'file_name': file[2],
                'file_path': file[3],
                'file_type': file[4],
                'file_size': file[5],
                'uploaded_by': file[6],
                'created_at': file[7].isoformat() if file[7] else None
            })
        
        return result
    
    # ==================== 统计分析 ====================
    
    def get_statistics(self, user_id: int = None) -> Dict[str, Any]:
        """
        获取报告统计数据
        
        Args:
            user_id: 用户ID（可选，管理员查看全部）
            
        Returns:
            统计数据
        """
        if user_id:
            # 用户个人统计
            total = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE user_id = :user_id',
                {'user_id': user_id}
            ).fetchone()[0]
            
            pending = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE user_id = :user_id AND status = "pending"',
                {'user_id': user_id}
            ).fetchone()[0]
            
            in_progress = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE user_id = :user_id AND status IN ("assigned", "in_progress")',
                {'user_id': user_id}
            ).fetchone()[0]
            
            completed = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE user_id = :user_id AND status = "completed"',
                {'user_id': user_id}
            ).fetchone()[0]
        else:
            # 全局统计
            total = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests'
            ).fetchone()[0]
            
            pending = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE status = "pending"'
            ).fetchone()[0]
            
            in_progress = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE status IN ("assigned", "in_progress")'
            ).fetchone()[0]
            
            completed = self.db.session.execute(
                'SELECT COUNT(*) FROM report_requests WHERE status = "completed"'
            ).fetchone()[0]
        
        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed
        }
    
    # ==================== 报告类型 ====================
    
    def get_report_types(self) -> List[Dict[str, str]]:
        """获取报告类型列表"""
        return [
            {
                'value': 'tech_optimization',
                'label': '技术路线优化',
                'description': '分析不同技术方案的经济性和可行性'
            },
            {
                'value': 'market_layout',
                'label': '区域市场布局',
                'description': '分析特定区域的市场机会和布局建议'
            },
            {
                'value': 'policy_analysis',
                'label': '政策影响分析',
                'description': '深度解读政策对企业的影响'
            },
            {
                'value': 'competitor_analysis',
                'label': '竞争对手分析',
                'description': '分析主要竞争对手的战略和动向'
            },
            {
                'value': 'investment_support',
                'label': '投资决策支持',
                'description': '为重大投资决策提供数据支持'
            }
        ]
