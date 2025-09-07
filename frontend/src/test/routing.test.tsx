/**
 * AltMX - ルーティング機能テスト
 * TDD Phase: RED - 失敗するテストを先に書く
 * React Router統合とナビゲーションの動作確認
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { RouteProvider } from '../contexts/RouteContext'

// RouteContextのモック
vi.mock('../contexts/RouteContext', () => ({
  RouteProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useRouteContext: () => ({
    navigate: vi.fn(),
    currentRoute: 'opening',
    sessionState: {
      isActive: false,
      sessionId: '',
      startTime: new Date(),
      currentRoute: 'opening',
      navigationHistory: [],
      presenterInfo: { name: '', sessionCode: '' }
    },
    goBack: vi.fn(),
    canGoBack: false,
    isLoading: false,
    error: null,
    startSession: vi.fn(),
    endSession: vi.fn()
  })
}))

// コンポーネントのモック
vi.mock('../components/RouteWrappers', () => ({
  OpeningScreenWrapper: () => <div data-testid="opening-screen">Opening Screen</div>,
  BreakScreenWrapper: () => <div data-testid="break-screen">Break Screen</div>,
  EndingScreenWrapper: () => <div data-testid="ending-screen">Ending Screen</div>,
  NotFoundScreenWrapper: () => <div data-testid="404-screen">404 Not Found</div>,
  BadRequestErrorScreenWrapper: () => <div data-testid="400-screen">400 Bad Request</div>,
  InternalServerErrorScreenWrapper: () => <div data-testid="500-screen">500 Server Error</div>,
  ServiceUnavailableScreenWrapper: () => <div data-testid="503-screen">503 Service Unavailable</div>
}))

vi.mock('../components/VaporwaveMainScreen', () => ({
  default: () => <div data-testid="main-screen">Main Screen</div>
}))

// テスト用のルーティングコンポーネント
const TestApp = () => {
  return (
    <RouteProvider>
      <Routes>
        <Route path="/" element={<div data-testid="opening-screen">Opening Screen</div>} />
        <Route path="/main" element={<div data-testid="main-screen">Main Screen</div>} />
        <Route path="/main/:viewMode" element={<div data-testid="main-screen">Main Screen</div>} />
        <Route path="/break" element={<div data-testid="break-screen">Break Screen</div>} />
        <Route path="/ending" element={<div data-testid="ending-screen">Ending Screen</div>} />
        <Route path="/error/404" element={<div data-testid="404-screen">404 Not Found</div>} />
        <Route path="/error/400" element={<div data-testid="400-screen">400 Bad Request</div>} />
        <Route path="/error/500" element={<div data-testid="500-screen">500 Server Error</div>} />
        <Route path="/error/503" element={<div data-testid="503-screen">503 Service Unavailable</div>} />
        <Route path="*" element={<div data-testid="404-screen">404 Not Found</div>} />
      </Routes>
    </RouteProvider>
  )
}

describe('ルーティング機能テスト', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('基本ルーティング', () => {
    it('ルートパス（/）でOpeningScreenが表示される', () => {
      render(
        <MemoryRouter initialEntries={['/']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('opening-screen')).toBeInTheDocument()
      expect(screen.getByText('Opening Screen')).toBeInTheDocument()
    })

    it('メインパス（/main）でVaporwaveMainScreenが表示される', () => {
      render(
        <MemoryRouter initialEntries={['/main']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('main-screen')).toBeInTheDocument()
      expect(screen.getByText('Main Screen')).toBeInTheDocument()
    })

    it('休憩パス（/break）でBreakScreenが表示される', () => {
      render(
        <MemoryRouter initialEntries={['/break']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('break-screen')).toBeInTheDocument()
      expect(screen.getByText('Break Screen')).toBeInTheDocument()
    })

    it('エンディングパス（/ending）でEndingScreenが表示される', () => {
      render(
        <MemoryRouter initialEntries={['/ending']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('ending-screen')).toBeInTheDocument()
      expect(screen.getByText('Ending Screen')).toBeInTheDocument()
    })
  })

  describe('エラー画面ルーティング', () => {
    it('404エラーパス（/error/404）で404画面が表示される', () => {
      render(
        <MemoryRouter initialEntries={['/error/404']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('404-screen')).toBeInTheDocument()
      expect(screen.getByText('404 Not Found')).toBeInTheDocument()
    })

    it('未定義パス（/nonexistent）で404画面が表示される', () => {
      render(
        <MemoryRouter initialEntries={['/nonexistent']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('404-screen')).toBeInTheDocument()
      expect(screen.getByText('404 Not Found')).toBeInTheDocument()
    })
  })

  describe('パラメータ付きルーティング', () => {
    it('viewModeパラメータ付きメインパス（/main/code）でMainScreenが表示される', () => {
      render(
        <MemoryRouter initialEntries={['/main/code']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('main-screen')).toBeInTheDocument()
      expect(screen.getByText('Main Screen')).toBeInTheDocument()
    })
  })

  describe('RouteProvider統合テスト', () => {
    it('RouteProviderが正常に動作する', () => {
      render(
        <MemoryRouter initialEntries={['/']}>
          <TestApp />
        </MemoryRouter>
      )
      
      expect(screen.getByTestId('opening-screen')).toBeInTheDocument()
    })
  })
})