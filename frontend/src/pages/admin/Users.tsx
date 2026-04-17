import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function AdminUsers() {
  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get('/admin/users'),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">用户管理</h1>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-semibold">ID</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">昵称</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">手机号</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">角色</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">状态</th>
              <th className="px-6 py-3 text-left text-sm font-semibold">注册时间</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {users?.map((user: any) => (
              <tr key={user.id} className="hover:bg-white/5">
                <td className="px-6 py-4 text-sm">{user.id}</td>
                <td className="px-6 py-4 text-sm">{user.nickname}</td>
                <td className="px-6 py-4 text-sm">{user.phone}</td>
                <td className="px-6 py-4 text-sm">{user.role}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    user.status === 'active' 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {user.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">
                  {formatDate(user.created_at, 'yyyy-MM-dd')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
