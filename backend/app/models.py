from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # user, editor, admin
    status = db.Column(db.String(20), default='active')  # active, banned
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 新增字段
    position = db.Column(db.String(100))  # 职位
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))  # 所属企业
    im_app_config = db.Column(db.JSON)  # IM应用配置(企业微信、钉钉、飞书)
    
    subscriptions = db.relationship('Subscription', backref='user', lazy='dynamic')
    favorites = db.relationship('UserFavorite', backref='user', lazy='dynamic')
    history = db.relationship('UserHistory', backref='user', lazy='dynamic')
    company = db.relationship('Company', foreign_keys=[company_id], backref='employees')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    features = db.Column(db.JSON)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    auto_renew = db.Column(db.Boolean, default=False)
    push_channels = db.Column(db.JSON)  # {"wechat": "wx_id", "enterprise_wechat": "corp_id"}
    custom_keywords = db.Column(db.JSON)  # ["keyword1", "keyword2"]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plan = db.relationship('SubscriptionPlan', backref='subscriptions')

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # power, energy, coal, etc.
    name = db.Column(db.String(100), nullable=False)  # 电力, 能源, 煤炭, etc.
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # 图标名称或URL
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    source = db.Column(db.String(100), index=True)
    source_url = db.Column(db.String(500), unique=True)
    category = db.Column(db.String(50), index=True)  # ndrc, coal, power, new_energy
    tags = db.Column(db.JSON)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    is_reviewed = db.Column(db.Boolean, default=False)
    is_top = db.Column(db.Boolean, default=False)
    is_carousel = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Keyword(db.Model):
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50))
    weight = db.Column(db.Integer, default=1)
    search_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50))  # government, industry, media
    crawl_rules = db.Column(db.JSON)
    crawl_interval = db.Column(db.Integer, default=86400)  # seconds
    last_crawl_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, error, disabled
    error_msg = db.Column(db.Text)
    priority = db.Column(db.String(10), default='P1')  # P0, P1, P2
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BroadcastTask(db.Model):
    __tablename__ = 'broadcast_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_type = db.Column(db.String(50))  # all, plan, custom
    target_ids = db.Column(db.JSON)
    channel = db.Column(db.String(50))  # wechat, enterprise_wechat, both
    scheduled_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, sending, completed, failed
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BroadcastLog(db.Model):
    __tablename__ = 'broadcast_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('broadcast_tasks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    channel = db.Column(db.String(50))
    content = db.Column(db.Text)
    status = db.Column(db.String(20))  # sent, failed, read
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    error_msg = db.Column(db.Text)

class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class CrawlLog(db.Model):
    __tablename__ = 'crawl_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    status = db.Column(db.String(20))  # success, failed
    articles_count = db.Column(db.Integer, default=0)
    error_msg = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)

class DailyBrief(db.Model):
    __tablename__ = 'daily_briefs'
    
    id = db.Column(db.Integer, primary_key=True)
    brief_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    content = db.Column(db.JSON)
    ai_suggestion = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 新增字段：唯一链接标识
    share_token = db.Column(db.String(32), unique=True, nullable=False, index=True)  # 唯一分享token
    
    # 新增字段：两个版本的内容
    standard_content = db.Column(db.JSON)  # 标准版内容（不含决策建议）
    premium_content = db.Column(db.JSON)   # 高级版内容（含决策建议）
    
    # 统计字段
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    share_count = db.Column(db.Integer, default=0)  # 分享次数
    
    def generate_share_token(self):
        """生成唯一的分享token"""
        import hashlib
        import secrets
        # 使用日期+随机字符串生成token
        raw = f"{self.brief_date}{secrets.token_hex(8)}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def get_share_url(self, version='standard'):
        """
        获取分享链接
        
        Args:
            version: 版本类型 (standard/premium)
        """
        base_url = "http://localhost:5173"  # TODO: 从配置读取
        return f"{base_url}/briefs/{self.share_token}?v={version}"
    
    def to_dict(self, version='standard', include_suggestion=False):
        """
        转换为字典
        
        Args:
            version: 版本类型 (standard/premium)
            include_suggestion: 是否包含决策建议
        """
        # 根据版本选择内容
        if version == 'premium' and self.premium_content:
            content = self.premium_content
        else:
            content = self.standard_content or self.content
        
        result = {
            'id': self.id,
            'brief_date': self.brief_date.strftime('%Y-%m-%d'),
            'content': content,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'share_url': self.get_share_url(version),
            'view_count': self.view_count,
            'share_count': self.share_count
        }
        
        # 高级版包含决策建议
        if include_suggestion or version == 'premium':
            result['ai_suggestion'] = self.ai_suggestion
        
        return result

