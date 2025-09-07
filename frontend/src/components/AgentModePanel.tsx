/**
 * AI Agent Mode Panel - トグルスイッチUI
 * エージェントのモードをトグルスイッチで安全に切り替え
 */

import React, { useState, useEffect } from 'react'
import '../styles/agent-mode-panel.css'

// Agent Mode Types
export interface AgentModeConfig {
  mode: string
  quality_level: string
  personality: string
  focus_areas: string[]
  session_goals: string[]
  audience: string
  time_limit?: number
}

export interface CurrentModeResponse {
  mode?: string
  quality_level?: string
  personality?: string
  focus_areas?: string[]
  session_goals?: string[]
  audience?: string
  time_limit?: number
}

export interface ModeDeclarationResponse {
  success: boolean
  message: string
  current_mode: string
  system_prompt: string
  configuration: AgentModeConfig
}

interface AgentModeDefinition {
  key: string
  name: string
  icon: string
  description: string
  tooltip: string
  defaultQuality: string
  defaultPersonality: string
  color: string
}

const AGENT_MODES: AgentModeDefinition[] = [
  {
    key: 'chat',
    name: 'Chat',
    icon: '💬',
    description: '通常の会話モード',
    tooltip: '一般的な質問や会話に適したモード。カジュアルで親しみやすい応答スタイルで、日常的なやり取りや情報収集に最適です。',
    defaultQuality: 'development',
    defaultPersonality: 'friendly',
    color: '#64B5F6'
  },
  {
    key: 'coding',
    name: 'Coding',
    icon: '💻',
    description: '本格的な開発支援',
    tooltip: 'プログラミングタスクに特化したモード。コード作成、バグ修正、ライブラリ使用方法の説明など、開発作業全般をサポートします。',
    defaultQuality: 'development',
    defaultPersonality: 'professional',
    color: '#4CAF50'
  },
  {
    key: 'live_coding',
    name: 'Live',
    icon: '🎥',
    description: '配信向け解説付き開発',
    tooltip: 'ライブコーディングやペアプログラミング向けモード。実装手順を詳しく説明しながら、視聴者にも分かりやすい形でコードを書きます。',
    defaultQuality: 'production',
    defaultPersonality: 'mentor',
    color: '#FF6B6B'
  },
  {
    key: 'production',
    name: 'Production',
    icon: '🏭',
    description: '企業レベル品質',
    tooltip: '本番環境に投入するコードの作成モード。セキュリティ、パフォーマンス、保守性を重視し、エンタープライズグレードの品質を実現します。',
    defaultQuality: 'production',
    defaultPersonality: 'expert',
    color: '#9C27B0'
  },
  {
    key: 'code_review',
    name: 'Review',
    icon: '🔍',
    description: 'コード品質チェック',
    tooltip: 'コードレビューに特化したモード。バグ、セキュリティリスク、パフォーマンス問題、コーディングスタンダードの違反などを詳細に分析します。',
    defaultQuality: 'staging',
    defaultPersonality: 'expert',
    color: '#FF9800'
  },
  {
    key: 'debug',
    name: 'Debug',
    icon: '🐛',
    description: '問題解決に特化',
    tooltip: 'バグ修正とトラブルシューティング専用モード。エラーの原因分析、デバッグ手法の提案、修正コードの作成を効率的に行います。',
    defaultQuality: 'development',
    defaultPersonality: 'expert',
    color: '#F44336'
  },
  {
    key: 'teaching',
    name: 'Teaching',
    icon: '👨‍🏫',
    description: '初心者向け丁寧指導',
    tooltip: 'プログラミング学習者向けの教育モード。基礎概念から丁寧に説明し、段階的な学習をサポート。質問しやすい環境を提供します。',
    defaultQuality: 'development',
    defaultPersonality: 'mentor',
    color: '#00BCD4'
  },
  {
    key: 'architecture',
    name: 'Architecture',
    icon: '🏗️',
    description: 'システム設計',
    tooltip: 'システムアーキテクチャ設計専用モード。スケーラビリティ、可用性、セキュリティを考慮した大規模システムの設計と技術選定を支援します。',
    defaultQuality: 'production',
    defaultPersonality: 'expert',
    color: '#607D8B'
  }
]

