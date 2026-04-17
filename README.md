# 蒙小碳·能源站 - 能源电力煤炭资讯订阅平台

## 项目简介
面向能源电力煤炭企业的专业资讯订阅站，提供实时行业动态、政策解读、数据看板和个性化推送服务。

## ✨ 核心功能

### 平台支持 🖥️
- ✅ **Windows** 10/11
- ✅ **macOS** 10.15+
- ✅ **Linux** (Ubuntu, CentOS, Debian 等)
- 📝 详细部署指南：[PLATFORM.md](PLATFORM.md)

### 已实现功能 ✅
- **用户系统**
  - 用户注册/登录（JWT认证）
  - 个人中心（资料管理、收藏、历史）
  - 角色权限管理（用户/编辑/管理员）

- **内容管理**
  - 文章列表/详情/搜索
  - 分类筛选（发改委/煤炭/电力/新能源）
  - 文章收藏和浏览历史
  - 焦点轮播和置顶推荐

- **数据抓取**
  - 5个核心数据源爬虫
    - 国家发改委
    - 国家能源局
    - 中国煤炭市场网
    - 北极星电力网
    - 中国新能源网
  - 自动去重和数据清洗
  - 定时调度（每日自动抓取）

- **AI 内容生成**
  - 每日简报自动生成
  - 今日一句话决策建议
  - 关键词提取
  - 内容摘要生成

- **数据看板**
  - 能源核心指标展示
  - 价格走势图表
  - 分类统计分析
  - 实时数据可视化

- **管理后台**
  - 数据仪表盘
  - 文章管理（审核/编辑/删除）
  - 用户管理
  - 数据源配置
  - 抓取日志查看
  - 简报生成管理

### 开发中功能 🚧
- 订阅套餐购买流程
- 企业微信/个人微信推送
- 个性化关键词定制
- 响应式设计优化

## 技术栈
- **前端**: React 18 + TypeScript + Vite 5 + TailwindCSS + shadcn/ui + Recharts
- **后端**: Flask 3.x + SQLAlchemy + JWT + APScheduler
- **数据库**: MySQL 8.0 + Redis 7.x
- **爬虫**: Scrapy 2.8+
- **AI**: MiniMax API（支持模拟模式）
- **部署**: Docker + Docker Compose + Nginx

## 项目结构
```
├── frontend/          # React 前端应用
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── lib/          # 工具库
│   │   └── App.tsx       # 主应用
│   └── package.json
├── backend/           # Flask 后端
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── models.py     # 数据模型
│   │   ├── schemas.py    # 数据验证
│   │   └── services/     # 业务服务
│   ├── app.py            # 应用入口
│   ├── config.py         # 配置文件
│   └── init_db.py        # 数据库初始化
├── crawler/           # Scrapy 爬虫
│   └── energy_crawler/
│       ├── spiders/      # 爬虫脚本
│       └── pipelines.py  # 数据处理
├── docker-compose.yml # Docker 编排
└── start.sh           # 启动脚本
```

## 快速开始

> 💡 **新手推荐**：查看 [快速开始指南 (QUICKSTART.md)](QUICKSTART.md) 获取 5 分钟快速启动教程

### 方式一：使用启动脚本（推荐）

#### macOS / Linux
```bash
chmod +x start.sh
./start.sh
```

停止服务：
```bash
chmod +x stop.sh
./stop.sh
```

#### Windows
双击运行 `start.bat` 或在命令行中执行：
```cmd
start.bat
```

停止服务：
```cmd
stop.bat
```

### 方式二：手动启动

#### 1. 启动数据库和缓存
```bash
docker-compose up -d mysql redis
```

#### 2. 初始化数据库
```bash
cd backend
python3 init_db.py
```

#### 3. 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

#### 5. 运行爬虫（可选）
```bash
cd crawler
pip install -r requirements.txt

# 抓取发改委数据
scrapy crawl ndrc

# 抓取煤炭数据
scrapy crawl coal

# 抓取电力数据
scrapy crawl power

# 抓取新能源数据
scrapy crawl newenergy

# 抓取国家能源局数据
scrapy crawl nea
```

## 访问地址

- **前端门户**: http://localhost:5173
- **后端API**: http://localhost:5000
- **管理后台**: http://localhost:5173/admin
- **API文档**: http://localhost:5000/swagger-ui

## 登录信息

### 管理员账号
- 手机号: `13800138000`
- 密码: `admin123`

### 测试用户
- 手机号: `13900139000`
- 密码: `test123`

## 环境变量配置

创建 `backend/.env` 文件：
```env
# 数据库配置（默认使用 3307 端口避免冲突）
DATABASE_URL=mysql+pymysql://root:password@localhost:3307/energy_station

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production

# MiniMax AI 配置（可选）
MINIMAX_API_KEY=your-minimax-api-key
MINIMAX_GROUP_ID=your-group-id

# Flask 配置
FLASK_ENV=development
```

