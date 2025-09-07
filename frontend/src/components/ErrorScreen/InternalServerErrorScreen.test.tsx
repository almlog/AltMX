/**
 * InternalServerErrorScreen (500エラー画面) Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 * 仕様書: /src/ui/03-error-screens.md
 */

import { render, screen, fireEvent, waitFor } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import InternalServerErrorScreen from './InternalServerErrorScreen'

describe('InternalServerErrorScreen Component (500 Internal Server Error)', () => {
  const mockOnRecordingSwitch = vi.fn()
  const mockOnEmergencyMode = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本表示', () => {
    it('500エラーコードが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText('500')).toBeInTheDocument()
    })

    it('Internal Server Errorのタイトルが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText('INTERNAL SERVER ERROR')).toBeInTheDocument()
    })

    it('AltMXのメッセージが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText(/なんまらヤバいことになったっしょ/)).toBeInTheDocument()
    })

    it('録画デモ切替ボタンが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText('📼 録画デモに切替')).toBeInTheDocument()
    })

    it('緊急モードボタンが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText('🚨 緊急モード')).toBeInTheDocument()
    })
  })

  describe('ステータス表示', () => {
    it('サーバーエラーステータスが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText('サーバー: エラー')).toBeInTheDocument()
    })

    it('バックアップOKステータスが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByText('バックアップ: OK')).toBeInTheDocument()
    })

    it('ステータス要素にテストIDが設定される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByTestId('server-status')).toBeInTheDocument()
      expect(screen.getByTestId('backup-status')).toBeInTheDocument()
    })
  })

  describe('アクションボタン', () => {
    it('録画デモボタンをクリックするとコールバックが呼ばれる', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      
      const recordingButton = screen.getByText('📼 録画デモに切替')
      fireEvent.click(recordingButton)
      
      expect(mockOnRecordingSwitch).toHaveBeenCalledTimes(1)
    })

    it('緊急モードボタンをクリックするとコールバックが呼ばれる', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      
      const emergencyButton = screen.getByText('🚨 緊急モード')
      fireEvent.click(emergencyButton)
      
      expect(mockOnEmergencyMode).toHaveBeenCalledTimes(1)
    })
  })

  describe('デザイン・スタイル', () => {
    it('500エラー画面のメインクラスが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('error-screen-container')
      expect(container).toHaveClass('error-screen-500')
    })

    it('ピンクテーマが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('pink-theme')
    })

    it('エラーコードにグリッチ効果クラスが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const errorCode = screen.getByText('500')
      expect(errorCode).toHaveClass('error-code-large')
      expect(errorCode).toHaveClass('glitch-effect')
    })

    it('ネオングロー効果が適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('neon-glow-pink')
    })
  })

  describe('アニメーション', () => {
    it('グリッチインアニメーションクラスが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const errorCode = screen.getByText('500')
      expect(errorCode).toHaveClass('glitch-in')
    })

    it('数字グリッチアニメーションが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const errorCode = screen.getByText('500')
      expect(errorCode).toHaveClass('number-glitch')
    })

    it('背景パーティクル要素が表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByTestId('background-particles')).toBeInTheDocument()
    })
  })

  describe('レスポンシブ対応', () => {
    it('レスポンシブレイアウトクラスが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const container = screen.getByTestId('error-screen-container')
      expect(container).toHaveClass('responsive-layout')
    })
  })

  describe('アクセシビリティ', () => {
    it('エラーメッセージに適切なロールが設定される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const errorMessage = screen.getByTestId('error-message')
      expect(errorMessage).toHaveAttribute('role', 'alert')
    })

    it('アクションボタンにARIAラベルが設定される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const recordingButton = screen.getByLabelText('録画デモに切り替え')
      const emergencyButton = screen.getByLabelText('緊急モードを開始')
      
      expect(recordingButton).toBeInTheDocument()
      expect(emergencyButton).toBeInTheDocument()
    })
  })

  describe('パーティクル効果', () => {
    it('複数のパーティクル要素が表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      const particles = screen.getAllByTestId(/particle-\d+/)
      expect(particles.length).toBeGreaterThan(3)
    })

    it('パーティクルにアニメーションクラスが適用される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
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
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByTestId('error-details')).toBeInTheDocument()
    })

    it('タイムスタンプが表示される', () => {
      render(
        <InternalServerErrorScreen 
          onRecordingSwitch={mockOnRecordingSwitch}
          onEmergencyMode={mockOnEmergencyMode}
        />
      )
      expect(screen.getByTestId('error-timestamp')).toBeInTheDocument()
    })
  })
})