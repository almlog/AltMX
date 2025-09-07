/**
 * BadRequestErrorScreen (400エラー画面) Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 * 仕様書: /src/ui/03-error-screens.md
 */

import { render, screen, fireEvent, waitFor } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BadRequestErrorScreen from './BadRequestErrorScreen'

describe('BadRequestErrorScreen Component (400 Bad Request)', () => {
  const mockOnRecordingSwitch = vi.fn()
  const mockOnRetry = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本表示', () => {
    it('400エラーコードが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText('400')).toBeInTheDocument()
    })

    it('Bad Requestのタイトルが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText('BAD REQUEST')).toBeInTheDocument()
    })

    it('AltMXのメッセージが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText(/あれ？なんか変なデータ来たっしょ/)).toBeInTheDocument()
    })

    it('録画デモボタンが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText('📼 録画デモを再生')).toBeInTheDocument()
    })

    it('もう一度試すボタンが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText('🔄 もう一度試す')).toBeInTheDocument()
    })
  })

  describe('ステータス表示', () => {
    it('AIスタンバイ中ステータスが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText('AI: スタンバイ中')).toBeInTheDocument()
    })

    it('録画準備完了ステータスが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByText('録画: 準備完了')).toBeInTheDocument()
    })

    it('ステータス要素にテストIDが設定される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByTestId('ai-status')).toBeInTheDocument()
      expect(screen.getByTestId('recording-status')).toBeInTheDocument()
    })
  })

  describe('アクションボタン', () => {
    it('録画デモボタンをクリックするとコールバックが呼ばれる', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      
      const recordingButton = screen.getByText('📼 録画デモを再生')
      fireEvent.click(recordingButton)
      
      expect(mockOnRecordingSwitch).toHaveBeenCalledTimes(1)
    })

    it('リトライボタンをクリックするとコールバックが呼ばれる', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      
      const retryButton = screen.getByText('🔄 もう一度試す')
      fireEvent.click(retryButton)
      
      expect(mockOnRetry).toHaveBeenCalledTimes(1)
    })
  })

  describe('デザイン・スタイル', () => {
    it('400エラー画面のメインクラスが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('error-screen-container')
      expect(container).toHaveClass('error-screen-400')
    })

    it('オレンジテーマが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('orange-theme')
    })

    it('エラーコードにグリッチ効果クラスが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const errorCode = screen.getByText('400')
      expect(errorCode).toHaveClass('error-code-large')
      expect(errorCode).toHaveClass('glitch-effect')
    })

    it('ネオングロー効果が適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('neon-glow-orange')
    })
  })

  describe('アニメーション', () => {
    it('グリッチインアニメーションクラスが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const errorCode = screen.getByText('400')
      expect(errorCode).toHaveClass('glitch-in')
    })

    it('数字グリッチアニメーションが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const errorCode = screen.getByText('400')
      expect(errorCode).toHaveClass('number-glitch')
    })

    it('背景パーティクル要素が表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByTestId('background-particles')).toBeInTheDocument()
    })
  })

  describe('レスポンシブ対応', () => {
    it('レスポンシブレイアウトクラスが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('responsive-layout')
    })
  })

  describe('アクセシビリティ', () => {
    it('エラーメッセージに適切なロールが設定される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const errorMessage = screen.getByTestId('error-message')
      expect(errorMessage).toHaveAttribute('role', 'alert')
    })

    it('アクションボタンにARIAラベルが設定される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const recordingButton = screen.getByLabelText('録画デモを再生する')
      const retryButton = screen.getByLabelText('リクエストを再試行する')
      
      expect(recordingButton).toBeInTheDocument()
      expect(retryButton).toBeInTheDocument()
    })
  })

  describe('パーティクル効果', () => {
    it('複数のパーティクル要素が表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const particles = screen.getAllByTestId(/particle-\d+/)
      expect(particles.length).toBeGreaterThan(3)
    })

    it('パーティクルにアニメーションクラスが適用される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      const particles = screen.getAllByTestId(/particle-\d+/)
      particles.forEach(particle => {
        expect(particle).toHaveClass('particle-float')
      })
    })
  })

  describe('エラー情報表示', () => {
    it('エラー詳細情報が表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByTestId('error-details')).toBeInTheDocument()
    })

    it('タイムスタンプが表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByTestId('error-timestamp')).toBeInTheDocument()
    })

    it('リクエスト情報が表示される', () => {
      render(
        <BadRequestErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onRetry={mockOnRetry}
        />
      )
      expect(screen.getByTestId('request-info')).toBeInTheDocument()
    })
  })
})