import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

// Mock data - TODO: Replace with Supabase queries
const mockStats = {
  totalReceipts: 23,
  totalAmount: 1234.50,
  pending: 3,
  employees: 1
}

const mockReceipts = [
  {
    id: 1,
    amount: 45.50,
    category: 'Fuel',
    date: '2024-01-15',
    status: 'pending' as const,
    description: 'Diesel for tractor maintenance'
  },
  {
    id: 2,
    amount: 120.00,
    category: 'Equipment',
    date: '2024-01-15',
    status: 'approved' as const,
    description: 'New work gloves and safety equipment'
  },
  {
    id: 3,
    amount: 85.75,
    category: 'Supplies',
    date: '2024-01-14',
    status: 'rejected' as const,
    description: 'Seeds for spring planting'
  }
]

const StatusBadge = ({ status }: { status: 'pending' | 'approved' | 'rejected' }) => {
  const variants = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800'
  }
  return (
    <Badge className={variants[status]}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  )
}

export function OverviewPage() {
  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Receipts</CardTitle>
            <span className="text-sm text-gray-400">📄</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.totalReceipts}</div>
            <p className="text-xs text-muted-foreground">Your submissions</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
            <span className="text-sm text-gray-400">💰</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${mockStats.totalAmount.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <span className="text-sm text-gray-400">📅</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.pending}</div>
            <p className="text-xs text-muted-foreground">Awaiting approval</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Employees</CardTitle>
            <span className="text-sm text-gray-400">👥</span>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.employees}</div>
            <p className="text-xs text-muted-foreground">Active users</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Receipts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Receipts</CardTitle>
          <CardDescription>Your recent expense submissions</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Amount</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockReceipts.map((receipt) => (
                <TableRow key={receipt.id}>
                  <TableCell>${receipt.amount.toFixed(2)}</TableCell>
                  <TableCell>{receipt.category}</TableCell>
                  <TableCell>{receipt.date}</TableCell>
                  <TableCell>
                    <StatusBadge status={receipt.status} />
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="ghost" size="sm">
                        👁️
                      </Button>
                      <Button variant="ghost" size="sm">
                        ✏️
                      </Button>
                      <Button variant="ghost" size="sm">
                        🗑️
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
