/**
 * AltMX - ターボモードボタン
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'

interface TurboModeButtonProps {
  isActive: boolean
  onToggle: () => void
}

const TurboModeButton: FC<TurboModeButtonProps> = ({ isActive, onToggle }) => {
  return (
    <div className="turbo-mode-container">
      <button
        className={`turbo-mode-button ${isActive ? 'active' : ''}`}
        onClick={onToggle}
        aria-label="ターボモード切り替え"
      >
        <div className="turbo-icon">
          <div className="icon-lightning">
            <div className="lightning-bolt"></div>
          </div>
          <div className="icon-particles">
            <div className="particle particle-1"></div>
            <div className="particle particle-2"></div>
            <div className="particle particle-3"></div>
          </div>
        </div>
        
        <div className="turbo-text">
          <span className="turbo-label">TURBO</span>
          <span className="turbo-status">
            {isActive ? 'ON' : 'OFF'}
          </span>
        </div>

        {/* エフェクト用要素 */}
        <div className="turbo-glow"></div>
        <div className="turbo-ripple"></div>
      </button>

      {/* ターボモード説明 */}
      <div className="turbo-description">
        <span className={`description-text ${isActive ? 'active' : ''}`}>
          {isActive 
            ? '高速コード生成モード' 
            : 'クリックで高速化'
          }
        </span>
      </div>
    </div>
  )
}

export default TurboModeButton