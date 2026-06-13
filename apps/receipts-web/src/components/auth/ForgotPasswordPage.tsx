import { useState } from 'react'
import type { FormEvent } from 'react'
import { LiseliLogo } from './LiseliLogo'
import { authHelpers } from '../../lib/supabase/client'
import { getBranding } from '../../config/branding'

export function ForgotPasswordPage() {
  const branding = getBranding()
  
  const [email, setEmail] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(false)
    setLoading(true)

    // Basic validation
    if (!email) {
      setError('Please enter your email address')
      setLoading(false)
      return
    }

    const { error: resetError } = await authHelpers.resetPasswordForEmail(email)
    
    if (resetError) {
      setError(resetError.message)
    } else {
      setSuccess(true)
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Logo */}
          <div className="mb-8">
            <LiseliLogo size="lg" />
          </div>

          {/* Heading */}
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Forgot Password?</h2>
          <p className="text-sm text-gray-600 mb-6">
            Enter your email address and we'll send you a link to reset your password.
          </p>

          {/* Success Message */}
          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-sm text-green-600">
                Check your email for password reset instructions.
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Email Form */}
          {!success && (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-4 py-3 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  disabled={loading}
                  required
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-md font-medium text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  backgroundColor: branding.colors.primary,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.backgroundColor = branding.colors.primaryDark
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = branding.colors.primary
                }}
              >
                {loading ? 'Sending...' : 'Send reset link'}
              </button>
            </form>
          )}

          {/* Back to Login Link */}
          <div className="mt-6 text-center">
            <a
              href="/"
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Back to login
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
