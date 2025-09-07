/**
 * AltMX - Route Context & Session Management
 * React Routerを統合したアプリケーションルーティングコンテキスト
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import type { RouteNames, SessionState, RouteContextValue, NavigationHistory } from '../types/routing'

const RouteContext = createContext<RouteContextValue | null>(null)

interface RouteProviderProps {
  children: React.ReactNode
}

export const RouteProvider: React.FC<RouteProviderProps> = ({ children }) => {
  // React Router hooks
  const navigate = useNavigate()
  const location = useLocation()

  // Session state management
  const [sessionState, setSessionState] = useState<SessionState>({
    isActive: false,
    sessionId: '',
    startTime: new Date(),
    currentRoute: 'opening',
    navigationHistory: [],
    presenterInfo: {
      name: '',
      sessionCode: ''
    }
  })

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // パスからルート名を取得
  const getRouteNameFromPath = useCallback((pathname: string): RouteNames => {
    if (pathname === '/') return 'opening'
    if (pathname.startsWith('/main')) return 'main'
    if (pathname === '/break') return 'break'
    if (pathname === '/ending') return 'ending'
    if (pathname === '/error/404') return 'error-404'
    if (pathname === '/error/400') return 'error-400'
    if (pathname === '/error/500') return 'error-500'
    if (pathname === '/error/503') return 'error-503'
    return 'error-404' // デフォルトは404
  }, [])

  // 現在のルートを取得
  const currentRoute = getRouteNameFromPath(location.pathname)

  // ナビゲーション履歴の更新
  const addToNavigationHistory = useCallback((routeName: RouteNames, params?: any, state?: any) => {
    const historyEntry: NavigationHistory = {
      routeName,
      timestamp: new Date(),
      params,
      state
    }

    setSessionState(prev => ({
      ...prev,
      currentRoute: routeName,
      navigationHistory: [...prev.navigationHistory, historyEntry]
    }))
  }, [])

  // カスタムナビゲーション関数
  const customNavigate = useCallback((route: RouteNames, params?: any, state?: any) => {
    setIsLoading(true)
    setError(null)

    try {
      let path = ''

      switch (route) {
        case 'opening':
          path = '/'
          break
        case 'main':
          path = params?.viewMode ? `/main/${params.viewMode}` : '/main'
          break
        case 'break':
          path = '/break'
          break
        case 'ending':
          path = '/ending'
          break
        case 'error-404':
          path = '/error/404'
          break
        case 'error-400':
          path = '/error/400'
          break
        case 'error-500':
          path = '/error/500'
          break
        case 'error-503':
          path = '/error/503'
          break
        default:
          path = '/error/404'
      }

      // React Routerでナビゲーション実行
      navigate(path, { state })

      // 履歴に追加
      addToNavigationHistory(route, params, state)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Navigation failed')
      console.error('Navigation error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [navigate, addToNavigationHistory])

  // 戻る機能
  const goBack = useCallback(() => {
    if (sessionState.navigationHistory.length > 1) {
      setIsLoading(true)
      try {
        navigate(-1)
        setSessionState(prev => ({
          ...prev,
          navigationHistory: prev.navigationHistory.slice(0, -1)
        }))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Go back failed')
      } finally {
        setIsLoading(false)
      }
    }
  }, [navigate, sessionState.navigationHistory])

  // 戻ることができるかどうか
  const canGoBack = sessionState.navigationHistory.length > 1

  // セッション開始
  const startSession = useCallback((presenterName: string, sessionCode: string) => {
    const sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    setSessionState(prev => ({
      ...prev,
      isActive: true,
      sessionId,
      startTime: new Date(),
      presenterInfo: {
        name: presenterName,
        sessionCode
      }
    }))
  }, [])

  // セッション終了
  const endSession = useCallback(() => {
    setSessionState(prev => ({
      ...prev,
      isActive: false,
      sessionId: '',
      presenterInfo: {
        name: '',
        sessionCode: ''
      }
    }))
    customNavigate('opening')
  }, [customNavigate])

  // 現在のルート変更時の履歴更新
  useEffect(() => {
    const newRoute = getRouteNameFromPath(location.pathname)
    if (newRoute !== sessionState.currentRoute) {
      addToNavigationHistory(newRoute)
    }
  }, [location.pathname, getRouteNameFromPath, addToNavigationHistory, sessionState.currentRoute])

  const contextValue: RouteContextValue = {
    currentRoute,
    sessionState,
    navigate: customNavigate,
    goBack,
    canGoBack,
    isLoading,
    error
  }

  // セッション管理メソッドをコンテキストに追加
  const extendedContextValue = {
    ...contextValue,
    startSession,
    endSession
  } as RouteContextValue & {
    startSession: typeof startSession
    endSession: typeof endSession
  }

  return (
    <RouteContext.Provider value={extendedContextValue}>
      {children}
    </RouteContext.Provider>
  )
}

// カスタムフック
export const useRouteContext = () => {
  const context = useContext(RouteContext)
  if (!context) {
    throw new Error('useRouteContext must be used within a RouteProvider')
  }
  return context
}

export default RouteContext