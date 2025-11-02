import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { usePurchases } from '@/hooks/finance/usePurchases'
import { usePurchaseMutations } from '@/hooks/finance/usePurchaseMutations'
import { useExpenseTypes, useCurrencies } from '@/hooks/finance/useReferenceData'
import { StatusBadge } from '../components/StatusBadge'
import { useToast } from '@/components/ui/use-toast'
import type { PurchaseStatus } from '@/types'

export function AdminPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<PurchaseStatus | 'all'>('all')
  const [supplierFilter] = useState('')
  const { toast } = useToast()

  // Query all active purchases
  const { data: purchases, loading, error, refetch } = usePurchases({ isActive: true })
  
  // Load reference data
  const { data: expenseTypes } = useExpenseTypes(undefined, { enabled: !loading })
  const { data: currencies } = useCurrencies({ enabled: !loading })
  
  // Mutation hooks
  const purchaseMutations = usePurchaseMutations({ isActive: true })

  // Create lookup maps for reference data
  const expenseTypeMap = useMemo(() => {
    const map = new Map<number, string>()
    expenseTypes.forEach((type) => {
      map.set(type.id, type.name)
    })
    return map
  }, [expenseTypes])

  const currencyMap = useMemo(() => {
    const map = new Map<number, string>()
    currencies.forEach((currency) => {
      map.set(currency.id, currency.symbol ?? currency.name)
    })
    return map
  }, [currencies])

  const formatAmount = (amount: number, currencyId?: number | null) => {
    const symbol = currencyId ? currencyMap.get(currencyId) : null
    return symbol ? `${symbol} ${amount.toFixed(2)}` : `K ${amount.toFixed(2)}`
  }

  const resolveExpenseType = (expenseTypeId?: number | null, otherCategory?: string | null) => {
    if (otherCategory) return otherCategory
    if (!expenseTypeId) return 'Other'
    return expenseTypeMap.get(expenseTypeId) ?? `Type #${expenseTypeId}`
  }

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  // Filter purchases based on search and filters
  const filteredPurchases = useMemo(() => {
    if (!purchases) return []
    
    return purchases.filter((purchase) => {
      // Status filter
      if (statusFilter !== 'all' && purchase.status !== statusFilter) {
        return false
      }

      // Search term filter (searches in expense type and other_category)
      if (searchTerm) {
        const expenseType = resolveExpenseType(purchase.expense_type_id, purchase.other_category).toLowerCase()
        const receiptId = purchase.receipt_id?.toString() || ''
        const searchLower = searchTerm.toLowerCase()
        
        if (!expenseType.includes(searchLower) && !receiptId.includes(searchLower)) {
          return false
        }
      }

      // Supplier filter - Note: We don't have supplier in purchase table, would need to join with receipt
      // For now, we'll skip this filter
      
      return true
    })
  }, [purchases, statusFilter, searchTerm, supplierFilter])

  const handleApprove = async (id: number) => {
    const result = await purchaseMutations.updateStatus(id, 'approved')
    if (result) {
      toast({
        title: "Success",
        description: "Purchase approved successfully",
        variant: "success",
      })
      refetch()
    } else if (purchaseMutations.error) {
      toast({
        title: "Error",
        description: purchaseMutations.error.message,
        variant: "destructive",
      })
    }
  }

  const handleReject = async (id: number) => {
    const result = await purchaseMutations.updateStatus(id, 'rejected')
    if (result) {
      toast({
        title: "Success",
        description: "Purchase rejected successfully",
        variant: "success",
      })
      refetch()
    } else if (purchaseMutations.error) {
      toast({
        title: "Error",
        description: purchaseMutations.error.message,
        variant: "destructive",
      })
    }
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
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value as PurchaseStatus | 'all')}
            className="w-32 px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="querying">Querying</option>
          </select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Employee Receipts</CardTitle>
          <CardDescription>
            Review and manage expense submissions ({filteredPurchases.length} {filteredPurchases.length === 1 ? 'item' : 'items'})
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-500">Loading purchases...</div>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="text-red-500 mb-4">Error loading purchases</div>
              <p className="text-sm text-gray-600 mb-4">{error.message}</p>
              <Button onClick={() => refetch()}>Retry</Button>
            </div>
          ) : filteredPurchases.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="text-6xl text-gray-400 mb-4">📄</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No purchases found</h3>
              <p className="text-gray-500">
                {purchases && purchases.length > 0 
                  ? 'Try adjusting your filters to see more results.'
                  : 'No purchases have been submitted yet.'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Receipt ID</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Expense Type</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredPurchases.map((purchase) => (
                  <TableRow key={purchase.id}>
                    <TableCell>#{purchase.receipt_id || 'N/A'}</TableCell>
                    <TableCell>{formatAmount(purchase.amount, purchase.currency_id)}</TableCell>
                    <TableCell>{resolveExpenseType(purchase.expense_type_id, purchase.other_category)}</TableCell>
                    <TableCell>{formatDate(purchase.captured_timestamp)}</TableCell>
                    <TableCell>
                      <StatusBadge status={purchase.status} />
                    </TableCell>
                    <TableCell className="text-xs text-gray-500">
                      {purchase.user_id ? purchase.user_id.substring(0, 8) + '...' : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        {purchase.status === 'pending' && (
                          <>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="text-green-600 hover:text-green-700"
                              onClick={() => handleApprove(purchase.id)}
                              disabled={purchaseMutations.loading}
                            >
                              Approve
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="text-red-600 hover:text-red-700"
                              onClick={() => handleReject(purchase.id)}
                              disabled={purchaseMutations.loading}
                            >
                              Reject
                            </Button>
                          </>
                        )}
                        {purchase.status !== 'pending' && (
                          <Button variant="outline" size="sm" disabled>
                            {purchase.status === 'approved' ? 'Approved' : purchase.status === 'rejected' ? 'Rejected' : 'Querying'}
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
