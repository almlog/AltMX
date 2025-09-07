/**
 * NotFoundScreen (404エラー画面) Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 * 仕様書: /src/ui/03-error-screens.md
 */

import { render, screen, fireEvent, waitFor } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import NotFoundScreen from './NotFoundScreen'

describe('NotFoundScreen Component (404 Error)', () => {
  const mockOnRecordingSwitch = vi.fn()
  const mockOnRetry = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本表示', () => {
    it('404エラーコードが大型表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText('404')).toBeInTheDocument()
      expect(screen.getByText('404')).toHaveClass('error-code-large')
    })

    it('Not Foundメッセージが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText('NOT FOUND')).toBeInTheDocument()
    })

    it('AltMXからの親しみやすいメッセージが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText(/探してるファイル、どっか行っちゃったわ/)).toBeInTheDocument()
      expect(screen.getByText(/したっけ、録画のやつ見せるね/)).toBeInTheDocument()
    })
  })

  describe('アクションボタン', () => {
    it('録画デモを再生ボタンが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText('🎬 録画デモを再生')).toBeInTheDocument()
    })

    it('最初からボタンが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText('🏠 最初から')).toBeInTheDocument()
    })

    it('録画デモボタンをクリックするとコールバックが呼ばれる', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      
      const recordingButton = screen.getByText('🎬 録画デモを再生')
      fireEvent.click(recordingButton)
      
      expect(mockOnRecordingSwitch).toHaveBeenCalledTimes(1)
    })

    it('最初からボタンをクリックするとコールバックが呼ばれる', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      
      const retryButton = screen.getByText('🏠 最初から')
      fireEvent.click(retryButton)
      
      expect(mockOnRetry).toHaveBeenCalledTimes(1)
    })
  })

  describe('ステータス表示', () => {
    it('検索ステータスが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText('検索中...')).toBeInTheDocument()
    })

    it('代替案ステータスが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByText('代替案: あり')).toBeInTheDocument()
    })

    it('ステータスインジケーターが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const indicators = screen.getAllByTestId('status-indicator')
      expect(indicators).toHaveLength(2)
    })
  })

  describe('デザイン・スタイル', () => {
    it('シアン系カラーテーマが適用される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('error-screen-404')
      expect(container).toHaveClass('cyan-theme')
    })

    it('グリッチ効果のクラスが適用される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const errorCode = screen.getByText('404')
      expect(errorCode).toHaveClass('glitch-effect')
    })

    it('ネオングロー効果が適用される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('neon-glow-cyan')
    })
  })

  describe('ASCII Art装飾', () => {
    it('ASCII Art装飾が表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByTestId('ascii-art-decoration')).toBeInTheDocument()
    })

    it('ASCII Artに適切なクラスが適用される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const asciiArt = screen.getByTestId('ascii-art-decoration')
      expect(asciiArt).toHaveClass('ascii-decoration')
    })
  })

  describe('アニメーション', () => {
    it('グリッチ入場アニメーションが適用される', async () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const container = screen.getByTestId('error-screen-container')
      
      await waitFor(() => {
        expect(container).toHaveClass('glitch-in')
      })
    })

    it('パーティクルエフェクトが表示される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      expect(screen.getByTestId('particle-effects')).toBeInTheDocument()
    })
  })

  describe('レスポンシブ対応', () => {
    it('モバイル向けレイアウトクラスが適用される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('responsive-layout')
    })
  })

  describe('アクセシビリティ', () => {
    it('適切なARIAラベルが設定される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveAttribute('role', 'alert')
      expect(container).toHaveAttribute('aria-live', 'polite')
    })

    it('ボタンに適切なARIAラベルが設定される', () => {
      render(<NotFoundScreen onRecordingSwitch={mockOnRecordingSwitch} onRetry={mockOnRetry} />)
      
      const recordingButton = screen.getByText('🎬 録画デモを再生')
      expect(recordingButton).toHaveAttribute('aria-label', '録画デモに切り替える')
      
      const retryButton = screen.getByText('🏠 最初から')
      expect(retryButton).toHaveAttribute('aria-label', 'ホーム画面に戻る')
    })
  })
})