/**
 * useCodeGeneration Hook - Green段階（テストを通すための実装）
 * WebSocketを使ったリアルタイムコード生成フック
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { 
  CodeGenerationWebSocket, 
  ProgressMessage, 
  CompletionMessage, 
  ErrorMessage 
} from '../services/codeGenerationWebSocket'

export interface GeneratedFile {
  filename: string
  content: string
  language: string
  description?: string
}

export interface ProgressState {
  stage: 'idle' | 'parsing' | 'generating' | 'validating' | 'organizing'
  progress: number // 0.0 - 1.0
  message: string
}

export interface GenerationRequestParams {
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

export interface CodeGenerationState {
  // Connection state
  isConnected: boolean
  isConnecting: boolean
  
  // Generation state
  isGenerating: boolean
  progress: ProgressState
  generatedFiles: GeneratedFile[]
  
  // Error state
  error: ErrorMessage | null
  
  // Actions
  connect: () => Promise<boolean>
  disconnect: () => void
  generateCode: (request: GenerationRequestParams) => Promise<void>
  clearError: () => void
  clearFiles: () => void
}

export function useCodeGeneration(): CodeGenerationState {
  // Connection state
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  
  // Generation state
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState<ProgressState>({
    stage: 'idle',
    progress: 0,
    message: ''
  })
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>([])
  
  // Error state
  const [error, setError] = useState<ErrorMessage | null>(null)
  
  // WebSocket instance
  const websocketRef = useRef<CodeGenerationWebSocket | null>(null)

  // Initialize WebSocket
  useEffect(() => {
    websocketRef.current = new CodeGenerationWebSocket()
    
    // Set up event handlers
    websocketRef.current.onConnectionStateChange((connected) => {
      setIsConnected(connected)
      if (!connected) {
        setIsConnecting(false)
        setIsGenerating(false)
      }
    })

    websocketRef.current.onProgress((message: ProgressMessage) => {
      setProgress({
        stage: message.stage,
        progress: message.progress,
        message: message.message
      })
      setIsGenerating(true)
    })

    websocketRef.current.onCompletion((message: CompletionMessage) => {
      if (message.success) {
        setGeneratedFiles(message.files)
        setProgress({
          stage: 'idle',
          progress: 1,
          message: '生成が完了しました'
        })
      } else {
        setError({
          type: 'error',
          error: 'GENERATION_FAILED',
          message: '生成に失敗しました'
        })
      }
      setIsGenerating(false)
    })

    websocketRef.current.onError((message: ErrorMessage) => {
      setError(message)
      setIsGenerating(false)
      setProgress({
        stage: 'idle',
        progress: 0,
        message: ''
      })
    })

    // Cleanup on unmount
    return () => {
      if (websocketRef.current) {
        websocketRef.current.disconnect()
        websocketRef.current = null
      }
    }
  }, [])

  // Connection functions
  const connect = useCallback(async (): Promise<boolean> => {
    if (!websocketRef.current || isConnected || isConnecting) {
      return false
    }

    setIsConnecting(true)
    setError(null)

    try {
      const success = await websocketRef.current.connect()
      setIsConnecting(false)
      return success
    } catch (error) {
      setIsConnecting(false)
      setError({
        type: 'error',
        error: 'CONNECTION_FAILED',
        message: '接続に失敗しました: ' + (error as Error).message
      })
      return false
    }
  }, [isConnected, isConnecting])

  const disconnect = useCallback((): void => {
    if (websocketRef.current) {
      websocketRef.current.disconnect()
    }
    setIsGenerating(false)
    setProgress({
      stage: 'idle',
      progress: 0,
      message: ''
    })
  }, [])

  // Generation function
  const generateCode = useCallback(async (request: GenerationRequestParams): Promise<void> => {
    if (!websocketRef.current || !isConnected || isGenerating) {
      throw new Error('Cannot generate code: WebSocket not connected or already generating')
    }

    setError(null)
    setGeneratedFiles([])
    setIsGenerating(true)
    setProgress({
      stage: 'parsing',
      progress: 0,
      message: 'リクエストを処理しています...'
    })

    try {
      await websocketRef.current.sendGenerationRequest(request)
    } catch (error) {
      setIsGenerating(false)
      setProgress({
        stage: 'idle',
        progress: 0,
        message: ''
      })
      throw error
    }
  }, [isConnected, isGenerating])

  // Utility functions
  const clearError = useCallback((): void => {
    setError(null)
  }, [])

  const clearFiles = useCallback((): void => {
    setGeneratedFiles([])
    setProgress({
      stage: 'idle',
      progress: 0,
      message: ''
    })
  }, [])

  return {
    // State
    isConnected,
    isConnecting,
    isGenerating,
    progress,
    generatedFiles,
    error,
    
    // Actions
    connect,
    disconnect,
    generateCode,
    clearError,
    clearFiles
  }
}