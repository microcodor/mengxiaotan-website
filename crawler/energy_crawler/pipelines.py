from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymysql
from datetime import datetime
import hashlib
import json

class DuplicatesPipeline:
    def __init__(self):
        self.urls_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('source_url')
        
        if url in self.urls_seen:
            raise DropItem(f"Duplicate item found: {url}")
        else:
            self.urls_seen.add(url)
            return item

class DatabasePipeline:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_url=crawler.settings.get('DATABASE_URL')
        )

    def open_spider(self, spider):
        # Parse database URL
        # Format: mysql+pymysql://user:password@host:port/database
        parts = self.db_url.replace('mysql+pymysql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        host_port = host_db[0].split(':')
        
        self.conn = pymysql.connect(
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 3306,
            user=user_pass[0],
            password=user_pass[1],
            database=host_db[1],
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Check if article already exists
        self.cursor.execute(
            "SELECT id FROM articles WHERE source_url = %s",
            (adapter.get('source_url'),)
        )
        
        if self.cursor.fetchone():
            spider.logger.info(f"Article already exists: {adapter.get('title')}")
            return item
        
        # Insert new article (默认审核通过)
        sql = """
            INSERT INTO articles 
            (title, summary, content, source, source_url, category, tags, published_at, created_at, is_reviewed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        tags_json = json.dumps(adapter.get('tags', []), ensure_ascii=False) if adapter.get('tags') else '[]'
        
        self.cursor.execute(sql, (
            adapter.get('title'),
            adapter.get('summary'),
            adapter.get('content'),
            adapter.get('source'),
            adapter.get('source_url'),
            adapter.get('category'),
            tags_json,
            adapter.get('published_at', datetime.now()),
            datetime.now(),
            True  # 爬虫入库的文章默认审核通过
        ))
        
        self.conn.commit()
        spider.logger.info(f"Article saved (auto-reviewed): {adapter.get('title')}")
        
        return item
