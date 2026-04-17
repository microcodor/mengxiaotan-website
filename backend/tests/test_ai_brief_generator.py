"""
AI简报生成器集成测试
使用mock避免实际API调用
"""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.models import Article, DailyBrief, Subscription, SubscriptionPlan, User
from app.services.ai_brief_generator import AIBriefGenerator


@pytest.fixture
def generator():
    """创建AI简报生成器实例"""
    return AIBriefGenerator(
        api_key='test_api_key',
        group_id='test_group_id',
        api_url='https://api.minimax.chat/v1/test'
    )


@pytest.fixture
def sample_articles(app, db_session):
    """创建测试文章"""
    with app.app_context():
        articles = []
        categories = ['ndrc', 'coal', 'power', 'new_energy']
        
        target_date = date.today() - timedelta(days=1)
        published_at = datetime.combine(target_date, datetime.min.time())
        
        for i in range(30):
            article = Article(
                title=f'测试文章 {i+1}',
                summary=f'这是测试文章 {i+1} 的摘要',
                content=f'这是测试文章 {i+1} 的内容',
                source='测试来源',
                source_url=f'http://test.com/article/{i+1}',
                category=categories[i % 4],
                tags=['测试', '能源'],
                view_count=100 - i,
                like_count=50 - i,
                is_reviewed=True,
                published_at=published_at + timedelta(hours=i)
            )
            db_session.add(article)
            articles.append(article)
        
        db_session.commit()
        return articles