interface AgentModePanelProps {
  onModeChange?: (mode: string) => void
}

export const AgentModePanel: React.FC<AgentModePanelProps> = ({ onModeChange }) => {
  const [currentMode, setCurrentMode] = useState<string>('chat')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [lastMessage, setLastMessage] = useState<string>('')
  const [isExpanded, setIsExpanded] = useState<boolean>(false)

  // 現在のモード状態を取得
  const fetchCurrentMode = async () => {
    try {
      const response = await fetch('/api/agent/current-mode')
      if (response.ok) {
        const data: CurrentModeResponse = await response.json()
        if (data.mode) {
          setCurrentMode(data.mode)
        }
      }
    } catch (error) {
      console.error('Failed to fetch current mode:', error)
    }
  }

  // モード変更APIコール
  const declareMode = async (modeKey: string) => {
    const mode = AGENT_MODES.find(m => m.key === modeKey)
    if (!mode) return

    setIsLoading(true)
    
    try {
      const requestBody = {
        mode: mode.key,
        quality_level: mode.defaultQuality,
        personality: mode.defaultPersonality,
        focus_areas: [],
        constraints: [],
        session_goals: [],
        audience: 'general'
      }

      const response = await fetch('/api/agent/declare-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (response.ok) {
        const data: ModeDeclarationResponse = await response.json()
        if (data.success) {
          setCurrentMode(data.current_mode)
          setLastMessage(data.message)
          onModeChange?.(data.current_mode)
          
          // 成功メッセージを3秒後にクリア
          setTimeout(() => setLastMessage(''), 3000)
        }
      } else {
        setLastMessage('モード変更に失敗しました')
      }
    } catch (error) {
      console.error('Mode declaration failed:', error)
      setLastMessage('通信エラーが発生しました')
    } finally {
      setIsLoading(false)
    }
  }

  // 初期化時に現在のモードを取得
  useEffect(() => {
    fetchCurrentMode()
  }, [])

  const getCurrentModeInfo = () => {
    return AGENT_MODES.find(mode => mode.key === currentMode) || AGENT_MODES[0]
  }

  const currentModeInfo = getCurrentModeInfo()

  return (
    <div className={`agent-mode-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* ヘッダー部分 - 常に表示 */}
      <div 
        className="mode-header"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ borderColor: currentModeInfo.color }}
      >
        <div className="current-mode-display">
          <span className="mode-icon">{currentModeInfo.icon}</span>
          <span className="mode-name">{currentModeInfo.name}</span>
          <span className="mode-status">Active</span>
        </div>
        <div className="toggle-arrow">
          {isExpanded ? '▼' : '▶'}
        </div>
      </div>

      {/* 展開時のモード選択エリア */}
      {isExpanded && (
        <div className="mode-selection-area">
          <div className="mode-title">AI Agent Mode Settings</div>
          
          {/* メッセージ表示 */}
          {lastMessage && (
            <div className="mode-message">
              {lastMessage}
            </div>
          )}

          {/* モードトグルスイッチ群 */}
          <div className="mode-toggles">
            {AGENT_MODES.map((mode) => (
              <div key={mode.key} className="mode-toggle-row" title={mode.tooltip}>
                <div className="mode-info">
                  <span className="mode-icon">{mode.icon}</span>
                  <div className="mode-details">
                    <span className="mode-label">{mode.name}</span>
                    <span className="mode-desc">{mode.description}</span>
                  </div>
                </div>
                
                <div className="toggle-switch-container">
                  <label className="toggle-switch">
                    <input
                      type="radio"
                      name="agent-mode"
                      value={mode.key}
                      checked={currentMode === mode.key}
                      onChange={() => !isLoading && declareMode(mode.key)}
                      disabled={isLoading}
                    />
                    <span 
                      className="toggle-slider"
                      style={{ 
                        '--active-color': mode.color,
                        backgroundColor: currentMode === mode.key ? mode.color : '#ddd'
                      } as React.CSSProperties}
                    >
                      <span className="toggle-handle"></span>
                    </span>
                  </label>
                </div>
              </div>
            ))}
          </div>

          {/* ローディング表示 */}
          {isLoading && (
            <div className="mode-loading">
              <span>モード変更中...</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AgentModePanel