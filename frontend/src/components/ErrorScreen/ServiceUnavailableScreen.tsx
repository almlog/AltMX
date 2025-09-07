/**
 * AltMX - 503 Service Unavailable Error Screen
 * 仕様書: /src/ui/03-error-screens.md
 */

import { FC, useMemo, useState, useEffect } from 'react'

interface ServiceUnavailableScreenProps {
  onRecordingSwitch: () => void
  onWaitAndRetry: () => void
}

const ServiceUnavailableScreen: FC<ServiceUnavailableScreenProps> = ({
  onRecordingSwitch,
  onWaitAndRetry
}) => {
  const [countdown, setCountdown] = useState(30)

  // パーティクル要素の生成
  const particles = useMemo(() => {
    return Array.from({ length: 8 }, (_, index) => ({
      id: index,
      delay: index * 0.3,
      size: Math.random() * 4 + 1.5
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

  // 推定復旧時間
  const estimatedRecovery = useMemo(() => {
    const now = new Date()
    const recovery = new Date(now.getTime() + 30 * 1000)
    return recovery.toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }, [])

  // カウントダウンタイマー
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  return (
    <div 
      className="error-screen-container error-screen-503 purple-theme neon-glow-purple responsive-layout"
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
          503
        </div>

        {/* エラータイトル */}
        <h1 className="error-title">SERVICE UNAVAILABLE</h1>

        {/* AltMXからのメッセージ */}
        <div 
          className="altmx-message error-message" 
          data-testid="error-message"
          role="alert"
        >
          <p>ちょっと混雑してるみたいっしょ...</p>
          <p>録画デモなら、すぐ見せられるよ！</p>
        </div>

        {/* カウントダウンタイマー */}
        <div className="countdown-section">
          <div className="countdown-timer" data-testid="countdown-timer">
            <span className="timer-label">復旧まで:</span>
            <span className="timer-value">{countdown}秒</span>
          </div>
        </div>

        {/* システムステータス */}
        <div className="system-status">
          <div className="status-item overload-status" data-testid="api-status">
            <span className="status-indicator overload"></span>
            <span>API: 過負荷</span>
          </div>
          <div className="status-item wait-status" data-testid="wait-time-status">
            <span className="status-indicator wait"></span>
            <span>待機時間: 30秒</span>
          </div>
        </div>

        {/* アクションボタン */}
        <div className="action-buttons">
          <button
            className="action-button primary"
            onClick={onRecordingSwitch}
            aria-label="録画を再生する"
          >
            📼 録画を再生
          </button>
          <button
            className="action-button secondary"
            onClick={onWaitAndRetry}
            aria-label="30秒待機してから再試行"
          >
            ⏳ 30秒待つ
          </button>
        </div>

        {/* エラー詳細情報 */}
        <div className="error-info">
          <div className="error-details" data-testid="error-details">
            <div className="detail-item">
              <span className="detail-label">Error Code:</span>
              <span className="detail-value">SERVICE_UNAVAILABLE</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Module:</span>
              <span className="detail-value">AltMX-Gateway</span>
            </div>
          </div>
          
          <div className="server-load-info" data-testid="server-load-info">
            <h4 className="info-title">サーバー負荷情報:</h4>
            <div className="detail-item">
              <span className="detail-label">Current Load:</span>
              <span className="detail-value">98%</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Queue Size:</span>
              <span className="detail-value">245</span>
            </div>
          </div>

          <div className="estimated-recovery" data-testid="estimated-recovery">
            <div className="detail-item">
              <span className="detail-label">推定復旧時間:</span>
              <span className="detail-value">{estimatedRecovery}</span>
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

export default ServiceUnavailableScreen