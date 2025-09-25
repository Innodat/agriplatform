import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

// Mock data - TODO: Replace with Supabase queries
const mockReceipts = [
  {
    id: 1,
    employeeName: 'John Smith',
    amount: 45.50,
    category: 'Fuel',
    supplier: 'Shell Station',
    date: '2024-01-15',
    status: 'pending' as const,
    description: 'Diesel for tractor maintenance'
  },
  {
    id: 2,
    employeeName: 'Sarah Johnson',
    amount: 120.00,
    category: 'Equipment',
    supplier: 'Farm Supply Co',
    date: '2024-01-15',
    status: 'approved' as const,
    description: 'New work gloves and safety equipment'
  },
  {
    id: 3,
    employeeName: 'Mike Wilson',
    amount: 85.75,
    category: 'Supplies',
    supplier: 'Seed & Feed Store',
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

export function AdminPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [supplierFilter, setSupplierFilter] = useState('')

  const handleApprove = (id: number) => {
    console.log('Approving receipt:', id)
    // TODO: Implement approval logic
  }

  const handleReject = (id: number) => {
    console.log('Rejecting receipt:', id)
    // TODO: Implement rejection logic
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-semibold">Admin Panel</h3>
          <p className="text-gray-600">Manage all employee receipts and approvals</p>
        </div>
        <div className="flex space-x-2">
          <Input 
            placeholder="🔍 Search receipts..." 
            className="w-64" 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Input 
            placeholder="Filter by supplier..." 
            className="w-48" 
            value={supplierFilter}
            onChange={(e) => setSupplierFilter(e.target.value)}
          />
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-32 px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Employee Receipts</CardTitle>
          <CardDescription>Review and manage expense submissions</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Supplier</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockReceipts.map((receipt) => (
                <TableRow key={receipt.id}>
                  <TableCell>{receipt.employeeName}</TableCell>
                  <TableCell>${receipt.amount.toFixed(2)}</TableCell>
                  <TableCell>{receipt.category}</TableCell>
                  <TableCell>{receipt.supplier}</TableCell>
                  <TableCell>{receipt.date}</TableCell>
                  <TableCell>
                    <StatusBadge status={receipt.status} />
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                      {receipt.status === 'pending' && (
                        <>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="text-green-600 hover:text-green-700"
                            onClick={() => handleApprove(receipt.id)}
                          >
                            Approve
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="text-red-600 hover:text-red-700"
                            onClick={() => handleReject(receipt.id)}
                          >
                            Reject
                          </Button>
                        </>
                      )}
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
