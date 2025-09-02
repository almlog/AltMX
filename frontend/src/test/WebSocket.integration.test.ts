/**
 * WebSocket Integration Tests - Red段階（失敗するテスト）
 * WebSocket・リアルタイム統合テスト
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'

// Test用のインポート（実装前なのでエラーになる想定）
import { CodeGenerationWebSocket } from '../services/codeGenerationWebSocket'
import { useCodeGeneration } from '../hooks/useCodeGeneration'

// WebSocket Mock
class MockWebSocket {
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3

  url: string
  readyState: number = MockWebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    // 非同期で接続完了をシミュレート
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 100)
  }

  send(data: string) {
    // メッセージ送信のシミュレート
    console.log('MockWebSocket send:', data)
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }

  // テスト用：メッセージ受信シミュレート
  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }))
    }
  }

  // テスト用：エラーシミュレート
  simulateError() {
    if (this.onerror) {
      this.onerror(new Event('error'))
    }
  }

  // テスト用：接続状態の強制設定
  setReadyState(state: number) {
    this.readyState = state
  }
}

describe('CodeGenerationWebSocket', () => {
  let websocket: CodeGenerationWebSocket
  let mockWebSocketConstructor: vi.MockedFunction<any>
  let currentMockInstance: MockWebSocket

  beforeEach(() => {
    // WebSocketをモック
    mockWebSocketConstructor = vi.fn((url: string) => {
      currentMockInstance = new MockWebSocket(url)
      return currentMockInstance
    })
    global.WebSocket = mockWebSocketConstructor as any
    
    // Clear all mocks
    vi.clearAllMocks()
  })

  afterEach(() => {
    websocket?.disconnect()
  })

  it('WebSocket接続が正しく確立される', async () => {
    websocket = new CodeGenerationWebSocket()
    
    const connectPromise = websocket.connect()
    
    // WebSocketが作成されることを確認
    expect(mockWebSocketConstructor).toHaveBeenCalledWith(
      expect.stringContaining('ws://localhost:8000/ws/code-generation')
    )
    
    // 接続完了まで待機
    await expect(connectPromise).resolves.toBe(true)
    
    // 少し待ってから状態確認（非同期処理のため）
    await new Promise(resolve => setTimeout(resolve, 150))
    expect(websocket.isConnected()).toBe(true)
  })

  it('接続状態の変更が正しく検知される', async () => {
    websocket = new CodeGenerationWebSocket()
    
    const connectionStateCallback = vi.fn()
    websocket.onConnectionStateChange(connectionStateCallback)
    
    await websocket.connect()
    
    // 接続状態変更コールバックが呼ばれることを確認
    expect(connectionStateCallback).toHaveBeenCalledWith(true)
  })

  it('進捗メッセージが正しく受信される', async () => {
    websocket = new CodeGenerationWebSocket()
    
    const progressCallback = vi.fn()
    websocket.onProgress(progressCallback)
    
    await websocket.connect()
    await new Promise(resolve => setTimeout(resolve, 150))
    
    // 進捗メッセージをシミュレート
    const mockProgress = {
      type: 'progress',
      stage: 'parsing',
      progress: 0.25,
      message: 'プロンプトを解析しています...'
    }
    
    currentMockInstance.simulateMessage(mockProgress)
    
    expect(progressCallback).toHaveBeenCalledWith(mockProgress)
  })

  it('生成完了メッセージが正しく受信される', async () => {
    websocket = new CodeGenerationWebSocket()
    
    const completionCallback = vi.fn()
    websocket.onCompletion(completionCallback)
    
    await websocket.connect()
    await new Promise(resolve => setTimeout(resolve, 150))
    
    // 完了メッセージをシミュレート
    const mockCompletion = {
      type: 'completion',
      sessionId: 'test-session-123',
      files: [
        { filename: 'App.tsx', content: 'import React...', language: 'typescript' }
      ],
      success: true
    }
    
    currentMockInstance.simulateMessage(mockCompletion)
    
    expect(completionCallback).toHaveBeenCalledWith(mockCompletion)
  })

  it('エラーメッセージが正しく受信される', async () => {
    websocket = new CodeGenerationWebSocket()
    
    const errorCallback = vi.fn()
    websocket.onError(errorCallback)
    
    await websocket.connect()
    await new Promise(resolve => setTimeout(resolve, 150))
    
    // エラーメッセージをシミュレート
    const mockError = {
      type: 'error',
      error: 'API_ERROR',
      message: 'AI APIへの接続でエラーが発生しました'
    }
    
    currentMockInstance.simulateMessage(mockError)
    
    expect(errorCallback).toHaveBeenCalledWith(mockError)
  })

  it('自動再接続機能が動作する', async () => {
    websocket = new CodeGenerationWebSocket()
    
    await websocket.connect()
    await new Promise(resolve => setTimeout(resolve, 150))
    expect(websocket.isConnected()).toBe(true)
    
    // 接続が切断されることをシミュレート
    currentMockInstance.close()
    
    // 少し待って自動再接続を確認
    await new Promise(resolve => setTimeout(resolve, 1100)) // 再接続は1秒後
    
    // 新しいWebSocketインスタンスが作成されることを確認
    expect(mockWebSocketConstructor).toHaveBeenCalledTimes(2)
  })

  it('代前リクエストが正しく送信される', async () => {
    websocket = new CodeGenerationWebSocket()
    
    await websocket.connect()
    await new Promise(resolve => setTimeout(resolve, 150))
    
    const mockRequest = {
      prompt: 'Create a React component',
      template: 'react-component',
      complexity: 'simple' as const
    }
    
    const sendSpy = vi.spyOn(currentMockInstance, 'send')
    
    await websocket.sendGenerationRequest(mockRequest)
    
    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify({
      type: 'generate',
      ...mockRequest
    }))
  })

  it('切断処理が正しく動作する', async () => {
    websocket = new CodeGenerationWebSocket()
    
    await websocket.connect()
    await new Promise(resolve => setTimeout(resolve, 150))
    expect(websocket.isConnected()).toBe(true)
    
    const closeSpy = vi.spyOn(currentMockInstance, 'close')
    
    websocket.disconnect()
    
    // 少し待って非同期処理完了
    await new Promise(resolve => setTimeout(resolve, 10))
    
    expect(closeSpy).toHaveBeenCalled()
    expect(websocket.isConnected()).toBe(false)
  })
})

describe('useCodeGeneration Hook', () => {
  let hookMockInstance: MockWebSocket

  beforeEach(() => {
    global.WebSocket = vi.fn((url: string) => {
      hookMockInstance = new MockWebSocket(url)
      return hookMockInstance
    }) as any
  })

  it('フックが正しく初期化される', () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    expect(result.current.isConnected).toBe(false)
    expect(result.current.isGenerating).toBe(false)
    expect(result.current.progress).toEqual({
      stage: 'idle',
      progress: 0,
      message: ''
    })
    expect(result.current.generatedFiles).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('接続処理が正しく動作する', async () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    await act(async () => {
      await result.current.connect()
    })
    
    expect(result.current.isConnected).toBe(true)
  })

  it('コード生成リクエストが正しく送信される', async () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    await act(async () => {
      await result.current.connect()
    })
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })
    
    const mockRequest = {
      prompt: 'Create a login form',
      template: 'react-form',
      complexity: 'medium' as const
    }
    
    await act(async () => {
      await result.current.generateCode(mockRequest)
    })
    
    expect(result.current.isGenerating).toBe(true)
  })

  it('進捗更新が正しく反映される', async () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    await act(async () => {
      await result.current.connect()
    })
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })
    
    act(() => {
      hookMockInstance.simulateMessage({
        type: 'progress',
        stage: 'generating',
        progress: 0.5,
        message: 'コードを生成しています...'
      })
    })
    
    expect(result.current.progress).toEqual({
      stage: 'generating',
      progress: 0.5,
      message: 'コードを生成しています...'
    })
  })

  it('生成完了時に結果が正しく反映される', async () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    await act(async () => {
      await result.current.connect()
    })
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })
    
    act(() => {
      hookMockInstance.simulateMessage({
        type: 'completion',
        sessionId: 'test-session',
        files: [
          { filename: 'LoginForm.tsx', content: 'import React...', language: 'typescript' }
        ],
        success: true
      })
    })
    
    expect(result.current.isGenerating).toBe(false)
    expect(result.current.generatedFiles).toHaveLength(1)
    expect(result.current.generatedFiles[0].filename).toBe('LoginForm.tsx')
  })

  it('エラー処理が正しく動作する', async () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    await act(async () => {
      await result.current.connect()
    })
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 150))
    })
    
    act(() => {
      hookMockInstance.simulateMessage({
        type: 'error',
        error: 'VALIDATION_ERROR',
        message: 'プロンプトの検証でエラーが発生しました'
      })
    })
    
    expect(result.current.error).toEqual({
      type: 'error',
      error: 'VALIDATION_ERROR',
      message: 'プロンプトの検証でエラーが発生しました'
    })
    expect(result.current.isGenerating).toBe(false)
  })

  it('切断処理が正しく動作する', async () => {
    const { result } = renderHook(() => useCodeGeneration())
    
    await act(async () => {
      await result.current.connect()
    })
    
    expect(result.current.isConnected).toBe(true)
    
    act(() => {
      result.current.disconnect()
    })
    
    expect(result.current.isConnected).toBe(false)
  })
})