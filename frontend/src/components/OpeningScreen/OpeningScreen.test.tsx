/**
 * OpeningScreen Component Tests
 * TDD Phase: RED - 失敗するテストを先に書く
 */

import { render, screen, fireEvent, waitFor } from '../../test/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import OpeningScreen from './OpeningScreen'

describe('OpeningScreen Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本表示', () => {
    it('AltMXロゴが表示される', () => {
      render(<OpeningScreen />)
      expect(screen.getByText('AltMX')).toBeInTheDocument()
      expect(screen.getByText('AI Collaboration System')).toBeInTheDocument()
    })

    it('バージョン情報が表示される', () => {
      render(<OpeningScreen />)
      expect(screen.getByText('v2.0')).toBeInTheDocument()
    })

    it('プレゼンター名入力フィールドが表示される', () => {
      render(<OpeningScreen />)
      expect(screen.getByLabelText('Presenter ID')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('あなたの名前を入力')).toBeInTheDocument()
    })

    it('セッションコード入力フィールドが表示される', () => {
      render(<OpeningScreen />)
      expect(screen.getByLabelText('Session Code')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('セッションコード（オプション）')).toBeInTheDocument()
    })

    it('START SYSTEMボタンが表示される', () => {
      render(<OpeningScreen />)
      expect(screen.getByText('🚀 START SYSTEM')).toBeInTheDocument()
    })
  })

  describe('ステータス表示', () => {
    it('AI、Server、Usersのステータスが表示される', () => {
      render(<OpeningScreen />)
      expect(screen.getByText('AI: Online')).toBeInTheDocument()
      expect(screen.getByText('Server: Ready')).toBeInTheDocument()
      expect(screen.getByText('Users: 0')).toBeInTheDocument()
    })

    it('ステータスインジケーターが表示される', () => {
      render(<OpeningScreen />)
      const indicators = screen.getAllByTestId('status-indicator')
      expect(indicators).toHaveLength(3)
    })
  })

  describe('バリデーション', () => {
    it('プレゼンター名が空の場合エラーが表示される', async () => {
      render(<OpeningScreen />)
      
      const startButton = screen.getByText('🚀 START SYSTEM')
      fireEvent.click(startButton)

      await waitFor(() => {
        const presenterInput = screen.getByPlaceholderText('あなたの名前を入力')
        expect(presenterInput).toHaveClass('error')
      })
    })

    it('有効な入力でローディングが開始される', async () => {
      render(<OpeningScreen />)
      
      const presenterInput = screen.getByPlaceholderText('あなたの名前を入力')
      const startButton = screen.getByText('🚀 START SYSTEM')

      fireEvent.change(presenterInput, { target: { value: '太郎' } })
      fireEvent.click(startButton)

      // ローディングが開始されることを確認
      await waitFor(() => {
        expect(screen.getByText('システム起動中...')).toBeInTheDocument()
      })
    })
  })

  describe('アニメーション', () => {
    it('ロゴにパルスアニメーションが適用される', () => {
      render(<OpeningScreen />)
      const logo = screen.getByText('AltMX')
      expect(logo).toHaveClass('logo-pulse')
    })

    it('フェードインアニメーションが適用される', () => {
      render(<OpeningScreen />)
      const bootContainer = document.querySelector('.boot-container')
      expect(bootContainer).toHaveClass('fade-in')
    })
  })

  describe('ブートシーケンス', () => {
    it('ブートシーケンスが表示される', async () => {
      render(<OpeningScreen showBootSequence={true} />)
      
      await waitFor(() => {
        expect(screen.getByText('ALTMX SYSTEM v2.0.1')).toBeInTheDocument()
        expect(screen.getByText('Initializing AI Core... [OK]')).toBeInTheDocument()
        expect(screen.getByText('System Ready.')).toBeInTheDocument()
      })
    })
  })

  describe('ローディング', () => {
    it('ローディング画面が表示される', async () => {
      render(<OpeningScreen />)
      
      const presenterInput = screen.getByPlaceholderText('あなたの名前を入力')
      const startButton = screen.getByText('🚀 START SYSTEM')

      fireEvent.change(presenterInput, { target: { value: '太郎' } })
      fireEvent.click(startButton)

      await waitFor(() => {
        expect(screen.getByText('システム起動中...')).toBeInTheDocument()
      })
    })

    it('ローディングプログレスバーが動作する', async () => {
      render(<OpeningScreen />)
      
      const presenterInput = screen.getByPlaceholderText('あなたの名前を入力')
      const startButton = screen.getByText('🚀 START SYSTEM')

      fireEvent.change(presenterInput, { target: { value: '太郎' } })
      fireEvent.click(startButton)

      await waitFor(() => {
        const progressBar = screen.getByTestId('loading-progress')
        expect(progressBar).toBeInTheDocument()
      })
    })
  })

  describe('キーボード操作', () => {
    it('Enterキーでローディングが開始される', async () => {
      render(<OpeningScreen />)
      
      const presenterInput = screen.getByPlaceholderText('あなたの名前を入力')
      
      fireEvent.change(presenterInput, { target: { value: '太郎' } })
      fireEvent.keyPress(document, { key: 'Enter', code: 'Enter' })

      await waitFor(() => {
        expect(screen.getByText('システム起動中...')).toBeInTheDocument()
      })
    })
  })

  describe('サイバーパンクエフェクト', () => {
    it('背景グラデーションが適用される', () => {
      render(<OpeningScreen />)
      const bgContainer = screen.getByTestId('bg-container')
      expect(bgContainer).toHaveClass('bg-gradient-animation')
    })

    it('グリッドオーバーレイが表示される', () => {
      render(<OpeningScreen />)
      const gridOverlay = screen.getByTestId('grid-overlay')
      expect(gridOverlay).toBeInTheDocument()
    })

    it('スキャンラインが表示される', () => {
      render(<OpeningScreen />)
      const scanlines = screen.getByTestId('scanlines')
      expect(scanlines).toBeInTheDocument()
    })
  })
})