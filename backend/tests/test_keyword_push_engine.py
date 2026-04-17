"""
Unit tests for KeywordPushEngine

Tests the keyword matching algorithm including:
- Exact matching in title, summary, tags, content
- Fuzzy matching using jieba
- Weighted scoring
- Score normalization
"""

import pytest
from datetime import datetime
from app.services.keyword_push_engine import KeywordPushEngine
from app.models import Article


class TestKeywordPushEngine:
    """Test KeywordPushEngine class"""
    
    @pytest.fixture
    def engine(self):
        """Create KeywordPushEngine instance"""
        return KeywordPushEngine()
    
    @pytest.fixture
    def sample_article(self):
        """Create a sample article for testing"""
        article = Article()
        article.id = 1
        article.title = "光伏产业发展迅速"
        article.summary = "2024年光伏发电装机容量持续增长"
        article.content = "光伏产业在新能源领域占据重要地位，风电和储能技术也在快速发展"
        article.tags = ["光伏", "新能源", "发电"]
        article.published_at = datetime(2024, 1, 15)
        return article
    
    def test_exact_match_in_title(self, engine, sample_article):
        """测试标题精确匹配"""
        keywords = ["光伏"]
        score = engine.calculate_relevance_score(sample_article, keywords)
        
        # 标题匹配应该有分数
        assert score > 0.0
        assert score <= 1.0
    
    def test_exact_match_in_summary(self, engine):
        """测试摘要精确匹配"""
        article = Article()
        article.title = "能源行业新闻"
        article.summary = "风电装机容量增长"
        article.content = ""
        article.tags = []
        
        keywords = ["风电"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 摘要匹配应该有分数
        assert score > 0.0
        assert score <= 1.0
    
    def test_exact_match_in_tags(self, engine):
        """测试标签精确匹配"""
        article = Article()
        article.title = "能源新闻"
        article.summary = "行业动态"
        article.content = ""
        article.tags = ["储能", "电池"]
        
        keywords = ["储能"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 标签匹配应该有分数
        assert score > 0.0
        assert score <= 1.0
    
    def test_fuzzy_match_in_content(self, engine):
        """测试内容模糊匹配"""
        article = Article()
        article.title = "能源新闻"
        article.summary = "行业动态"
        article.content = "碳中和目标推动清洁能源发展"
        article.tags = []
        
        keywords = ["碳中和"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 内容匹配应该有分数
        assert score > 0.0
        assert score <= 1.0
    
    def test_no_match(self, engine):
        """测试无匹配情况"""
        article = Article()
        article.title = "煤炭行业新闻"
        article.summary = "煤炭价格上涨"
        article.content = "煤炭市场供需关系"
        article.tags = ["煤炭"]
        
        keywords = ["光伏", "风电"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 无匹配应该返回0分
        assert score == 0.0
    
    def test_multiple_keywords_match(self, engine, sample_article):
        """测试多个关键词匹配"""
        keywords = ["光伏", "风电", "储能"]
        score = engine.calculate_relevance_score(sample_article, keywords)
        
        # 多个关键词匹配应该有分数
        assert score > 0.0
        assert score <= 1.0
    
    def test_empty_keywords(self, engine, sample_article):
        """测试空关键词列表"""
        keywords = []
        score = engine.calculate_relevance_score(sample_article, keywords)
        
        # 空关键词应该返回0分
        assert score == 0.0
    
    def test_score_normalization(self, engine):
        """测试分数归一化"""
        article = Article()
        article.title = "光伏风电储能"
        article.summary = "光伏风电储能发展"
        article.content = "光伏风电储能技术"
        article.tags = ["光伏", "风电", "储能"]
        
        keywords = ["光伏", "风电", "储能"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 分数应该在0.0-1.0范围内
        assert 0.0 <= score <= 1.0
    
    def test_title_weight_higher_than_summary(self, engine):
        """测试标题权重高于摘要"""
        article_title = Article()
        article_title.title = "光伏产业"
        article_title.summary = ""
        article_title.content = ""
        article_title.tags = []
        
        article_summary = Article()
        article_summary.title = ""
        article_summary.summary = "光伏产业"
        article_summary.content = ""
        article_summary.tags = []
        
        keywords = ["光伏"]
        score_title = engine.calculate_relevance_score(article_title, keywords)
        score_summary = engine.calculate_relevance_score(article_summary, keywords)
        
        # 标题匹配的分数应该高于摘要匹配
        assert score_title > score_summary
    
    def test_summary_weight_higher_than_tags(self, engine):
        """测试摘要权重高于标签"""
        article_summary = Article()
        article_summary.title = ""
        article_summary.summary = "光伏产业"
        article_summary.content = ""
        article_summary.tags = []
        
        article_tags = Article()
        article_tags.title = ""
        article_tags.summary = ""
        article_tags.content = ""
        article_tags.tags = ["光伏"]
        
        keywords = ["光伏"]
        score_summary = engine.calculate_relevance_score(article_summary, keywords)
        score_tags = engine.calculate_relevance_score(article_tags, keywords)
        
        # 摘要匹配的分数应该高于标签匹配
        assert score_summary > score_tags
    
    def test_tags_weight_higher_than_content(self, engine):
        """测试标签权重高于内容"""
        article_tags = Article()
        article_tags.title = ""
        article_tags.summary = ""
        article_tags.content = ""
        article_tags.tags = ["光伏"]
        
        article_content = Article()
        article_content.title = ""
        article_content.summary = ""
        article_content.content = "光伏产业发展"
        article_content.tags = []
        
        keywords = ["光伏"]
        score_tags = engine.calculate_relevance_score(article_tags, keywords)
        score_content = engine.calculate_relevance_score(article_content, keywords)
        
        # 标签匹配的分数应该高于内容匹配
        assert score_tags > score_content
    
    def test_fuzzy_match_compound_word(self, engine):
        """测试模糊匹配复合词"""
        article = Article()
        article.title = ""
        article.summary = ""
        article.content = "光伏发电技术不断进步"
        article.tags = []
        
        keywords = ["光伏"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 应该能匹配"光伏发电"中的"光伏"
        assert score > 0.0
    
    def test_match_articles_sorting(self, engine):
        """测试文章匹配和排序"""
        article1 = Article()
        article1.id = 1
        article1.title = "光伏产业"
        article1.summary = ""
        article1.content = ""
        article1.tags = []
        article1.published_at = datetime(2024, 1, 15)
        
        article2 = Article()
        article2.id = 2
        article2.title = ""
        article2.summary = "光伏发展"
        article2.content = ""
        article2.tags = []
        article2.published_at = datetime(2024, 1, 16)
        
        article3 = Article()
        article3.id = 3
        article3.title = "煤炭新闻"
        article3.summary = ""
        article3.content = ""
        article3.tags = []
        article3.published_at = datetime(2024, 1, 17)
        
        articles = [article1, article2, article3]
        keywords = ["光伏"]
        
        matched = engine.match_articles(keywords, articles)
        
        # 应该只匹配article1和article2
        assert len(matched) == 2
        # article1应该排在前面（标题权重高于摘要）
        assert matched[0].id == 1
        assert matched[1].id == 2
    
    def test_match_articles_empty_keywords(self, engine):
        """测试空关键词匹配"""
        articles = [Article(), Article()]
        keywords = []
        
        matched = engine.match_articles(keywords, articles)
        
        # 空关键词应该返回空列表
        assert len(matched) == 0
    
    def test_match_articles_empty_articles(self, engine):
        """测试空文章列表"""
        articles = []
        keywords = ["光伏"]
        
        matched = engine.match_articles(keywords, articles)
        
        # 空文章列表应该返回空列表
        assert len(matched) == 0
    
    def test_match_articles_same_score_sort_by_time(self, engine):
        """测试相同分数按时间排序"""
        article1 = Article()
        article1.id = 1
        article1.title = "光伏产业"
        article1.summary = ""
        article1.content = ""
        article1.tags = []
        article1.published_at = datetime(2024, 1, 15)
        
        article2 = Article()
        article2.id = 2
        article2.title = "光伏发展"
        article2.summary = ""
        article2.content = ""
        article2.tags = []
        article2.published_at = datetime(2024, 1, 16)
        
        articles = [article1, article2]
        keywords = ["光伏"]
        
        matched = engine.match_articles(keywords, articles)
        
        # 相同分数应该按发布时间降序排序
        assert len(matched) == 2
        assert matched[0].id == 2  # 更新的文章排在前面
        assert matched[1].id == 1
    
    def test_none_values_handling(self, engine):
        """测试None值处理"""
        article = Article()
        article.title = None
        article.summary = None
        article.content = None
        article.tags = None
        
        keywords = ["光伏"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # None值应该被正确处理，返回0分
        assert score == 0.0
    
    def test_tags_not_list(self, engine):
        """测试tags不是列表的情况"""
        article = Article()
        article.title = ""
        article.summary = ""
        article.content = ""
        article.tags = "光伏"  # 不是列表
        
        keywords = ["光伏"]
        score = engine.calculate_relevance_score(article, keywords)
        
        # 应该能正确处理，不抛出异常
        assert score >= 0.0
