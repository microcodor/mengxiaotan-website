"""
Property-based tests for KeywordPushEngine

**Validates: Requirements 3.3, 3.5, 3.9**

Uses hypothesis to test universal properties of the keyword matching algorithm:
- Property 2: Keyword matching correctness
- Property 3: Article sorting and truncation correctness
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from app.services.keyword_push_engine import KeywordPushEngine
from app.models import Article


# Custom strategies for generating test data
@st.composite
def article_strategy(draw):
    """Generate random Article objects"""
    article = Article()
    article.id = draw(st.integers(min_value=1, max_value=10000))
    article.title = draw(st.text(min_size=5, max_size=100))
    article.summary = draw(st.text(min_size=10, max_size=200))
    article.content = draw(st.text(min_size=20, max_size=500))
    article.tags = draw(st.lists(st.text(min_size=2, max_size=20), max_size=10))
    
    # Generate published_at within last year
    days_ago = draw(st.integers(min_value=0, max_value=365))
    article.published_at = datetime.now() - timedelta(days=days_ago)
    article.created_at = article.published_at
    
    return article


@st.composite
def keyword_list_strategy(draw):
    """Generate random keyword lists (1-20 keywords)"""
    # Use Chinese characters and common energy-related terms
    keywords = draw(st.lists(
        st.text(min_size=1, max_size=10, alphabet='光伏风电储能煤炭石油天然气核能水电氢能碳中和新能源'),
        min_size=1,
        max_size=20,
        unique=True
    ))
    return keywords


class TestKeywordMatchingProperties:
    """Property-based tests for keyword matching algorithm"""
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keywords=keyword_list_strategy(),
        article=article_strategy()
    )
    @settings(max_examples=100, deadline=1000)  # Increase deadline for jieba loading
    def test_property_2_score_range(self, keywords, article):
        """
        Property 2: 关键词匹配正确性 - 分数范围
        **Validates: Requirements 3.3, 3.5**
        
        For any article and keywords, the relevance score must be in range [0.0, 1.0]
        """
        engine = KeywordPushEngine()
        score = engine.calculate_relevance_score(article, keywords)
        assert 0.0 <= score <= 1.0, f"Score {score} is out of range [0.0, 1.0]"
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能'),
        extra_text=st.text(min_size=0, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_2_title_match_gives_positive_score(self, keyword, extra_text):
        """
        Property 2: 关键词匹配正确性 - 标题匹配
        **Validates: Requirements 3.3**
        
        If a keyword appears in the title, the article should have a positive score
        """
        engine = KeywordPushEngine()
        article = Article()
        article.title = f"{extra_text}{keyword}{extra_text}"
        article.summary = ""
        article.content = ""
        article.tags = []
        
        keywords = [keyword]
        score = engine.calculate_relevance_score(article, keywords)
        
        assert score > 0.0, f"Title contains keyword '{keyword}' but score is {score}"
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能'),
        extra_text=st.text(min_size=0, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_2_summary_match_gives_positive_score(self, keyword, extra_text):
        """
        Property 2: 关键词匹配正确性 - 摘要匹配
        **Validates: Requirements 3.3**
        
        If a keyword appears in the summary, the article should have a positive score
        """
        engine = KeywordPushEngine()
        article = Article()
        article.title = ""
        article.summary = f"{extra_text}{keyword}{extra_text}"
        article.content = ""
        article.tags = []
        
        keywords = [keyword]
        score = engine.calculate_relevance_score(article, keywords)
        
        assert score > 0.0, f"Summary contains keyword '{keyword}' but score is {score}"
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=100)
    def test_property_2_tags_match_gives_positive_score(self, keyword):
        """
        Property 2: 关键词匹配正确性 - 标签匹配
        **Validates: Requirements 3.3**
        
        If a keyword appears in tags, the article should have a positive score
        """
        engine = KeywordPushEngine()
        article = Article()
        article.title = ""
        article.summary = ""
        article.content = ""
        article.tags = [keyword, "其他标签"]
        
        keywords = [keyword]
        score = engine.calculate_relevance_score(article, keywords)
        
        assert score > 0.0, f"Tags contain keyword '{keyword}' but score is {score}"
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=100)
    def test_property_2_title_weight_higher_than_summary(self, keyword):
        """
        Property 2: 关键词匹配正确性 - 权重计算
        **Validates: Requirements 3.5**
        
        Title matches should have higher weight than summary matches
        """
        engine = KeywordPushEngine()
        article_title = Article()
        article_title.title = keyword
        article_title.summary = ""
        article_title.content = ""
        article_title.tags = []
        
        article_summary = Article()
        article_summary.title = ""
        article_summary.summary = keyword
        article_summary.content = ""
        article_summary.tags = []
        
        keywords = [keyword]
        score_title = engine.calculate_relevance_score(article_title, keywords)
        score_summary = engine.calculate_relevance_score(article_summary, keywords)
        
        assert score_title > score_summary, \
            f"Title score {score_title} should be > summary score {score_summary}"
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=100)
    def test_property_2_summary_weight_higher_than_tags(self, keyword):
        """
        Property 2: 关键词匹配正确性 - 权重计算
        **Validates: Requirements 3.5**
        
        Summary matches should have higher weight than tag matches
        """
        engine = KeywordPushEngine()
        article_summary = Article()
        article_summary.title = ""
        article_summary.summary = keyword
        article_summary.content = ""
        article_summary.tags = []
        
        article_tags = Article()
        article_tags.title = ""
        article_tags.summary = ""
        article_tags.content = ""
        article_tags.tags = [keyword]
        
        keywords = [keyword]
        score_summary = engine.calculate_relevance_score(article_summary, keywords)
        score_tags = engine.calculate_relevance_score(article_tags, keywords)
        
        assert score_summary > score_tags, \
            f"Summary score {score_summary} should be > tags score {score_tags}"
    
    # Feature: subscription-enhancement, Property 2: 关键词匹配正确性
    @given(
        keywords=keyword_list_strategy()
    )
    @settings(max_examples=100)
    def test_property_2_empty_article_gives_zero_score(self, keywords):
        """
        Property 2: 关键词匹配正确性 - 空文章
        **Validates: Requirements 3.3**
        
        An empty article should always have zero score
        """
        engine = KeywordPushEngine()
        article = Article()
        article.title = ""
        article.summary = ""
        article.content = ""
        article.tags = []
        
        score = engine.calculate_relevance_score(article, keywords)
        assert score == 0.0, f"Empty article should have score 0.0, got {score}"


class TestArticleSortingProperties:
    """Property-based tests for article sorting and truncation"""
    
    # Feature: subscription-enhancement, Property 3: 文章排序和截断正确性
    @given(
        articles=st.lists(article_strategy(), min_size=1, max_size=100),
        keywords=keyword_list_strategy()
    )
    @settings(max_examples=100)
    def test_property_3_matched_articles_sorted_by_relevance(self, articles, keywords):
        """
        Property 3: 文章排序和截断正确性 - 相关度排序
        **Validates: Requirements 3.9**
        
        Matched articles should be sorted by relevance score in descending order
        """
        engine = KeywordPushEngine()
        matched = engine.match_articles(keywords, articles)
        
        # Calculate scores for matched articles
        scores = [engine.calculate_relevance_score(article, keywords) for article in matched]
        
        # Verify descending order
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], \
                f"Articles not sorted by relevance: {scores[i]} < {scores[i + 1]}"
    
    # Feature: subscription-enhancement, Property 3: 文章排序和截断正确性
    @given(
        num_articles=st.integers(min_value=51, max_value=200),
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=50)
    def test_property_3_truncation_to_50_articles(self, num_articles, keyword):
        """
        Property 3: 文章排序和截断正确性 - 截断到50篇
        **Validates: Requirements 3.9**
        
        When matched articles exceed 50, only top 50 should be returned
        """
        engine = KeywordPushEngine()
        # Create articles that all match the keyword
        articles = []
        for i in range(num_articles):
            article = Article()
            article.id = i
            article.title = f"{keyword}文章{i}"
            article.summary = ""
            article.content = ""
            article.tags = []
            article.published_at = datetime.now() - timedelta(days=i)
            article.created_at = article.published_at
            articles.append(article)
        
        keywords = [keyword]
        matched = engine.match_articles(keywords, articles)
        
        # Should return exactly 50 articles
        assert len(matched) == 50, \
            f"Expected 50 articles, got {len(matched)} from {num_articles} matching articles"
    
    # Feature: subscription-enhancement, Property 3: 文章排序和截断正确性
    @given(
        num_articles=st.integers(min_value=1, max_value=49),
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=50)
    def test_property_3_no_truncation_under_50(self, num_articles, keyword):
        """
        Property 3: 文章排序和截断正确性 - 少于50篇不截断
        **Validates: Requirements 3.9**
        
        When matched articles are less than 50, all should be returned
        """
        engine = KeywordPushEngine()
        # Create articles that all match the keyword
        articles = []
        for i in range(num_articles):
            article = Article()
            article.id = i
            article.title = f"{keyword}文章{i}"
            article.summary = ""
            article.content = ""
            article.tags = []
            article.published_at = datetime.now() - timedelta(days=i)
            article.created_at = article.published_at
            articles.append(article)
        
        keywords = [keyword]
        matched = engine.match_articles(keywords, articles)
        
        # Should return all articles
        assert len(matched) == num_articles, \
            f"Expected {num_articles} articles, got {len(matched)}"
    
    # Feature: subscription-enhancement, Property 3: 文章排序和截断正确性
    @given(
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=100)
    def test_property_3_same_score_sorted_by_time(self, keyword):
        """
        Property 3: 文章排序和截断正确性 - 相同分数按时间排序
        **Validates: Requirements 3.9**
        
        Articles with same relevance score should be sorted by published_at descending
        """
        engine = KeywordPushEngine()
        # Create articles with same score (all in title)
        articles = []
        for i in range(10):
            article = Article()
            article.id = i
            article.title = keyword  # Same keyword = same score
            article.summary = ""
            article.content = ""
            article.tags = []
            # Different published times
            article.published_at = datetime.now() - timedelta(days=i)
            article.created_at = article.published_at
            articles.append(article)
        
        keywords = [keyword]
        matched = engine.match_articles(keywords, articles)
        
        # Verify sorted by time descending (newer first)
        for i in range(len(matched) - 1):
            assert matched[i].published_at >= matched[i + 1].published_at, \
                f"Articles with same score not sorted by time: {matched[i].published_at} < {matched[i + 1].published_at}"
    
    # Feature: subscription-enhancement, Property 3: 文章排序和截断正确性
    @given(
        num_articles=st.integers(min_value=60, max_value=100),
        keyword=st.text(min_size=2, max_size=10, alphabet='光伏风电储能')
    )
    @settings(max_examples=50)
    def test_property_3_top_50_are_most_relevant(self, num_articles, keyword):
        """
        Property 3: 文章排序和截断正确性 - 返回最相关的50篇
        **Validates: Requirements 3.9**
        
        The returned 50 articles should be the most relevant ones
        """
        engine = KeywordPushEngine()
        # Create articles with varying relevance
        articles = []
        for i in range(num_articles):
            article = Article()
            article.id = i
            # Vary the match location to create different scores
            if i < 20:
                article.title = keyword  # High score
                article.summary = ""
            elif i < 40:
                article.title = ""
                article.summary = keyword  # Medium score
            else:
                article.title = ""
                article.summary = ""
                article.tags = [keyword]  # Lower score
            article.content = ""
            article.published_at = datetime.now() - timedelta(days=i)
            article.created_at = article.published_at
            articles.append(article)
        
        keywords = [keyword]
        matched = engine.match_articles(keywords, articles)
        
        # Should return 50 articles
        assert len(matched) == 50
        
        # Calculate the minimum score in returned articles
        min_returned_score = min(
            engine.calculate_relevance_score(article, keywords) for article in matched
        )
        
        # All non-returned articles should have score <= min_returned_score
        returned_ids = {article.id for article in matched}
        for article in articles:
            if article.id not in returned_ids:
                score = engine.calculate_relevance_score(article, keywords)
                assert score <= min_returned_score, \
                    f"Non-returned article has higher score {score} than min returned {min_returned_score}"
