import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardLayout from './components/DashboardLayout'
import AdminLayout from './components/AdminLayout'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import ArticleList from './pages/ArticleList'
import ArticleDetail from './pages/ArticleDetail'
import Login from './pages/Login'
import Register from './pages/Register'
import Subscription from './pages/Subscription'

// 用户工作台页面
import UserDashboard from './pages/UserDashboard'
import Profile from './pages/Profile'
import Orders from './pages/Orders'
import PushSettings from './pages/PushSettings'
import CompanyInfo from './pages/CompanyInfo'
import CompanyBusiness from './pages/CompanyBusiness'
import CompanyProfile from './pages/CompanyProfile'
import DigitalTwin from './pages/DigitalTwin'
import DigitalTwinDetail from './pages/DigitalTwinDetail'
import CustomReports from './pages/CustomReports'
import CustomReportDetail from './pages/CustomReportDetail'
import Monitoring from './pages/Monitoring'
import MonitoringAlerts from './pages/MonitoringAlerts'

// 管理后台页面
import AdminDashboard from './pages/admin/Dashboard'
import AdminArticles from './pages/admin/Articles'
import AdminUsers from './pages/admin/Users'
import AdminOrders from './pages/admin/Orders'
import AdminBroadcast from './pages/admin/Broadcast'
import AdminPushManagement from './pages/admin/PushManagement'
import AdminCrawler from './pages/admin/Crawler'
import AdminCategories from './pages/admin/Categories'
import AdminCompanies from './pages/admin/Companies'
import AdminScheduler from './pages/admin/Scheduler'
import AdminMonitor from './pages/admin/Monitor'
import AdminReports from './pages/admin/Reports'

function App() {
  return (
    <Routes>
      {/* 公开路由 */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="articles" element={<ArticleList />} />
        <Route path="articles/:id" element={<ArticleDetail />} />
        <Route path="category/:category" element={<ArticleList />} />
        <Route path="subscription" element={<Subscription />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>
      
      {/* 用户工作台路由（需要登录） */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<UserDashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="subscription" element={<Subscription />} />
        <Route path="orders" element={<Orders />} />
        <Route path="push" element={<PushSettings />} />
        <Route path="company" element={<CompanyInfo />} />
        <Route path="company/business" element={<CompanyBusiness />} />
        <Route path="company/profile" element={<CompanyProfile />} />
        <Route path="digital-twin" element={<DigitalTwin />} />
        <Route path="digital-twin/:id" element={<DigitalTwinDetail />} />
        <Route path="reports" element={<CustomReports />} />
        <Route path="reports/:id" element={<CustomReportDetail />} />
        <Route path="monitoring" element={<Monitoring />} />
        <Route path="monitoring/alerts" element={<MonitoringAlerts />} />
      </Route>

      {/* 管理后台路由（需要管理员权限） */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="articles" element={<AdminArticles />} />
        <Route path="users" element={<AdminUsers />} />
        <Route path="orders" element={<AdminOrders />} />
        <Route path="broadcast" element={<AdminBroadcast />} />
        <Route path="push" element={<AdminPushManagement />} />
        <Route path="crawler" element={<AdminCrawler />} />
        <Route path="categories" element={<AdminCategories />} />
        <Route path="companies" element={<AdminCompanies />} />
        <Route path="scheduler" element={<AdminScheduler />} />
        <Route path="monitor" element={<AdminMonitor />} />
        <Route path="reports" element={<AdminReports />} />
      </Route>
    </Routes>
  )
}

export default App
