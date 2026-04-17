import { Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireAdmin?: boolean
}

export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const [checking, setChecking] = useState(true)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')

    if (!token || !userStr) {
      setChecking(false)
      return
    }

    try {
      const userData = JSON.parse(userStr)
      setUser(userData)
    } catch (error) {
      console.error('解析用户信息失败:', error)
    } finally {
      setChecking(false)
    }
  }, [])

  // 检查中显示加载
  if (checking) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-400 mx-auto mb-4"></div>
          <p className="text-gray-400">验证中...</p>
        </div>
      </div>
    )
  }

  // 未登录
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // 需要管理员权限但用户不是管理员
  if (requireAdmin && user.role !== 'admin' && user.role !== 'editor') {
    alert('您没有访问此页面的权限')
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}
