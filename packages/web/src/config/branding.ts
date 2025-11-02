/**
 * Branding Configuration
 * 
 * Centralized branding configuration for the platform.
 * Future: Load from database based on organization for multi-org support.
 */

export interface BrandingConfig {
  organizationName: string
  tagline: string
  motto: string
  colors: {
    primary: string
    primaryDark: string
    primaryLight: string
    dots: string[]
  }
  logo?: {
    url: string
    alt: string
  }
}

/**
 * Default Liseli Foundation branding
 */
export const defaultBranding: BrandingConfig = {
  organizationName: 'Liseli',
  tagline: 'FOUNDATION',
  motto: 'Be the Light',
  colors: {
    primary: '#14B8A6',      // teal-500
    primaryDark: '#0D9488',   // teal-600
    primaryLight: '#5EEAD4',  // teal-300
    dots: ['#14B8A6', '#10B981', '#FBBF24', '#F97316'] // teal, green, yellow, orange
  }
}

/**
 * Get current branding configuration
 * Future: Load from database based on organization context
 */
export const getBranding = (): BrandingConfig => {
  return defaultBranding
}
