import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog } from '@/components/ui/dialog'
import { usePurchases } from '@/hooks/finance/usePurchases'
import { usePurchaseMutations } from '@/hooks/finance/usePurchaseMutations'
import { useExpenseTypes, useCurrencies } from '@/hooks/finance/useReferenceData'
import { StatusBadge } from '../components/StatusBadge'
import { AddReceiptDialog } from '../components/AddReceiptDialog'
import { useToast } from '@/components/ui/use-toast'

export function TodayPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const { toast } = useToast()
  
  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0]
  
  // Query today's purchases
  const { data: purchases, loading, error, refetch } = usePurchases({
    capturedOn: today,
    isActive: true
  })
  
  // Load reference data
  const { data: expenseTypes } = useExpenseTypes(undefined, { enabled: !loading })
  const { data: currencies } = useCurrencies({ enabled: !loading })
  
  // Mutation hooks for delete operations
  const purchaseMutations = usePurchaseMutations({ capturedOn: today, isActive: true })

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

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this purchase?')) {
      const result = await purchaseMutations.archive(id)
      if (result) {
        toast({
          title: "Success",
          description: "Purchase deleted successfully",
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
  }

  const handleAddSuccess = () => {
    setIsAddDialogOpen(false)
    refetch()
  }

  return (
    <>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-xl font-semibold">Today's Receipts</h3>
            <p className="text-gray-600">Manage your expenses for {new Date().toLocaleDateString()}</p>
          </div>
          <Button onClick={() => setIsAddDialogOpen(true)}>
            ➕ Add Receipt
          </Button>
        </div>

        {loading ? (
          <Card>
            <CardContent className="flex items-center justify-center py-12">
              <div className="text-gray-500">Loading today's receipts...</div>
            </CardContent>
          </Card>
        ) : error ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <div className="text-red-500 mb-4">Error loading receipts</div>
              <p className="text-sm text-gray-600 mb-4">{error.message}</p>
              <Button onClick={() => refetch()}>Retry</Button>
            </CardContent>
          </Card>
        ) : purchases && purchases.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {purchases.map((purchase) => (
              <Card key={purchase.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">
                        {formatAmount(purchase.amount, purchase.currency_id)}
                      </CardTitle>
                      <CardDescription>
                        {resolveExpenseType(purchase.expense_type_id, purchase.other_category)} • Receipt #{purchase.receipt_id}
                      </CardDescription>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <StatusBadge status={purchase.status} />
                      <Badge variant="outline">{formatTime(purchase.captured_timestamp)}</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-end space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDelete(purchase.id)}
                      disabled={purchaseMutations.loading}
                    >
                      🗑️ Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <div className="text-6xl text-gray-400 mb-4">📄</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No receipts today</h3>
              <p className="text-gray-500 text-center mb-4">
                You haven't submitted any receipts today. Click the button above to add your first receipt.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <AddReceiptDialog onClose={handleAddSuccess} />
      </Dialog>
    </>
  )
}
