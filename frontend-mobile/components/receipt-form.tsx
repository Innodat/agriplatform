"use client"

// Fix all remaining TypeScript lint errors: add missing parameter types, use React.JSX.Element for JSX, and ensure all arrow functions are typed

// Utility to truncate text for dropdown display
function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 1) + "…";
}

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
  other_category: string
  reimbursable: boolean
  captured_timestamp?: string
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
  const { toast } = require("@/hooks/use-toast")
  const [receipt, setReceipt] = useState<ReceiptData>({
    currency: "INR",
    purchase_items: [{ expense_type_id: "", amount: 0, other_category: "", reimbursable: true, captured_timestamp: new Date().toISOString().split("T")[0] }],
    ...receiptData,
  })
  // Checkbox is checked if some purchase items are reimbursable
  const [ownMoney, setOwnMoney] = useState(() => {
    if (receiptData?.purchase_items && receiptData.purchase_items.length > 0) {
      return receiptData.purchase_items.some(item => item.reimbursable === true);
    }
    return true;
  });
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

  const fetchExpenseTypes = async (): Promise<void> => {
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
      const sortExpenseTypes = (types: ExpenseType[]): ExpenseType[] => {
        // Group by expense_category, sort each group alphabetically, but put 'Other' last within its category
        const grouped: { [cat: string]: ExpenseType[] } = {};
        types.forEach((type: ExpenseType) => {
          if (!grouped[type.expense_category.name]) grouped[type.expense_category.name] = [];
          grouped[type.expense_category.name].push(type);
        });
        // Sort each group: all except 'Other' alphabetically, then 'Other' last
        const sortedGroups = Object.keys(grouped)
          .sort()
          .map((cat: string) => {
            const group = grouped[cat];
            const others = group.filter((t) => t.name.toLowerCase() === "other");
            const rest = group.filter((t) => t.name.toLowerCase() !== "other").sort((a, b) => a.name.localeCompare(b.name));
            return [...rest, ...others];
          });
        // Flatten all groups
        return ([] as ExpenseType[]).concat(...sortedGroups);
      };
      if (error) {
        console.error("Error fetching expense types:", error)
        // Fallback data for demo
        const fallbackData = [
          { id: "4", name: "Office Supplies", expense_category: { id: "3", name: "Business" } },
          { id: "1", name: "Other", expense_category: { id: "1", name: "Other" } },
          { id: "2", name: "Groceries", expense_category: { id: "2", name: "Food" } },
          { id: "3", name: "Restaurants", expense_category: { id: "2", name: "Food" } },
        ];
        setExpenseTypes(sortExpenseTypes(fallbackData));
      } else {
        setExpenseTypes(sortExpenseTypes(data || []));
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
        const displayA = `${a.expense_category.name} - ${a.name}`
        const displayB = `${b.expense_category.name} - ${b.name}`
        return displayA.localeCompare(displayB)
      })
      setExpenseTypes(fallbackData)
    } finally {
      setLoadingExpenseTypes(false)
    }
  }

  const getExpenseTypeDisplayName = (expenseType: ExpenseType) => {
    // For all others, show "Category - Type"
    return `${expenseType.expense_category.name} - ${expenseType.name}`
  }

  const getSelectedExpenseType = (expenseTypeId: string): ExpenseType | undefined => {
    return expenseTypes.find((et: ExpenseType) => et.id === expenseTypeId)
  }

  const isOtherExpenseType = (expenseTypeId: string): boolean => {
    const expenseType = getSelectedExpenseType(expenseTypeId)
    return expenseType?.name.toLowerCase() === "other"
  }

  // Update reimbursable field for all items when ownMoney changes
  useEffect(() => {
    setReceipt((prev: ReceiptData) => {
      const updated = {
        ...prev,
        purchase_items: prev.purchase_items.map((item: PurchaseItem) => ({ ...item, reimbursable: ownMoney })),
      };
      return updated;
    });
  }, [ownMoney]);

  const handleImageCapture = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0]
    if (file) {
      processImageFile(file)
    }
  }

  const processImageFile = (file: File): void => {
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
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>): void => {
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

  const addPurchaseItem = (): void => {
    setReceipt((prev: ReceiptData) => ({
      ...prev,
      purchase_items: [
        ...prev.purchase_items,
        { expense_type_id: "", amount: 0, other_category: "", reimbursable: ownMoney },
      ],
    }))
  }

  const removePurchaseItem = (index: number): void => {
    if (receipt.purchase_items.length > 1) {
      setReceipt((prev: ReceiptData) => ({
        ...prev,
        purchase_items: prev.purchase_items.filter((_, i) => i !== index),
      }))
    }
  }

  const updatePurchaseItem = (index: number, field: keyof PurchaseItem, value: any): void => {
    setReceipt((prev: ReceiptData) => ({
      ...prev,
      purchase_items: prev.purchase_items.map((item: PurchaseItem, i: number) => (i === index ? { ...item, [field]: value } : item)),
    }))
  }

  const calculateTotal = (): number => {
    return receipt.purchase_items.reduce((sum: number, item: PurchaseItem) => sum + (item.amount || 0), 0)
  }

  const handleSave = async (): Promise<void> => {
    setIsLoading(true)
    let errorOccurred = false;
    try {
      // Save to Supabase
      if (isEditing && receiptData?.id) {
        // Update modified_timestamp in receipt
        const { error: receiptError } = await supabase
          .from("receipt")
          .update({ modified_timestamp: new Date().toISOString() })
          .eq("id", receiptData.id);
        if (receiptError) throw receiptError;
      }

      // Insert or update purchase items
      for (const item of receipt.purchase_items) {
        console.log("Saving purchase item payload:", item);
        if (isEditing && item.id) {
          const { error: purchaseError, data: updateData } = await supabase
            .from("purchase")
            .update({
              expense_type_id: item.expense_type_id,
              amount: item.amount,
              other_category: item.other_category,
              reimbursable: item.reimbursable,
              captured_timestamp: item.captured_timestamp || new Date().toISOString().split("T")[0],
            })
            .eq("id", item.id);
          console.log("Supabase update response:", { error: purchaseError, data: updateData });
          if (purchaseError) throw purchaseError;
        } else if (receiptData?.id) {
          const { error: purchaseError, data: insertData } = await supabase
            .from("purchase")
            .insert({
              receipt_id: receiptData.id,
              expense_type_id: item.expense_type_id,
              amount: item.amount,
              other_category: item.other_category,
              reimbursable: item.reimbursable,
              captured_timestamp: item.captured_timestamp || new Date().toISOString().split("T")[0],
            });
          console.log("Supabase insert response:", { error: purchaseError, data: insertData });
          if (purchaseError) throw purchaseError;
        }
      }
    } catch (error: any) {
      errorOccurred = true;
      console.error("Error saving receipt:", error);
      if (toast) {
        toast({
          title: "Error saving receipt",
          description: error?.message || "An unexpected error occurred.",
          variant: "destructive",
        });
      } else {
        alert("Error saving receipt: " + (error?.message || "An unexpected error occurred."));
      }
    } finally {
      setIsLoading(false);
      if (!errorOccurred) {
        onSave(receipt);
      }
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
                value={
                  receipt.purchase_items[0]?.captured_timestamp
                    ? receipt.purchase_items[0].captured_timestamp.length === 10
                      ? receipt.purchase_items[0].captured_timestamp
                      : receipt.purchase_items[0].captured_timestamp.split("T")[0]
                    : new Date().toISOString().split("T")[0]
                }
                onChange={(e) => setReceipt((prev) => ({
                  ...prev,
                  purchase_items: prev.purchase_items.map((item, idx) => ({
                    ...item,
                    captured_timestamp: e.target.value,
                  })),
                }))}
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
            <Checkbox
              id="ownMoney"
              checked={ownMoney}
              onCheckedChange={(checked) => setOwnMoney(checked as boolean)}
            />
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

            {receipt.purchase_items.map((item: PurchaseItem, index: number) => (
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
                      onOpenChange={(open: boolean) => setOpenComboboxes((prev) => ({ ...prev, [index]: open }))}
                    >
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          role="combobox"
                          aria-expanded={openComboboxes[index] || false}
                          className="w-full justify-between mt-1 h-10 bg-transparent"
                        >
                          <span
                            style={{
                              maxWidth: "calc(100% - 2rem)",
                              display: "inline-block",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                              verticalAlign: "middle",
                            }}
                          >
                            {item.expense_type_id
                              ? expenseTypes.find((type: ExpenseType) => type.id === item.expense_type_id)
                                ? truncateText(getExpenseTypeDisplayName(
                                    expenseTypes.find((type: ExpenseType) => type.id === item.expense_type_id)!,
                                  ), 30)
                                : "Select type..."
                              : "Select type..."}
                          </span>
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
                                (() => {
                                  // Group expenseTypes by category, and sort each group alphabetically, but put 'Other' last within its category
                                  const grouped: { [cat: string]: ExpenseType[] } = {};
                                  expenseTypes.forEach((type: ExpenseType) => {
                                    if (!grouped[type.expense_category.name]) grouped[type.expense_category.name] = [];
                                    grouped[type.expense_category.name].push(type);
                                  });
                                  // Render each category group with header
                                  const result: React.JSX.Element[] = [];
                                  Object.keys(grouped).sort().forEach((cat: string) => {
                                    result.push(
                                      <div key={cat} className="px-2 py-1 text-xs font-semibold text-gray-500 bg-gray-50">
                                        {cat}
                                      </div>
                                    );
                                    // Sort all except 'Other' alphabetically, then 'Other' last
                                    const group = grouped[cat];
                                    const others = group.filter((t) => t.name.toLowerCase() === "other");
                                    const rest = group.filter((t) => t.name.toLowerCase() !== "other").sort((a, b) => a.name.localeCompare(b.name));
                                    [...rest, ...others].forEach((expenseType: ExpenseType) => {
                                      result.push(
                                        <CommandItem
                                          key={expenseType.id}
                                          value={getExpenseTypeDisplayName(expenseType)}
                                          onSelect={() => {
                                            updatePurchaseItem(index, "expense_type_id", expenseType.id);
                                            setOpenComboboxes((prev: Record<number, boolean>) => ({ ...prev, [index]: false }));
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
                                      );
                                    });
                                  });
                                  return result;
                                })()
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
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => updatePurchaseItem(index, "amount", Number.parseFloat(e.target.value) || 0)}
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
                      value={item.other_category ?? ""}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => updatePurchaseItem(index, "other_category", e.target.value)}
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
