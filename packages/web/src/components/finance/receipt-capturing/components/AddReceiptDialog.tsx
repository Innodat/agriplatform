import { useState } from 'react'
import { DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Trash2 } from 'lucide-react'
import { useReceiptMutations } from '@/hooks/finance/useReceiptMutations'
import { usePurchaseMutations } from '@/hooks/finance/usePurchaseMutations'
import { useExpenseTypes, useCurrencies } from '@/hooks/finance/useReferenceData'
import { supabase } from '@/lib/supabase/client'
import { useToast } from '@/components/ui/use-toast'
import type { ReceiptInsert, PurchaseInsert } from '@/types'

interface LineItem {
  id: string
  expenseTypeId: number | null
  otherCategory?: string
  amount: number
  description: string
}

interface AddReceiptDialogProps {
  onClose: () => void
}

export function AddReceiptDialog({ onClose }: AddReceiptDialogProps) {
  const [supplier, setSupplier] = useState('')
  const [currencyId, setCurrencyId] = useState<number | null>(null)
  const [isReimbursable, setIsReimbursable] = useState(false)
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [lineItems, setLineItems] = useState<LineItem[]>([
    {
      id: '1',
      expenseTypeId: null,
      amount: 0,
      description: ''
    }
  ])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  // Load reference data
  const { data: expenseTypes } = useExpenseTypes()
  const { data: currencies } = useCurrencies()

  // Mutation hooks
  const receiptMutations = useReceiptMutations()
  const purchaseMutations = usePurchaseMutations()

  // Set default currency to first one if available
  if (currencyId === null && currencies.length > 0) {
    setCurrencyId(currencies[0].id)
  }

  const addLineItem = () => {
    const newItem: LineItem = {
      id: Date.now().toString(),
      expenseTypeId: null,
      amount: 0,
      description: ''
    }
    setLineItems([...lineItems, newItem])
  }

  const removeLineItem = (id: string) => {
    if (lineItems.length > 1) {
      setLineItems(lineItems.filter(item => item.id !== id))
    }
  }

  const updateLineItem = (id: string, field: keyof LineItem, value: any) => {
    setLineItems(lineItems.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ))
  }

  const handleSubmit = async () => {
    setError(null)
    setIsSubmitting(true)

    try {
      // Validate inputs
      if (!supplier.trim()) {
        throw new Error('Supplier is required')
      }

      if (!currencyId) {
        throw new Error('Currency is required')
      }

      if (lineItems.length === 0) {
        throw new Error('At least one line item is required')
      }

      for (const item of lineItems) {
        if (!item.expenseTypeId && !item.otherCategory) {
          throw new Error('Each line item must have an expense type')
        }
        if (item.amount <= 0) {
          throw new Error('Each line item must have a positive amount')
        }
      }

      // Get current user
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        throw new Error('You must be logged in to submit a receipt')
      }

      // Create receipt
      const receiptPayload: ReceiptInsert = {
        supplier,
        content_id: null, // TODO: Handle file upload
        created_by: user.id,
        updated_by: user.id,
      }

      const receipt = await receiptMutations.create(receiptPayload)
      if (!receipt) {
        throw new Error(receiptMutations.error?.message || 'Failed to create receipt')
      }

      // Create purchases for each line item
      const purchasePromises = lineItems.map(async (item) => {
        const purchasePayload: PurchaseInsert = {
          receipt_id: receipt.id,
          expense_type_id: item.expenseTypeId,
          other_category: item.otherCategory || null,
          currency_id: currencyId,
          amount: item.amount,
          captured_timestamp: `${date}T${new Date().toTimeString().split(' ')[0]}`,
          reimbursable: isReimbursable,
          user_id: user.id,
          status: 'pending',
          created_by: user.id,
          updated_by: user.id,
        }

        const purchase = await purchaseMutations.create(purchasePayload)
        if (!purchase) {
          throw new Error(purchaseMutations.error?.message || 'Failed to create purchase')
        }
        return purchase
      })

      await Promise.all(purchasePromises)

      // Success - show toast and close dialog
      toast({
        title: "Success",
        description: `Receipt submitted with ${lineItems.length} ${lineItems.length === 1 ? 'item' : 'items'}`,
        variant: "success",
      })
      onClose()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const totalAmount = lineItems.reduce((sum, item) => sum + (item.amount || 0), 0)
  const selectedCurrency = currencies.find(c => c.id === currencyId)
  const currencySymbol = selectedCurrency?.symbol || selectedCurrency?.name || 'K'

  return (
    <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Add New Receipt</DialogTitle>
        <DialogDescription>
          Submit a new expense receipt with line items for approval.
        </DialogDescription>
      </DialogHeader>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* Receipt Header */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Receipt Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="supplier">Supplier *</Label>
                <Input
                  id="supplier"
                  placeholder="Enter supplier name"
                  value={supplier}
                  onChange={(e) => setSupplier(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Currency *</Label>
                <select 
                  id="currency"
                  value={currencyId || ''} 
                  onChange={(e) => setCurrencyId(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  disabled={isSubmitting}
                >
                  <option value="">Select currency</option>
                  {currencies.map((currency) => (
                    <option key={currency.id} value={currency.id}>
                      {currency.name} ({currency.symbol || currency.name})
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date *</Label>
                <Input
                  id="date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  disabled={isSubmitting}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reimbursable">Reimbursable</Label>
                <select 
                  id="reimbursable"
                  value={isReimbursable ? 'yes' : 'no'} 
                  onChange={(e) => setIsReimbursable(e.target.value === 'yes')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  disabled={isSubmitting}
                >
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Line Items */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Line Items</CardTitle>
            <Button 
              type="button" 
              variant="outline" 
              size="sm" 
              onClick={addLineItem}
              disabled={isSubmitting}
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Item
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {lineItems.map((item, index) => (
              <div key={item.id} className="border rounded-lg p-4 space-y-4">
                <div className="flex justify-between items-center">
                  <h4 className="font-medium">Item {index + 1}</h4>
                  {lineItems.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeLineItem(item.id)}
                      disabled={isSubmitting}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Expense Type *</Label>
                    <select 
                      value={item.expenseTypeId || ''} 
                      onChange={(e) => updateLineItem(item.id, 'expenseTypeId', e.target.value ? Number(e.target.value) : null)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      disabled={isSubmitting}
                    >
                      <option value="">Select type</option>
                      {expenseTypes.map((type) => (
                        <option key={type.id} value={type.id}>
                          {type.name}
                        </option>
                      ))}
                      <option value="0">Other</option>
                    </select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Amount *</Label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={item.amount || ''}
                      onChange={(e) => updateLineItem(item.id, 'amount', parseFloat(e.target.value) || 0)}
                      disabled={isSubmitting}
                    />
                  </div>
                </div>
                
                {item.expenseTypeId === 0 && (
                  <div className="space-y-2">
                    <Label>Other Category *</Label>
                    <Input
                      placeholder="Specify category"
                      value={item.otherCategory || ''}
                      onChange={(e) => updateLineItem(item.id, 'otherCategory', e.target.value)}
                      disabled={isSubmitting}
                    />
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Brief description of the expense"
                    value={item.description}
                    onChange={(e) => updateLineItem(item.id, 'description', e.target.value)}
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            ))}
            
            <div className="flex justify-end pt-4 border-t">
              <div className="text-lg font-semibold">
                Total: {currencySymbol} {totalAmount.toFixed(2)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <DialogFooter>
        <Button 
          type="button" 
          variant="outline" 
          onClick={onClose}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button 
          type="button" 
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Receipt'}
        </Button>
      </DialogFooter>
    </DialogContent>
  )
}
