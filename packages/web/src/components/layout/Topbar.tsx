import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useState } from 'react'

export function Topbar() {
  const [userRole, setUserRole] = useState<'employee' | 'admin'>('employee')

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-gray-900">AgriPlatform</h1>
              <p className="text-sm text-gray-500">Digital Twin Platform</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Select value={userRole} onValueChange={(value: 'employee' | 'admin') => setUserRole(value)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="employee">Employee</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
              </SelectContent>
            </Select>
            <div className="text-sm text-gray-500">
              Welcome, {userRole === 'admin' ? 'Financial Admin' : 'John Doe'}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
