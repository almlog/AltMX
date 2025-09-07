/**
 * AltMX - Ending Screen (エンディング画面)
 * セッション完了時の神聖な締めくくり画面
 * 仕様書: /src/ui/04-break-ending-screens.md
 */

import { FC, useMemo, useEffect, useState } from 'react'

interface SessionStats {
  toolsCreated: number
  linesGenerated: number
  sessionDuration: number // 分単位
  successRate: number
}

interface CreatedTool {
  name: string
  type: string
  complexity: 'simple' | 'medium' | 'complex'
}

interface NextAction {
  type: 'consultation' | 'download' | 'community'
  title: string
  url: string
  qrCode?: string
}

interface EndingScreenProps {
  sessionStats: SessionStats
  createdTools: CreatedTool[]
  nextActions: NextAction[]
  onComplete: () => void
  autoCompleteAfter?: number
}

const EndingScreen: FC<EndingScreenProps> = ({
  sessionStats,
  createdTools,
  nextActions,
  onComplete,
  autoCompleteAfter = 10000 // 10秒後に自動完了
}) => {
  const [showStats, setShowStats] = useState(false)

  // 聖なる粒子の生成
  const sacredParticles = useMemo(() => {
    return Array.from({ length: 12 }, (_, index) => ({
      id: index,
      delay: index * 0.2,
      size: Math.random() * 3 + 1.5,
      x: Math.random() * 100,
      y: Math.random() * 100
    }))
  }, [])

  // ゴールド紙吹雪の生成
  const goldConfetti = useMemo(() => {
    return Array.from({ length: 20 }, (_, index) => ({
      id: index,
      delay: index * 0.1,
      size: Math.random() * 4 + 2,
      x: Math.random() * 100,
      rotation: Math.random() * 360
    }))
  }, [])

  // オーラリングの生成
  const auraRings = useMemo(() => {
    return Array.from({ length: 4 }, (_, index) => ({
      id: index,
      delay: index * 0.5,
      scale: 1 + index * 0.3
    }))
  }, [])

  // 統計数値のフォーマット
  const formatNumber = (num: number): string => {
    return num.toLocaleString('ja-JP')
  }

  // セッション時間のフォーマット
  const formatDuration = (minutes: number): string => {
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const remainingMinutes = minutes % 60
      return `${hours}時間${remainingMinutes}分`
    }
    return `${minutes}分`
  }

  // 複雑度バッジの色
  const getComplexityColor = (complexity: CreatedTool['complexity']): string => {
    switch (complexity) {
      case 'simple':
        return 'complexity-simple'
      case 'medium':
        return 'complexity-medium'
      case 'complex':
        return 'complexity-complex'
      default:
        return 'complexity-simple'
    }
  }

  // アクション実行
  const handleAction = (action: NextAction) => {
    window.open(action.url, '_blank')
  }

  // エフェクト開始タイミング
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowStats(true)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  // 自動完了タイマー
  useEffect(() => {
    if (autoCompleteAfter > 0) {
      const timer = setTimeout(() => {
        onComplete()
      }, autoCompleteAfter)

      return () => clearTimeout(timer)
    }
  }, [autoCompleteAfter, onComplete])

  return (
    <div 
      className="ending-screen heavenly-theme sacred-glow responsive-layout"
      data-testid="ending-screen-container"
      role="main"
      aria-label="セッション完了画面"
      onClick={onComplete}
    >
      {/* 天からの光線エフェクト */}
      <div className="light-rays" data-testid="light-rays">
        <div className="ray ray-1"></div>
        <div className="ray ray-2"></div>
        <div className="ray ray-3"></div>
        <div className="ray ray-4"></div>
        <div className="ray ray-5"></div>
      </div>

      {/* 聖なる粒子エフェクト */}
      <div className="sacred-particles" data-testid="sacred-particles">
        {sacredParticles.map(particle => (
          <div
            key={particle.id}
            className="sacred-particle"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              animationDelay: `${particle.delay}s`
            }}
          />
        ))}
      </div>

      {/* ゴールド紙吹雪エフェクト */}
      <div className="gold-confetti" data-testid="gold-confetti">
        {goldConfetti.map(confetti => (
          <div
            key={confetti.id}
            className="confetti-piece"
            style={{
              left: `${confetti.x}%`,
              width: `${confetti.size}px`,
              height: `${confetti.size}px`,
              transform: `rotate(${confetti.rotation}deg)`,
              animationDelay: `${confetti.delay}s`
            }}
          />
        ))}
      </div>

      {/* オーラリングエフェクト */}
      <div className="aura-rings" data-testid="aura-rings">
        {auraRings.map(ring => (
          <div
            key={ring.id}
            className="aura-ring"
            style={{
              transform: `scale(${ring.scale})`,
              animationDelay: `${ring.delay}s`
            }}
          />
        ))}
      </div>

      {/* メインコンテンツ */}
      <div className="ending-content">
        {/* タイトル */}
        <h1 className="ending-title title-glow pulse-sacred">
          SESSION COMPLETED
        </h1>

        {/* AltMXからの最終メッセージ */}
        <div className="final-message" data-testid="final-message">
          <p>お疲れ様でした！素晴らしいセッションでしたね〜</p>
          <p>一緒にたくさんのツールを作れて、めっちゃ楽しかったっしょ！</p>
          <p>これからも開発を楽しんでくださいね✨</p>
        </div>

        {/* セッション統計 */}
        <div 
          className={`session-stats ${showStats ? 'stats-visible' : ''}`} 
          data-testid="session-stats"
          aria-describedby="session-stats-description"
        >
          <div className="stat-item">
            <div className="stat-number count-up" data-testid="animated-number">
              {formatNumber(sessionStats.toolsCreated)}
            </div>
            <div className="stat-label">ツール作成</div>
          </div>
          <div className="stat-item">
            <div className="stat-number count-up" data-testid="animated-number">
              {formatNumber(sessionStats.linesGenerated)}
            </div>
            <div className="stat-label">行のコード生成</div>
          </div>
          <div className="stat-item">
            <div className="stat-number count-up" data-testid="animated-number">
              {formatDuration(sessionStats.sessionDuration)}
            </div>
            <div className="stat-label">セッション時間</div>
          </div>
          <div className="stat-item">
            <div className="stat-number count-up" data-testid="animated-number">
              {sessionStats.successRate}%
            </div>
            <div className="stat-label">成功率</div>
          </div>
        </div>

        <div id="session-stats-description" className="sr-only">
          今回のセッションで作成したツール数、生成したコード行数、セッション時間、成功率を表示しています
        </div>

        {/* 作成ツール一覧 */}
        <div className="created-tools" data-testid="created-tools-list">
          <h3 className="tools-title">作成したツール</h3>
          <div className="tools-grid">
            {createdTools.map((tool, index) => (
              <div key={index} className="tool-item">
                <div className="tool-name">{tool.name}</div>
                <div className="tool-type">{tool.type}</div>
                <div 
                  className={`complexity-badge ${getComplexityColor(tool.complexity)}`}
                  data-testid={`complexity-${tool.complexity}`}
                >
                  {tool.complexity}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ネクストアクション */}
        <div className="next-actions" data-testid="next-actions">
          <h3 className="actions-title">次のステップ</h3>
          <div className="actions-grid">
            {nextActions.map((action, index) => (
              <div key={index} className="action-card">
                <button
                  className="action-button"
                  onClick={() => handleAction(action)}
                  aria-label={
                    action.type === 'consultation' ? '無料相談を予約する' :
                    action.type === 'download' ? '開発資料をダウンロードする' :
                    'コミュニティに参加する'
                  }
                >
                  <div className="action-title">{action.title}</div>
                  <div className="action-url">{action.url}</div>
                </button>
                {action.qrCode && (
                  <div className="qr-code" data-testid={`qr-code-${action.type}`}>
                    <img src={action.qrCode} alt={`${action.title}のQRコード`} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 装飾要素 */}
      <div className="decoration-elements">
        <div className="sacred-border"></div>
        <div className="heavenly-glow"></div>
      </div>
    </div>
  )
}

export default EndingScreen