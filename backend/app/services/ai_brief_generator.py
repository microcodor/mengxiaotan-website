"""
AI简报生成器
使用MiniMax API生成每日行业简报
"""
import requests
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from app import db
from app.models import Article, DailyBrief, Subscription, SubscriptionPlan
import logging

logger = logging.getLogger(__name__)


class AIBriefGenerator:
    """AI简报生成器"""
    
    def __init__(self, api_key: str, group_id: str, api_url: str):
        """
        初始化AI简报生成器
        
        Args:
            api_key: MiniMax API密钥
            group_id: MiniMax Group ID
            api_url: MiniMax API URL
        """
        self.api_key = api_key
        self.group_id = group_id
        self.api_url = api_url
        self.retry_count = 0
        self.max_retries = 3
    
    def collect_articles(self, target_date: date, limit: int = 30) -> List[Article]:
        """
        收集指定日期的热门文章
        
        Args:
            target_date: 目标日期
            limit: 文章数量限制
            
        Returns:
            文章列表（按浏览量+点赞数排序）
        """
        # 计算日期范围（当天0点到23:59:59）
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # 查询文章，按浏览量+点赞数排序
        articles = Article.query.filter(
            Article.published_at >= start_datetime,
            Article.published_at <= end_datetime,
            Article.is_reviewed == True
        ).order_by(
            (Article.view_count + Article.like_count).desc()
        ).limit(limit).all()
        
        logger.info(f"收集到 {len(articles)} 篇文章，日期: {target_date}")
        return articles
    
    def call_minimax_api(self, prompt: str) -> Optional[str]:
        """
        调用MiniMax API生成内容
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的内容，失败返回None
        """
        if not self.api_key or not self.group_id:
            logger.error("MiniMax API配置不完整")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'abab6.5-chat',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'tokens_to_generate': 2048,
            'temperature': 0.7,
            'top_p': 0.95
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('choices') and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    logger.info(f"MiniMax API调用成功，生成内容长度: {len(content)}")
                    return content
                else:
                    logger.error(f"MiniMax API返回格式异常: {result}")
                    return None
            else:
                logger.error(f"MiniMax API调用失败: {response.status_code}, {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("MiniMax API调用超时")
            return None
        except Exception as e:
            logger.error(f"MiniMax API调用异常: {e}")
            return None
    
    def format_brief_content(self, articles: List[Article], ai_response: str) -> Dict:
        """
        格式化简报内容
        
        Args:
            articles: 文章列表
            ai_response: AI生成的内容
            
        Returns:
            格式化后的简报内容（JSON结构）
        """
        # 按分类组织文章
        content_by_category = {
            'ndrc': [],
            'coal': [],
            'power': [],
            'new_energy': []
        }
        
        for article in articles:
            category = article.category
            if category in content_by_category:
                content_by_category[category].append({
                    'title': article.title,
                    'summary': article.summary or '',
                    'url': f'/articles/{article.id}',
                    'source': article.source,
                    'published_at': article.published_at.strftime('%Y-%m-%d %H:%M') if article.published_at else ''
                })
        
        # 构造完整的简报内容
        brief_content = {
            'content': content_by_category,
            'ai_summary': ai_response[:1000] if ai_response else '',  # 限制1000字
            'generated_at': datetime.utcnow().isoformat(),
            'article_count': len(articles)
        }
        
        return brief_content

    
    def generate_daily_brief(self, target_date: date = None) -> Optional[Dict]:
        """
        生成每日简报
        
        Args:
            target_date: 目标日期，默认为昨天
            
        Returns:
            生成的简报信息，失败返回None
        """
        # 默认生成昨天的简报
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        # 检查是否已生成
        existing_brief = DailyBrief.query.filter_by(brief_date=target_date).first()
        if existing_brief:
            logger.info(f"简报已存在: {target_date}")
            return {
                'brief_id': existing_brief.id,
                'content': existing_brief.content,
                'ai_suggestion': existing_brief.ai_suggestion,
                'generated_at': existing_brief.generated_at,
                'status': 'existing'
            }
        
        # 收集文章
        articles = self.collect_articles(target_date, limit=30)
        
        if not articles:
            logger.warning(f"没有找到文章: {target_date}")
            return None
        
        # 构造Prompt
        prompt = self._build_prompt(articles)
        
        # 调用MiniMax API
        ai_response = self.call_minimax_api(prompt)
        
        if not ai_response:
            logger.error("AI生成失败")
            # 如果失败且未达到最大重试次数，返回None以便重试
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                logger.info(f"将在1小时后重试，当前重试次数: {self.retry_count}")
                return None
            else:
                logger.error("已达到最大重试次数，使用默认简报")
                ai_response = self._generate_default_brief(articles)
        
        # 格式化内容
        brief_content = self.format_brief_content(articles, ai_response)
        
        # 提取AI建议（针对高级版用户）
        ai_suggestion = self._extract_ai_suggestion(ai_response)
        
        # 保存到数据库
        try:
            daily_brief = DailyBrief(
                brief_date=target_date,
                content=brief_content,  # 保留原始完整内容
                ai_suggestion=ai_suggestion,
                generated_at=datetime.utcnow()
            )
            
            # 生成唯一分享token
            daily_brief.share_token = daily_brief.generate_share_token()
            
            # 生成标准版内容（不含决策建议）
            standard_content = brief_content.copy()
            daily_brief.standard_content = standard_content
            
            # 生成高级版内容（含决策建议）
            premium_content = brief_content.copy()
            premium_content['ai_suggestion'] = ai_suggestion
            daily_brief.premium_content = premium_content
            
            db.session.add(daily_brief)
            db.session.commit()
            
            logger.info(f"简报生成成功: {target_date}, ID: {daily_brief.id}, Token: {daily_brief.share_token}")
            
            # 重置重试计数
            self.retry_count = 0
            
            return {
                'brief_id': daily_brief.id,
                'content': brief_content,
                'ai_suggestion': ai_suggestion,
                'generated_at': daily_brief.generated_at,
                'share_token': daily_brief.share_token,
                'standard_url': daily_brief.get_share_url('standard'),
                'premium_url': daily_brief.get_share_url('premium'),
                'status': 'created'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存简报失败: {e}")
            return None
    
    def _build_prompt(self, articles: List[Article]) -> str:
        """
        构造MiniMax API的Prompt
        
        Args:
            articles: 文章列表
            
        Returns:
            Prompt字符串
        """
        # 按分类组织文章摘要
        articles_by_category = {}
        for article in articles:
            category = article.category
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append({
                'title': article.title,
                'summary': article.summary or '',
                'source': article.source
            })
        
        # 构造文章摘要文本
        articles_summary = ""
        category_names = {
            'ndrc': '发改委动态',
            'coal': '煤炭行业',
            'power': '电力行业',
            'new_energy': '新能源'
        }
        
        for category, name in category_names.items():
            if category in articles_by_category:
                articles_summary += f"\n【{name}】\n"
                for idx, article in enumerate(articles_by_category[category][:10], 1):
                    articles_summary += f"{idx}. {article['title']}\n"
                    if article['summary']:
                        articles_summary += f"   摘要: {article['summary'][:100]}...\n"
                    articles_summary += f"   来源: {article['source']}\n"
        
        # 构造完整Prompt
        prompt = f"""你是一位资深的能源行业分析师。请根据以下文章生成一份专业的每日简报。

文章列表：
{articles_summary}

要求：
1. 总结行业热点（不超过300字）
2. 解读重要政策（不超过300字）
3. 分析市场趋势（不超过300字）
4. 提供决策建议（不超过100字）

请用专业、简洁的语言撰写，总字数控制在1000字以内。
"""
        
        return prompt
    
    def _extract_ai_suggestion(self, ai_response: str) -> str:
        """
        从AI响应中提取决策建议
        
        Args:
            ai_response: AI生成的完整内容
            
        Returns:
            决策建议文本
        """
        # 尝试提取"决策建议"部分
        if '决策建议' in ai_response:
            parts = ai_response.split('决策建议')
            if len(parts) > 1:
                # 提取决策建议后的内容，去除前导符号（如：、冒号等）
                suggestion = parts[1].strip()
                # 移除开头的标点符号
                suggestion = suggestion.lstrip('：:、，,。. \t\n')
                # 限制长度
                return suggestion[:200]
        
        # 如果没有明确的决策建议部分，返回空字符串
        return ""
    
    def _generate_default_brief(self, articles: List[Article]) -> str:
        """
        生成默认简报（当AI调用失败时使用）
        
        Args:
            articles: 文章列表
            
        Returns:
            默认简报内容
        """
        brief = f"今日共收集到 {len(articles)} 篇能源行业资讯。\n\n"
        
        # 按分类统计
        category_count = {}
        for article in articles:
            category = article.category
            category_count[category] = category_count.get(category, 0) + 1
        
        category_names = {
            'ndrc': '发改委动态',
            'coal': '煤炭行业',
            'power': '电力行业',
            'new_energy': '新能源'
        }
        
        for category, count in category_count.items():
            name = category_names.get(category, category)
            brief += f"- {name}: {count} 篇\n"
        
        brief += "\n请查看详细文章列表获取更多信息。"
        
        return brief
    
    def push_brief_to_users(self, brief_id: int) -> Dict:
        """
        推送简报给订阅用户
        
        Args:
            brief_id: 简报ID
            
        Returns:
            推送结果统计
        """
        from app.services.push_service import push_manager
        
        # 获取简报
        brief = DailyBrief.query.get(brief_id)
        if not brief:
            logger.error(f"简报不存在: {brief_id}")
            return {'error': '简报不存在'}
        
        # 获取活跃订阅用户（标准版和高级版）
        active_subscriptions = Subscription.query.join(
            SubscriptionPlan
        ).filter(
            Subscription.status == 'active',
            Subscription.end_date > datetime.utcnow(),
            SubscriptionPlan.name.in_(['标准版', '高级版'])
        ).all()
        
        if not active_subscriptions:
            logger.info("没有符合条件的订阅用户")
            return {'message': '没有符合条件的订阅用户', 'sent': 0}
        
        # 分别推送给标准版和高级版用户
        standard_users = []
        premium_users = []
        
        for sub in active_subscriptions:
            if sub.plan.name == '标准版':
                standard_users.append(sub.user_id)
            elif sub.plan.name == '高级版':
                premium_users.append(sub.user_id)
        
        results = {
            'standard': {'sent': 0, 'failed': 0},
            'premium': {'sent': 0, 'failed': 0}
        }
        
        # 推送给标准版用户（不包含决策建议）
        if standard_users:
            content = self._format_brief_for_push(brief, include_suggestion=False)
            for user_id in standard_users:
                push_result = push_manager.send_to_user(
                    user_id,
                    content,
                    channels=['wechat_work'],
                    message_type='markdown',
                    title='蒙小碳·每日简报'
                )
                if push_result.get('wechat_work'):
                    results['standard']['sent'] += 1
                else:
                    results['standard']['failed'] += 1
        
        # 推送给高级版用户（包含决策建议）
        if premium_users:
            content = self._format_brief_for_push(brief, include_suggestion=True)
            for user_id in premium_users:
                push_result = push_manager.send_to_user(
                    user_id,
                    content,
                    channels=['wechat_work'],
                    message_type='markdown',
                    title='蒙小碳·每日简报'
                )
                if push_result.get('wechat_work'):
                    results['premium']['sent'] += 1
                else:
                    results['premium']['failed'] += 1
        
        logger.info(f"简报推送完成: {results}")
        return results
    
    def _format_brief_for_push(self, brief: DailyBrief, include_suggestion: bool = False) -> str:
        """
        格式化简报内容用于推送
        
        Args:
            brief: 简报对象
            include_suggestion: 是否包含决策建议
            
        Returns:
            格式化后的Markdown内容
        """
        # 根据版本选择内容
        if include_suggestion:
            content = brief.premium_content or brief.content
            version = 'premium'
        else:
            content = brief.standard_content or brief.content
            version = 'standard'
        
        ai_summary = content.get('ai_summary', '')
        
        markdown = f"""# 蒙小碳·每日简报

**日期**: {brief.brief_date.strftime('%Y年%m月%d日')}

---

## 📊 今日概览

{ai_summary}

---
"""
        
        # 添加决策建议（仅高级版）
        if include_suggestion and brief.ai_suggestion:
            markdown += f"""## 💡 决策建议

{brief.ai_suggestion}

---

"""
        
        # 添加查看链接
        view_url = brief.get_share_url(version)
        markdown += f"*[点击查看完整简报]({view_url})*"
        
        return markdown
