/**
 * BreakScreen (休憩画面) Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 * 仕様書: /src/ui/04-break-ending-screens.md
 */

import { render, screen, fireEvent, waitFor, act } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BreakScreen from './BreakScreen'
import { useTimer } from '../../hooks/useTimer'

// タイマーをモック化
vi.mock('../../hooks/useTimer')
const mockedUseTimer = vi.mocked(useTimer)

describe('BreakScreen Component (休憩画面)', () => {
  const mockOnComplete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    // デフォルトのタイマー状態
    mockedUseTimer.mockReturnValue({
      timeRemaining: 300, // 5分
      isRunning: true,
      start: vi.fn(),
      pause: vi.fn(),
      reset: vi.fn()
    })
  })

  describe('基本表示', () => {
    it('休憩画面のタイトルが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByText('BREAK TIME')).toBeInTheDocument()
    })

    it('カウントダウンタイマーが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByText('05:00')).toBeInTheDocument()
      expect(screen.getByTestId('countdown-timer')).toBeInTheDocument()
    })

    it('次セッション予告が表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByText('NEXT SESSION')).toBeInTheDocument()
      expect(screen.getByTestId('next-session-preview')).toBeInTheDocument()
    })

    it('参加者向けメッセージが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByText(/ちょっと休憩だっしょ/)).toBeInTheDocument()
      expect(screen.getByTestId('break-message')).toBeInTheDocument()
    })
  })

  describe('カウントダウンタイマー機能', () => {
    it('MM:SS形式で時間が表示される', () => {
      mockedUseTimer.mockReturnValue({
        timeRemaining: 300,
        isRunning: true,
        start: vi.fn(),
        pause: vi.fn(),
        reset: vi.fn()
      })
      
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByText('05:00')).toBeInTheDocument()
    })

    it('残り時間が正しく更新される', () => {
      const { rerender } = render(<BreakScreen onComplete={mockOnComplete} />)
      
      // タイマーを240秒（4:00）に更新
      mockedUseTimer.mockReturnValue({
        timeRemaining: 240,
        isRunning: true,
        start: vi.fn(),
        pause: vi.fn(),
        reset: vi.fn()
      })
      
      rerender(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByText('04:00')).toBeInTheDocument()
    })

    it('残り1分以下で警告色に変化する', () => {
      mockedUseTimer.mockReturnValue({
        timeRemaining: 50, // 50秒
        isRunning: true,
        start: vi.fn(),
        pause: vi.fn(),
        reset: vi.fn()
      })
      
      render(<BreakScreen onComplete={mockOnComplete} />)
      const timer = screen.getByTestId('countdown-timer')
      expect(timer).toHaveClass('warning-time')
    })

    it('タイマーが0になったらコールバックが呼ばれる', async () => {
      mockedUseTimer.mockReturnValue({
        timeRemaining: 0,
        isRunning: false,
        start: vi.fn(),
        pause: vi.fn(),
        reset: vi.fn()
      })
      
      render(<BreakScreen onComplete={mockOnComplete} />)
      
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('ビジュアルウェーブバー', () => {
    it('ビジュアライザー風バーが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByTestId('visual-wave-bars')).toBeInTheDocument()
    })

    it('複数のウェーブバーが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const bars = screen.getAllByTestId('wave-bar')
      expect(bars.length).toBeGreaterThan(5)
    })

    it('ウェーブバーにアニメーションクラスが適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const bars = screen.getAllByTestId('wave-bar')
      bars.forEach(bar => {
        expect(bar).toHaveClass('wave-bounce')
      })
    })
  })

  describe('次セッション予告', () => {
    it('次セッションのタイトルが表示される', () => {
      const nextSessionInfo = {
        title: 'Advanced AI Features',
        description: 'より高度なAI機能を実装します',
        estimatedDuration: 45
      }
      
      render(<BreakScreen onComplete={mockOnComplete} nextSessionInfo={nextSessionInfo} />)
      expect(screen.getByText('Advanced AI Features')).toBeInTheDocument()
    })

    it('次セッションの説明が表示される', () => {
      const nextSessionInfo = {
        title: 'Advanced AI Features',
        description: 'より高度なAI機能を実装します',
        estimatedDuration: 45
      }
      
      render(<BreakScreen onComplete={mockOnComplete} nextSessionInfo={nextSessionInfo} />)
      expect(screen.getByText('より高度なAI機能を実装します')).toBeInTheDocument()
    })

    it('推定時間が表示される', () => {
      const nextSessionInfo = {
        title: 'Advanced AI Features',
        description: 'より高度なAI機能を実装します',
        estimatedDuration: 45
      }
      
      render(<BreakScreen onComplete={mockOnComplete} nextSessionInfo={nextSessionInfo} />)
      expect(screen.getByText('約45分')).toBeInTheDocument()
    })
  })

  describe('デザイン・スタイル', () => {
    it('休憩画面のメインクラスが適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const container = screen.getByTestId('break-screen-container')
      expect(container).toHaveClass('break-screen')
      expect(container).toHaveClass('vaporwave-theme')
    })

    it('大型タイマー表示のスタイルが適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const timer = screen.getByTestId('countdown-timer')
      expect(timer).toHaveClass('timer-display')
    })

    it('グラデーション背景が適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const container = screen.getByTestId('break-screen-container')
      expect(container).toHaveClass('gradient-background')
    })
  })

  describe('アニメーション', () => {
    it('タイトルにパルス効果が適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const title = screen.getByText('BREAK TIME')
      expect(title).toHaveClass('pulse-effect')
    })

    it('背景グラデーションアニメーションが適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const background = screen.getByTestId('animated-background')
      expect(background).toHaveClass('gradient-animation')
    })

    it('フローティングパーティクルが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      expect(screen.getByTestId('floating-particles')).toBeInTheDocument()
    })
  })

  describe('レスポンシブ対応', () => {
    it('モバイル向けレイアウトクラスが適用される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const container = screen.getByTestId('break-screen-container')
      expect(container).toHaveClass('responsive-layout')
    })
  })

  describe('アクセシビリティ', () => {
    it('適切なARIAラベルが設定される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const timer = screen.getByTestId('countdown-timer')
      expect(timer).toHaveAttribute('aria-live', 'polite')
      expect(timer).toHaveAttribute('aria-label', 'カウントダウンタイマー')
    })

    it('休憩メッセージに適切なロールが設定される', () => {
      render(<BreakScreen onComplete={mockOnComplete} />)
      const message = screen.getByTestId('break-message')
      expect(message).toHaveAttribute('role', 'status')
    })
  })

  describe('制御ボタン', () => {
    it('一時停止ボタンが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} showControls={true} />)
      expect(screen.getByText('⏸️ 一時停止')).toBeInTheDocument()
    })

    it('スキップボタンが表示される', () => {
      render(<BreakScreen onComplete={mockOnComplete} showControls={true} />)
      expect(screen.getByText('⏭️ スキップ')).toBeInTheDocument()
    })

    it('スキップボタンをクリックするとコールバックが呼ばれる', () => {
      render(<BreakScreen onComplete={mockOnComplete} showControls={true} />)
      
      const skipButton = screen.getByText('⏭️ スキップ')
      fireEvent.click(skipButton)
      
      expect(mockOnComplete).toHaveBeenCalledTimes(1)
    })
  })
})