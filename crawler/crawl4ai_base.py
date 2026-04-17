"""
Crawl4AI爬虫基类
提供通用的爬取和保存功能
"""
import asyncio
import sys
import re
from datetime import datetime, date
from pathlib import Path
import pytz

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import JsonCssExtractionStrategy
import pymysql
import json

class Crawl4AIBase:
    """Crawl4AI爬虫基类"""
    
    def __init__(self, source_name, base_url, category='energy', date_filter='today'):
        self.source_name = source_name
        self.base_url = base_url
        self.category = category
        self.date_filter = date_filter  # 'today', 'this_month', 'all'
        
        # 中国时区
        self.china_tz = pytz.timezone('Asia/Shanghai')
        
        # 数据库配置
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'jinchun123',
            'database': 'energy_station',
            'charset': 'utf8mb4'
        }
        
        # 子类需要实现的配置
        self.list_schema = None  # 列表页CSS选择器配置
        self.detail_schema = None  # 详情页CSS选择器配置
    
    def get_today_date(self):
        """获取今天的日期（中国时区）"""
        return datetime.now(self.china_tz).date()
    
    def extract_date_from_content(self, content, title=''):
        """从内容中提取发布日期"""
        if not content:
            return None
        
        # 合并标题和内容前2000字符用于日期提取
        text = (title + '\n' + content[:2000])
        
        today = self.get_today_date()
        
        # 日期格式模式（按优先级排序）
        date_patterns = [
            # ISO格式: 2026-04-16
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 中文格式: 2026年04月16日
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 斜杠格式: 2026/04/16
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 点号格式: 2026.04.16
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
            
            # 今天、今日
            (r'今[天日]', lambda m: today),
            
            # 时间戳格式: 2026-04-16 10:30:00
            (r'(\d{4})-(\d{1,2})-(\d{1,2})\s+\d{1,2}:\d{1,2}', lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        ]
        
        # 尝试匹配各种日期格式
        for pattern, converter in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    extracted_date = converter(match)
                    # 验证日期是否合理（不能是未来日期，不能太久远）
                    if extracted_date <= today and (today - extracted_date).days < 365:
                        return extracted_date
                except (ValueError, AttributeError):
                    continue
        
        return None
    
    def is_today_article(self, content, title=''):
        """检查是否是今天的文章"""
        extracted_date = self.extract_date_from_content(content, title)
        today = self.get_today_date()
        
        if extracted_date:
            # 根据date_filter判断
            if self.date_filter == 'all':
                return True, extracted_date
            elif self.date_filter == 'this_month':
                # 检查是否是本月
                is_this_month = (extracted_date.year == today.year and 
                                extracted_date.month == today.month)
                return is_this_month, extracted_date
            else:  # 'today'
                is_today = extracted_date == today
                return is_today, extracted_date
        
        # 如果无法提取日期，返回None表示不确定
        return None, None
    
    def get_list_schema(self):
        """获取列表页选择器配置（子类可覆盖）"""
        return self.list_schema
    
    def get_detail_schema(self):
        """获取详情页选择器配置（子类可覆盖）"""
        return self.detail_schema
    
    def process_url(self, url):
        """处理URL，补全相对路径（子类可覆盖）"""
        if not url:
            return None
        
        # 如果是完整URL，直接返回
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        # 如果是相对路径，补全
        if url.startswith('/'):
            # 提取base_url的域名部分
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        
        # 其他情况，拼接base_url
        return self.base_url.rstrip('/') + '/' + url.lstrip('/')
    
    def is_valid_article_content(self, content, url='', title=''):
        """验证文章内容是否有效"""
        if not content or len(content) < 100:
            return False, "内容太短"
        
        # 检查是否是404页面
        if 'HTTP Status 404' in content[:500]:
            return False, "404页面(HTTP Status 404)"
        
        if '404' in content[:500] and ('not found' in content[:500].lower() or '找不到' in content[:500]):
            return False, "404页面"
        
        if '页面不存在' in content[:500] or '页面未找到' in content[:500]:
            return False, "404页面"
        
        # 检查是否是反爬验证页面
        anti_bot_keywords = [
            '验证码', '人机验证', '安全验证', '滑动验证',
            'Access Denied', 'Forbidden', 'blocked',
            'captcha', 'CAPTCHA', 'robot check',
            '请完成安全验证', '请输入验证码',
            '访问被拒绝', '访问受限'
        ]
        
        check_text = content[:1000]  # 检查前1000字符
        for keyword in anti_bot_keywords:
            if keyword in check_text:
                return False, f"反爬验证页面({keyword})"
        
        # 检查是否是非详情页（列表页、导航页等）
        # 只检查标题，不检查内容（因为导航栏会出现在内容中）
        non_article_title_keywords = [
            '交易数据', '市场动态', '行情中心', '数据中心',
            '政策规则', '平台公告', '企业报荟萃',
            '首页', '登录', '注册', '搜索结果'
        ]
        
        # 只检查标题
        title_lower = title.lower()
        for keyword in non_article_title_keywords:
            if keyword in title_lower:
                return False, f"非详情页({keyword})"
        
        # 特殊检查：如果标题就是"关于我们"、"联系我们"、"网站地图"，则判定为非详情页
        if title in ['关于我们', '联系我们', '网站地图', 'About Us', 'Contact Us', 'Site Map']:
            return False, f"非详情页({title})"
        
        # 检查URL是否包含非文章路径
        non_article_paths = [
            '/data/', '/market/', '/trade/', '/about/', 
            '/contact/', '/search/', '/login/', '/register/'
        ]
        for path in non_article_paths:
            if path in url.lower():
                return False, f"非文章URL({path})"
        
        # 检查是否全是链接（内容主要是URL）
        # 统计http/https出现的次数
        http_count = content.count('http://') + content.count('https://')
        content_length = len(content)
        
        # 如果内容较短且包含大量链接，可能是导航页
        if content_length < 2000 and http_count > 10:
            return False, f"内容主要是链接({http_count}个链接)"
        
        # 如果链接密度过高（每100字符超过1.5个链接）
        # 放宽限制，因为有些网站导航栏链接很多
        if content_length > 0 and (http_count / content_length * 100) > 1.5:
            return False, f"链接密度过高({http_count}个链接/{content_length}字符)"
        
        return True, "有效"
    
    def extract_from_markdown(self, result):
        """从Markdown提取链接（备用方案）"""
        articles = []
        
        if not result.markdown or not result.links:
            return articles
        
        # 从内部链接中提取
        for link in result.links.get('internal', []):
            href = link.get('href', '')
            text = link.get('text', '')
            
            # 过滤无效链接
            if not href or not text:
                continue
            
            # 过滤导航链接
            if any(skip in href.lower() for skip in ['javascript:', '#', 'mailto:', '.css', '.js', '.jpg', '.png']):
                continue
            
            # 过滤非文章链接
            if any(skip in href.lower() for skip in ['/data/', '/market/', '/trade/', '/about/', '/contact/']):
                continue
            
            articles.append({
                'title': text.strip(),
                'url': href,
                'published_date': None
            })
        
        return articles
    
    async def crawl(self, max_articles=10, date_filter='today'):
        """执行爬取
        
        Args:
            max_articles: 最大文章数
            date_filter: 日期过滤 ('today', 'this_month', 'all')
        """
        self.date_filter = date_filter  # 保存日期过滤设置
        print(f"\n{'='*60}")
        print(f"🚀 开始爬取 {self.source_name}")
        print(f"📍 URL: {self.base_url}")
        print(f"{'='*60}\n")
        
        # 配置浏览器 - 添加反爬虫绕过参数
        browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            verbose=False,
            # 添加User-Agent和其他反爬虫绕过参数
            extra_args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ],
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # 第1步：爬取列表页
                articles = await self.crawl_list_page(crawler)
                
                if not articles:
                    print("❌ 未找到任何文章链接")
                    return 0
                
                print(f"\n✅ 找到 {len(articles)} 篇文章")
                
                # 第2步：爬取详情页
                saved_count = await self.crawl_article_details(crawler, articles[:max_articles])
                
                print(f"\n{'='*60}")
                print(f"📊 爬取完成")
                print(f"✅ 新增文章: {saved_count} 篇")
                print(f"{'='*60}\n")
                
                return saved_count
                
        except Exception as e:
            print(f"❌ 爬取过程出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    async def crawl_list_page(self, crawler):
        """爬取列表页"""
        print("📋 步骤1: 爬取列表页...")
        
        # 获取列表页选择器配置
        list_schema = self.get_list_schema()
        
        if list_schema:
            # 使用CSS选择器提取
            extraction_strategy = JsonCssExtractionStrategy(list_schema, verbose=False)
            run_config = CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                cache_mode=CacheMode.BYPASS,
                wait_until="domcontentloaded",
                page_timeout=60000,
                delay_before_return_html=2.0,
            )
        else:
            # 不使用提取策略，直接获取Markdown
            run_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="domcontentloaded",
                page_timeout=60000,
                delay_before_return_html=2.0,
            )
        
        result = await crawler.arun(url=self.base_url, config=run_config)
        
        if not result.success:
            print(f"❌ 列表页加载失败: {result.error_message}")
            return []
        
        print(f"✅ 列表页加载成功")
        
        articles = []
        
        # 尝试从CSS选择器提取
        if result.extracted_content:
            try:
                articles = json.loads(result.extracted_content)
                print(f"📊 CSS选择器提取到 {len(articles)} 个链接")
            except json.JSONDecodeError:
                print("⚠️  CSS选择器提取失败，尝试Markdown方案")
        
        # 如果CSS提取失败，尝试从Markdown提取
        if not articles:
            articles = self.extract_from_markdown(result)
            print(f"📊 Markdown提取到 {len(articles)} 个链接")
        
        # 处理URL
        valid_articles = []
        for article in articles:
            if article.get('title') and article.get('url'):
                article['url'] = self.process_url(article['url'])
                if article['url']:
                    valid_articles.append(article)
        
        print(f"✅ 有效文章: {len(valid_articles)} 篇")
        
        return valid_articles
    
    async def crawl_article_details(self, crawler, articles):
        """爬取文章详细内容"""
        print(f"\n📖 步骤2: 爬取文章详情...")
        
        saved_count = 0
        total = len(articles)
        
        for i, article in enumerate(articles, 1):
            try:
                print(f"\n[{i}/{total}] {article['title'][:50]}...")
                
                # 获取详情页选择器配置
                detail_schema = self.get_detail_schema()
                
                if detail_schema:
                    # 使用CSS选择器提取
                    detail_strategy = JsonCssExtractionStrategy(detail_schema, verbose=False)
                    detail_config = CrawlerRunConfig(
                        extraction_strategy=detail_strategy,
                        cache_mode=CacheMode.BYPASS,
                        page_timeout=30000,
                        delay_before_return_html=1.0,
                    )
                else:
                    # 使用Markdown提取
                    detail_config = CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        page_timeout=30000,
                        delay_before_return_html=1.0,
                    )
                
                result = await crawler.arun(url=article['url'], config=detail_config)
                
                # 尝试提取内容（即使success为False也尝试）
                content_extracted = False
                
                if result.success and result.extracted_content:
                    # 优先使用CSS选择器提取的内容
                    try:
                        detail = json.loads(result.extracted_content)
                        if isinstance(detail, list) and len(detail) > 0:
                            detail = detail[0]
                        
                        article['content'] = detail.get('content', '')
                        article['summary'] = detail.get('summary', '')
                        if article['content']:
                            content_extracted = True
                    except:
                        pass
                
                # 如果CSS提取失败，尝试使用Markdown（即使success为False）
                if not content_extracted and result.markdown:
                    article['content'] = result.markdown.raw_markdown if result.markdown.raw_markdown else ''
                    article['summary'] = article['content'][:200] if article['content'] else ''
                    if article['content']:
                        content_extracted = True
                
                # 验证内容是否有效
                if content_extracted and article.get('content'):
                    # 1. 验证内容质量
                    is_valid, reason = self.is_valid_article_content(
                        article['content'], 
                        article.get('url', ''),
                        article.get('title', '')
                    )
                    
                    if not is_valid:
                        print(f"  ⚠️  跳过: {reason}")
                        continue
                    
                    # 2. 检查是否是今天的文章
                    is_today, article_date = self.is_today_article(
                        article['content'],
                        article.get('title', '')
                    )
                    
                    if is_today is False:
                        # 明确不是今天的文章
                        print(f"  ⏭️  跳过: 非当日文章({article_date})")
                        continue
                    elif is_today is None:
                        # 无法确定日期，给出警告但仍然保存
                        print(f"  ⚠️  警告: 无法提取发布日期，仍然保存")
                    else:
                        # 是今天的文章
                        print(f"  ✓ 当日文章({article_date})")
                    
                    # 3. 保存到数据库
                    if self.save_article(article):
                        saved_count += 1
                        print(f"  ✅ 保存成功")
                    else:
                        print(f"  ⏭️  已存在")
                else:
                    print(f"  ❌ 内容提取失败")
                
                # 避免请求过快
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"  ❌ 处理出错: {str(e)}")
                continue
        
        return saved_count
    
    def save_article(self, article):
        """保存文章到数据库"""
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM articles WHERE source_url = %s",
                (article.get('url', ''),)
            )
            
            if cursor.fetchone():
                return False
            
            # 处理发布时间
            published_at = article.get('published_date')
            if published_at:
                try:
                    # 尝试多种时间格式
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
                        try:
                            published_at = datetime.strptime(str(published_at)[:10], fmt)
                            break
                        except:
                            continue
                    else:
                        published_at = datetime.now()
                except:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()
            
            # 插入新文章
            sql = """
                INSERT INTO articles 
                (title, summary, content, source, source_url, category, published_at, created_at, is_reviewed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                article.get('title', '')[:200],  # 限制标题长度
                article.get('summary', '')[:500],  # 限制摘要长度
                article.get('content', ''),
                self.source_name,
                article.get('url', ''),
                self.category,
                published_at,
                datetime.now(),
                True  # 自动设置为已审核
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"    ❌ 保存出错: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
