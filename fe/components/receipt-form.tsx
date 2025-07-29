"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/hooks/use-auth"
import { supabase } from "@/lib/supabase"
import { ArrowLeft, Camera, Plus, Trash2, Save, Upload } from "lucide-react"

interface ExpenseType {
  id: string
  name: string
  expense_category: {
    id: string
    name: string
  }
}

interface PurchaseItem {
  id?: string
  expense_type_id: string
  amount: number
  description: string
  reimburse: boolean
}

interface ReceiptData {
  id?: string
  captured_date: string
  currency: string
  receipt_image?: string
  purchase_items: PurchaseItem[]
}

interface ReceiptFormProps {
  receiptData?: ReceiptData
  onBack: () => void
  onSave: (receipt: ReceiptData) => void
}

export default function ReceiptForm({ receiptData, onBack, onSave }: ReceiptFormProps) {
  const [receipt, setReceipt] = useState<ReceiptData>({
    captured_date: new Date().toISOString().split("T")[0],
    currency: "INR",
    purchase_items: [{ expense_type_id: "", amount: 0, description: "", reimburse: true }],
    ...receiptData,
  })
  const [ownMoney, setOwnMoney] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [receiptImage, setReceiptImage] = useState<string | null>(receiptData?.receipt_image || null)
  const [expenseTypes, setExpenseTypes] = useState<ExpenseType[]>([])
  const [loadingExpenseTypes, setLoadingExpenseTypes] = useState(true)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const dropZoneRef = useRef<HTMLDivElement>(null)
  const { user } = useAuth()
  const [openComboboxes, setOpenComboboxes] = useState<{ [key: number]: boolean }>({})

  // Currency options (you can expand this or fetch from your currency table)
  const currencies = [
    { value: "INR", label: "₹ INR", symbol: "₹" },
    { value: "USD", label: "$ USD", symbol: "$" },
    { value: "EUR", label: "€ EUR", symbol: "€" },
    { value: "GBP", label: "£ GBP", symbol: "£" },
  ]

  const getCurrentCurrencySymbol = () => {
    return currencies.find((c) => c.value === receipt.currency)?.symbol || "₹"
  }

  // Fetch expense types on component mount
  useEffect(() => {
    fetchExpenseTypes()
  }, [])

  const fetchExpenseTypes = async () => {
    try {
      setLoadingExpenseTypes(true)

      const { data, error } = await supabase
        .from("expense_type")
        .select(`
        id,
        name,
        expense_category (
          id,
          name
        )
      `)
        .order("name") // This already orders by name

      if (error) {
        console.error("Error fetching expense types:", error)
        // Fallback data for demo - sorted alphabetically
        const fallbackData = [
          { id: "4", name: "Office Supplies", expense_category: { id: "3", name: "Business" } },
          { id: "1", name: "Other", expense_category: { id: "1", name: "Other" } },
          { id: "2", name: "Groceries", expense_category: { id: "2", name: "Food" } },
          { id: "3", name: "Restaurants", expense_category: { id: "2", name: "Food" } },
        ].sort((a, b) => {
          const displayA = a.name.toLowerCase() === "other" ? "Other" : `${a.expense_category.name} - ${a.name}`
          const displayB = b.name.toLowerCase() === "other" ? "Other" : `${b.expense_category.name} - ${b.name}`
          return displayA.localeCompare(displayB)
        })
        setExpenseTypes(fallbackData)
      } else {
        // Sort the data alphabetically by display name
        const sortedData = (data || []).sort((a, b) => {
          const displayA = a.name.toLowerCase() === "other" ? "Other" : `${a.expense_category.name} - ${a.name}`
          const displayB = b.name.toLowerCase() === "other" ? "Other" : `${b.expense_category.name} - ${b.name}`
          return displayA.localeCompare(displayB)
        })
        setExpenseTypes(sortedData)
      }
    } catch (error) {
      console.error("Error fetching expense types:", error)
      // Fallback data - sorted alphabetically
      const fallbackData = [
        { id: "4", name: "Office Supplies", expense_category: { id: "3", name: "Business" } },
        { id: "1", name: "Other", expense_category: { id: "1", name: "Other" } },
        { id: "2", name: "Groceries", expense_category: { id: "2", name: "Food" } },
        { id: "3", name: "Restaurants", expense_category: { id: "2", name: "Food" } },
      ].sort((a, b) => {
        const displayA = a.name.toLowerCase() === "other" ? "Other" : `${a.expense_category.name} - ${a.name}`
        const displayB = b.name.toLowerCase() === "other" ? "Other" : `${b.expense_category.name} - ${b.name}`
        return displayA.localeCompare(displayB)
      })
      setExpenseTypes(fallbackData)
    } finally {
      setLoadingExpenseTypes(false)
    }
  }

  const getExpenseTypeDisplayName = (expenseType: ExpenseType) => {
    // Special case for "Other" - just show "Other"
    if (expenseType.name.toLowerCase() === "other") {
      return "Other"
    }
    // For all others, show "Category - Type"
    return `${expenseType.expense_category.name} - ${expenseType.name}`
  }

  const getSelectedExpenseType = (expenseTypeId: string) => {
    return expenseTypes.find((et) => et.id === expenseTypeId)
  }

  const isOtherExpenseType = (expenseTypeId: string) => {
    const expenseType = getSelectedExpenseType(expenseTypeId)
    return expenseType?.name.toLowerCase() === "other"
  }

  // Update reimburse field for all items when ownMoney changes
  useEffect(() => {
    setReceipt((prev) => ({
      ...prev,
      purchase_items: prev.purchase_items.map((item) => ({ ...item, reimburse: !ownMoney })),
    }))
  }, [ownMoney])

  const handleImageCapture = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      processImageFile(file)
    }
  }

  const processImageFile = (file: File) => {
    // Validate file type
    if (!file.type.startsWith("image/")) {
      alert("Please select an image file.")
      return
    }

    // Validate file size (e.g., max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      alert("Image file is too large. Please select a file smaller than 10MB.")
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target?.result as string
      setReceiptImage(imageUrl)
      setReceipt((prev) => ({ ...prev, receipt_image: imageUrl }))
    }
    reader.readAsDataURL(file)
  }

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    const imageFile = files.find((file) => file.type.startsWith("image/"))

    if (imageFile) {
      processImageFile(imageFile)
    } else if (files.length > 0) {
      alert("Please drop an image file.")
    }
  }

  const addPurchaseItem = () => {
    setReceipt((prev) => ({
      ...prev,
      purchase_items: [
        ...prev.purchase_items,
        { expense_type_id: "", amount: 0, description: "", reimburse: !ownMoney },
      ],
    }))
  }

  const removePurchaseItem = (index: number) => {
    if (receipt.purchase_items.length > 1) {
      setReceipt((prev) => ({
        ...prev,
        purchase_items: prev.purchase_items.filter((_, i) => i !== index),
      }))
    }
  }

  const updatePurchaseItem = (index: number, field: keyof PurchaseItem, value: any) => {
    setReceipt((prev) => ({
      ...prev,
      purchase_items: prev.purchase_items.map((item, i) => (i === index ? { ...item, [field]: value } : item)),
    }))
  }

  const calculateTotal = () => {
    return receipt.purchase_items.reduce((sum, item) => sum + (item.amount || 0), 0)
  }

  const handleSave = async () => {
    setIsLoading(true)

    try {
      // Here you would save to Supabase
      // For now, we'll just call the onSave callback
      onSave(receipt)
    } catch (error) {
      console.error("Error saving receipt:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const isEditing = !!receiptData?.id

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="bg-teal-600 text-white p-4 flex items-center">
          <Button variant="ghost" size="sm" onClick={onBack} className="text-white hover:bg-teal-700 p-2 mr-3">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-xl font-semibold">{isEditing ? "Edit Receipt" : "Add Receipt"}</h1>
        </div>

        <div className="p-4 space-y-6">
          {/* Receipt Image Capture */}
          <div className="space-y-3">
            <Label className="text-sm font-medium text-gray-700">Receipt Image</Label>

            {receiptImage ? (
              <div className="relative">
                <img
                  src={receiptImage || "/placeholder.svg"}
                  alt="Receipt"
                  className="w-full h-48 object-cover rounded-lg border border-gray-300"
                />
                <div className="absolute top-2 right-2 flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (fileInputRef.current) {
                        fileInputRef.current.setAttribute("capture", "environment")
                        fileInputRef.current.click()
                      }
                    }}
                    className="bg-white/90 hover:bg-white"
                  >
                    <Camera className="h-4 w-4 mr-1" />
                    Scan
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      if (fileInputRef.current) {
                        fileInputRef.current.removeAttribute("capture")
                        fileInputRef.current.click()
                      }
                    }}
                    className="bg-white/90 hover:bg-white"
                  >
                    <Upload className="h-4 w-4 mr-1" />
                    Upload
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {/* Camera Scan Option */}
                <Button
                  variant="outline"
                  onClick={() => {
                    if (fileInputRef.current) {
                      fileInputRef.current.setAttribute("capture", "environment")
                      fileInputRef.current.click()
                    }
                  }}
                  className="h-32 border-2 border-dashed border-gray-300 hover:border-teal-500 flex flex-col items-center justify-center space-y-2 bg-transparent"
                >
                  <Camera className="h-8 w-8 text-gray-400" />
                  <span className="text-sm text-gray-600 text-center">Scan with Camera</span>
                </Button>

                {/* File Upload Option with Drag & Drop */}
                <div
                  ref={dropZoneRef}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => {
                    if (fileInputRef.current) {
                      fileInputRef.current.removeAttribute("capture")
                      fileInputRef.current.click()
                    }
                  }}
                  className={cn(
                    "h-32 border-2 border-dashed flex flex-col items-center justify-center space-y-2 bg-transparent cursor-pointer transition-colors",
                    isDragOver ? "border-teal-500 bg-teal-50" : "border-gray-300 hover:border-teal-500",
                  )}
                >
                  <Upload className={cn("h-8 w-8", isDragOver ? "text-teal-500" : "text-gray-400")} />
                  <span className={cn("text-sm text-center", isDragOver ? "text-teal-600" : "text-gray-600")}>
                    {isDragOver ? "Drop image here" : "Upload Image or Drag & Drop"}
                  </span>
                </div>
              </div>
            )}

            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageCapture} className="hidden" />
          </div>

          {/* Date and Currency Row */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date" className="text-sm font-medium text-gray-700">
                Date
              </Label>
              <Input
                id="date"
                type="date"
                value={receipt.captured_date}
                onChange={(e) => setReceipt((prev) => ({ ...prev, captured_date: e.target.value }))}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency" className="text-sm font-medium text-gray-700">
                Currency
              </Label>
              <Select
                value={receipt.currency}
                onValueChange={(value) => setReceipt((prev) => ({ ...prev, currency: value }))}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select currency" />
                </SelectTrigger>
                <SelectContent>
                  {currencies.map((currency) => (
                    <SelectItem key={currency.value} value={currency.value}>
                      {currency.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Own Money Checkbox */}
          <div className="flex items-center space-x-2">
            <Checkbox id="ownMoney" checked={ownMoney} onCheckedChange={(checked) => setOwnMoney(checked as boolean)} />
            <Label htmlFor="ownMoney" className="text-sm font-medium text-gray-700">
              Own money
            </Label>
          </div>

          {/* Purchase Items */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium text-gray-700">Purchase Items</Label>
              <Button
                variant="outline"
                size="sm"
                onClick={addPurchaseItem}
                className="text-teal-600 border-teal-600 hover:bg-teal-50 bg-transparent"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Item
              </Button>
            </div>

            {receipt.purchase_items.map((item, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Item {index + 1}</span>
                  {receipt.purchase_items.length > 1 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removePurchaseItem(index)}
                      className="text-red-600 hover:text-red-800 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-xs text-gray-600">Spending Type</Label>
                    <Popover
                      open={openComboboxes[index] || false}
                      onOpenChange={(open) => setOpenComboboxes((prev) => ({ ...prev, [index]: open }))}
                    >
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          role="combobox"
                          aria-expanded={openComboboxes[index] || false}
                          className="w-full justify-between mt-1 h-10 bg-transparent"
                        >
                          {item.expense_type_id
                            ? expenseTypes.find((type) => type.id === item.expense_type_id)
                              ? getExpenseTypeDisplayName(
                                  expenseTypes.find((type) => type.id === item.expense_type_id)!,
                                )
                              : "Select type..."
                            : "Select type..."}
                          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-full p-0" align="start">
                        <Command>
                          <CommandInput placeholder="Search spending types..." className="h-9" />
                          <CommandList>
                            <CommandEmpty>No spending type found.</CommandEmpty>
                            <CommandGroup>
                              {loadingExpenseTypes ? (
                                <CommandItem disabled>Loading...</CommandItem>
                              ) : expenseTypes.length === 0 ? (
                                <CommandItem disabled>No expense types found</CommandItem>
                              ) : (
                                expenseTypes.map((expenseType) => (
                                  <CommandItem
                                    key={expenseType.id}
                                    value={getExpenseTypeDisplayName(expenseType)}
                                    onSelect={() => {
                                      updatePurchaseItem(index, "expense_type_id", expenseType.id)
                                      setOpenComboboxes((prev) => ({ ...prev, [index]: false }))
                                    }}
                                  >
                                    <Check
                                      className={cn(
                                        "mr-2 h-4 w-4",
                                        item.expense_type_id === expenseType.id ? "opacity-100" : "opacity-0",
                                      )}
                                    />
                                    {getExpenseTypeDisplayName(expenseType)}
                                  </CommandItem>
                                ))
                              )}
                            </CommandGroup>
                          </CommandList>
                        </Command>
                      </PopoverContent>
                    </Popover>
                  </div>
                  <div>
                    <Label className="text-xs text-gray-600">Amount ({getCurrentCurrencySymbol()})</Label>
                    <Input
                      type="number"
                      value={item.amount || ""}
                      onChange={(e) => updatePurchaseItem(index, "amount", Number.parseFloat(e.target.value) || 0)}
                      placeholder="0.00"
                      className="mt-1"
                    />
                  </div>
                </div>

                {/* Description field - only visible if spending type is "Other" */}
                {isOtherExpenseType(item.expense_type_id) && (
                  <div>
                    <Label className="text-xs text-gray-600">Description</Label>
                    <Input
                      value={item.description}
                      onChange={(e) => updatePurchaseItem(index, "description", e.target.value)}
                      placeholder="Describe the item"
                      className="mt-1"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Total Amount */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold text-gray-700">Total Amount:</span>
              <span className="text-xl font-bold text-teal-600">
                {getCurrentCurrencySymbol()}
                {calculateTotal().toFixed(2)}
              </span>
            </div>
          </div>

          {/* Save Button */}
          <Button
            onClick={handleSave}
            disabled={
              isLoading ||
              loadingExpenseTypes ||
              receipt.purchase_items.some(
                (item) =>
                  !item.expense_type_id ||
                  item.expense_type_id === "loading" ||
                  item.expense_type_id === "no-data" ||
                  !item.amount,
              )
            }
            className="w-full bg-teal-600 hover:bg-teal-700 disabled:bg-gray-400 text-white font-medium py-3 rounded-lg"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {isEditing ? "Update Receipt" : "Save Receipt"}
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