> 💡 **端口说明**: 项目默认使用 **3307** 端口运行 MySQL，避免与本地 MySQL 冲突。  
> 详细配置请查看 [端口配置说明 (PORT_CONFIG.md)](PORT_CONFIG.md)

## 定时任务

系统已配置以下定时任务（自动运行）：

| 任务 | 执行时间 | 说明 |
|------|---------|------|
| 抓取发改委数据 | 每天 6:00, 18:00 | 获取最新政策动态 |
| 抓取煤炭数据 | 每天 7:00, 19:00 | 获取煤炭市场信息 |
| 抓取电力数据 | 每天 7:30, 19:30 | 获取电力行业动态 |
| 抓取新能源数据 | 每天 8:00 | 获取新能源资讯 |
| 抓取能源局数据 | 每天 6:30 | 获取能源局公告 |
| 生成每日简报 | 每天 9:00 | AI 生成今日简报 |

## API 接口

### 公开接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/articles` - 获取文章列表
- `GET /api/articles/:id` - 获取文章详情
- `GET /api/articles/carousel` - 获取轮播文章
- `GET /api/articles/daily-brief` - 获取今日简报

### 需要登录
- `GET /api/auth/me` - 获取当前用户信息
- `GET /api/users/profile` - 获取用户资料
- `PUT /api/users/profile` - 更新用户资料
- `GET /api/users/favorites` - 获取收藏列表
- `GET /api/users/history` - 获取浏览历史
- `POST /api/articles/:id/favorite` - 收藏文章
- `DELETE /api/articles/:id/favorite` - 取消收藏

### 管理员接口
- `GET /api/admin/dashboard` - 仪表盘数据
- `GET /api/admin/articles` - 文章管理
- `POST /api/admin/articles/:id/review` - 审核文章
- `GET /api/admin/users` - 用户管理
- `GET /api/admin/daily-brief` - 查看简报
- `POST /api/admin/daily-brief` - 生成简报
- `GET /api/admin/sources` - 数据源管理
- `GET /api/admin/crawl-logs` - 抓取日志

## 开发进度

当前进度：**约 60%**

- ✅ 基础架构（100%）
- ✅ 数据库设计（100%）
- ✅ 用户认证（100%）
- ✅ 文章管理（100%）
- ✅ 数据抓取（30% - 5/34 数据源）
- ✅ AI 内容生成（80%）
- ✅ 数据看板（70%）
- ✅ 管理后台（70%）
- 🚧 订阅系统（30%）
- 🚧 推送系统（0%）
- 🚧 响应式设计（40%）

## 下一步计划

1. **完善数据源**（P0）
   - 添加剩余 29 个数据源爬虫
   - 实现 AI 联网搜索补全

2. **订阅与推送**（P1）
   - 完成订阅购买流程
   - 对接企业微信/个人微信
   - 实现定时推送功能

3. **视觉优化**（P1）
   - 玻璃态设计风格
   - 深色主题优化
   - 移动端响应式适配

4. **性能优化**（P2）
   - 接口缓存
   - 图片懒加载
   - 代码分割

## 常见问题

### 1. Python 依赖安装失败
**错误信息**: `Could not find a version that satisfies the requirement Flask`

**原因**: 网络问题或 pip 源不可用

**解决方案**:

#### 快速修复（推荐）
```bash
# macOS/Linux
chmod +x fix-dependencies.sh
./fix-dependencies.sh

# Windows
fix-dependencies.bat
```

#### 手动修复
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 端口被占用（MySQL 3306）
**错误信息**: `bind: address already in use`

**原因**: 本地已经运行了 MySQL 服务

**解决方案**:

#### 方案一：使用端口检查工具（推荐）
```bash
# macOS/Linux
chmod +x check-ports.sh
./check-ports.sh

# Windows
check-ports.bat
```

#### 方案二：停止本地 MySQL
```bash
# macOS (Homebrew)
brew services stop mysql

# Linux
sudo systemctl stop mysql

# Windows
net stop MySQL80
```

#### 方案三：项目已配置使用 3307 端口
项目默认配置已改为使用 3307 端口，避免与本地 MySQL 冲突。
直接运行 `./start.sh` 或 `start.bat` 即可。

### 2. 数据库连接失败
确保 MySQL 容器已启动：
```bash
docker-compose ps
docker-compose logs mysql
```

### 2. 前端无法访问后端
检查后端是否正常运行，确保 CORS 配置正确。

### 3. 爬虫抓取失败
- 检查网络连接
- 查看目标网站是否可访问
- 检查爬虫规则是否需要更新

### 4. AI 功能不可用
如果没有配置 MiniMax API Key，系统会使用模拟数据，功能仍可正常使用。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## License

MIT
