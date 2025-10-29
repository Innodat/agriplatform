import { LiseliLogo } from './LiseliLogo'

export function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
      <LiseliLogo size="lg" />
      
      <div className="mt-8 flex flex-col items-center">
        {/* Spinner */}
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        
        {/* Loading text */}
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  )
}
