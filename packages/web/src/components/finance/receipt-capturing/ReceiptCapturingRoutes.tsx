import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { OverviewPage } from './pages/OverviewPage'
import { TodayPage } from './pages/TodayPage'
import { AdminPage } from './pages/AdminPage'

export function ReceiptCapturingRoutes() {
  const [userRole] = useState<'employee' | 'admin'>('employee') // TODO: Get from auth context

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Receipt Capturing</h2>
        <p className="text-gray-600">Track and manage expense receipts</p>
      </div>
      
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="today">Today</TabsTrigger>
          {userRole === 'admin' && (
            <TabsTrigger value="admin">Admin</TabsTrigger>
          )}
        </TabsList>
        
        <TabsContent value="overview">
          <OverviewPage />
        </TabsContent>
        
        <TabsContent value="today">
          <TodayPage />
        </TabsContent>
        
        {userRole === 'admin' && (
          <TabsContent value="admin">
            <AdminPage />
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
