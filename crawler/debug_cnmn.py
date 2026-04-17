"""
调试中国有色金属报爬虫
"""
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        verbose=False
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="domcontentloaded",
            page_timeout=60000,
            delay_before_return_html=2.0,
        )
        
        result = await crawler.arun(url="https://paper.cnmn.com.cn/", config=run_config)
        
        if result.success:
            print("✅ 页面加载成功\n")
            
            # 检查links
            if result.links:
                print(f"Internal links: {len(result.links.get('internal', []))}")
                print(f"External links: {len(result.links.get('external', []))}")
                
                print("\n前10个内部链接:")
                for i, link in enumerate(result.links.get('internal', [])[:10], 1):
                    print(f"{i}. {link.get('text', 'NO TEXT')[:50]} | {link.get('href', '')}")
                
                # 查找包含 Content.aspx 的链接
                content_links = [link for link in result.links.get('internal', []) if 'Content.aspx' in link.get('href', '')]
                print(f"\n包含 Content.aspx 的链接: {len(content_links)}")
                for link in content_links[:5]:
                    print(f"  - {link.get('text', 'NO TEXT')[:50]} | {link.get('href', '')}")
            else:
                print("❌ 没有提取到links")
            
            # 检查markdown
            if result.markdown:
                print(f"\nMarkdown长度: {len(result.markdown.raw_markdown)}")
                print(f"\nMarkdown前500字符:")
                print(result.markdown.raw_markdown[:500])
            else:
                print("❌ 没有提取到markdown")
        else:
            print(f"❌ 页面加载失败: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
