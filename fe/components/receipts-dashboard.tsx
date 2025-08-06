"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { supabase } from "@/lib/supabase"
import { useAuth } from "@/hooks/use-auth"
import { Pencil, ChevronLeft, ChevronRight, LogOut, User } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import ReceiptForm from "./receipt-form"

interface Receipt {
  id: string
  category: string
  amount: number
  captured_date: string
  is_today: boolean
  purchase_items?: any[]
}

interface EditingReceipt {
  id: string
  category: string
  amount: number
}

export default function ReceiptsDashboard() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [loading, setLoading] = useState(true)
  const [editingReceipt, setEditingReceipt] = useState<EditingReceipt | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null)
  const [isSigningOut, setIsSigningOut] = useState(false)
  const { user, signOut } = useAuth()
  // Adaptive itemsPerPage: 5 for mobile, 8 for tablet, 10 for desktop
  const getItemsPerPage = () => {
    if (typeof window !== "undefined") {
      const width = window.innerWidth;
      if (width <= 600) return 5; // mobile
      if (width <= 900) return 8; // tablet
      return 10; // desktop
    }
    return 10;
  };
  const [itemsPerPage, setItemsPerPage] = useState(getItemsPerPage());

  useEffect(() => {
    const handleResize = () => {
      setItemsPerPage(getItemsPerPage());
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Demo data for preview (will be replaced with real data when Supabase is connected)
  const demoReceipts: Receipt[] = Array.from({ length: 25 }, (_, i) => {
    const categories = [
      "Stationary, Office",
      "Toiletries",
      "Food, Beverages",
      "Food",
      "Toiletries, Personal Care",
      "Toys, Entertainment",
      "Stationary",
      "Electronics",
      "Transport",
      "Medical",
      "Books",
      "Clothing",
      "Grocery",
      "Dining",
      "Subscription",
      "Gift",
      "Pet Care",
      "Fitness",
      "Travel",
      "Education",
      "Insurance",
      "Charity",
      "Home",
      "Garden",
      "Miscellaneous"
    ];
    const today = new Date();
    const date = new Date(today.getTime() - (i * 86400000)); // spread dates over last 25 days
    return {
      id: (i + 1).toString(),
      category: categories[i % categories.length],
      amount: Math.floor(Math.random() * 5000) + 50,
      captured_date: date.toLocaleDateString("en-GB"),
      is_today: date.toDateString() === today.toDateString(),
      purchase_items: [],
    };
  });

  useEffect(() => {
    if (user) {
      fetchReceipts()
    }
  }, [user])

  const fetchReceipts = async () => {
    try {
      setLoading(true)

      // Fetch receipts and their purchases
      const { data, error } = await supabase
        .from("receipt")
        .select(`
          id,
          is_active,
          created_timestamp,
          created_user_id,
          modified_user_id,
          modified_timestamp,
          purchase (
            *,
            expense_type (
              name,
              expense_category (
                name
              )
            )
          )
        `)
        .order("created_timestamp", { ascending: false })

      if (error) {
        console.log("Database query error:", error.message)
        console.log("Using demo data")
        setReceipts(demoReceipts)
      } else if (data && data.length > 0) {
        console.log("Fetched data:", data)

        // Process the data to match our interface - one entry per receipt
        const processedReceipts = data.map((receipt: any) => {
          // Extract unique categories from purchase items
          const allCategories =
            receipt.purchase?.map((item: any) => {
              // If joined data is available, use expense_type and expense_category names
              if (item.expense_type && item.expense_type.expense_category) {
                return `${item.expense_type.expense_category.name}-${item.expense_type.name}`;
              }
              console.log("No expense_type found for item:", item);
            }) || [];
          const uniqueCategories = [...new Set(allCategories)];
          const categories = uniqueCategories.join(", ");

          const totalAmount = receipt.purchase?.reduce((sum: number, item: any) => sum + (item.amount || 0), 0) || 0;

          // Use the latest captured_timestamp from purchases as the receipt date
          let capturedDate = receipt.purchase && receipt.purchase.length > 0
            ? new Date(Math.max(...receipt.purchase.map((item: any) => new Date(item.captured_timestamp).getTime())))
            : new Date(receipt.created_timestamp);
          const today = new Date();
          const isToday = capturedDate.toDateString() === today.toDateString();

          return {
            id: receipt.id,
            category: categories,
            amount: totalAmount,
            captured_date: capturedDate.toLocaleDateString("en-GB"),
            is_today: isToday,
            purchase_items: receipt.purchase,
          };
        });

        // Sort by date (most recent first)
        processedReceipts.sort((a: any, b: any) => {
          const dateA = new Date(a.captured_date.split("/").reverse().join("-"));
          const dateB = new Date(b.captured_date.split("/").reverse().join("-"));
          return dateB.getTime() - dateA.getTime();
        });

        setReceipts(processedReceipts);
      } else {
        // No data found, use demo data
        console.log("No data found, using demo data");
        const sortedDemoData = [...demoReceipts].sort((a, b) => {
          const dateA = new Date(a.captured_date.split("/").reverse().join("-"));
          const dateB = new Date(b.captured_date.split("/").reverse().join("-"));
          return dateB.getTime() - dateA.getTime();
        });
        setReceipts(sortedDemoData);
      }
    } catch (error) {
      console.log("Using demo data due to error:", error)
      // Sort demo data by date
      const sortedDemoData = [...demoReceipts].sort((a, b) => {
        const dateA = new Date(a.captured_date.split("/").reverse().join("-"))
        const dateB = new Date(b.captured_date.split("/").reverse().join("-"))
        return dateB.getTime() - dateA.getTime()
      })
      setReceipts(sortedDemoData)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedReceipt(null)
    setShowForm(true)
  }

  const handleEdit = (receipt: Receipt) => {
    if (receipt.is_today) {
      // Convert receipt data to the format expected by ReceiptForm
      const receiptData = {
        id: receipt.id,
        purchase_items: receipt.purchase_items || [
          { category: receipt.category, amount: receipt.amount, description: "", reimburse: true },
        ],
      };
      setSelectedReceipt(receiptData as any);
      setShowForm(true);
    }
  }

  const handleFormBack = () => {
    setShowForm(false)
    setSelectedReceipt(null)
  }

  const handleFormSave = async (receiptData: any) => {
    // Here you would save to Supabase
    console.log("Saving receipt:", receiptData);

    // Update modified_timestamp to today when editing
    if (receiptData.id) {
      await supabase
        .from("receipt")
        .update({ modified_timestamp: new Date().toISOString() })
        .eq("id", receiptData.id);
    }

    // For now, just refresh the list and go back
    await fetchReceipts();
    setShowForm(false);
    setSelectedReceipt(null);
  }

  const handleSignOut = async () => {
    setIsSigningOut(true)
    try {
      const { error } = await signOut()
      if (error) {
        console.error("Error signing out:", error.message)
        // You could show a toast notification here
      }
      // The useAuth hook will automatically update the user state
      // and the login screen will be shown
    } catch (error) {
      console.error("Unexpected error during sign out:", error)
    } finally {
      setIsSigningOut(false)
    }
  }

  const getUserDisplayName = () => {
    if (!user) return ""
    return user.user_metadata?.full_name || user.email || "User"
  }

  const totalPages = Math.ceil(receipts.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentReceipts = receipts.slice(startIndex, endIndex)

  if (showForm) {
    return <ReceiptForm receiptData={selectedReceipt} onBack={handleFormBack} onSave={handleFormSave} />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading receipts...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="bg-teal-600 text-white p-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">Receipts</h1>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="text-white hover:bg-teal-700 p-2">
                <User className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="px-2 py-1.5 text-sm text-gray-700">
                <div className="font-medium">Signed in as</div>
                <div className="text-gray-500 truncate">{getUserDisplayName()}</div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleSignOut}
                disabled={isSigningOut}
                className="text-red-600 focus:text-red-600 focus:bg-red-50"
              >
                <LogOut className="h-4 w-4 mr-2" />
                {isSigningOut ? "Signing out..." : "Sign out"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Add Button */}
        <div className="p-4">
          <Button
            onClick={handleAdd}
            className="w-full bg-teal-600 hover:bg-teal-700 text-white font-medium py-3 rounded-md"
          >
            ADD
          </Button>
        </div>

        {/* Table */}
    <div className="px-4">
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Table Header */}
        <div className="bg-gray-50 grid grid-cols-[1fr_80px_80px_40px] gap-2 p-3 text-sm font-medium text-gray-700 border-b">
          <div>Category</div>
          <div>Amount</div>
          <div>Date</div>
          <div></div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-gray-200">
          {currentReceipts.map((receipt: any) => (
            <div
              key={receipt.id}
              className={`grid grid-cols-[1fr_80px_80px_40px] gap-2 p-3 text-sm ${receipt.is_today ? "bg-green-50" : "bg-white"}`}
            >
              <div className="truncate">{receipt.category}</div>
              <div>₹{receipt.amount}</div>
              <div className="text-gray-600">{receipt.captured_date}</div>
              <div className="flex justify-end">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleEdit(receipt)}
                  disabled={!receipt.is_today}
                  className={`h-6 px-2 ${
                    receipt.is_today ? "text-blue-600 hover:text-blue-800" : "text-gray-400 cursor-not-allowed"
                  }`}
                >
                  <Pencil className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCurrentPage((prev: any) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="text-gray-600"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>

          <span className="text-sm text-gray-600">{currentPage}</span>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCurrentPage((prev: any) => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="text-teal-600"
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>
    </div>
  )
}
