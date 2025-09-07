/**
 * AltMX - メイン画面（ヴェイパーウェイブUI）
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import { useState, useEffect } from 'react'
import type { FC } from 'react'
import SidePanel from './SidePanel'
import CodeDisplayArea from './CodeDisplayArea'
import ActionButtons from './ActionButtons'
import ProgressBar from './ProgressBar'
import { CodeGenerationForm } from './CodeGeneration/RequestForm'
import { PreviewPanel } from './CodeGeneration/PreviewPanel'
import AgentModePanel from './AgentModePanel'
import type { GeneratedFile, GenerationRequest } from './CodeGeneration/RequestForm'
import { generateCode } from '../services/codeGenerationApi'

// Chat API types
interface ChatRequest {
  message: string
  use_sapporo_dialect: boolean
}

interface ChatResponse {
  response: string
  dialect_applied: boolean
  thinking_time_ms: number
  mood: string
  car_status: string
}

export interface VaporwaveMainScreenState {
  currentView: 'code' | 'tree' | 'file' | 'preview'
  currentTab: 'chat' | 'code-gen'
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
  isGenerating: boolean
  generatedFiles: GeneratedFile[]
  selectedGeneratedFile: GeneratedFile | null
  generationError: string | null
  currentAgentMode: string
}

interface FileNode {
  name: string
  type: 'file' | 'folder'
  path: string
  children?: FileNode[]
}

const VaporwaveMainScreen: FC = () => {
  const [state, setState] = useState<VaporwaveMainScreenState>({
    currentView: 'code',
    currentTab: 'chat',
    altmxStatus: {
      recognition: 'online',
      generation: 'turbo',
      quality: 'maximum',
      speed: 245
    },
    talkLog: [
      {
        type: 'ai',
        message: 'システム起動完了。なんまら準備万端だっしょ！',
        timestamp: new Date()
      }
    ],
    codeContent: {
      currentCode: '// AltMX Code Generation Area\n// Your code will appear here...',
      fileTree: [
        {
          name: 'src',
          type: 'folder',
          path: '/src',
          children: [
            { name: 'App.tsx', type: 'file', path: '/src/App.tsx' },
            { name: 'main.tsx', type: 'file', path: '/src/main.tsx' }
          ]
        }
      ],
      selectedFile: '/src/App.tsx',
      previewUrl: ''
    },
    progress: {
      current: 0,
      message: 'Ready',
      isActive: false
    },
    isTurboMode: false,
    isGenerating: false,
    generatedFiles: [],
    selectedGeneratedFile: null,
    generationError: null,
    currentAgentMode: 'chat'
  })

  // Chat API integration
  const sendChatMessage = async (message: string) => {
    // Add user message to talk log
    setState(prev => ({
      ...prev,
      talkLog: [...prev.talkLog, {
        type: 'user',
        message,
        timestamp: new Date()
      }]
    }))

    console.log('Sending message to API:', message)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          use_sapporo_dialect: true
        } as ChatRequest),
      })

      console.log('Response status:', response.status)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const chatResponse: ChatResponse = await response.json()
      console.log('Chat response:', chatResponse)
      
      // Add AI response to talk log
      setState(prev => ({
        ...prev,
        talkLog: [...prev.talkLog, {
          type: 'ai',
          message: chatResponse.response,
          timestamp: new Date()
        }],
        altmxStatus: {
          ...prev.altmxStatus,
          speed: Math.round(1000 / chatResponse.thinking_time_ms * 1000) // Convert to rough tokens/second
        }
      }))

    } catch (error) {
      console.error('Chat API error:', error)
      console.error('Error details:', error.message)
      // Add error message to talk log
      setState(prev => ({
        ...prev,
        talkLog: [...prev.talkLog, {
          type: 'ai',
          message: `接続エラー: ${error.message}`,
          timestamp: new Date()
        }]
      }))
    }
  }

  // プログレスバー更新のシミュレーション
  useEffect(() => {
    if (state.progress.isActive) {
      const interval = setInterval(() => {
        setState(prev => ({
          ...prev,
          progress: {
            ...prev.progress,
            current: Math.min(prev.progress.current + Math.random() * 10, 100)
          }
        }))
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [state.progress.isActive])

  const handleViewChange = (view: VaporwaveMainScreenState['currentView']) => {
    setState(prev => ({ ...prev, currentView: view }))
  }

  const handleTabChange = (tab: VaporwaveMainScreenState['currentTab']) => {
    setState(prev => ({ ...prev, currentTab: tab }))
  }

  const handleGenerateCode = async (request: GenerationRequest) => {
    setState(prev => ({ ...prev, isGenerating: true, generationError: null }))
    
    try {
      const response = await generateCode(request)
      
      if (response.success && response.generated_files.length > 0) {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          generatedFiles: response.generated_files,
          selectedGeneratedFile: response.generated_files[0]
        }))
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        generationError: error instanceof Error ? error.message : '生成に失敗しました'
      }))
    }
  }

  const handleCancelGeneration = () => {
    setState(prev => ({ ...prev, isGenerating: false }))
  }

  const handleAction = (action: 'generate' | 'debug' | 'deploy' | 'save') => {
    setState(prev => ({
      ...prev,
      progress: {
        current: 0,
        message: `${action.toUpperCase()} 実行中...`,
        isActive: true
      }
    }))

    // 5秒後に完了
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        progress: {
          current: 100,
          message: 'Complete!',
          isActive: false
        }
      }))
    }, 5000)
  }

  const toggleTurboMode = () => {
    setState(prev => ({ ...prev, isTurboMode: !prev.isTurboMode }))
  }

  const handleAgentModeChange = (mode: string) => {
    setState(prev => ({ ...prev, currentAgentMode: mode }))
    console.log('Agent mode changed to:', mode)
  }

  return (
    <div className="vaporwave-main-screen">
      <div className="main-layout">
        {/* 左パネル: AltMXステータス、トークログ */}
        <SidePanel 
          altmxStatus={state.altmxStatus}
          talkLog={state.talkLog}
          isTurboMode={state.isTurboMode}
          onTurboToggle={toggleTurboMode}
          onSendMessage={sendChatMessage}
        />

        {/* エージェントモードパネル */}
        <AgentModePanel onModeChange={handleAgentModeChange} />

        {/* メインエリア: コード表示 */}
        <div className="main-area">
          {/* タブメニュー */}
          <div className="tab-menu" style={{ marginBottom: '20px' }}>
            <button
              onClick={() => handleTabChange('chat')}
              className={state.currentTab === 'chat' ? 'tab-active' : ''}
              style={{ marginRight: '10px', padding: '10px 20px' }}
            >
              チャット
            </button>
            <button
              onClick={() => handleTabChange('code-gen')}
              className={state.currentTab === 'code-gen' ? 'tab-active' : ''}
              style={{ padding: '10px 20px' }}
            >
              コード生成
            </button>
          </div>

          {/* タブコンテンツ */}
          {state.currentTab === 'chat' ? (
            <>
              <CodeDisplayArea
                currentView={state.currentView}
                codeContent={state.codeContent}
                onViewChange={handleViewChange}
              />
              {/* 下部: アクションボタン */}
              <ActionButtons onAction={handleAction} />
            </>
          ) : (
            <div className="code-gen-area">
              {state.generatedFiles.length === 0 ? (
                <CodeGenerationForm
                  onSubmit={handleGenerateCode}
                  onCancel={handleCancelGeneration}
                  isGenerating={state.isGenerating}
                  error={state.generationError || undefined}
                />
              ) : (
                <PreviewPanel
                  file={state.selectedGeneratedFile}
                  files={state.generatedFiles}
                />
              )}
            </div>
          )}
          
          {/* プログレスバー */}
          {(state.progress.isActive || state.isGenerating) && (
            <ProgressBar 
              progress={state.isGenerating ? 50 : state.progress.current}
              message={state.isGenerating ? '生成中...' : state.progress.message}
            />
          )}
        </div>
      </div>

      {/* 背景エフェクト */}
      <div className="vaporwave-background">
        <div className="neon-grid"></div>
        <div className="scanlines"></div>
        <div className="particles"></div>
      </div>
    </div>
  )
}

export default VaporwaveMainScreen