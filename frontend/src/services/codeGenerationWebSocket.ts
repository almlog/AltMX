/**
 * Code Generation WebSocket Service - Green段階（テストを通すための実装）
 * WebSocketを使ったリアルタイム通信サービス
 */

export interface ProgressMessage {
  type: 'progress'
  stage: 'parsing' | 'generating' | 'validating' | 'organizing'
  progress: number // 0.0 - 1.0
  message: string
}

export interface CompletionMessage {
  type: 'completion'
  sessionId: string
  files: Array<{
    filename: string
    content: string
    language: string
    description?: string
  }>
  success: boolean
}

export interface ErrorMessage {
  type: 'error'
  error: string
  message: string
}

export interface GenerationRequest {
  type: 'generate'
  prompt: string
  template: string
  complexity: 'simple' | 'medium' | 'complex'
  options?: {
    includeTests?: boolean
    includeDocs?: boolean
    useTypeScript?: boolean
    useTailwind?: boolean
  }
}

type WebSocketMessage = ProgressMessage | CompletionMessage | ErrorMessage

export class CodeGenerationWebSocket {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // 1秒
  private isManuallyDisconnected = false

  // Callback handlers
  private progressHandlers: ((message: ProgressMessage) => void)[] = []
  private completionHandlers: ((message: CompletionMessage) => void)[] = []
  private errorHandlers: ((message: ErrorMessage) => void)[] = []
  private connectionStateHandlers: ((connected: boolean) => void)[] = []

  constructor(baseUrl: string = 'ws://localhost:8000') {
    this.url = `${baseUrl}/ws/code-generation`
  }

  /**
   * WebSocket接続を確立
   */
  async connect(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected to:', this.url)
          this.reconnectAttempts = 0
          this.notifyConnectionState(true)
          resolve(true)
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.notifyConnectionState(false)
          
          if (!this.isManuallyDisconnected) {
            this.attemptReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.notifyConnectionState(false)
          reject(new Error('Failed to connect to WebSocket'))
        }

        // 接続タイムアウト
        setTimeout(() => {
          if (this.ws?.readyState !== WebSocket.OPEN) {
            reject(new Error('Connection timeout'))
          }
        }, 5000)

      } catch (error) {
        reject(error)
      }
    })
  }

  /**
   * WebSocket切断
   */
  disconnect(): void {
    this.isManuallyDisconnected = true
    if (this.ws) {
      this.ws.close()
    }
    this.ws = null
    this.notifyConnectionState(false)
  }

  /**
   * 接続状態確認
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === 1
  }

  /**
   * コード生成リクエスト送信
   */
  async sendGenerationRequest(request: Omit<GenerationRequest, 'type'>): Promise<void> {
    if (!this.isConnected()) {
      throw new Error('WebSocket is not connected')
    }

    const message: GenerationRequest = {
      type: 'generate',
      ...request
    }

    this.ws!.send(JSON.stringify(message))
  }

  /**
   * 進捗更新コールバック登録
   */
  onProgress(handler: (message: ProgressMessage) => void): void {
    this.progressHandlers.push(handler)
  }

  /**
   * 生成完了コールバック登録
   */
  onCompletion(handler: (message: CompletionMessage) => void): void {
    this.completionHandlers.push(handler)
  }

  /**
   * エラーコールバック登録
   */
  onError(handler: (message: ErrorMessage) => void): void {
    this.errorHandlers.push(handler)
  }

  /**
   * 接続状態変更コールバック登録
   */
  onConnectionStateChange(handler: (connected: boolean) => void): void {
    this.connectionStateHandlers.push(handler)
  }

  /**
   * メッセージハンドリング
   */
  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'progress':
        this.progressHandlers.forEach(handler => handler(message))
        break
      
      case 'completion':
        this.completionHandlers.forEach(handler => handler(message))
        break
      
      case 'error':
        this.errorHandlers.forEach(handler => handler(message))
        break
      
      default:
        console.warn('Unknown message type:', message)
    }
  }

  /**
   * 接続状態変更通知
   */
  private notifyConnectionState(connected: boolean): void {
    this.connectionStateHandlers.forEach(handler => handler(connected))
  }

  /**
   * 自動再接続試行
   */
  private async attemptReconnect(): Promise<void> {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(async () => {
      try {
        await this.connect()
      } catch (error) {
        console.error('Reconnection failed:', error)
      }
    }, this.reconnectDelay * this.reconnectAttempts)
  }
}