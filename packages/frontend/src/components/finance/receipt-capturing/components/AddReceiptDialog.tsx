import { useState } from 'react'
import { DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Trash2 } from 'lucide-react'

interface LineItem {
  id: string
  expenseType: string
  otherCategory?: string
  amount: number
  description: string
}

interface AddReceiptDialogProps {
  onClose: () => void
}

export function AddReceiptDialog({ onClose }: AddReceiptDialogProps) {
  const [supplier, setSupplier] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [isReimbursable, setIsReimbursable] = useState(false)
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [lineItems, setLineItems] = useState<LineItem[]>([
    {
      id: '1',
      expenseType: '',
      amount: 0,
      description: ''
    }
  ])

  const addLineItem = () => {
    const newItem: LineItem = {
      id: Date.now().toString(),
      expenseType: '',
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

  const handleSubmit = () => {
    console.log('Submitting receipt:', {
      supplier,
      currency,
      isReimbursable,
      date,
      lineItems
    })
    // TODO: Implement Supabase submission
    onClose()
  }

  const totalAmount = lineItems.reduce((sum, item) => sum + (item.amount || 0), 0)

  return (
    <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Add New Receipt</DialogTitle>
        <DialogDescription>
          Submit a new expense receipt with line items for approval.
        </DialogDescription>
      </DialogHeader>
      
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
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <select 
                  id="currency"
                  value={currency} 
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="ZAR">ZAR (R)</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="reimbursable">Reimbursable</Label>
                <select 
                  id="reimbursable"
                  value={isReimbursable ? 'yes' : 'no'} 
                  onChange={(e) => setIsReimbursable(e.target.value === 'yes')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
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
            <Button type="button" variant="outline" size="sm" onClick={addLineItem}>
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
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Expense Category *</Label>
                    <select 
                      value={item.expenseType} 
                      onChange={(e) => updateLineItem(item.id, 'expenseType', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      <option value="">Select category</option>
                      <option value="fuel">Fuel</option>
                      <option value="equipment">Equipment</option>
                      <option value="supplies">Supplies</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="other">Other</option>
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
                    />
                  </div>
                </div>
                
                {item.expenseType === 'other' && (
                  <div className="space-y-2">
                    <Label>Other Category *</Label>
                    <Input
                      placeholder="Specify category"
                      value={item.otherCategory || ''}
                      onChange={(e) => updateLineItem(item.id, 'otherCategory', e.target.value)}
                    />
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Brief description of the expense"
                    value={item.description}
                    onChange={(e) => updateLineItem(item.id, 'description', e.target.value)}
                  />
                </div>
              </div>
            ))}
            
            <div className="flex justify-end pt-4 border-t">
              <div className="text-lg font-semibold">
                Total: {currency === 'USD' ? '$' : currency === 'EUR' ? '€' : 'R'}{totalAmount.toFixed(2)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="button" onClick={handleSubmit}>
          Submit Receipt
        </Button>
      </DialogFooter>
    </DialogContent>
  )
}
