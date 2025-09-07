/**
 * EndingScreen (エンディング画面) Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 * 仕様書: /src/ui/04-break-ending-screens.md
 */

import { render, screen, fireEvent, waitFor, act } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import EndingScreen from './EndingScreen'

describe('EndingScreen Component (エンディング画面)', () => {
  const mockSessionStats = {
    toolsCreated: 5,
    linesGenerated: 1247,
    sessionDuration: 1800, // 30分
    successRate: 96.5
  }

  const mockCreatedTools = [
    { name: 'REST APIクライアント', type: 'API Tool', complexity: 'medium' as const },
    { name: 'データバリデーター', type: 'Utility', complexity: 'simple' as const },
    { name: 'CI/CDパイプライン', type: 'DevOps', complexity: 'complex' as const }
  ]

  const mockNextActions = [
    { 
      type: 'consultation' as const, 
      title: '無料相談予約', 
      url: 'https://altmx.ai/consultation',
      qrCode: 'data:image/png;base64,test-qr-code'
    },
    { 
      type: 'download' as const, 
      title: '開発資料DL', 
      url: 'https://altmx.ai/resources'
    },
    { 
      type: 'community' as const, 
      title: 'コミュニティ参加', 
      url: 'https://community.altmx.ai'
    }
  ]

  const mockOnComplete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本表示', () => {
    it('エンディング画面のタイトルが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('SESSION COMPLETED')).toBeInTheDocument()
    })

    it('AltMXからの最終メッセージが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('final-message')).toBeInTheDocument()
      expect(screen.getByText(/お疲れ様でした/)).toBeInTheDocument()
    })

    it('セッション統計が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('session-stats')).toBeInTheDocument()
    })

    it('作成ツール一覧が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('created-tools-list')).toBeInTheDocument()
    })

    it('ネクストアクションセクションが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('next-actions')).toBeInTheDocument()
    })
  })

  describe('セッション統計表示', () => {
    it('作成ツール数が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('ツール作成')).toBeInTheDocument()
    })

    it('生成コード行数が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('1,247')).toBeInTheDocument()
      expect(screen.getByText('行のコード生成')).toBeInTheDocument()
    })

    it('セッション時間が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('30分')).toBeInTheDocument()
      expect(screen.getByText('セッション時間')).toBeInTheDocument()
    })

    it('成功率が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('96.5%')).toBeInTheDocument()
      expect(screen.getByText('成功率')).toBeInTheDocument()
    })
  })

  describe('作成ツール一覧', () => {
    it('各ツールの名前が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('REST APIクライアント')).toBeInTheDocument()
      expect(screen.getByText('データバリデーター')).toBeInTheDocument()
      expect(screen.getByText('CI/CDパイプライン')).toBeInTheDocument()
    })

    it('各ツールのタイプが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('API Tool')).toBeInTheDocument()
      expect(screen.getByText('Utility')).toBeInTheDocument()
      expect(screen.getByText('DevOps')).toBeInTheDocument()
    })

    it('複雑度に応じたバッジが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('complexity-medium')).toBeInTheDocument()
      expect(screen.getByTestId('complexity-simple')).toBeInTheDocument()
      expect(screen.getByTestId('complexity-complex')).toBeInTheDocument()
    })
  })

  describe('ネクストアクション', () => {
    it('全てのアクションボタンが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByText('無料相談予約')).toBeInTheDocument()
      expect(screen.getByText('開発資料DL')).toBeInTheDocument()
      expect(screen.getByText('コミュニティ参加')).toBeInTheDocument()
    })

    it('QRコードが表示される（相談予約）', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('qr-code-consultation')).toBeInTheDocument()
    })

    it('アクションボタンをクリックするとURLが開かれる', () => {
      const mockOpen = vi.spyOn(window, 'open').mockImplementation(() => null)
      
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      
      const consultationButton = screen.getByText('無料相談予約')
      fireEvent.click(consultationButton)
      
      expect(mockOpen).toHaveBeenCalledWith('https://altmx.ai/consultation', '_blank')
      
      mockOpen.mockRestore()
    })
  })

  describe('天からの効果（Heavenly Effects）', () => {
    it('光線エフェクト要素が表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('light-rays')).toBeInTheDocument()
    })

    it('聖なる粒子エフェクトが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('sacred-particles')).toBeInTheDocument()
    })

    it('ゴールド紙吹雪エフェクトが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('gold-confetti')).toBeInTheDocument()
    })

    it('オーラリングエフェクトが表示される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      expect(screen.getByTestId('aura-rings')).toBeInTheDocument()
    })
  })

  describe('デザイン・スタイル', () => {
    it('エンディング画面のメインクラスが適用される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const container = screen.getByTestId('ending-screen-container')
      expect(container).toHaveClass('ending-screen')
      expect(container).toHaveClass('heavenly-theme')
    })

    it('神聖なグロー効果が適用される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const container = screen.getByTestId('ending-screen-container')
      expect(container).toHaveClass('sacred-glow')
    })

    it('レスポンシブレイアウトクラスが適用される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const container = screen.getByTestId('ending-screen-container')
      expect(container).toHaveClass('responsive-layout')
    })
  })

  describe('アニメーション', () => {
    it('タイトルにグロー・パルス効果が適用される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const title = screen.getByText('SESSION COMPLETED')
      expect(title).toHaveClass('title-glow')
      expect(title).toHaveClass('pulse-sacred')
    })

    it('統計数値にカウントアップアニメーションが適用される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const statsNumbers = screen.getAllByTestId('animated-number')
      expect(statsNumbers.length).toBeGreaterThan(0)
      statsNumbers.forEach(number => {
        expect(number).toHaveClass('count-up')
      })
    })
  })

  describe('アクセシビリティ', () => {
    it('適切なARIAラベルが設定される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const mainSection = screen.getByTestId('ending-screen-container')
      expect(mainSection).toHaveAttribute('role', 'main')
      expect(mainSection).toHaveAttribute('aria-label', 'セッション完了画面')
    })

    it('統計情報にアクセシブルな説明が設定される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const stats = screen.getByTestId('session-stats')
      expect(stats).toHaveAttribute('aria-describedby', 'session-stats-description')
    })

    it('ネクストアクションボタンに適切なラベルが設定される', () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      const consultationButton = screen.getByLabelText('無料相談を予約する')
      const downloadButton = screen.getByLabelText('開発資料をダウンロードする')
      const communityButton = screen.getByLabelText('コミュニティに参加する')
      
      expect(consultationButton).toBeInTheDocument()
      expect(downloadButton).toBeInTheDocument()
      expect(communityButton).toBeInTheDocument()
    })
  })

  describe('完了機能', () => {
    it('画面をクリックすると完了コールバックが呼ばれる', async () => {
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
        />
      )
      
      const container = screen.getByTestId('ending-screen-container')
      fireEvent.click(container)
      
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledTimes(1)
      })
    })

    it('自動完了タイマーが設定される', async () => {
      vi.useFakeTimers()
      
      render(
        <EndingScreen 
          sessionStats={mockSessionStats}
          createdTools={mockCreatedTools}
          nextActions={mockNextActions}
          onComplete={mockOnComplete}
          autoCompleteAfter={1000}
        />
      )
      
      await act(async () => {
        vi.advanceTimersByTime(1000)
      })
      
      expect(mockOnComplete).toHaveBeenCalledTimes(1)
      
      vi.useRealTimers()
    })
  })
})