"""
关键词推送引擎 (KeywordPushEngine)

职责: 基于用户关键词匹配文章并推送
"""

import jieba
from typing import List, Dict, Any
from app.models import Article


class KeywordPushEngine:
    """关键词推送引擎"""
    
    # 权重配置
    WEIGHT_TITLE = 3.0
    WEIGHT_SUMMARY = 2.0
    WEIGHT_TAGS = 1.5
    WEIGHT_CONTENT = 1.0
    
    def __init__(self):
        """初始化关键词推送引擎"""
        pass
    
    def calculate_relevance_score(self, article: Article, keywords: List[str]) -> float:
        """
        计算文章与关键词的相关度分数
        
        Args:
            article: 文章对象
            keywords: 用户关键词列表
            
        Returns:
            0.0 - 1.0 的相关度分数
            
        算法:
        1. 精确匹配: 关键词完全出现在标题、摘要、标签或内容中
        2. 模糊匹配: 使用jieba分词进行模糊匹配
        3. 权重计算:
           - 标题匹配: 权重 3.0
           - 摘要匹配: 权重 2.0
           - 标签匹配: 权重 1.5
           - 内容匹配: 权重 1.0
        4. 相关度分数: score = Σ(match_weight * keyword_weight) / total_keywords
        5. 归一化到 0.0-1.0 范围
        """
        if not keywords:
            return 0.0
        
        score = 0.0
        matched_keywords = 0
        
        for keyword in keywords:
            keyword_matched = False
            keyword_score = 0.0
            
            # 标题匹配 (精确匹配优先)
            if article.title and keyword in article.title:
                keyword_score = max(keyword_score, self.WEIGHT_TITLE)
                keyword_matched = True
            
            # 摘要匹配 (精确匹配优先)
            if article.summary and keyword in article.summary:
                keyword_score = max(keyword_score, self.WEIGHT_SUMMARY)
                keyword_matched = True
            
            # 标签匹配
            if article.tags and isinstance(article.tags, list):
                if any(keyword in tag for tag in article.tags):
                    keyword_score = max(keyword_score, self.WEIGHT_TAGS)
                    keyword_matched = True
            
            # 内容匹配 (模糊匹配)
            if article.content and not keyword_matched:
                if self._fuzzy_match(keyword, article.content):
                    keyword_score = max(keyword_score, self.WEIGHT_CONTENT)
                    keyword_matched = True
            
            # 如果没有精确匹配，尝试模糊匹配标题和摘要
            if not keyword_matched:
                if article.title and self._fuzzy_match(keyword, article.title):
                    keyword_score = max(keyword_score, self.WEIGHT_TITLE)
                    keyword_matched = True
                elif article.summary and self._fuzzy_match(keyword, article.summary):
                    keyword_score = max(keyword_score, self.WEIGHT_SUMMARY)
                    keyword_matched = True
            
            if keyword_matched:
                score += keyword_score
                matched_keywords += 1
        
        # 归一化分数到 0.0-1.0 范围
        if matched_keywords > 0:
            # 最大可能分数是所有关键词都匹配标题 (每个关键词 * WEIGHT_TITLE)
            max_possible_score = len(keywords) * self.WEIGHT_TITLE
            normalized_score = score / max_possible_score
            return min(normalized_score, 1.0)
        
        return 0.0
    
    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        """
        使用jieba分词进行模糊匹配
        
        Args:
            keyword: 关键词
            text: 待匹配的文本
            
        Returns:
            是否匹配
        """
        if not keyword or not text:
            return False
        
        # 首先检查精确匹配
        if keyword in text:
            return True
        
        # 使用jieba分词
        words = list(jieba.cut(text))
        
        # 检查关键词是否在分词结果中，或者分词结果中是否包含关键词
        for word in words:
            if keyword == word or keyword in word or word in keyword:
                return True
        
        return False
    
    def match_articles(self, keywords: List[str], articles: List[Article]) -> List[Article]:
        """
        匹配文章
        
        Args:
            keywords: 用户关键词列表
            articles: 待匹配的文章列表
            
        Returns:
            匹配的文章列表（按相关度排序）
        """
        if not keywords or not articles:
            return []
        
        # 计算每篇文章的相关度分数
        article_scores = []
        for article in articles:
            score = self.calculate_relevance_score(article, keywords)
            if score > 0.0:
                article_scores.append((article, score))
        
        # 按相关度分数降序排序，相同分数按发布时间降序
        article_scores.sort(
            key=lambda x: (x[1], x[0].published_at if x[0].published_at else x[0].created_at),
            reverse=True
        )
        
        # 返回排序后的文章列表，最多50篇
        return [article for article, score in article_scores[:50]]
    
    def push_matched_articles(self, user_id: int) -> Dict[str, Any]:
        """
        推送匹配的文章给用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            {
                'matched_count': int,
                'pushed_count': int,
                'status': str
            }
        """
        from app.models import Subscription, Article
        from app.services.push_service import push_manager
        from datetime import datetime, timedelta
        
        # 1. 获取用户的关键词配置
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).filter(Subscription.end_date > datetime.utcnow()).first()
        
        if not subscription:
            return {
                'matched_count': 0,
                'pushed_count': 0,
                'status': 'no_active_subscription'
            }
        
        keywords = subscription.custom_keywords or []
        
        # 2. 获取待推送的文章（最近24小时发布的文章）
        yesterday = datetime.utcnow() - timedelta(days=1)
        articles = Article.query.filter(
            Article.published_at >= yesterday,
            Article.is_reviewed == True
        ).all()
        
        if not articles:
            return {
                'matched_count': 0,
                'pushed_count': 0,
                'status': 'no_articles'
            }
        
        # 3. 匹配文章
        if keywords:
            # 使用关键词匹配
            matched_articles = self.match_articles(keywords, articles)
        else:
            # 未设置关键词，推送热门文章（按浏览量和点赞数排序）
            matched_articles = sorted(
                articles,
                key=lambda x: (x.view_count + x.like_count * 2, x.published_at),
                reverse=True
            )[:50]
        
        if not matched_articles:
            return {
                'matched_count': 0,
                'pushed_count': 0,
                'status': 'no_matches'
            }
        
        # 4. 调用推送服务
        # 构造推送内容
        content = self._format_article_push_content(matched_articles, keywords)
        
        # 发送推送
        push_service = push_manager.get_service('wechat_work')
        if push_service:
            success = push_service.send(
                user_id,
                content,
                message_type='markdown',
                title='蒙小碳·关键词推送'
            )
            
            return {
                'matched_count': len(matched_articles),
                'pushed_count': 1 if success else 0,
                'status': 'success' if success else 'push_failed'
            }
        else:
            return {
                'matched_count': len(matched_articles),
                'pushed_count': 0,
                'status': 'no_push_service'
            }
    
    def _format_article_push_content(self, articles: List[Article], keywords: List[str]) -> str:
        """
        格式化文章推送内容为 Markdown
        
        Args:
            articles: 匹配的文章列表
            keywords: 关键词列表
            
        Returns:
            Markdown 格式的推送内容
        """
        from datetime import datetime
        
        if keywords:
            title = f"# 🔍 关键词推送\n\n**关键词**: {', '.join(keywords)}\n"
        else:
            title = "# 📰 热门文章推送\n\n"
        
        content = title
        content += f"**日期**: {datetime.now().strftime('%Y年%m月%d日')}\n"
        content += f"**匹配文章**: {len(articles)} 篇\n\n"
        content += "---\n\n"
        
        # 显示前10篇文章
        for i, article in enumerate(articles[:10], 1):
            content += f"## {i}. {article.title}\n\n"
            if article.summary:
                # 截断摘要到100字
                summary = article.summary[:100] + '...' if len(article.summary) > 100 else article.summary
                content += f"{summary}\n\n"
            content += f"**分类**: {article.category} | **来源**: {article.source}\n"
            content += f"**发布时间**: {article.published_at.strftime('%Y-%m-%d %H:%M') if article.published_at else '未知'}\n\n"
            content += "---\n\n"
        
        if len(articles) > 10:
            content += f"\n*还有 {len(articles) - 10} 篇相关文章，请访问网站查看更多*\n\n"
        
        content += "*查看完整内容，请访问 [蒙小碳·能源站](http://localhost:5173)*"
        
        return content
