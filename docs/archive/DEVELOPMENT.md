# 开发指南

## 目录
- [环境准备](#环境准备)
- [项目启动](#项目启动)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [常用命令](#常用命令)
- [调试技巧](#调试技巧)

---

## 环境准备

### 必需软件
- **Python**: 3.9+
- **Node.js**: 18+
- **Docker**: 20+
- **Docker Compose**: 2.0+
- **MySQL**: 8.0+
- **Redis**: 7.x

### 推荐工具
- **IDE**: VS Code / PyCharm
- **API 测试**: Postman / Insomnia
- **数据库工具**: DBeaver / MySQL Workbench

---

## 项目启动

### 1. 克隆项目
```bash
git clone <repository-url>
cd energy-station
```

### 2. 快速启动（推荐）
```bash
chmod +x start.sh
./start.sh
```

### 3. 手动启动

#### 启动数据库
```bash
docker-compose up -d mysql redis
```

#### 初始化数据库
```bash
cd backend
python3 init_db.py
```

#### 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### 启动前端
```bash
cd frontend
npm install
npm run dev
```

---

## 开发流程

### 后端开发

#### 1. 添加新的 API 接口

**步骤**:
1. 在 `backend/app/models.py` 中定义数据模型
2. 在 `backend/app/schemas.py` 中定义数据验证
3. 在 `backend/app/api/` 中创建路由文件
4. 在 `backend/app/api/__init__.py` 中注册蓝图

**示例**:
```python
# models.py
class Example(db.Model):
    __tablename__ = 'examples'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

# schemas.py
class ExampleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

# api/examples.py
from flask.views import MethodView
from app.api import examples_bp

@examples_bp.route('/')
class ExampleList(MethodView):
    @examples_bp.response(200, ExampleSchema(many=True))
    def get(self):
        return Example.query.all()
```

#### 2. 添加新的爬虫

**步骤**:
1. 在 `crawler/energy_crawler/spiders/` 创建爬虫文件
2. 继承 `scrapy.Spider` 类
3. 定义 `name`, `allowed_domains`, `start_urls`
4. 实现 `parse()` 方法

**示例**:
```python
import scrapy
from energy_crawler.items import ArticleItem

class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['example.com']
    start_urls = ['https://example.com/news']

    def parse(self, response):
        for article in response.css('div.article'):
            item = ArticleItem()
            item['title'] = article.css('h2::text').get()
            item['url'] = article.css('a::attr(href)').get()
            yield item
```

#### 3. 添加定时任务

在 `backend/app/scheduler.py` 中添加:
```python
def my_task():
    print("执行任务...")

scheduler.add_job(
    my_task,
    CronTrigger(hour='9', minute='0'),
    id='my_task',
    name='我的任务'
)
```

### 前端开发

#### 1. 添加新页面

**步骤**:
1. 在 `frontend/src/pages/` 创建页面组件
2. 在 `frontend/src/App.tsx` 中添加路由
3. 在导航组件中添加链接

**示例**:
```tsx
// pages/Example.tsx
export default function Example() {
  return (
    <div>
      <h1>示例页面</h1>
    </div>
  )
}

// App.tsx
import Example from './pages/Example'

<Route path="example" element={<Example />} />
```

#### 2. 调用 API

使用 TanStack Query:
```tsx
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'

function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['examples'],
    queryFn: () => api.get('/examples'),
  })

  if (isLoading) return <div>加载中...</div>
  
  return <div>{data?.items?.map(...)}</div>
}
```

#### 3. 添加新组件

在 `frontend/src/components/` 创建:
```tsx
interface Props {
  title: string
}

export default function MyComponent({ title }: Props) {
  return (
    <div className="glass-card p-6">
      <h2>{title}</h2>
    </div>
  )
}
```

---

## 代码规范

### Python (后端)
- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 函数和变量使用 snake_case
- 类名使用 PascalCase
- 添加类型注解和文档字符串

```python
def get_articles(category: str, page: int = 1) -> List[Article]:
    """获取文章列表
    
    Args:
        category: 文章分类
        page: 页码
        
    Returns:
        文章列表
    """
    return Article.query.filter_by(category=category).paginate(page=page)
```

### TypeScript (前端)
- 使用 2 空格缩进
- 组件使用 PascalCase
- 函数和变量使用 camelCase
- 使用 TypeScript 类型注解
- 使用函数式组件和 Hooks

```tsx
interface Article {
  id: number
  title: string
}

export default function ArticleList() {
  const [articles, setArticles] = useState<Article[]>([])
  
  return (
    <div>
      {articles.map(article => (
        <div key={article.id}>{article.title}</div>
      ))}
    </div>
  )
}
```

---

## 常用命令

### 后端

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 数据库迁移
flask db init
flask db migrate -m "描述"
flask db upgrade

# 运行爬虫
cd crawler
scrapy crawl ndrc
scrapy crawl coal
scrapy crawl power
```

### 前端

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```

### Docker

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看运行状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec mysql mysql -uroot -p
```

---

## 调试技巧

### 后端调试

#### 1. 使用 Flask 调试模式
```python
if __name__ == '__main__':
    app.run(debug=True)
```

#### 2. 打印日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug('调试信息')
app.logger.info('普通信息')
app.logger.error('错误信息')
```

#### 3. 使用 pdb 调试器
```python
import pdb; pdb.set_trace()
```

#### 4. 查看 SQL 查询
```python
from flask import g
import time

@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start
    print(f'请求耗时: {diff:.3f}s')
    return response
```

### 前端调试

#### 1. 使用 React DevTools
安装浏览器扩展: React Developer Tools

#### 2. 使用 console.log
```tsx
console.log('数据:', data)
console.table(articles)
console.error('错误:', error)
```

#### 3. 使用 debugger
```tsx
function MyComponent() {
  debugger  // 浏览器会在此处暂停
  return <div>...</div>
}
```

#### 4. 查看网络请求
打开浏览器开发者工具 -> Network 标签

### 数据库调试

#### 1. 连接数据库
```bash
docker-compose exec mysql mysql -uroot -p
# 密码: password
```

#### 2. 常用 SQL
```sql
-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESC articles;

-- 查询数据
SELECT * FROM articles LIMIT 10;

-- 统计数据
SELECT category, COUNT(*) FROM articles GROUP BY category;
```

---

## 测试

### 后端测试
```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest

# 查看覆盖率
pytest --cov=app tests/
```

### 前端测试
```bash
# 安装测试依赖
npm install -D vitest @testing-library/react

# 运行测试
npm run test
```

---

## 部署

### 开发环境
```bash
./start.sh
```

### 生产环境
```bash
# 构建前端
cd frontend
npm run build

# 启动 Docker 服务
docker-compose -f docker-compose.prod.yml up -d
```

---

## 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :5000
lsof -i :5173

# 杀死进程
kill -9 <PID>
```

### 2. 数据库连接失败
- 检查 MySQL 容器是否运行
- 检查数据库配置是否正确
- 检查防火墙设置

### 3. 前端无法访问后端
- 检查 CORS 配置
- 检查后端是否正常运行
- 检查 API 地址配置

### 4. 爬虫抓取失败
- 检查网络连接
- 检查目标网站是否可访问
- 更新爬虫规则

---

## 资源链接

- [Flask 文档](https://flask.palletsprojects.com/)
- [React 文档](https://react.dev/)
- [Scrapy 文档](https://docs.scrapy.org/)
- [TailwindCSS 文档](https://tailwindcss.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

---

**最后更新**: 2026-04-10
