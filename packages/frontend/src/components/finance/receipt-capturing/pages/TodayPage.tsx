import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

// Mock data - TODO: Replace with Supabase queries
const mockTodayReceipts = [
  {
    id: 4,
    amount: 32.25,
    category: 'Fuel',
    supplier: 'Shell Station',
    description: 'Gas for pickup truck',
    timestamp: '09:30 AM',
    status: 'pending' as const
  },
  {
    id: 5,
    amount: 67.80,
    category: 'Maintenance',
    supplier: 'AutoCare Services',
    description: 'Oil change for harvester',
    timestamp: '11:15 AM',
    status: 'pending' as const
  }
]

export function TodayPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-semibold">Today's Receipts</h3>
          <p className="text-gray-600">Manage your expenses for {new Date().toLocaleDateString()}</p>
        </div>
        <Button>
          ➕ Add Receipt
        </Button>
      </div>

      {mockTodayReceipts.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {mockTodayReceipts.map((receipt) => (
            <Card key={receipt.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">${receipt.amount.toFixed(2)}</CardTitle>
                    <CardDescription>{receipt.category} • {receipt.supplier}</CardDescription>
                  </div>
                  <Badge variant="outline">{receipt.timestamp}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">{receipt.description}</p>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" size="sm">
                    ✏️ Edit
                  </Button>
                  <Button variant="outline" size="sm">
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
  )
}
