import { getBranding } from '../../config/branding'

interface LiseliLogoProps {
  size?: 'sm' | 'md' | 'lg'
  showTagline?: boolean
  showMotto?: boolean
}

export function LiseliLogo({ 
  size = 'lg', 
  showTagline = true, 
  showMotto = true 
}: LiseliLogoProps) {
  const branding = getBranding()
  
  const sizeClasses = {
    sm: {
      dots: 'w-2 h-2',
      dotsGap: 'gap-1',
      logo: 'text-3xl',
      tagline: 'text-xs',
      motto: 'text-sm'
    },
    md: {
      dots: 'w-3 h-3',
      dotsGap: 'gap-1.5',
      logo: 'text-4xl',
      tagline: 'text-sm',
      motto: 'text-base'
    },
    lg: {
      dots: 'w-3 h-3',
      dotsGap: 'gap-2',
      logo: 'text-5xl',
      tagline: 'text-sm',
      motto: 'text-base'
    }
  }
  
  const classes = sizeClasses[size]
  
  return (
    <div className="flex flex-col items-center">
      {/* Four colored dots */}
      <div className={`flex ${classes.dotsGap} mb-4`}>
        {branding.colors.dots.map((color, index) => (
          <div
            key={index}
            className={`${classes.dots} rounded-full`}
            style={{ backgroundColor: color }}
          />
        ))}
      </div>
      
      {/* Organization name */}
      <h1 
        className={`${classes.logo} font-bold mb-1`}
        style={{ color: branding.colors.primary }}
      >
        {branding.organizationName}
      </h1>
      
      {/* Tagline */}
      {showTagline && (
        <div 
          className={`${classes.tagline} font-semibold tracking-widest text-gray-600 mb-1`}
        >
          {branding.tagline}
        </div>
      )}
      
      {/* Motto */}
      {showMotto && (
        <div className={`${classes.motto} italic text-gray-400`}>
          {branding.motto}
        </div>
      )}
    </div>
  )
}
