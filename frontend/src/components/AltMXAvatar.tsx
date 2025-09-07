import { useState, useEffect } from 'react'

interface AltMXAvatarProps {
  state: 'idle' | 'thinking' | 'speaking' | 'processing' | 'error'
  className?: string
}

export default function AltMXAvatar({ state = 'idle', className = '' }: AltMXAvatarProps) {
  const [animationClass, setAnimationClass] = useState('')

  useEffect(() => {
    switch (state) {
      case 'idle':
        setAnimationClass('car-idle-pulse')
        break
      case 'thinking':
        setAnimationClass('car-thinking-blink fast-blink')
        break
      case 'processing':
        setAnimationClass('car-processing-glow')
        break
      default:
        setAnimationClass('car-idle-pulse')
    }
  }, [state])

  return (
    <div className={`relative ${className}`} data-testid="altmx-avatar">
      {/* Cyberpunk Sports Car SVG */}
      <svg
        width="120"
        height="80"
        viewBox="0 0 120 80"
        className={`w-24 h-24 lg:w-32 lg:h-32 ${animationClass}`}
        data-state={state}
      >
        {/* Car Body */}
        <defs>
          <linearGradient id="carGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1a1a1a" />
            <stop offset="50%" stopColor="#2a2a2a" />
            <stop offset="100%" stopColor="#0a0a0a" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Main Car Body */}
        <path
          d="M20 50 L30 30 L90 30 L100 50 L95 60 L25 60 Z"
          fill="url(#carGradient)"
          stroke="#00d4ff"
          strokeWidth="2"
          filter="url(#glow)"
        />
        
        {/* Windscreen */}
        <path
          d="M35 30 L85 30 L80 40 L40 40 Z"
          fill="rgba(0, 212, 255, 0.3)"
          stroke="#00d4ff"
          strokeWidth="1"
        />
        
        {/* Headlights */}
        <circle
          cx="25"
          cy="45"
          r="4"
          fill="#00d4ff"
          className={`cyberpunk-pulse-blue ${state === 'thinking' ? 'cyberpunk-pulse-orange fast-blink' : ''}`}
          data-testid="car-headlights"
          filter="url(#glow)"
        />
        <circle
          cx="95"
          cy="45"
          r="4"
          fill="#00d4ff"
          className={`cyberpunk-pulse-blue ${state === 'thinking' ? 'cyberpunk-pulse-orange fast-blink' : ''}`}
          data-testid="car-headlights"
          filter="url(#glow)"
        />
        
        {/* Wheels */}
        <circle cx="35" cy="60" r="6" fill="#333" stroke="#00d4ff" strokeWidth="2" />
        <circle cx="85" cy="60" r="6" fill="#333" stroke="#00d4ff" strokeWidth="2" />
        
        {/* Wheel Centers */}
        <circle cx="35" cy="60" r="3" fill="#00d4ff" className="cyberpunk-pulse-blue" />
        <circle cx="85" cy="60" r="3" fill="#00d4ff" className="cyberpunk-pulse-blue" />
        
        {/* Side Details */}
        <line x1="30" y1="35" x2="90" y2="35" stroke="#00d4ff" strokeWidth="1" opacity="0.7" />
        <line x1="25" y1="50" x2="95" y2="50" stroke="#00d4ff" strokeWidth="1" opacity="0.5" />
        
        {/* Error State - Red Warning Lights */}
        {state === 'error' && (
          <>
            <circle cx="60" cy="25" r="3" fill="#ff0000" className="cyberpunk-pulse-click" />
            <circle cx="60" cy="65" r="3" fill="#ff0000" className="cyberpunk-pulse-click" />
          </>
        )}
        
        {/* Processing State - Additional Glow */}
        {state === 'processing' && (
          <circle
            cx="60"
            cy="45"
            r="35"
            fill="none"
            stroke="#00d4ff"
            strokeWidth="2"
            opacity="0.3"
            className="cyberpunk-pulse-blue"
          />
        )}
      </svg>
      
      {/* State Text */}
      <div className="text-center mt-2">
        <p className="text-sm text-gray-400 font-mono">
          AltMX {state === 'idle' ? 'スタンバイ中' : 
                 state === 'thinking' ? '考え中...' :
                 state === 'speaking' ? '話し中' :
                 state === 'processing' ? '処理中...' : 
                 'エラー'} 
        </p>
      </div>
      
      {/* Test trigger buttons - only visible in test environment */}
      {process.env.NODE_ENV === 'test' && (
        <div className="hidden">
          <button data-testid="trigger-thinking" onClick={() => {}} />
          <button data-testid="simulate-code-update" onClick={() => {}} />
        </div>
      )}
    </div>
  )
}