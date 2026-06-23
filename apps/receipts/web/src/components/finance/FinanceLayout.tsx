import type { ReactNode } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface FinanceLayoutProps {
  children: ReactNode
}

export function FinanceLayout({ children }: FinanceLayoutProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Finance</h1>
        <p className="text-gray-600">Manage financial operations and expense tracking</p>
      </div>
      
      <Tabs defaultValue="receipt-capturing" className="space-y-4">
        <TabsList>
          <TabsTrigger value="receipt-capturing">Receipt Capturing</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="budgets">Budgets</TabsTrigger>
        </TabsList>
        
        <TabsContent value="receipt-capturing" className="space-y-4">
          {children}
        </TabsContent>
        
        <TabsContent value="reports" className="space-y-4">
          <div className="text-center py-12">
            <p className="text-gray-500">Reports module coming soon...</p>
          </div>
        </TabsContent>
        
        <TabsContent value="budgets" className="space-y-4">
          <div className="text-center py-12">
            <p className="text-gray-500">Budgets module coming soon...</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
