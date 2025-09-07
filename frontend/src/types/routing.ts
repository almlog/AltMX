/**
 * AltMX - Router Types & Interfaces
 * React Router の型定義とルーティング設計
 * 仕様書ベース: UI仕様書 01-04 各画面
 */

export type RouteNames = 
  | 'opening'
  | 'main'
  | 'break'
  | 'ending'
  | 'error-404'
  | 'error-400'
  | 'error-500'
  | 'error-503'

export type ViewModes = 
  | 'code'
  | 'tree'
  | 'file'
  | 'preview'

export type ErrorTypes = 
  | '404'
  | '400'
  | '500'
  | '503'

// ルート情報インターフェース
export interface RouteInfo {
  path: string
  name: RouteNames
  component: string
  title: string
  description: string
  theme: string
  protected?: boolean
}

// オープニング画面の状態
export interface OpeningScreenState {
  showBootSequence: boolean
  presenterName: string
  sessionCode: string
  isLoading: boolean
  loadingProgress: number
  loadingMessage: string
  systemReady: boolean
}

// メイン画面の状態（ヴェイパーウェイブUI）
export interface VaporwaveMainScreenState {
  currentView: ViewModes
  altmxStatus: {
    recognition: 'online' | 'offline'
    generation: 'turbo' | 'normal' | 'eco'
    quality: 'maximum' | 'high' | 'medium'
    speed: number // tokens/second
  }
  talkLog: Array<{
    type: 'user' | 'ai'
    message: string
    timestamp: Date
  }>
  codeContent: {
    currentCode: string
    fileTree: FileNode[]
    selectedFile: string
    previewUrl: string
  }
  progress: {
    current: number
    message: string
    isActive: boolean
  }
  isTurboMode: boolean
}

// ファイルツリーノード
export interface FileNode {
  name: string
  type: 'file' | 'directory'
  path: string
  children?: FileNode[]
  size?: number
  lastModified?: Date
}

// 休憩画面の状態
export interface BreakScreenState {
  timeRemaining: number // 秒単位（0-300）
  isCountingDown: boolean
  nextSessionInfo: {
    title: string
    description: string
    estimatedDuration: number
  }
  waveAnimation: {
    bars: number[]
    frequency: number
  }
}

// エンディング画面の状態
export interface EndingScreenState {
  sessionStats: {
    toolsCreated: number
    linesGenerated: number
    sessionDuration: number
    successRate: number
  }
  createdTools: Array<{
    name: string
    type: string
    complexity: 'simple' | 'medium' | 'complex'
  }>
  finalMessage: string
  nextActions: Array<{
    type: 'consultation' | 'download' | 'community'
    title: string
    url: string
    qrCode?: string
  }>
  heavenlyEffects: {
    lightRays: boolean
    particles: boolean
    confetti: boolean
    auraRings: boolean
  }
}

// エラー画面の状態
export interface ErrorScreenState {
  errorType: ErrorTypes
  errorCode: string
  errorMessage: string
  altmxMessage: string
  timestamp: string
  canRetry: boolean
  canSwitchToRecording: boolean
  estimatedRecoveryTime?: string
  serverLoadInfo?: {
    currentLoad: number
    queueSize: number
  }
}

// ナビゲーション履歴
export interface NavigationHistory {
  routeName: RouteNames
  timestamp: Date
  params?: Record<string, any>
  state?: any
}

// セッション管理
export interface SessionState {
  isActive: boolean
  sessionId: string
  startTime: Date
  currentRoute: RouteNames
  navigationHistory: NavigationHistory[]
  presenterInfo: {
    name: string
    sessionCode: string
  }
}

// ルートコンテキスト
export interface RouteContextValue {
  currentRoute: RouteNames
  sessionState: SessionState
  navigate: (route: RouteNames, params?: any, state?: any) => void
  goBack: () => void
  canGoBack: boolean
  isLoading: boolean
  error: string | null
}

// ルートパラメータ型
export interface RouteParams {
  errorType?: ErrorTypes
  viewMode?: ViewModes
  fileId?: string
  sessionCode?: string
}

// ルート設定
export const ROUTE_CONFIG: Record<RouteNames, RouteInfo> = {
  opening: {
    path: '/',
    name: 'opening',
    component: 'OpeningScreen',
    title: 'AltMX - System Boot',
    description: 'システム起動・プレゼンターログイン',
    theme: 'vaporwave-boot',
    protected: false
  },
  main: {
    path: '/main/:viewMode?',
    name: 'main',
    component: 'VaporwaveMainScreen',
    title: 'AltMX - Live Coding Session',
    description: 'メインライブコーディング画面',
    theme: 'vaporwave-main',
    protected: true
  },
  break: {
    path: '/break',
    name: 'break',
    component: 'BreakScreen',
    title: 'AltMX - Break Time',
    description: '休憩画面（5分タイマー）',
    theme: 'vaporwave-break',
    protected: true
  },
  ending: {
    path: '/ending',
    name: 'ending',
    component: 'EndingScreen',
    title: 'AltMX - Session Complete',
    description: 'セッション完了・神聖エンディング',
    theme: 'heavenly-ending',
    protected: true
  },
  'error-404': {
    path: '/error/404',
    name: 'error-404',
    component: 'NotFoundScreen',
    title: 'AltMX - Page Not Found',
    description: '404エラー画面（シアンテーマ）',
    theme: 'error-cyan'
  },
  'error-400': {
    path: '/error/400',
    name: 'error-400',
    component: 'BadRequestErrorScreen',
    title: 'AltMX - Bad Request',
    description: '400エラー画面（オレンジテーマ）',
    theme: 'error-orange'
  },
  'error-500': {
    path: '/error/500',
    name: 'error-500',
    component: 'InternalServerErrorScreen',
    title: 'AltMX - Server Error',
    description: '500エラー画面（ピンクテーマ）',
    theme: 'error-pink'
  },
  'error-503': {
    path: '/error/503',
    name: 'error-503',
    component: 'ServiceUnavailableScreen',
    title: 'AltMX - Service Unavailable',
    description: '503エラー画面（紫テーマ）',
    theme: 'error-purple'
  }
}

// ルート遷移パターン
export const ROUTE_TRANSITIONS: Record<RouteNames, RouteNames[]> = {
  opening: ['main', 'error-404', 'error-400', 'error-500', 'error-503'],
  main: ['break', 'ending', 'error-404', 'error-400', 'error-500', 'error-503'],
  break: ['main'],
  ending: ['opening'],
  'error-404': ['opening', 'main'],
  'error-400': ['opening', 'main'],
  'error-500': ['opening', 'main'],
  'error-503': ['opening', 'main']
}