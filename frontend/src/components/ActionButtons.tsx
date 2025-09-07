/**
 * AltMX - アクションボタン群（GENERATE/DEBUG/DEPLOY/SAVE）
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'

interface ActionButtonsProps {
  onAction: (action: 'generate' | 'debug' | 'deploy' | 'save') => void
}

const ActionButtons: FC<ActionButtonsProps> = ({ onAction }) => {
  const buttons = [
    {
      id: 'generate' as const,
      label: 'GENERATE',
      icon: '⚡',
      color: 'cyan',
      description: 'AIコード生成開始'
    },
    {
      id: 'debug' as const,
      label: 'DEBUG',
      icon: '🔍',
      color: 'pink',
      description: 'デバッグモード'
    },
    {
      id: 'deploy' as const,
      label: 'DEPLOY',
      icon: '🚀',
      color: 'green',
      description: 'デプロイ実行'
    },
    {
      id: 'save' as const,
      label: 'SAVE',
      icon: '💾',
      color: 'orange',
      description: 'プロジェクト保存'
    }
  ]

  const handleButtonClick = (action: typeof buttons[0]['id']) => {
    onAction(action)
  }

  return (
    <div className="action-buttons">
      <div className="buttons-container">
        {buttons.map((button) => (
          <button
            key={button.id}
            className={`action-button ${button.color}`}
            onClick={() => handleButtonClick(button.id)}
            aria-label={button.description}
          >
            <div className="button-content">
              {/* アイコン */}
              <div className="button-icon">
                <span className="icon-symbol">{button.icon}</span>
                <div className="icon-glow"></div>
              </div>
              
              {/* ラベル */}
              <div className="button-label">
                <span className="label-text">{button.label}</span>
              </div>
            </div>

            {/* エフェクト要素 */}
            <div className="button-glow"></div>
            <div className="button-ripple"></div>
            <div className="button-scanline"></div>
            
            {/* ホバー時のパーティクル */}
            <div className="button-particles">
              <div className="particle particle-1"></div>
              <div className="particle particle-2"></div>
              <div className="particle particle-3"></div>
              <div className="particle particle-4"></div>
            </div>
          </button>
        ))}
      </div>

      {/* 背景エフェクト */}
      <div className="buttons-background">
        <div className="background-glow"></div>
        <div className="background-grid"></div>
      </div>
    </div>
  )
}

export default ActionButtons