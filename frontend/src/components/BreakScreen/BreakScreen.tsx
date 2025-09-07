/**
 * AltMX - 休憩画面（5分カウントダウン）
 * 仕様書: /src/ui/04-break-ending-screens.md
 */

import { FC, useEffect, useMemo } from 'react'
import { useTimer } from '../../hooks/useTimer'

interface NextSessionInfo {
  title: string
  description: string
  estimatedDuration: number
}

interface BreakScreenProps {
  onComplete: () => void
  nextSessionInfo?: NextSessionInfo
  showControls?: boolean
}

const BreakScreen: FC<BreakScreenProps> = ({
  onComplete,
  nextSessionInfo = {
    title: 'Next Session',
    description: '次のセッションを準備中です...',
    estimatedDuration: 30
  },
  showControls = false
}) => {
  // 5分（300秒）のタイマー
  const { timeRemaining, isRunning, start, pause } = useTimer(300, onComplete)

  // コンポーネントマウント時にタイマー開始
  useEffect(() => {
    start()
  }, [start])

  // 0秒になったらコールバック実行
  useEffect(() => {
    if (timeRemaining === 0) {
      onComplete()
    }
  }, [timeRemaining, onComplete])

  // MM:SS形式のフォーマット
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  // 警告時間判定（1分以下）
  const isWarningTime = timeRemaining <= 60

  // ビジュアルウェーブバーの生成
  const waveBars = useMemo(() => {
    return Array.from({ length: 12 }, (_, index) => ({
      id: index,
      height: Math.random() * 100 + 20,
      delay: index * 0.1
    }))
  }, [])

  const handleSkip = () => {
    onComplete()
  }

  return (
    <div 
      className="break-screen vaporwave-theme gradient-background responsive-layout"
      data-testid="break-screen-container"
    >
      {/* アニメーション背景 */}
      <div className="animated-background gradient-animation" data-testid="animated-background">
        <div className="floating-particles" data-testid="floating-particles">
          <div className="particle float-1"></div>
          <div className="particle float-2"></div>
          <div className="particle float-3"></div>
          <div className="particle float-4"></div>
          <div className="particle float-5"></div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="break-content">
        {/* タイトル */}
        <h1 className="break-title pulse-effect">BREAK TIME</h1>

        {/* カウントダウンタイマー */}
        <div 
          className={`timer-display countdown-timer ${isWarningTime ? 'warning-time' : ''}`}
          data-testid="countdown-timer"
          aria-live="polite"
          aria-label="カウントダウンタイマー"
        >
          {formatTime(timeRemaining)}
        </div>

        {/* 参加者向けメッセージ */}
        <div className="break-message" data-testid="break-message" role="status">
          <p>ちょっと休憩だっしょ〜</p>
          <p>コーヒーでも飲んで、リフレッシュしてくださいね！</p>
        </div>

        {/* ビジュアルウェーブバー */}
        <div className="visual-wave-bars" data-testid="visual-wave-bars">
          {waveBars.map(bar => (
            <div
              key={bar.id}
              className="wave-bar wave-bounce"
              data-testid="wave-bar"
              style={{
                height: `${bar.height}%`,
                animationDelay: `${bar.delay}s`
              }}
            />
          ))}
        </div>

        {/* 次セッション予告 */}
        <div className="next-session-preview" data-testid="next-session-preview">
          <h3 className="next-session-title">NEXT SESSION</h3>
          <div className="session-info">
            <h4 className="session-name">{nextSessionInfo.title}</h4>
            <p className="session-description">{nextSessionInfo.description}</p>
            <span className="session-duration">約{nextSessionInfo.estimatedDuration}分</span>
          </div>
        </div>

        {/* 制御ボタン（オプション） */}
        {showControls && (
          <div className="break-controls">
            <button
              className="control-button pause-button"
              onClick={pause}
              disabled={!isRunning}
            >
              {isRunning ? '⏸️ 一時停止' : '▶️ 再開'}
            </button>
            <button
              className="control-button skip-button"
              onClick={handleSkip}
            >
              ⏭️ スキップ
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default BreakScreen