class TestAIBriefGenerator:
    """AI简报生成器测试"""
    
    def test_collect_articles(self, app, generator, sample_articles):
        """测试文章收集功能"""
        with app.app_context():
            target_date = date.today() - timedelta(days=1)
            articles = generator.collect_articles(target_date, limit=30)
            
            # 验证返回30篇文章
            assert len(articles) == 30
            
            # 验证按浏览量+点赞数排序（降序）
            for i in range(len(articles) - 1):
                score1 = articles[i].view_count + articles[i].like_count
                score2 = articles[i+1].view_count + articles[i+1].like_count
                assert score1 >= score2
    
    def test_collect_articles_empty(self, app, generator):
        """测试没有文章时的收集功能"""
        with app.app_context():
            target_date = date.today() - timedelta(days=10)
            articles = generator.collect_articles(target_date, limit=30)
            
            # 验证返回空列表
            assert len(articles) == 0
    
    @patch('requests.post')
    def test_call_minimax_api_success(self, mock_post, generator):
        """测试MiniMax API调用成功"""
        # Mock API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': '这是AI生成的简报内容'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # 调用API
        result = generator.call_minimax_api('测试prompt')
        
        # 验证结果
        assert result == '这是AI生成的简报内容'
        assert mock_post.called
    
    @patch('requests.post')
    def test_call_minimax_api_failure(self, mock_post, generator):
        """测试MiniMax API调用失败"""
        # Mock API失败响应
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        # 调用API
        result = generator.call_minimax_api('测试prompt')
        
        # 验证返回None
        assert result is None
    
    @patch('requests.post')
    def test_call_minimax_api_timeout(self, mock_post, generator):
        """测试MiniMax API超时"""
        import requests
        
        # Mock超时异常
        mock_post.side_effect = requests.exceptions.Timeout()
        
        # 调用API
        result = generator.call_minimax_api('测试prompt')
        
        # 验证返回None
        assert result is None
    
    def test_format_brief_content(self, app, generator, sample_articles):
        """测试简报内容格式化"""
        with app.app_context():
            ai_response = '这是AI生成的简报内容，包含行业热点、政策解读和市场趋势分析。'
            
            # 格式化内容
            brief_content = generator.format_brief_content(sample_articles[:10], ai_response)
            
            # 验证结构
            assert 'content' in brief_content
            assert 'ai_summary' in brief_content
            assert 'generated_at' in brief_content
            assert 'article_count' in brief_content
            
            # 验证分类
            assert 'ndrc' in brief_content['content']
            assert 'coal' in brief_content['content']
            assert 'power' in brief_content['content']
            assert 'new_energy' in brief_content['content']
            
            # 验证文章数量
            assert brief_content['article_count'] == 10
    
    def test_format_brief_content_long_summary(self, app, generator, sample_articles):
        """测试简报内容格式化（超长摘要截断）"""
        with app.app_context():
            # 创建超过1000字的AI响应
            ai_response = '测试' * 600  # 1200字
            
            # 格式化内容
            brief_content = generator.format_brief_content(sample_articles[:10], ai_response)
            
            # 验证摘要被截断到1000字
            assert len(brief_content['ai_summary']) == 1000
    
    @patch.object(AIBriefGenerator, 'call_minimax_api')
    @patch.object(AIBriefGenerator, 'collect_articles')
    def test_generate_daily_brief_success(self, mock_collect, mock_api, app, generator, sample_articles):
        """测试简报生成成功"""
        with app.app_context():
            # Mock方法
            mock_collect.return_value = sample_articles[:30]
            mock_api.return_value = '这是AI生成的简报内容'
            
            # 生成简报
            target_date = date.today() - timedelta(days=1)
            result = generator.generate_daily_brief(target_date)
            
            # 验证结果
            assert result is not None
            assert 'brief_id' in result
            assert 'content' in result
            assert 'ai_suggestion' in result
            assert 'generated_at' in result
            assert result['status'] == 'created'
            
            # 验证数据库记录
            brief = DailyBrief.query.get(result['brief_id'])
            assert brief is not None
            assert brief.brief_date == target_date
    
    @patch.object(AIBriefGenerator, 'call_minimax_api')
    @patch.object(AIBriefGenerator, 'collect_articles')
    def test_generate_daily_brief_existing(self, mock_collect, mock_api, app, generator, sample_articles, db_session):
        """测试简报已存在时的处理"""
        with app.app_context():
            target_date = date.today() - timedelta(days=1)
            
            # 创建已存在的简报
            existing_brief = DailyBrief(
                brief_date=target_date,
                content={'test': 'data'},
                ai_suggestion='测试建议',
                generated_at=datetime.utcnow()
            )
            db_session.add(existing_brief)
            db_session.commit()
            
            # 尝试生成简报
            result = generator.generate_daily_brief(target_date)
            
            # 验证返回已存在的简报
            assert result is not None
            assert result['status'] == 'existing'
            assert result['brief_id'] == existing_brief.id
    
    @patch.object(AIBriefGenerator, 'call_minimax_api')
    @patch.object(AIBriefGenerator, 'collect_articles')
    def test_generate_daily_brief_no_articles(self, mock_collect, mock_api, app, generator):
        """测试没有文章时的简报生成"""
        with app.app_context():
            # Mock返回空列表
            mock_collect.return_value = []
            
            # 生成简报
            target_date = date.today() - timedelta(days=1)
            result = generator.generate_daily_brief(target_date)
            
            # 验证返回None
            assert result is None
    
    @patch.object(AIBriefGenerator, 'call_minimax_api')
    @patch.object(AIBriefGenerator, 'collect_articles')
    def test_generate_daily_brief_api_failure_with_retry(self, mock_collect, mock_api, app, generator, sample_articles):
        """测试API失败时的重试机制"""
        with app.app_context():
            # Mock方法
            mock_collect.return_value = sample_articles[:30]
            mock_api.return_value = None  # API失败
            
            # 生成简报
            target_date = date.today() - timedelta(days=1)
            result = generator.generate_daily_brief(target_date)
            
            # 第一次失败应返回None以便重试
            assert result is None
            assert generator.retry_count == 1
    
    @patch.object(AIBriefGenerator, 'call_minimax_api')
    @patch.object(AIBriefGenerator, 'collect_articles')
    def test_generate_daily_brief_max_retries(self, mock_collect, mock_api, app, generator, sample_articles):
        """测试达到最大重试次数后使用默认简报"""
        with app.app_context():
            # Mock方法
            mock_collect.return_value = sample_articles[:30]
            mock_api.return_value = None  # API失败
            
            # 设置重试次数为最大值
            generator.retry_count = 3
            
            # 生成简报
            target_date = date.today() - timedelta(days=1)
            result = generator.generate_daily_brief(target_date)
            
            # 应该使用默认简报
            assert result is not None
            assert 'brief_id' in result
            # 验证使用了默认简报内容
            brief = DailyBrief.query.get(result['brief_id'])
            assert '今日共收集到' in brief.content['ai_summary']
    
    def test_extract_ai_suggestion(self, generator):
        """测试提取AI决策建议"""
        ai_response = """
        行业热点：光伏产业持续增长
        
        政策解读：新能源补贴政策出台
        
        市场趋势：储能市场快速发展
        
        决策建议：建议关注光伏产业链上游硅料价格走势，预计未来一周将有所回落。
        """
        
        suggestion = generator._extract_ai_suggestion(ai_response)
        
        # 验证提取到建议
        assert '建议关注光伏产业链' in suggestion
        assert len(suggestion) <= 200
    
    def test_extract_ai_suggestion_no_suggestion(self, generator):
        """测试没有决策建议时的提取"""
        ai_response = "这是一段没有决策建议的内容"
        
        suggestion = generator._extract_ai_suggestion(ai_response)
        
        # 验证返回空字符串
        assert suggestion == ""
    
    def test_generate_default_brief(self, app, generator, sample_articles):
        """测试生成默认简报"""
        with app.app_context():
            default_brief = generator._generate_default_brief(sample_articles[:30])
            
            # 验证包含文章数量
            assert '30 篇' in default_brief
            
            # 验证包含分类统计
            assert '发改委动态' in default_brief or '煤炭行业' in default_brief
    
    def test_build_prompt(self, app, generator, sample_articles):
        """测试构造Prompt"""
        with app.app_context():
            prompt = generator._build_prompt(sample_articles[:10])
            
            # 验证Prompt包含必要元素
            assert '资深的能源行业分析师' in prompt
            assert '行业热点' in prompt
            assert '政策解读' in prompt
            assert '市场趋势' in prompt
            assert '决策建议' in prompt
            
            # 验证包含文章信息
            assert '测试文章' in prompt
    
    @patch('app.services.push_service.push_manager')
    def test_push_brief_to_users(self, mock_push_manager, app, generator, db_session):
        """测试推送简报给用户"""
        with app.app_context():
            # 创建测试数据
            # 创建订阅套餐
            standard_plan = SubscriptionPlan(
                name='标准版',
                price=299,
                duration_days=365,
                features={}
            )
            premium_plan = SubscriptionPlan(
                name='高级版',
                price=599,
                duration_days=365,
                features={}
            )
            db_session.add(standard_plan)
            db_session.add(premium_plan)
            db_session.commit()
            
            # 创建用户和订阅
            user1 = User(phone='13800000001', nickname='用户1', role='user')
            user2 = User(phone='13800000002', nickname='用户2', role='user')
            db_session.add(user1)
            db_session.add(user2)
            db_session.commit()
            
            sub1 = Subscription(
                user_id=user1.id,
                plan_id=standard_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            sub2 = Subscription(
                user_id=user2.id,
                plan_id=premium_plan.id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status='active'
            )
            db_session.add(sub1)
            db_session.add(sub2)
            db_session.commit()
            
            # 创建简报
            brief = DailyBrief(
                brief_date=date.today() - timedelta(days=1),
                content={'ai_summary': '测试简报内容'},
                ai_suggestion='测试建议',
                generated_at=datetime.utcnow()
            )
            db_session.add(brief)
            db_session.commit()
            
            # Mock推送管理器
            mock_push_manager.send_to_user.return_value = {'wechat_work': True}
            
            # 推送简报
            result = generator.push_brief_to_users(brief.id)
            
            # 验证推送结果
            assert 'standard' in result
            assert 'premium' in result
            assert result['standard']['sent'] == 1
            assert result['premium']['sent'] == 1
    
    @patch('app.services.push_service.push_manager')
    def test_push_brief_no_users(self, mock_push_manager, app, generator, db_session):
        """测试没有订阅用户时的推送"""
        with app.app_context():
            # 创建简报
            brief = DailyBrief(
                brief_date=date.today() - timedelta(days=1),
                content={'ai_summary': '测试简报内容'},
                ai_suggestion='测试建议',
                generated_at=datetime.utcnow()
            )
            db_session.add(brief)
            db_session.commit()
            
            # 推送简报
            result = generator.push_brief_to_users(brief.id)
            
            # 验证返回消息
            assert 'message' in result
            assert result['sent'] == 0
    
    def test_format_brief_for_push_with_suggestion(self, app, generator, db_session):
        """测试格式化简报用于推送（包含建议）"""
        with app.app_context():
            brief = DailyBrief(
                brief_date=date.today() - timedelta(days=1),
                content={'ai_summary': '测试简报内容'},
                ai_suggestion='测试决策建议',
                generated_at=datetime.utcnow()
            )
            db_session.add(brief)
            db_session.commit()
            
            # 格式化（包含建议）
            markdown = generator._format_brief_for_push(brief, include_suggestion=True)
            
            # 验证包含建议
            assert '决策建议' in markdown
            assert '测试决策建议' in markdown
    
    def test_format_brief_for_push_without_suggestion(self, app, generator, db_session):
        """测试格式化简报用于推送（不包含建议）"""
        with app.app_context():
            brief = DailyBrief(
                brief_date=date.today() - timedelta(days=1),
                content={'ai_summary': '测试简报内容'},
                ai_suggestion='测试决策建议',
                generated_at=datetime.utcnow()
            )
            db_session.add(brief)
            db_session.commit()
            
            # 格式化（不包含建议）
            markdown = generator._format_brief_for_push(brief, include_suggestion=False)
            
            # 验证不包含建议
            assert '决策建议' not in markdown
            assert '测试决策建议' not in markdown
