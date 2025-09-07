/**
 * AltMX - 500 Internal Server Error Screen
 * 仕様書: /src/ui/03-error-screens.md
 */

import { FC, useMemo } from 'react'

interface InternalServerErrorScreenProps {
  onRecordingSwitch: () => void
  onEmergencyMode: () => void
}

const InternalServerErrorScreen: FC<InternalServerErrorScreenProps> = ({
  onRecordingSwitch,
  onEmergencyMode
}) => {
  // パーティクル要素の生成
  const particles = useMemo(() => {
    return Array.from({ length: 6 }, (_, index) => ({
      id: index,
      delay: index * 0.5,
      size: Math.random() * 4 + 2
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
      className="error-screen-container error-screen-500 pink-theme neon-glow-pink responsive-layout"
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
          500
        </div>

        {/* エラータイトル */}
        <h1 className="error-title">INTERNAL SERVER ERROR</h1>

        {/* AltMXからのメッセージ */}
        <div 
          className="altmx-message error-message" 
          data-testid="error-message"
          role="alert"
        >
          <p>なんまらヤバいことになったっしょ！</p>
          <p>でも大丈夫、録画があるから見せるわ〜</p>
        </div>

        {/* システムステータス */}
        <div className="system-status">
          <div className="status-item error-status" data-testid="server-status">
            <span className="status-indicator error"></span>
            <span>サーバー: エラー</span>
          </div>
          <div className="status-item ok-status" data-testid="backup-status">
            <span className="status-indicator ok"></span>
            <span>バックアップ: OK</span>
          </div>
        </div>

        {/* アクションボタン */}
        <div className="action-buttons">
          <button
            className="action-button primary"
            onClick={onRecordingSwitch}
            aria-label="録画デモに切り替え"
          >
            📼 録画デモに切替
          </button>
          <button
            className="action-button secondary"
            onClick={onEmergencyMode}
            aria-label="緊急モードを開始"
          >
            🚨 緊急モード
          </button>
        </div>

        {/* エラー詳細情報 */}
        <div className="error-info">
          <div className="error-details" data-testid="error-details">
            <div className="detail-item">
              <span className="detail-label">Error Code:</span>
              <span className="detail-value">INTERNAL_SERVER_ERROR</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Module:</span>
              <span className="detail-value">AltMX-Core</span>
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

export default InternalServerErrorScreen