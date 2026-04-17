"""
智能内容提取工具
使用 trafilatura 库提取网页正文内容,过滤导航栏、侧边栏、广告等无关内容
"""
import trafilatura
from trafilatura.settings import use_config
import logging

logger = logging.getLogger(__name__)


class ContentExtractor:
    """智能内容提取器"""
    
    def __init__(self):
        """初始化提取器配置"""
        # 创建自定义配置
        self.config = use_config()
        # 设置提取选项
        self.config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
        
    def extract_content(self, html, url=None):
        """
        从HTML中提取正文内容
        
        Args:
            html: HTML字符串或响应对象
            url: 页面URL(可选,用于改进提取效果)
            
        Returns:
            dict: 包含提取结果的字典
                - content: 正文内容(Markdown格式)
                - title: 标题(如果能提取到)
                - author: 作者(如果能提取到)
                - date: 发布日期(如果能提取到)
                - success: 是否成功提取
        """
        try:
            # 如果传入的是Scrapy Response对象,获取其body
            if hasattr(html, 'body'):
                html_text = html.body.decode('utf-8', errors='ignore')
            elif isinstance(html, bytes):
                html_text = html.decode('utf-8', errors='ignore')
            else:
                html_text = str(html)
            
            # 使用trafilatura提取内容
            # include_comments=False: 不包含评论
            # include_tables=True: 包含表格(可能包含重要数据)
            # include_links=False: 不包含链接
            # no_fallback=False: 如果主要方法失败,使用备用方法
            # output_format='markdown': 输出Markdown格式
            extracted = trafilatura.extract(
                html_text,
                url=url,
                include_comments=False,
                include_tables=True,
                include_links=False,  # 关键: 不包含链接
                no_fallback=False,
                config=self.config,
                output_format='markdown',  # 输出Markdown格式
                with_metadata=True,   # 包含元数据
            )
            
            if not extracted:
                logger.warning(f"trafilatura无法提取内容: {url}")
                return {
                    'content': '',
                    'title': None,
                    'author': None,
                    'date': None,
                    'success': False
                }
            
            # 如果with_metadata=True,返回的是字典
            if isinstance(extracted, dict):
                content = extracted.get('text', '')
                title = extracted.get('title')
                author = extracted.get('author')
                date = extracted.get('date')
            else:
                # 如果是字符串,只有内容
                content = extracted
                title = None
                author = None
                date = None
            
            # 清理内容(移除链接和无关文本)
            content = self._clean_content(content)
            
            success = len(content) > 100  # 至少100字符才算成功
            
            if success:
                logger.info(f"✅ 成功提取内容: {len(content)} 字符")
            else:
                logger.warning(f"⚠️  提取的内容太短: {len(content)} 字符")
            
            return {
                'content': content,
                'title': title,
                'author': author,
                'date': date,
                'success': success
            }
            
        except Exception as e:
            logger.error(f"内容提取失败: {str(e)}")
            return {
                'content': '',
                'title': None,
                'author': None,
                'date': None,
                'success': False
            }
    
    def _clean_content(self, content):
        """
        清理提取的内容
        
        Args:
            content: 原始内容
            
        Returns:
            str: 清理后的内容
        """
        if not content:
            return ''
        
        import re
        
        # 1. 移除所有链接
        # 移除 Markdown 格式的链接 [text](url)
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # 移除 HTML 链接 <a href="...">text</a>
        content = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', content)
        
        # 移除纯URL (http://, https://, www.)
        content = re.sub(r'https?://[^\s]+', '', content)
        content = re.sub(r'www\.[^\s]+', '', content)
        
        # 2. 移除 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 3. 移除图片标记
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        
        # 4. 移除多余的空行
        lines = content.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            line = line.strip()
            
            # 跳过太短的行(可能是导航或无关内容)
            if len(line) < 5:
                if not prev_empty:
                    cleaned_lines.append('')
                    prev_empty = True
                continue
            
            # 过滤常见的导航和无关文本
            skip_patterns = [
                '首页', '返回', '上一页', '下一页', '更多',
                '关于我们', '联系我们', '版权所有', '备案号',
                '分享到', '收藏', '打印', '字号', '网站地图',
                'Copyright', '©', 'ICP', 'href=', 'src=',
                '主管', '主办', '有限公司',  # 版权信息
            ]
            
            if any(pattern in line for pattern in skip_patterns) and len(line) < 50:
                continue
            
            # 跳过包含链接残留的行
            if 'http' in line.lower() or 'www.' in line.lower():
                continue
            
            cleaned_lines.append(line)
            prev_empty = False
        
        # 合并清理后的内容
        content = '\n\n'.join(cleaned_lines)
        
        # 移除开头和结尾的空行
        content = content.strip()
        
        # 移除多余的空格
        content = re.sub(r' +', ' ', content)
        
        return content
    
    def extract_with_fallback(self, response, css_selectors=None):
        """
        使用trafilatura提取内容,如果失败则回退到CSS选择器
        
        Args:
            response: Scrapy Response对象
            css_selectors: CSS选择器列表(备用方案)
            
        Returns:
            dict: 提取结果
        """
        # 首先尝试使用trafilatura
        result = self.extract_content(response, url=response.url)
        
        if result['success']:
            return result
        
        # 如果trafilatura失败,尝试使用CSS选择器
        if css_selectors:
            logger.info("trafilatura失败,尝试使用CSS选择器")
            content_parts = []
            
            for selector in css_selectors:
                parts = response.css(selector).getall()
                if parts and len(parts) > 2:
                    content_parts = parts
                    logger.info(f'使用选择器 "{selector}" 提取到 {len(parts)} 段内容')
                    break
            
            if content_parts:
                content = '\n\n'.join([p.strip() for p in content_parts if p.strip() and len(p.strip()) > 10])
                content = self._clean_content(content)
                
                return {
                    'content': content,
                    'title': None,
                    'author': None,
                    'date': None,
                    'success': len(content) > 100
                }
        
        # 都失败了
        return result


# 创建全局实例
extractor = ContentExtractor()
