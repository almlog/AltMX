/**
 * AltMX - AltMXステータス表示パネル
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'

interface AltMXStatusPanelProps {
  status: {
    recognition: 'online' | 'offline'
    generation: 'turbo' | 'normal' | 'eco'
    quality: 'maximum' | 'high' | 'medium'
    speed: number
  }
}

const AltMXStatusPanel: FC<AltMXStatusPanelProps> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'status-online'
      case 'turbo': return 'status-turbo'
      case 'maximum': return 'status-maximum'
      default: return 'status-normal'
    }
  }

  return (
    <div className="altmx-status-panel neon-panel">
      <h3 className="panel-title">AltMX STATUS</h3>
      
      <div className="status-items">
        {/* 音声認識ステータス */}
        <div className="status-item">
          <span className="status-label">Recognition</span>
          <div className={`status-indicator ${getStatusColor(status.recognition)}`}>
            <div className="status-dot"></div>
            <span className="status-text">{status.recognition.toUpperCase()}</span>
          </div>
        </div>

        {/* 生成モード */}
        <div className="status-item">
          <span className="status-label">Generation</span>
          <div className={`status-indicator ${getStatusColor(status.generation)}`}>
            <div className="status-dot"></div>
            <span className="status-text">{status.generation.toUpperCase()}</span>
          </div>
        </div>

        {/* 品質設定 */}
        <div className="status-item">
          <span className="status-label">Quality</span>
          <div className={`status-indicator ${getStatusColor(status.quality)}`}>
            <div className="status-dot"></div>
            <span className="status-text">{status.quality.toUpperCase()}</span>
          </div>
        </div>

        {/* 処理速度 */}
        <div className="status-item">
          <span className="status-label">Speed</span>
          <div className="status-indicator status-speed">
            <span className="speed-value">{status.speed}</span>
            <span className="speed-unit">tokens/sec</span>
          </div>
        </div>
      </div>

      {/* ミニマル版AltMXアバター */}
      <div className="mini-avatar">
        <div className="avatar-glow">
          <div className="avatar-core"></div>
        </div>
        <div className="avatar-pulse"></div>
      </div>
    </div>
  )
}

export default AltMXStatusPanel