/**
 * AltMX - プログレスバー（パルスアニメーション付き）
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'
import { useEffect, useState } from 'react'

interface ProgressBarProps {
  progress: number // 0-100
  message: string
  isActive?: boolean
}

const ProgressBar: FC<ProgressBarProps> = ({ 
  progress, 
  message, 
  isActive = true 
}) => {
  const [displayProgress, setDisplayProgress] = useState(0)

  // プログレスの滑らかな更新
  useEffect(() => {
    const interval = setInterval(() => {
      setDisplayProgress(prev => {
        const diff = progress - prev
        if (Math.abs(diff) < 0.1) {
          return progress
        }
        return prev + diff * 0.1
      })
    }, 16) // 60fps

    return () => clearInterval(interval)
  }, [progress])

  const getProgressColor = (progress: number) => {
    if (progress < 30) return 'progress-red'
    if (progress < 70) return 'progress-orange'
    if (progress < 100) return 'progress-cyan'
    return 'progress-green'
  }

  const getStageMessage = (progress: number) => {
    if (progress < 20) return 'Initializing...'
    if (progress < 40) return 'Processing...'
    if (progress < 60) return 'Generating...'
    if (progress < 80) return 'Optimizing...'
    if (progress < 100) return 'Finalizing...'
    return 'Complete!'
  }

  return (
    <div className={`progress-bar-container ${isActive ? 'active' : ''}`}>
      <div className="progress-info">
        <div className="progress-message">
          <span className="message-text">{message}</span>
          <span className="stage-text">{getStageMessage(displayProgress)}</span>
        </div>
        <div className="progress-value">
          <span className="value-number">{Math.round(displayProgress)}</span>
          <span className="value-unit">%</span>
        </div>
      </div>

      <div className="progress-track">
        <div 
          className={`progress-fill ${getProgressColor(displayProgress)}`}
          style={{ width: `${displayProgress}%` }}
        >
          {/* プログレスバーのグラデーション */}
          <div className="progress-gradient"></div>
          
          {/* 光る先端 */}
          <div className="progress-tip"></div>
          
          {/* パルス効果 */}
          <div className="progress-pulse"></div>
        </div>

        {/* 背景パターン */}
        <div className="track-pattern"></div>
        
        {/* スキャンライン */}
        <div className="track-scanlines"></div>
      </div>

      {/* プログレス段階のマーカー */}
      <div className="progress-markers">
        {[25, 50, 75].map(marker => (
          <div 
            key={marker}
            className={`progress-marker ${displayProgress >= marker ? 'reached' : ''}`}
            style={{ left: `${marker}%` }}
          >
            <div className="marker-dot"></div>
            <div className="marker-glow"></div>
          </div>
        ))}
      </div>

      {/* 背景エフェクト */}
      <div className="progress-background-effects">
        <div className="background-particles">
          <div className="particle bg-particle-1"></div>
          <div className="particle bg-particle-2"></div>
          <div className="particle bg-particle-3"></div>
        </div>
        <div className="background-glow"></div>
      </div>
    </div>
  )
}

export default ProgressBar