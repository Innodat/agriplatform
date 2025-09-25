"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Calendar, DollarSign, FileText, Plus, Search, Users, Eye, Edit, Trash2, Download } from 'lucide-react'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

// Mock data - replace with Supabase queries
const mockReceipts = [
  {
    id: 1,
    employeeName: "John Smith",
    amount: 45.50,
    category: "Fuel",
    date: "2024-01-15",
    status: "pending",
    description: "Diesel for tractor maintenance"
  },
  {
    id: 2,
    employeeName: "Sarah Johnson",
    amount: 120.00,
    category: "Equipment",
    date: "2024-01-15",
    status: "approved",
    description: "New work gloves and safety equipment"
  },
  {
    id: 3,
    employeeName: "Mike Wilson",
    amount: 85.75,
    category: "Supplies",
    date: "2024-01-14",
    status: "rejected",
    description: "Seeds for spring planting"
  }
]

const mockTodayReceipts = [
  {
    id: 4,
    amount: 32.25,
    category: "Fuel",
    description: "Gas for pickup truck",
    timestamp: "09:30 AM"
  },
  {
    id: 5,
    amount: 67.80,
    category: "Maintenance",
    description: "Oil change for harvester",
    timestamp: "11:15 AM"
  }
]

export default function AgriPlatform() {
  const [activeTab, setActiveTab] = useState("overview")
  const [isAddReceiptOpen, setIsAddReceiptOpen] = useState(false)
  const [userRole, setUserRole] = useState("employee") // employee, admin

  const ReceiptForm = () => (
    <div className="grid gap-4 py-4">
      <div className="grid gap-2">
        <Label htmlFor="amount">Amount ($)</Label>
        <Input id="amount" type="number" step="0.01" placeholder="0.00" />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="category">Category</Label>
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="fuel">Fuel</SelectItem>
            <SelectItem value="equipment">Equipment</SelectItem>
            <SelectItem value="supplies">Supplies</SelectItem>
            <SelectItem value="maintenance">Maintenance</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="grid gap-2">
        <Label htmlFor="description">Description</Label>
        <Textarea id="description" placeholder="Brief description of the expense" />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="receipt">Receipt Image</Label>
        <Input id="receipt" type="file" accept="image/*" />
      </div>
    </div>
  )

  const StatusBadge = ({ status }: { status: string }) => {
    const variants = {
      pending: "bg-yellow-100 text-yellow-800",
      approved: "bg-green-100 text-green-800",
      rejected: "bg-red-100 text-red-800"
    }
    return (
      <Badge className={variants[status as keyof typeof variants]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-900">AgriPlatform</h1>
                <p className="text-sm text-gray-500">HR Management System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Select value={userRole} onValueChange={setUserRole}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="employee">Employee</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
              <div className="text-sm text-gray-500">
                Welcome, {userRole === "admin" ? "Financial Admin" : "John Doe"}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <div className="flex justify-between items-center">
              <TabsList className="grid w-full max-w-md grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="today">Today's Receipts</TabsTrigger>
                {userRole === "admin" && <TabsTrigger value="admin">Admin Panel</TabsTrigger>}
              </TabsList>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => console.log('Exporting to Sage...')}>
                    Export to Sage
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => console.log('Exporting to CSV...')}>
                    Export to CSV
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Receipts</CardTitle>
                    <FileText className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {userRole === "admin" ? "156" : "23"}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {userRole === "admin" ? "All employees" : "Your submissions"}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      ${userRole === "admin" ? "12,450.75" : "1,234.50"}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      This month
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Pending</CardTitle>
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {userRole === "admin" ? "24" : "3"}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Awaiting approval
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Employees</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {userRole === "admin" ? "12" : "1"}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Active users
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Receipts</CardTitle>
                  <CardDescription>
                    {userRole === "admin" ? "Latest submissions from all employees" : "Your recent expense submissions"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        {userRole === "admin" && <TableHead>Employee</TableHead>}
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
                          {userRole === "admin" && <TableCell>{receipt.employeeName}</TableCell>}
                          <TableCell>${receipt.amount.toFixed(2)}</TableCell>
                          <TableCell>{receipt.category}</TableCell>
                          <TableCell>{receipt.date}</TableCell>
                          <TableCell>
                            <StatusBadge status={receipt.status} />
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button variant="ghost" size="sm">
                                <Eye className="h-4 w-4" />
                              </Button>
                              {userRole === "admin" && (
                                <>
                                  <Button variant="ghost" size="sm">
                                    <Edit className="h-4 w-4" />
                                  </Button>
                                  <Button variant="ghost" size="sm">
                                    <Trash2 className="h-4 w-4" />
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
            </TabsContent>

            {/* Today's Receipts Tab */}
            <TabsContent value="today" className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold">Today's Receipts</h2>
                  <p className="text-gray-600">Manage your expenses for {new Date().toLocaleDateString()}</p>
                </div>
                <Dialog open={isAddReceiptOpen} onOpenChange={setIsAddReceiptOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Receipt
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                      <DialogTitle>Add New Receipt</DialogTitle>
                      <DialogDescription>
                        Submit a new expense receipt for approval.
                      </DialogDescription>
                    </DialogHeader>
                    <ReceiptForm />
                    <DialogFooter>
                      <Button type="submit" onClick={() => setIsAddReceiptOpen(false)}>
                        Submit Receipt
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                {mockTodayReceipts.map((receipt) => (
                  <Card key={receipt.id}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">${receipt.amount.toFixed(2)}</CardTitle>
                          <CardDescription>{receipt.category}</CardDescription>
                        </div>
                        <Badge variant="outline">{receipt.timestamp}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600">{receipt.description}</p>
                      <div className="flex justify-end space-x-2 mt-4">
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {mockTodayReceipts.length === 0 && (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <FileText className="h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No receipts today</h3>
                    <p className="text-gray-500 text-center mb-4">
                      You haven't submitted any receipts today. Click the button above to add your first receipt.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Admin Panel Tab */}
            {userRole === "admin" && (
              <TabsContent value="admin" className="space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold">Admin Panel</h2>
                    <p className="text-gray-600">Manage all employee receipts and approvals</p>
                  </div>
                  <div className="flex space-x-2">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="Search receipts..." className="pl-8" />
                    </div>
                    <Select>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Filter" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                      </SelectContent>
                    </Select>
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
                            <TableCell>{receipt.date}</TableCell>
                            <TableCell>
                              <StatusBadge status={receipt.status} />
                            </TableCell>
                            <TableCell>
                              <div className="flex space-x-2">
                                <Button variant="outline" size="sm">
                                  View
                                </Button>
                                {receipt.status === "pending" && (
                                  <>
                                    <Button variant="outline" size="sm" className="text-green-600">
                                      Approve
                                    </Button>
                                    <Button variant="outline" size="sm" className="text-red-600">
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
              </TabsContent>
            )}
          </Tabs>
        </div>
      </main>
    </div>
  )
}
