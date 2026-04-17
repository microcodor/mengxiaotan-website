"""
动态监测预警服务
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import and_, or_, desc
from app.models import db, MonitoringRule, MonitoringAlert, User, Company, Article
import json


class MonitoringService:
    """监测预警服务类"""
    
    @staticmethod
    def create_rule(user_id: int, company_id: int, rule_data: dict) -> MonitoringRule:
        """
        创建监测规则
        
        Args:
            user_id: 用户ID
            company_id: 企业ID
            rule_data: 规则数据
            
        Returns:
            MonitoringRule: 创建的规则对象
        """
        rule = MonitoringRule(
            user_id=user_id,
            company_id=company_id,
            name=rule_data['name'],
            type=rule_data['type'],
            keywords=json.dumps(rule_data['keywords'], ensure_ascii=False),
            threshold=rule_data.get('threshold'),
            level=rule_data.get('level', 'medium'),
            channels=json.dumps(rule_data.get('channels', ['system']), ensure_ascii=False),
            enabled=rule_data.get('enabled', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return rule
    
    @staticmethod
    def get_user_rules(user_id: int, enabled_only: bool = False) -> List[MonitoringRule]:
        """
        获取用户的监测规则
        
        Args:
            user_id: 用户ID
            enabled_only: 是否只返回启用的规则
            
        Returns:
            List[MonitoringRule]: 规则列表
        """
        query = MonitoringRule.query.filter_by(user_id=user_id)
        
        if enabled_only:
            query = query.filter_by(enabled=True)
        
        return query.order_by(desc(MonitoringRule.created_at)).all()
    
    @staticmethod
    def get_rule_by_id(rule_id: int, user_id: int) -> Optional[MonitoringRule]:
        """
        获取指定规则
        
        Args:
            rule_id: 规则ID
            user_id: 用户ID
            
        Returns:
            Optional[MonitoringRule]: 规则对象
        """
        return MonitoringRule.query.filter_by(
            id=rule_id,
            user_id=user_id
        ).first()
    
    @staticmethod
    def update_rule(rule_id: int, user_id: int, rule_data: dict) -> Optional[MonitoringRule]:
        """
        更新监测规则
        
        Args:
            rule_id: 规则ID
            user_id: 用户ID
            rule_data: 规则数据
            
        Returns:
            Optional[MonitoringRule]: 更新后的规则对象
        """
        rule = MonitoringService.get_rule_by_id(rule_id, user_id)
        
        if not rule:
            return None
        
        # 更新字段
        if 'name' in rule_data:
            rule.name = rule_data['name']
        if 'type' in rule_data:
            rule.type = rule_data['type']
        if 'keywords' in rule_data:
            rule.keywords = json.dumps(rule_data['keywords'], ensure_ascii=False)
        if 'threshold' in rule_data:
            rule.threshold = rule_data['threshold']
        if 'level' in rule_data:
            rule.level = rule_data['level']
        if 'channels' in rule_data:
            rule.channels = json.dumps(rule_data['channels'], ensure_ascii=False)
        if 'enabled' in rule_data:
            rule.enabled = rule_data['enabled']
        
        db.session.commit()
        
        return rule
    
    @staticmethod
    def delete_rule(rule_id: int, user_id: int) -> bool:
        """
        删除监测规则
        
        Args:
            rule_id: 规则ID
            user_id: 用户ID
            
        Returns:
            bool: 是否删除成功
        """
        rule = MonitoringService.get_rule_by_id(rule_id, user_id)
        
        if not rule:
            return False
        
        db.session.delete(rule)
        db.session.commit()
        
        return True
    
    @staticmethod
    def toggle_rule(rule_id: int, user_id: int, enabled: bool) -> Optional[MonitoringRule]:
        """
        启用/禁用规则
        
        Args:
            rule_id: 规则ID
            user_id: 用户ID
            enabled: 是否启用
            
        Returns:
            Optional[MonitoringRule]: 更新后的规则对象
        """
        rule = MonitoringService.get_rule_by_id(rule_id, user_id)
        
        if not rule:
            return None
        
        rule.enabled = enabled
        db.session.commit()
        
        return rule
    
    @staticmethod
    def check_article_match(article: Article, rules: List[MonitoringRule]) -> List[Dict]:
        """
        检查文章是否匹配监测规则
        
        Args:
            article: 文章对象
            rules: 规则列表
            
        Returns:
            List[Dict]: 匹配的规则和原因
        """
        matches = []
        
        # 文章内容
        content = f"{article.title} {article.summary or ''}"
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            # 解析关键词
            keywords = json.loads(rule.keywords)
            
            # 检查关键词匹配
            matched_keywords = []
            for keyword in keywords:
                if keyword in content:
                    matched_keywords.append(keyword)
            
            # 如果有关键词匹配
            if matched_keywords:
                matches.append({
                    'rule': rule,
                    'matched_keywords': matched_keywords,
                    'match_count': len(matched_keywords)
                })
        
        return matches
    
    @staticmethod
    def create_alert(rule: MonitoringRule, article: Article, matched_keywords: List[str]) -> MonitoringAlert:
        """
        创建预警记录
        
        Args:
            rule: 监测规则
            article: 文章对象
            matched_keywords: 匹配的关键词
            
        Returns:
            MonitoringAlert: 预警对象
        """
        # 生成预警标题
        title = f"【{rule.get_type_display()}】{article.title}"
        
        # 生成预警内容
        content = f"""