class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'article_id'),)

class UserHistory(db.Model):
    __tablename__ = 'user_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    is_pinned = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))  # offline, alipay, wechat
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled, refunded, refund_pending
    payment_time = db.Column(db.DateTime)
    payment_proof = db.Column(db.String(500))  # 支付凭证图片URL
    contact_info = db.Column(db.JSON)  # 联系方式
    remark = db.Column(db.Text)
    admin_note = db.Column(db.Text)  # 管理员备注
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 确认人
    confirmed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 新增字段 - 订阅系统完善
    payment_info = db.Column(db.JSON)  # OCR提取的支付信息
    refund_reason = db.Column(db.Text)  # 退款原因
    refund_status = db.Column(db.String(20))  # 退款状态: null, pending, approved, rejected
    refund_applied_at = db.Column(db.DateTime, index=True)  # 退款申请时间
    refund_processed_at = db.Column(db.DateTime)  # 退款处理时间
    refund_processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 退款处理人ID
    
    user = db.relationship('User', foreign_keys=[user_id], backref='orders')
    plan = db.relationship('SubscriptionPlan', backref='orders')
    confirmer = db.relationship('User', foreign_keys=[confirmed_by])
    refund_processor = db.relationship('User', foreign_keys=[refund_processed_by])

class RefundApplication(db.Model):
    __tablename__ = 'refund_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)  # pending, approved, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    processed_at = db.Column(db.DateTime)
    reject_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    order = db.relationship('Order', backref='refund_applications')
    user = db.relationship('User', foreign_keys=[user_id], backref='refund_applications')
    processor = db.relationship('User', foreign_keys=[processed_by])

class Company(db.Model):
    __tablename__ = 'companies'
    
    # 基础信息
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 企业名称
    short_name = db.Column(db.String(100))  # 企业简称
    unified_social_credit_code = db.Column(db.String(50), unique=True, index=True)  # 统一社会信用代码
    legal_representative = db.Column(db.String(50))  # 法定代表人
    registered_capital = db.Column(db.String(50))  # 注册资本
    establishment_date = db.Column(db.Date)  # 成立日期
    
    # 联系信息
    contact_person = db.Column(db.String(50))  # 联系人
    contact_phone = db.Column(db.String(20))  # 联系电话
    contact_email = db.Column(db.String(100))  # 联系邮箱
    
    # 地址信息
    province = db.Column(db.String(50))  # 省份
    city = db.Column(db.String(50))  # 城市
    district = db.Column(db.String(50))  # 区县
    address = db.Column(db.String(255))  # 详细地址
    
    # 企业规模
    employee_count = db.Column(db.String(50))  # 员工人数
    annual_revenue = db.Column(db.String(50))  # 年营业额
    
    # 行业信息
    industry = db.Column(db.String(100))  # 所属行业
    industry_category = db.Column(db.String(50))  # 行业类别
    
    # 企业简介
    description = db.Column(db.Text)  # 企业简介
    website = db.Column(db.String(255))  # 企业网站
    logo = db.Column(db.String(255))  # 企业Logo
    
    # 认证信息
    business_license = db.Column(db.String(255))  # 营业执照图片
    is_verified = db.Column(db.Boolean, default=False)  # 是否认证
    verified_at = db.Column(db.DateTime)  # 认证时间
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 认证人
    
    # 状态
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人
    
    # 关系
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_companies')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    businesses = db.relationship('CompanyBusiness', backref='company', lazy='dynamic', cascade='all, delete-orphan')

