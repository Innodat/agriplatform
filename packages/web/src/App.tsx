import { useState } from 'react'
import './App.css'
import { OverviewPage } from './components/finance/receipt-capturing/pages/OverviewPage'
import { TodayPage } from './components/finance/receipt-capturing/pages/TodayPage'
import { AdminPage } from './components/finance/receipt-capturing/pages/AdminPage'
import { Toaster } from './components/ui/toaster'
import { useAuth } from './contexts/AuthContext'
import { LoginPage } from './components/auth/LoginPage'
import { LoadingScreen } from './components/auth/LoadingScreen'

type TabType = 'overview' | 'today' | 'admin'

function App() {
  const { user, loading, isAdmin, signOut } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  // Show loading screen while checking auth
  if (loading) {
    return <LoadingScreen />
  }

  // Show login page if not authenticated
  if (!user) {
    return <LoginPage />
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPage />
      case 'today':
        return <TodayPage />
      case 'admin':
        return <AdminPage />
      default:
        return <OverviewPage />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Liseli</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Welcome, {user.email}</span>
              <button
                onClick={signOut}
                className="text-sm text-gray-500 hover:text-gray-700 underline"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm min-h-screen">
          <nav className="mt-8">
            <div className="px-4">
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Departments
              </h2>
              <ul className="mt-4 space-y-2">
                <li>
                  <a href="#" className="bg-blue-50 text-blue-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                    Finance
                  </a>
                </li>
                {/*<li>
                  <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                    Operations
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                    Inventory
                  </a>
                </li>*/}
              </ul>
            </div>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 p-8">
          {/* Finance Module Header */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Finance Department</h2>
            <p className="text-gray-600">Manage financial operations and expense tracking</p>
          </div>

          {/* Receipt Capturing Module */}
          <div className="bg-white rounded-lg shadow">
            {/* Module Tabs */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'overview'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('today')}
                  className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'today'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Today's Receipts
                </button>
                {/* Admin Panel - Only visible to admin users */}
                {isAdmin && (
                  <button
                    onClick={() => setActiveTab('admin')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'admin'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Admin Panel
                  </button>
                )}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {renderTabContent()}
            </div>
          </div>
        </main>
      </div>
      <Toaster />
    </div>
  )
}

export default App
