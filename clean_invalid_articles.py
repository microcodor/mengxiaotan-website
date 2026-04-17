#!/usr/bin/env python3
"""
清理数据库中的无效文章
- 包含链接的文章
- 内容太短的文章
- 包含导航文本的文章
"""
import sys
import os
sys.path.insert(0, 'backend')

from app import create_app, db
from app.models import Article
from sqlalchemy import or_, and_
import re

def check_invalid_articles():
    """检查无效文章"""
    app = create_app()
    
    with app.app_context():
        print("="*80)
        print("检查数据库中的无效文章")
        print("="*80)
        
        # 1. 检查包含链接的文章
        print("\n1. 检查包含链接的文章...")
        articles_with_links = Article.query.filter(
            or_(
                Article.content.like('%http://%'),
                Article.content.like('%https://%'),
                Article.content.like('%www.%'),
                Article.content.like('%href=%'),
                Article.content.like('%<a %')
            )
        ).all()
        
        print(f"   找到 {len(articles_with_links)} 篇包含链接的文章")
        
        if articles_with_links:
            print("\n   示例:")
            for article in articles_with_links[:5]:
                preview = article.content[:200] if article.content else ''
                print(f"   - ID: {article.id}, 标题: {article.title}")
                print(f"     来源: {article.source}, 长度: {len(article.content or '')}")
                print(f"     预览: {preview}...")
                print()
        
        # 2. 检查内容太短的文章
        print("\n2. 检查内容太短的文章 (< 100字)...")
        short_articles = Article.query.filter(
            or_(
                Article.content == None,
                Article.content == '',
                db.func.length(Article.content) < 100
            )
        ).all()
        
        print(f"   找到 {len(short_articles)} 篇内容太短的文章")
        
        # 3. 检查包含导航文本的文章
        print("\n3. 检查包含导航文本的文章...")
        nav_patterns = ['首页', '返回', '上一页', '下一页', '关于我们', '联系我们', '版权所有']
        
        articles_with_nav = []
        for pattern in nav_patterns:
            articles = Article.query.filter(Article.content.like(f'%{pattern}%')).all()
            articles_with_nav.extend(articles)
        
        # 去重
        articles_with_nav = list(set(articles_with_nav))
        print(f"   找到 {len(articles_with_nav)} 篇包含导航文本的文章")
        
        # 4. 统计总数
        print("\n" + "="*80)
        print("统计结果:")
        print("="*80)
        
        # 合并所有无效文章(去重)
        all_invalid = set(articles_with_links + short_articles + articles_with_nav)
        
        print(f"包含链接: {len(articles_with_links)} 篇")
        print(f"内容太短: {len(short_articles)} 篇")
        print(f"包含导航: {len(articles_with_nav)} 篇")
        print(f"总计无效: {len(all_invalid)} 篇")
        print(f"数据库总文章数: {Article.query.count()} 篇")
        print(f"无效比例: {len(all_invalid) / Article.query.count() * 100:.2f}%")
        
        return all_invalid

def clean_invalid_articles(dry_run=True):
    """清理无效文章"""
    app = create_app()
    
    with app.app_context():
        invalid_articles = check_invalid_articles()
        
        if not invalid_articles:
            print("\n✅ 没有找到无效文章")
            return
        
        print("\n" + "="*80)
        if dry_run:
            print("预览模式 - 不会实际删除")
        else:
            print("⚠️  准备删除无效文章")
        print("="*80)
        
        print(f"\n将要删除 {len(invalid_articles)} 篇文章:")
        
        # 按来源统计
        source_stats = {}
        for article in invalid_articles:
            source = article.source or '未知'
            source_stats[source] = source_stats.get(source, 0) + 1
        
        print("\n按来源统计:")
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count} 篇")
        
        if not dry_run:
            print("\n开始删除...")
            deleted_count = 0
            failed_count = 0
            
            # 获取所有要删除的文章ID
            article_ids = [article.id for article in invalid_articles]
            
            # 先删除user_history中的相关记录
            print(f"\n1. 删除user_history中的相关记录...")
            try:
                from app.models import UserHistory
                history_count = UserHistory.query.filter(UserHistory.article_id.in_(article_ids)).count()
                print(f"   找到 {history_count} 条历史记录")
                
                if history_count > 0:
                    UserHistory.query.filter(UserHistory.article_id.in_(article_ids)).delete(synchronize_session=False)
                    db.session.commit()
                    print(f"   ✅ 已删除 {history_count} 条历史记录")
            except Exception as e:
                print(f"   ⚠️  删除历史记录失败: {str(e)}")
                db.session.rollback()
            
            # 再删除文章
            print(f"\n2. 删除文章...")
            for article in invalid_articles:
                try:
                    db.session.delete(article)
                    deleted_count += 1
                    
                    if deleted_count % 50 == 0:
                        print(f"   已删除 {deleted_count} 篇...")
                        db.session.commit()
                
                except Exception as e:
                    print(f"   ❌ 删除失败: ID={article.id}, 错误={str(e)}")
                    failed_count += 1
                    db.session.rollback()
            
            # 最后提交
            try:
                db.session.commit()
            except Exception as e:
                print(f"   ❌ 最终提交失败: {str(e)}")
                db.session.rollback()
            
            print(f"\n✅ 删除完成:")
            print(f"   成功: {deleted_count} 篇")
            print(f"   失败: {failed_count} 篇")
            print(f"   剩余文章数: {Article.query.count()} 篇")
        else:
            print("\n💡 这是预览模式,没有实际删除")
            print("如果要真正删除,请运行: python clean_invalid_articles.py --delete")

if __name__ == '__main__':
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--delete':
        print("⚠️  警告: 即将删除无效文章!")
        response = input("确认删除? (yes/no): ")
        
        if response.lower() == 'yes':
            clean_invalid_articles(dry_run=False)
        else:
            print("已取消")
    else:
        # 默认预览模式
        clean_invalid_articles(dry_run=True)
