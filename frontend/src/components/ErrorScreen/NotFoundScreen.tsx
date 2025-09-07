/**
 * AltMX - 404 Not Found エラー画面
 * 仕様書: /src/ui/03-error-screens.md
 */

import { FC, useEffect, useState } from 'react'
import { useRouteContext } from '../../contexts/RouteContext'

interface NotFoundScreenProps {
  onRecordingSwitch?: () => void
  onRetry?: () => void
}

const NotFoundScreen: FC<NotFoundScreenProps> = ({
  onRecordingSwitch,
  onRetry
}) => {
  // ルーターコンテキストを取得
  const { navigate } = useRouteContext()
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    setIsAnimating(true)
  }, [])

  // ルーターナビゲーション用のハンドラー
  const handleRecordingSwitch = () => {
    // 従来のコールバック（後方互換性のため）
    onRecordingSwitch?.()
    // TODO: 録画デモページにナビゲーション
    console.log('Recording demo page navigation')
  }

  const handleRetry = () => {
    // 従来のコールバック（後方互換性のため）
    onRetry?.()
    // ホーム画面にナビゲーション
    navigate('opening')
  }

  return (
    <div 
      className={`error-screen-container error-screen-404 cyan-theme neon-glow-cyan responsive-layout ${isAnimating ? 'glitch-in' : ''}`}
      data-testid="error-screen-container"
      role="alert"
      aria-live="polite"
    >
      {/* 背景エフェクト */}
      <div className="error-background-effects">
        <div className="neon-grid"></div>
        <div className="scanlines"></div>
        <div data-testid="particle-effects" className="particle-effects">
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
          <div className="particle particle-4"></div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="error-content">
        {/* エラーコード大型表示 */}
        <div className="error-code-section">
          <div className="error-code-large glitch-effect" data-testid="error-code">
            404
          </div>
          <div className="error-title">
            NOT FOUND
          </div>
        </div>

        {/* ASCII Art装飾 */}
        <div className="ascii-decoration" data-testid="ascii-art-decoration">
          <pre>{`
    ╔═══════════════════════╗
    ║   ░░░░░░░░░░░░░░░░░   ║
    ║   ░ FILE NOT FOUND ░   ║
    ║   ░░░░░░░░░░░░░░░░░   ║
    ╚═══════════════════════╝
          `}</pre>
        </div>

        {/* AltMXメッセージ */}
        <div className="altmx-message-section">
          <div className="altmx-avatar-mini">
            <div className="avatar-glow"></div>
            <div className="avatar-core"></div>
          </div>
          <div className="altmx-message">
            <p>探してるファイル、どっか行っちゃったわ...</p>
            <p>したっけ、録画のやつ見せるね！</p>
          </div>
        </div>

        {/* アクションボタン */}
        <div className="error-action-buttons">
          <button
            className="error-button primary-button"
            onClick={handleRecordingSwitch}
            aria-label="録画デモに切り替える"
          >
            🎬 録画デモを再生
          </button>
          <button
            className="error-button secondary-button"
            onClick={handleRetry}
            aria-label="ホーム画面に戻る"
          >
            🏠 最初から
          </button>
        </div>

        {/* ステータス表示 */}
        <div className="error-status-section">
          <div className="status-item">
            <div className="status-indicator" data-testid="status-indicator">
              <div className="status-dot searching"></div>
            </div>
            <span className="status-text">検索中...</span>
          </div>
          <div className="status-item">
            <div className="status-indicator" data-testid="status-indicator">
              <div className="status-dot available"></div>
            </div>
            <span className="status-text">代替案: あり</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NotFoundScreen