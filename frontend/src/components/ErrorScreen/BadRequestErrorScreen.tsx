/**
 * AltMX - 400 Bad Request Error Screen
 * 仕様書: /src/ui/03-error-screens.md
 */

import { FC, useMemo } from 'react'

interface BadRequestErrorScreenProps {
  onRecordingSwitch: () => void
  onRetry: () => void
}

const BadRequestErrorScreen: FC<BadRequestErrorScreenProps> = ({
  onRecordingSwitch,
  onRetry
}) => {
  // パーティクル要素の生成
  const particles = useMemo(() => {
    return Array.from({ length: 5 }, (_, index) => ({
      id: index,
      delay: index * 0.4,
      size: Math.random() * 3 + 2
    }))
  }, [])

  // エラー発生タイムスタンプ
  const errorTimestamp = useMemo(() => {
    return new Date().toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }, [])

  return (
    <div 
      className="error-screen-container error-screen-400 orange-theme neon-glow-orange responsive-layout"
      data-testid="error-screen-container"
    >
      {/* 背景パーティクル効果 */}
      <div className="background-particles" data-testid="background-particles">
        {particles.map(particle => (
          <div
            key={particle.id}
            className="particle-float"
            data-testid={`particle-${particle.id}`}
            style={{
              animationDelay: `${particle.delay}s`,
              width: `${particle.size}px`,
              height: `${particle.size}px`
            }}
          />
        ))}
      </div>

      {/* メインエラーコンテンツ */}
      <div className="error-content">
        {/* エラーコード - 大型表示 */}
        <div className="error-code-large glitch-effect glitch-in number-glitch">
          400
        </div>

        {/* エラータイトル */}
        <h1 className="error-title">BAD REQUEST</h1>

        {/* AltMXからのメッセージ */}
        <div 
          className="altmx-message error-message" 
          data-testid="error-message"
          role="alert"
        >
          <p>あれ？なんか変なデータ来たっしょ...</p>
          <p>ちょっと録画デモに切り替えるわ！</p>
        </div>

        {/* システムステータス */}
        <div className="system-status">
          <div className="status-item standby-status" data-testid="ai-status">
            <span className="status-indicator standby"></span>
            <span>AI: スタンバイ中</span>
          </div>
          <div className="status-item ok-status" data-testid="recording-status">
            <span className="status-indicator ok"></span>
            <span>録画: 準備完了</span>
          </div>
        </div>

        {/* アクションボタン */}
        <div className="action-buttons">
          <button
            className="action-button primary"
            onClick={onRecordingSwitch}
            aria-label="録画デモを再生する"
          >
            📼 録画デモを再生
          </button>
          <button
            className="action-button secondary"
            onClick={onRetry}
            aria-label="リクエストを再試行する"
          >
            🔄 もう一度試す
          </button>
        </div>

        {/* エラー詳細情報 */}
        <div className="error-info">
          <div className="error-details" data-testid="error-details">
            <div className="detail-item">
              <span className="detail-label">Error Code:</span>
              <span className="detail-value">BAD_REQUEST</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Module:</span>
              <span className="detail-value">AltMX-Validator</span>
            </div>
          </div>
          
          <div className="request-info" data-testid="request-info">
            <h4 className="info-title">リクエスト情報:</h4>
            <div className="detail-item">
              <span className="detail-label">Method:</span>
              <span className="detail-value">POST</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Validation:</span>
              <span className="detail-value">Failed</span>
            </div>
          </div>
          
          <div className="error-timestamp" data-testid="error-timestamp">
            <span className="timestamp-label">発生時刻:</span>
            <span className="timestamp-value">{errorTimestamp}</span>
          </div>
        </div>
      </div>

      {/* 装飾要素 */}
      <div className="decoration-elements">
        <div className="scan-lines"></div>
        <div className="grid-overlay"></div>
      </div>
    </div>
  )
}

export default BadRequestErrorScreen