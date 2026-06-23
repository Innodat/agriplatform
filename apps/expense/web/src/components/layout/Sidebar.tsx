import { Button } from '@/components/ui/button'
import { 
  LayoutDashboard, 
  DollarSign, 
  Truck, 
  Users, 
  Settings,
  Receipt
} from 'lucide-react'

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <nav className="p-4 space-y-2">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Departments</h2>
        </div>
        
        <Button variant="ghost" className="w-full justify-start">
          <LayoutDashboard className="mr-2 h-4 w-4" />
          Dashboard
        </Button>
        
        <div className="space-y-1">
          <Button variant="ghost" className="w-full justify-start">
            <DollarSign className="mr-2 h-4 w-4" />
            Finance
          </Button>
          <div className="ml-6 space-y-1">
            <Button variant="ghost" className="w-full justify-start text-sm">
              <Receipt className="mr-2 h-3 w-3" />
              Receipt Capturing
            </Button>
          </div>
        </div>
        
        <Button variant="ghost" className="w-full justify-start">
          <Truck className="mr-2 h-4 w-4" />
          Logistics
        </Button>
        
        <Button variant="ghost" className="w-full justify-start">
          <Users className="mr-2 h-4 w-4" />
          HR
        </Button>
        
        <Button variant="ghost" className="w-full justify-start">
          <Settings className="mr-2 h-4 w-4" />
          Operations
        </Button>
      </nav>
    </aside>
  )
}