触发规则：{rule.name}
匹配关键词：{', '.join(matched_keywords)}

文章摘要：
{article.summary or '暂无摘要'}

建议措施：
请及时关注相关动态，评估对企业的影响。
"""
        
        alert = MonitoringAlert(
            rule_id=rule.id,
            user_id=rule.user_id,
            company_id=rule.company_id,
            title=title,
            content=content.strip(),
            level=rule.level,
            source_type='article',
            source_id=article.id,
            status='pending'
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    @staticmethod
    def get_user_alerts(
        user_id: int,
        level: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[MonitoringAlert]:
        """
        获取用户的预警记录
        
        Args:
            user_id: 用户ID
            level: 预警等级筛选
            status: 状态筛选
            limit: 返回数量限制
            
        Returns:
            List[MonitoringAlert]: 预警列表
        """
        query = MonitoringAlert.query.filter_by(user_id=user_id)
        
        if level:
            query = query.filter_by(level=level)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(desc(MonitoringAlert.created_at)).limit(limit).all()
    
    @staticmethod
    def get_alert_by_id(alert_id: int, user_id: int) -> Optional[MonitoringAlert]:
        """
        获取指定预警
        
        Args:
            alert_id: 预警ID
            user_id: 用户ID
            
        Returns:
            Optional[MonitoringAlert]: 预警对象
        """
        return MonitoringAlert.query.filter_by(
            id=alert_id,
            user_id=user_id
        ).first()
    
    @staticmethod
    def mark_alert_read(alert_id: int, user_id: int) -> Optional[MonitoringAlert]:
        """
        标记预警为已读
        
        Args:
            alert_id: 预警ID
            user_id: 用户ID
            
        Returns:
            Optional[MonitoringAlert]: 更新后的预警对象
        """
        alert = MonitoringService.get_alert_by_id(alert_id, user_id)
        
        if not alert:
            return None
        
        alert.status = 'read'
        db.session.commit()
        
        return alert
    
    @staticmethod
    def get_alert_statistics(user_id: int) -> Dict:
        """
        获取预警统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 统计信息
        """
        # 总预警数
        total = MonitoringAlert.query.filter_by(user_id=user_id).count()
        
        # 未读预警数
        unread = MonitoringAlert.query.filter_by(
            user_id=user_id,
            status='pending'
        ).count()
        
        # 按等级统计
        high = MonitoringAlert.query.filter_by(
            user_id=user_id,
            level='high'
        ).count()
        
        medium = MonitoringAlert.query.filter_by(
            user_id=user_id,
            level='medium'
        ).count()
        
        low = MonitoringAlert.query.filter_by(
            user_id=user_id,
            level='low'
        ).count()
        
        # 今日预警数
        from datetime import date
        today = date.today()
        today_count = MonitoringAlert.query.filter(
            MonitoringAlert.user_id == user_id,
            db.func.date(MonitoringAlert.created_at) == today
        ).count()
        
        return {
            'total': total,
            'unread': unread,
            'by_level': {
                'high': high,
                'medium': medium,
                'low': low
            },
            'today': today_count
        }
    
    @staticmethod
    def process_new_articles(articles: List[Article]) -> int:
        """
        处理新文章，检查是否触发预警
        
        Args:
            articles: 文章列表
            
        Returns:
            int: 创建的预警数量
        """
        # 获取所有启用的规则
        rules = MonitoringRule.query.filter_by(enabled=True).all()
        
        if not rules:
            return 0
        
        alert_count = 0
        
        for article in articles:
            # 检查文章是否匹配规则
            matches = MonitoringService.check_article_match(article, rules)
            
            # 为每个匹配的规则创建预警
            for match in matches:
                MonitoringService.create_alert(
                    rule=match['rule'],
                    article=article,
                    matched_keywords=match['matched_keywords']
                )
                alert_count += 1
        
        return alert_count
