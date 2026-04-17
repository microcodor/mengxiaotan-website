"""
测试Crawl4AI的输出格式
查看爬取到的各种数据格式
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import json

async def test_crawl_output():
    """测试爬取输出格式"""
    
    # 测试URL - 使用一个更稳定的页面
    test_url = "https://www.nbcnews.com/business"  # Crawl4AI文档中的示例URL
    
    print("="*80)
    print(f"🔍 测试URL: {test_url}")
    print("="*80)
    
    browser_config = BrowserConfig(
        browser_type="chromium",  # 或使用 "undetected" 绕过反爬虫
        headless=True,
        verbose=False,
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security"
        ]
    )
    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="domcontentloaded",
        page_timeout=30000,
        magic=True,  # 启用魔法模式，自动处理反爬虫
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("\n⏳ 正在爬取...")
        result = await crawler.arun(url=test_url, config=run_config)
        
        if result.success:
            print("\n✅ 爬取成功！\n")
            
            # 1. 基本信息
            print("="*80)
            print("📊 1. 基本信息")
            print("="*80)
            print(f"URL: {result.url}")
            print(f"状态码: {result.status_code}")
            print(f"成功: {result.success}")
            print(f"错误信息: {result.error_message}")
            
            # 2. HTML内容
            print("\n" + "="*80)
            print("📄 2. HTML内容")
            print("="*80)
            print(f"HTML长度: {len(result.html)} 字符")
            print(f"HTML预览（前500字符）:")
            print("-"*80)
            print(result.html[:500])
            print("-"*80)
            
            # 3. Markdown内容
            print("\n" + "="*80)
            print("📝 3. Markdown内容")
            print("="*80)
            if result.markdown:
                print(f"Raw Markdown长度: {len(result.markdown.raw_markdown)} 字符")
                print(f"Fit Markdown长度: {len(result.markdown.fit_markdown)} 字符")
                print(f"Markdown with Citations长度: {len(result.markdown.markdown_with_citations)} 字符")
                
                print(f"\n📝 Raw Markdown预览（前1000字符）:")
                print("-"*80)
                print(result.markdown.raw_markdown[:1000])
                print("-"*80)
                
                print(f"\n📝 Fit Markdown预览（前1000字符）:")
                print("-"*80)
                print(result.markdown.fit_markdown[:1000])
                print("-"*80)
            else:
                print("⚠️  无Markdown内容")
            
            # 4. 链接信息
            print("\n" + "="*80)
            print("🔗 4. 链接信息")
            print("="*80)
            if result.links:
                print(f"内部链接数: {len(result.links.get('internal', []))}")
                print(f"外部链接数: {len(result.links.get('external', []))}")
                
                print(f"\n前5个内部链接:")
                for i, link in enumerate(result.links.get('internal', [])[:5], 1):
                    print(f"  {i}. {link.get('text', 'No text')[:50]}")
                    print(f"     URL: {link.get('href', 'No href')}")
            else:
                print("⚠️  无链接信息")
            
            # 5. 媒体信息
            print("\n" + "="*80)
            print("🖼️  5. 媒体信息")
            print("="*80)
            if result.media:
                print(f"图片数: {len(result.media.get('images', []))}")
                print(f"视频数: {len(result.media.get('videos', []))}")
                print(f"音频数: {len(result.media.get('audios', []))}")
                
                if result.media.get('images'):
                    print(f"\n前3张图片:")
                    for i, img in enumerate(result.media['images'][:3], 1):
                        print(f"  {i}. {img.get('src', 'No src')}")
                        print(f"     Alt: {img.get('alt', 'No alt')}")
            else:
                print("⚠️  无媒体信息")
            
            # 6. 元数据
            print("\n" + "="*80)
            print("📋 6. 元数据")
            print("="*80)
            if result.metadata:
                print(json.dumps(result.metadata, indent=2, ensure_ascii=False))
            else:
                print("⚠️  无元数据")
            
            # 7. 提取的内容（如果有）
            print("\n" + "="*80)
            print("📦 7. 提取的内容")
            print("="*80)
            if result.extracted_content:
                print(f"提取内容长度: {len(result.extracted_content)} 字符")
                print(f"提取内容预览:")
                print("-"*80)
                print(result.extracted_content[:500])
                print("-"*80)
            else:
                print("⚠️  无提取内容（未配置提取策略）")
            
            # 8. 截图（如果有）
            print("\n" + "="*80)
            print("📸 8. 截图信息")
            print("="*80)
            if result.screenshot:
                print(f"截图数据长度: {len(result.screenshot)} 字节")
            else:
                print("⚠️  无截图（未启用截图功能）")
            
            # 9. 保存完整的Markdown到文件
            print("\n" + "="*80)
            print("💾 9. 保存输出到文件")
            print("="*80)
            
            output_dir = Path("crawler/test_output")
            output_dir.mkdir(exist_ok=True)
            
            # 保存Raw Markdown
            if result.markdown:
                raw_md_file = output_dir / "raw_markdown.md"
                with open(raw_md_file, 'w', encoding='utf-8') as f:
                    f.write(result.markdown.raw_markdown)
                print(f"✅ Raw Markdown已保存到: {raw_md_file}")
                
                # 保存Fit Markdown
                fit_md_file = output_dir / "fit_markdown.md"
                with open(fit_md_file, 'w', encoding='utf-8') as f:
                    f.write(result.markdown.fit_markdown)
                print(f"✅ Fit Markdown已保存到: {fit_md_file}")
            
            # 保存HTML
            html_file = output_dir / "page.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result.html)
            print(f"✅ HTML已保存到: {html_file}")
            
            # 保存元数据
            if result.metadata:
                metadata_file = output_dir / "metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(result.metadata, f, indent=2, ensure_ascii=False)
                print(f"✅ 元数据已保存到: {metadata_file}")
            
            # 保存链接信息
            if result.links:
                links_file = output_dir / "links.json"
                with open(links_file, 'w', encoding='utf-8') as f:
                    json.dump(result.links, f, indent=2, ensure_ascii=False)
                print(f"✅ 链接信息已保存到: {links_file}")
            
            print("\n" + "="*80)
            print("✅ 测试完成！请查看 crawler/test_output/ 目录下的文件")
            print("="*80)
            
        else:
            print(f"\n❌ 爬取失败: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(test_crawl_output())
