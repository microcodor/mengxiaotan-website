BOT_NAME = 'energy_crawler'

SPIDER_MODULES = ['energy_crawler.spiders']
NEWSPIDER_MODULE = 'energy_crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests
DOWNLOAD_DELAY = 2

# Disable cookies
COOKIES_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    'energy_crawler.middlewares.EnergySpiderMiddleware': 543,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'energy_crawler.middlewares.EnergyDownloaderMiddleware': 543,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'energy_crawler.pipelines.DuplicatesPipeline': 100,
    'energy_crawler.pipelines.DatabasePipeline': 300,
}

# Database settings
DATABASE_URL = 'mysql+pymysql://root:jinchun123@localhost:3306/energy_station'

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# Set settings whose default value is deprecated
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
FEED_EXPORT_ENCODING = 'utf-8'
