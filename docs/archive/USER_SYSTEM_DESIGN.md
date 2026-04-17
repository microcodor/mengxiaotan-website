# 用户体系设计方案

## 📋 用户角色定义

### 1. 普通用户 (role: 'user')
**功能权限：**
- ✅ 浏览文章列表
- ✅ 查看文章详情
- ✅ 查看数据看板
- ✅ 个人中心（个人信息、订阅管理）
- ✅ 订单管理（查看自己的订单）
- ✅ 推送设置（配置推送渠道）
- ❌ 不能访问管理后台

**登录后跳转：** `/dashboard` (用户工作台)

### 2. 管理员 (role: 'admin' 或 'editor')
**功能权限：**
- ✅ 所有普通用户权限
- ✅ 管理后台访问
- ✅ 文章管理（审核、编辑、删除）
- ✅ 用户管理
- ✅ 订单管理（审核、确认）
- ✅ 推送管理（群发消息）
- ✅ 爬虫管理（启动、停止、监控）
- ✅ 数据统计

**登录后跳转：** `/admin` (管理后台)

## 🗺️ 路由结构设计

```
/                          # 首页（公开）
├── /login                 # 登录页（公开）
├── /register              # 注册页（公开）
├── /articles              # 文章列表（公开）
├── /articles/:id          # 文章详情（公开）
├── /category/:category    # 分类文章（公开）
│
├── /dashboard             # 用户工作台（需登录）
│   ├── /dashboard/profile      # 个人信息
│   ├── /dashboard/subscription # 我的订阅
│   ├── /dashboard/orders       # 我的订单
│   └── /dashboard/push         # 推送设置
│
└── /admin                 # 管理后台（需管理员权限）
    ├── /admin/dashboard        # 数据仪表盘
    ├── /admin/articles         # 文章管理
    ├── /admin/users            # 用户管理
    ├── /admin/orders           # 订单管理
    ├── /admin/broadcast        # 推送管理
    └── /admin/crawler          # 爬虫管理
```

## 🔐 权限控制逻辑

### 登录后跳转规则
```typescript
if (user.role === 'admin' || user.role === 'editor') {
  navigate('/admin')  // 管理员 → 管理后台
} else {
  navigate('/dashboard')  // 普通用户 → 用户工作台
}
```

### 路由守卫
1. **公开路由** - 无需登录即可访问
2. **用户路由** - 需要登录（任何角色）
3. **管理员路由** - 需要管理员权限

## 📱 页面布局

### 1. 公开页面布局 (Layout.tsx)
- 顶部导航栏（Logo、菜单、登录/注册按钮）
- 内容区域
- 底部信息

### 2. 用户工作台布局 (DashboardLayout.tsx) - 新建
- 顶部导航栏（Logo、用户信息、退出）
- 左侧菜单（个人信息、订阅、订单、推送设置）
- 内容区域

### 3. 管理后台布局 (AdminLayout.tsx)
- 左侧菜单（管理功能）
- 顶部用户信息
- 内容区域

## 🎨 导航菜单设计

### 公开页面导航
```
首页 | 资讯 | 数据看板 | 订阅服务 | [登录] [注册]
```

### 用户工作台导航
```
[用户头像]
├── 个人信息
├── 我的订阅
├── 我的订单
├── 推送设置
└── 退出登录
```

### 管理后台导航
```
管理后台
├── 仪表盘
├── 文章管理
├── 用户管理
├── 订单管理
├── 推送管理
├── 爬虫管理
└── 退出登录
```

## 🔄 页面重构计划

### 需要新建的组件
1. `DashboardLayout.tsx` - 用户工作台布局
2. `ProtectedRoute.tsx` - 路由守卫组件
3. `UserDashboard.tsx` - 用户工作台首页

### 需要移动的页面
- `Profile.tsx` → `/dashboard/profile`
- `Subscription.tsx` → `/dashboard/subscription`
- `Orders.tsx` → `/dashboard/orders`
- `PushSettings.tsx` → `/dashboard/push`

### 需要修改的组件
- `Login.tsx` - 修改登录后跳转逻辑
- `Layout.tsx` - 优化公开页面导航
- `AdminLayout.tsx` - 已完成权限检查
- `App.tsx` - 重构路由结构

## 📝 实施步骤

1. ✅ 创建路由守卫组件
2. ✅ 创建用户工作台布局
3. ✅ 创建用户工作台首页
4. ✅ 修改登录逻辑（根据角色跳转）
5. ✅ 重构路由结构
6. ✅ 移动现有页面到新路由
7. ✅ 更新导航菜单
8. ✅ 测试权限控制

## 🎯 用户体验优化

### 登录流程
1. 用户输入手机号密码
2. 验证成功后保存用户信息和token
3. 根据角色自动跳转：
   - 管理员 → `/admin`
   - 普通用户 → `/dashboard`

### 权限提示
- 未登录访问需登录页面 → 跳转到登录页
- 普通用户访问管理后台 → 提示"无权限"并跳转到用户工作台
- 管理员可以访问所有页面

### 导航优化
- 顶部导航根据登录状态显示不同内容
- 登录后显示用户头像和快捷菜单
- 管理员在顶部导航显示"管理后台"入口

## 🔧 技术实现

### 路由守卫示例
```typescript
function ProtectedRoute({ children, requireAdmin = false }) {
  const token = localStorage.getItem('access_token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (!token) {
    return <Navigate to="/login" />
  }
  
  if (requireAdmin && user.role !== 'admin' && user.role !== 'editor') {
    return <Navigate to="/dashboard" />
  }
  
  return children
}
```

### 登录后跳转
```typescript
const handleLogin = async () => {
  const data = await api.post('/auth/login', { phone, password })
  setAuth(data.user, data.access_token)
  
  // 根据角色跳转
  if (data.user.role === 'admin' || data.user.role === 'editor') {
    navigate('/admin')
  } else {
    navigate('/dashboard')
  }
}
```
