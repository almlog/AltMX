/**
 * ServiceUnavailableScreen (503エラー画面) Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 * 仕様書: /src/ui/03-error-screens.md
 */

import { render, screen, fireEvent, waitFor, act } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ServiceUnavailableScreen from './ServiceUnavailableScreen'

describe('ServiceUnavailableScreen Component (503 Service Unavailable)', () => {
  const mockOnRecordingSwitch = vi.fn()
  const mockOnWaitAndRetry = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本表示', () => {
    it('503エラーコードが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText('503')).toBeInTheDocument()
    })

    it('Service Unavailableのタイトルが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText('SERVICE UNAVAILABLE')).toBeInTheDocument()
    })

    it('AltMXのメッセージが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText(/ちょっと混雑してるみたいっしょ/)).toBeInTheDocument()
    })

    it('録画再生ボタンが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText('📼 録画を再生')).toBeInTheDocument()
    })

    it('30秒待機ボタンが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText('⏳ 30秒待つ')).toBeInTheDocument()
    })
  })

  describe('ステータス表示', () => {
    it('API過負荷ステータスが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText('API: 過負荷')).toBeInTheDocument()
    })

    it('待機時間ステータスが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByText('待機時間: 30秒')).toBeInTheDocument()
    })

    it('ステータス要素にテストIDが設定される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('api-status')).toBeInTheDocument()
      expect(screen.getByTestId('wait-time-status')).toBeInTheDocument()
    })
  })

  describe('アクションボタン', () => {
    it('録画再生ボタンをクリックするとコールバックが呼ばれる', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      
      const recordingButton = screen.getByText('📼 録画を再生')
      fireEvent.click(recordingButton)
      
      expect(mockOnRecordingSwitch).toHaveBeenCalledTimes(1)
    })

    it('待機ボタンをクリックするとコールバックが呼ばれる', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      
      const waitButton = screen.getByText('⏳ 30秒待つ')
      fireEvent.click(waitButton)
      
      expect(mockOnWaitAndRetry).toHaveBeenCalledTimes(1)
    })
  })

  describe('デザイン・スタイル', () => {
    it('503エラー画面のメインクラスが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('error-screen-container')
      expect(container).toHaveClass('error-screen-503')
    })

    it('紫テーマが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('purple-theme')
    })

    it('エラーコードにグリッチ効果クラスが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const errorCode = screen.getByText('503')
      expect(errorCode).toHaveClass('error-code-large')
      expect(errorCode).toHaveClass('glitch-effect')
    })

    it('ネオングロー効果が適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('neon-glow-purple')
    })
  })

  describe('アニメーション', () => {
    it('グリッチインアニメーションクラスが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const errorCode = screen.getByText('503')
      expect(errorCode).toHaveClass('glitch-in')
    })

    it('数字グリッチアニメーションが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const errorCode = screen.getByText('503')
      expect(errorCode).toHaveClass('number-glitch')
    })

    it('背景パーティクル要素が表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('background-particles')).toBeInTheDocument()
    })
  })

  describe('レスポンシブ対応', () => {
    it('レスポンシブレイアウトクラスが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('responsive-layout')
    })
  })

  describe('アクセシビリティ', () => {
    it('エラーメッセージに適切なロールが設定される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const errorMessage = screen.getByTestId('error-message')
      expect(errorMessage).toHaveAttribute('role', 'alert')
    })

    it('アクションボタンにARIAラベルが設定される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const recordingButton = screen.getByLabelText('録画を再生する')
      const waitButton = screen.getByLabelText('30秒待機してから再試行')
      
      expect(recordingButton).toBeInTheDocument()
      expect(waitButton).toBeInTheDocument()
    })
  })

  describe('パーティクル効果', () => {
    it('複数のパーティクル要素が表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      const particles = screen.getAllByTestId(/particle-\d+/)
      expect(particles.length).toBeGreaterThan(3)
    })

    it('パーティクルにアニメーションクラスが適用される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
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
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('error-details')).toBeInTheDocument()
    })

    it('タイムスタンプが表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('error-timestamp')).toBeInTheDocument()
    })

    it('サーバー負荷情報が表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('server-load-info')).toBeInTheDocument()
    })
  })

  describe('待機カウントダウン機能', () => {
    it('カウントダウンタイマー要素が表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('countdown-timer')).toBeInTheDocument()
    })

    it('推定復旧時間が表示される', () => {
      render(
        <ServiceUnavailableScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onWaitAndRetry={mockOnWaitAndRetry}
        />
      )
      expect(screen.getByTestId('estimated-recovery')).toBeInTheDocument()
    })
  })
})