"""
短信内容截断的属性测试
使用 hypothesis 生成随机长度的内容，验证截断逻辑的正确性

**Validates: Requirements 6.13**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from app.services.sms_push_service import SMSPushService


class TestSMSTruncationProperty:
    """短信内容截断的属性测试类"""
    
    @pytest.fixture
    def sms_service(self, app):
        """创建短信推送服务实例"""
        with app.app_context():
            return SMSPushService(
                provider='aliyun',
                api_key='test_key',
                api_secret='test_secret'
            )
    
    # Property 6: 短信内容截断正确性
    @given(
        content=st.text(min_size=0, max_size=200),
        link=st.one_of(
            st.none(),
            st.text(min_size=10, max_size=50).map(lambda x: f"https://example.com/{x}")
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_sms_truncation_correctness(self, sms_service, content, link):
        """
        Property 6: 短信内容截断正确性
        
        **Validates: Requirements 6.13**
        
        测试内容:
        - 内容长度 ≤70字时发送完整内容
        - 内容长度 >70字时截断并附带链接
        - 使用 hypothesis 生成随机长度的内容
        """
        # 调用截断方法
        result, is_truncated = sms_service._truncate_content(content, link)
        
        # 属性1: 如果内容长度 ≤70字，应该返回完整内容，不截断
        if len(content) <= 70:
            assert result == content, f"内容长度≤70字时应返回完整内容，但实际返回: {result}"
            assert is_truncated is False, "内容长度≤70字时is_truncated应为False"
        
        # 属性2: 如果内容长度 >70字，应该截断
        if len(content) > 70:
            assert is_truncated is True, "内容长度>70字时is_truncated应为True"
            
            # 截断后的内容应该以"..."结尾
            assert "..." in result, "截断后的内容应包含'...'"
            
            # 如果提供了链接，截断后的内容应该包含链接
            if link:
                assert link in result, f"截断后的内容应包含链接: {link}"
            
            # 截断后的内容前67个字符应该是原内容的前67个字符
            truncated_prefix = result.split("...")[0]
            assert content.startswith(truncated_prefix), "截断后的内容前缀应该匹配原内容"
            
            # 截断的长度应该是67个字符（不包括"..."和链接）
            content_before_ellipsis = result.split("...")[0]
            assert len(content_before_ellipsis) == 67, f"截断长度应为67字符，实际为{len(content_before_ellipsis)}"
    
    @given(content_length=st.integers(min_value=0, max_value=200))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_truncation_boundary(self, sms_service, content_length):
        """
        测试截断边界条件
        
        **Validates: Requirements 6.13**
        
        验证在70字边界附近的行为
        """
        # 生成指定长度的内容
        content = "A" * content_length
        link = "https://example.com/article/123"
        
        result, is_truncated = sms_service._truncate_content(content, link)
        
        # 边界条件: 恰好70字
        if content_length == 70:
            assert result == content
            assert is_truncated is False
        
        # 边界条件: 69字（小于70）
        if content_length < 70:
            assert result == content
            assert is_truncated is False
        
        # 边界条件: 71字（大于70）
        if content_length > 70:
            assert is_truncated is True
            assert "..." in result
            if link:
                assert link in result
    
    @given(
        content=st.text(min_size=71, max_size=200),
        link=st.text(min_size=10, max_size=50).map(lambda x: f"https://example.com/{x}")
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_truncation_with_link(self, sms_service, content, link):
        """
        测试超长内容截断时链接的正确附加
        
        **Validates: Requirements 6.13**
        
        验证当内容>70字且提供链接时，链接被正确附加
        """
        # 确保内容长度>70
        assume(len(content) > 70)
        
        result, is_truncated = sms_service._truncate_content(content, link)
        
        # 应该被截断
        assert is_truncated is True
        
        # 结果应该包含"..."
        assert "..." in result
        
        # 结果应该包含链接
        assert link in result
        
        # 链接应该在"..."之后
        ellipsis_index = result.index("...")
        link_index = result.index(link)
        assert link_index > ellipsis_index, "链接应该在'...'之后"
        
        # 验证格式: "前67字...查看完整内容: {link}"
        expected_prefix = content[:67] + "..."
        assert result.startswith(expected_prefix), f"截断格式不正确，期望以'{expected_prefix}'开头"
    
    @given(content=st.text(min_size=0, max_size=70))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_no_truncation_for_short_content(self, sms_service, content):
        """
        测试短内容不被截断
        
        **Validates: Requirements 6.13**
        
        验证当内容≤70字时，无论是否提供链接，都不截断
        """
        # 确保内容长度≤70
        assume(len(content) <= 70)
        
        # 测试不提供链接的情况
        result_no_link, is_truncated_no_link = sms_service._truncate_content(content, None)
        assert result_no_link == content
        assert is_truncated_no_link is False
        
        # 测试提供链接的情况
        link = "https://example.com/article/123"
        result_with_link, is_truncated_with_link = sms_service._truncate_content(content, link)
        assert result_with_link == content
        assert is_truncated_with_link is False
        
        # 短内容不应该包含链接（即使提供了链接）
        assert link not in result_with_link
    
    @given(
        content=st.text(min_size=71, max_size=200)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_truncation_without_link(self, sms_service, content):
        """
        测试超长内容截断时不提供链接的情况
        
        **Validates: Requirements 6.13**
        
        验证当内容>70字但不提供链接时，只截断不附加链接
        """
        # 确保内容长度>70
        assume(len(content) > 70)
        
        result, is_truncated = sms_service._truncate_content(content, None)
        
        # 应该被截断
        assert is_truncated is True
        
        # 结果应该包含"..."
        assert result.endswith("...")
        
        # 结果应该是前67字+"..."
        expected = content[:67] + "..."
        assert result == expected, f"期望: {expected}, 实际: {result}"
        
        # 结果长度应该是70字
        assert len(result) == 70, f"截断后长度应为70字，实际为{len(result)}"
    
    @given(
        chinese_chars=st.integers(min_value=0, max_value=100),
        english_chars=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_mixed_language_truncation(self, sms_service, chinese_chars, english_chars):
        """
        测试中英文混合内容的截断
        
        **Validates: Requirements 6.13**
        
        验证中英文混合内容的字符计数和截断逻辑
        """
        # 生成中英文混合内容
        content = "中" * chinese_chars + "A" * english_chars
        total_length = chinese_chars + english_chars
        
        result, is_truncated = sms_service._truncate_content(content)
        
        # 验证截断逻辑
        if total_length <= 70:
            assert result == content
            assert is_truncated is False
        else:
            assert is_truncated is True
            assert "..." in result
            # 截断后的内容（不包括"..."）应该是67个字符
            content_before_ellipsis = result.replace("...", "")
            assert len(content_before_ellipsis) == 67
    
    @given(
        content=st.text(min_size=71, max_size=200),
        link=st.one_of(st.none(), st.just(""))
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_empty_link_handling(self, sms_service, content, link):
        """
        测试空链接或None链接的处理
        
        **Validates: Requirements 6.13**
        
        验证当链接为空或None时，截断逻辑仍然正确
        """
        # 确保内容长度>70
        assume(len(content) > 70)
        
        result, is_truncated = sms_service._truncate_content(content, link)
        
        # 应该被截断
        assert is_truncated is True
        
        # 结果应该是前67字+"..."
        expected = content[:67] + "..."
        
        # 如果链接为空字符串，不应该附加
        if link == "":
            assert result == expected
        # 如果链接为None，不应该附加
        elif link is None:
            assert result == expected
    
    @given(content=st.text(min_size=0, max_size=200))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_idempotence(self, sms_service, content):
        """
        测试截断操作的幂等性
        
        **Validates: Requirements 6.13**
        
        验证对同一内容多次调用截断方法，结果应该一致
        """
        link = "https://example.com/article/123"
        
        # 第一次调用
        result1, is_truncated1 = sms_service._truncate_content(content, link)
        
        # 第二次调用
        result2, is_truncated2 = sms_service._truncate_content(content, link)
        
        # 结果应该完全一致
        assert result1 == result2, "多次调用截断方法应返回相同结果"
        assert is_truncated1 == is_truncated2, "多次调用截断方法应返回相同的截断标志"
    
    @given(
        content=st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=0, max_size=200)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_unicode_handling(self, sms_service, content):
        """
        测试Unicode字符的正确处理
        
        **Validates: Requirements 6.13**
        
        验证包含各种Unicode字符（emoji、特殊符号等）的内容能正确截断
        """
        link = "https://example.com/article/123"
        
        result, is_truncated = sms_service._truncate_content(content, link)
        
        # 基本截断逻辑应该正确
        if len(content) <= 70:
            assert result == content
            assert is_truncated is False
        else:
            assert is_truncated is True
            assert "..." in result
            
            # 截断后的内容应该是有效的字符串
            assert isinstance(result, str)
            
            # 不应该出现字符串编码错误
            try:
                result.encode('utf-8')
            except UnicodeEncodeError:
                pytest.fail("截断后的内容包含无效的Unicode字符")