class CompanyBusiness(db.Model):
    __tablename__ = 'company_businesses'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # 业务信息
    business_type = db.Column(db.String(50), nullable=False)  # 业务类型
    business_name = db.Column(db.String(200), nullable=False)  # 业务名称
    business_scope = db.Column(db.Text)  # 业务范围描述
    
    # 业务规模
    annual_output = db.Column(db.String(100))  # 年产量/产能
    market_share = db.Column(db.String(50))  # 市场份额
    
    # 业务区域
    service_area = db.Column(db.String(255))  # 服务区域
    
    # 业务特点
    core_products = db.Column(db.JSON)  # 核心产品列表
    certifications = db.Column(db.JSON)  # 资质认证列表
    
    # 排序和状态
    sort_order = db.Column(db.Integer, default=0)  # 排序
    is_primary = db.Column(db.Boolean, default=False)  # 是否主营业务
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PermissionAccessLog(db.Model):
    """
    权限访问日志模型
    
    记录用户访问数据看板和功能的日志，包括访问时间、访问模块、订阅等级和访问结果。
    
    Validates: Requirements 5.8
    """
    __tablename__ = 'permission_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 用户ID
    feature = db.Column(db.String(100), nullable=False, index=True)  # 访问的功能/模块
    subscription_level = db.Column(db.String(20), nullable=False)  # 用户订阅等级
    allowed = db.Column(db.Boolean, nullable=False)  # 是否允许访问
    ip_address = db.Column(db.String(50))  # IP地址
    accessed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)  # 访问时间
    
    user = db.relationship('User', backref='permission_access_logs')

class MonitoringRule(db.Model):
    """
    监测规则模型
    
    用于配置动态监测预警规则，包括监测类型、关键词、预警阈值等。
    """
    __tablename__ = 'monitoring_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)  # 规则名称
    type = db.Column(db.String(20), nullable=False, index=True)  # policy, price, industry
    keywords = db.Column(db.JSON, nullable=False)  # 关键词列表
    threshold = db.Column(db.Numeric(10, 2))  # 预警阈值
    level = db.Column(db.String(20), default='medium', index=True)  # high, medium, low
    channels = db.Column(db.JSON, nullable=False)  # 推送渠道
    enabled = db.Column(db.Boolean, default=True, index=True)  # 是否启用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='monitoring_rules')
    company = db.relationship('Company', backref='monitoring_rules')
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'name': self.name,
            'type': self.type,
            'type_display': self.get_type_display(),
            'keywords': json.loads(self.keywords) if isinstance(self.keywords, str) else self.keywords,
            'threshold': float(self.threshold) if self.threshold else None,
            'level': self.level,
            'level_display': self.get_level_display(),
            'channels': json.loads(self.channels) if isinstance(self.channels, str) else self.channels,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_type_display(self):
        """获取监测类型显示名称"""
        type_map = {
            'policy': '政策监测',
            'price': '价格监测',
            'industry': '行业动态'
        }
        return type_map.get(self.type, self.type)
    
    def get_level_display(self):
        """获取预警等级显示名称"""
        level_map = {
            'high': '高',
            'medium': '中',
            'low': '低'
        }
        return level_map.get(self.level, self.level)

class MonitoringAlert(db.Model):
    """
    预警记录模型
    
    记录触发的预警信息，包括预警标题、内容、等级、状态等。
    """
    __tablename__ = 'monitoring_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('monitoring_rules.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)  # 预警标题
    content = db.Column(db.Text, nullable=False)  # 预警内容
    level = db.Column(db.String(20), nullable=False, index=True)  # high, medium, low
    source_type = db.Column(db.String(50))  # 来源类型
    source_id = db.Column(db.Integer)  # 来源ID
    status = db.Column(db.String(20), default='pending', index=True)  # pending, sent, read
    sent_at = db.Column(db.DateTime)  # 发送时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    rule = db.relationship('MonitoringRule', backref='alerts')
    user = db.relationship('User', backref='monitoring_alerts')
    company = db.relationship('Company', backref='monitoring_alerts')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'rule_name': self.rule.name if self.rule else None,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'title': self.title,
            'content': self.content,
            'level': self.level,
            'level_display': self.get_level_display(),
            'source_type': self.source_type,
            'source_id': self.source_id,
            'status': self.status,
            'status_display': self.get_status_display(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_level_display(self):
        """获取预警等级显示名称"""
        level_map = {
            'high': '高',
            'medium': '中',
            'low': '低'
        }
        return level_map.get(self.level, self.level)
    
    def get_status_display(self):
        """获取状态显示名称"""
        status_map = {
            'pending': '待发送',
            'sent': '已发送',
            'read': '已读'
        }
        return status_map.get(self.status, self.status)
