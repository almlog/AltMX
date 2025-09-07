/**
 * OpeningScreen Component
 * TDD Phase: GREEN - テストを通すための最小限の実装
 * 
 * オープニング画面（システム起動）
 * - プレゼンターログイン
 * - セッションコード入力
 * - システム起動アニメーション
 * - ブートシーケンス表示
 * 
 * Router統合版: useRouteContextでナビゲーション管理
 */

import React, { useState, useEffect, useCallback } from 'react'
import { useRouteContext } from '../../contexts/RouteContext'
import './OpeningScreen.css'

export interface OpeningScreenProps {
  onStart?: (data: { presenter: string; session: string }) => void;
  showBootSequence?: boolean;
}

interface OpeningScreenState {
  presenterName: string;
  sessionCode: string;
  isLoading: boolean;
  loadingProgress: number;
  loadingMessage: string;
  showBootSequence: boolean;
  bootSequenceExpanded: boolean;
  systemReady: boolean;
  hasError: boolean;
}

const OpeningScreen: React.FC<OpeningScreenProps> = ({ 
  onStart,
  showBootSequence = false
}) => {
  // ルーターコンテキストを取得
  const { navigate, startSession } = useRouteContext()

  const [state, setState] = useState<OpeningScreenState>({
    presenterName: '',
    sessionCode: '',
    isLoading: false,
    loadingProgress: 0,
    loadingMessage: 'システム起動中...',
    showBootSequence: false,
    bootSequenceExpanded: false,
    systemReady: true,
    hasError: false
  })

  // ブートシーケンス表示
  useEffect(() => {
    if (showBootSequence) {
      setTimeout(() => {
        setState(prev => ({ ...prev, showBootSequence: true }))
      }, 500)
    }
  }, [showBootSequence])

  // キーボードイベント処理
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !state.isLoading) {
        handleStart()
      }
    }

    document.addEventListener('keypress', handleKeyPress)
    return () => document.removeEventListener('keypress', handleKeyPress)
  }, [state.presenterName, state.sessionCode, state.isLoading])

  const handleInputChange = useCallback(<T extends keyof OpeningScreenState>(
    field: T,
    value: OpeningScreenState[T]
  ) => {
    setState(prev => ({ ...prev, [field]: value, hasError: false }))
  }, [])

  const toggleBootSequence = useCallback(() => {
    setState(prev => ({ ...prev, bootSequenceExpanded: !prev.bootSequenceExpanded }))
  }, [])

  const handleStart = useCallback(() => {
    // バリデーション
    if (!state.presenterName.trim()) {
      setState(prev => ({ ...prev, hasError: true }))
      return
    }

    // ローディング開始
    setState(prev => ({ 
      ...prev, 
      isLoading: true,
      loadingProgress: 0,
      loadingMessage: 'システム起動中...'
    }))

    // ローディングアニメーション
    const loadingMessages = [
      'システム起動中...',
      'AIエンジン初期化中...',
      'なんまら準備してるっしょ...',
      'WebSocket接続中...',
      'ユーザーインターフェース構築中...',
      'もうちょっとで完了するわ...',
      '起動完了！'
    ]

    let progress = 0
    let messageIndex = 0

    const loadingInterval = setInterval(() => {
      progress += Math.random() * 20
      if (progress > 100) progress = 100

      setState(prev => ({ 
        ...prev, 
        loadingProgress: progress,
        loadingMessage: loadingMessages[Math.min(messageIndex, loadingMessages.length - 1)]
      }))

      if (messageIndex < loadingMessages.length - 1) {
        messageIndex++
      }

      if (progress >= 100) {
        clearInterval(loadingInterval)
        setTimeout(() => {
          // セッション開始
          startSession(state.presenterName, state.sessionCode || 'default')
          
          // 従来のコールバック（後方互換性のため）
          onStart?.({
            presenter: state.presenterName,
            session: state.sessionCode || 'default'
          })
          
          // メイン画面にナビゲーション
          navigate('main')
        }, 1000)
      }
    }, 500)
  }, [state.presenterName, state.sessionCode, onStart, navigate, startSession])

  return (
    <div className="opening-screen" data-testid="opening-container">
      {/* 背景エフェクト */}
      <div className="bg-container bg-gradient-animation" data-testid="bg-container"></div>
      <div className="grid-overlay" data-testid="grid-overlay"></div>
      <div className="scanlines" data-testid="scanlines"></div>

      {/* ブートシーケンス - 折り畳みパネル */}
      {state.showBootSequence && (
        <div className="boot-sequence active">
          <div className="boot-toggle" onClick={toggleBootSequence}>
            <span className={`boot-toggle-icon ${state.bootSequenceExpanded ? 'expanded' : ''}`}>▶</span>
            <span>System Status</span>
          </div>
          <div className={`boot-content ${state.bootSequenceExpanded ? 'expanded' : ''}`}>
            <div className="boot-line">ALTMX SYSTEM v2.0.1</div>
            <div className="boot-line">Copyright (c) 2024 Your Company DX Team</div>
            <div className="boot-line">-----------------------------------------</div>
            <div className="boot-line">Initializing AI Core... [OK]</div>
            <div className="boot-line">Loading Neural Networks... [OK]</div>
            <div className="boot-line">Connecting to Claude API... [OK]</div>
            <div className="boot-line">WebSocket Server... [OK]</div>
            <div className="boot-line">Voice Recognition... [OK]</div>
            <div className="boot-line">-----------------------------------------</div>
            <div className="boot-line">System Ready.</div>
          </div>
        </div>
      )}

      {/* メインコンテンツ */}
      <div className="boot-container fade-in">
        <div className="main-content">
          <div className="logo-container">
            <div className="logo-version">v2.0</div>
            <div className="logo-main logo-pulse">AltMX</div>
            <div className="logo-sub">AI Collaboration System</div>
          </div>

          <div className="login-form">
            <div className="input-group">
              <label className="input-label" htmlFor="presenterName">Presenter ID</label>
              <input
                type="text"
                className={`input-field ${state.hasError ? 'error' : ''}`}
                placeholder="あなたの名前を入力"
                id="presenterName"
                value={state.presenterName}
                onChange={(e) => handleInputChange('presenterName', e.target.value)}
                disabled={state.isLoading}
              />
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="sessionCode">Session Code</label>
              <input
                type="text"
                className="input-field"
                placeholder="セッションコード（オプション）"
                id="sessionCode"
                value={state.sessionCode}
                onChange={(e) => handleInputChange('sessionCode', e.target.value)}
                disabled={state.isLoading}
              />
            </div>

            <button 
              className="start-button" 
              onClick={handleStart}
              disabled={state.isLoading}
            >
              🚀 START SYSTEM
            </button>
          </div>

          <div className="status-container">
            <div className="status-item">
              <span className="status-dot online" data-testid="status-indicator"></span>
              <span style={{ color: '#00ff41' }}>AI: Online</span>
            </div>
            <div className="status-item">
              <span className="status-dot online" data-testid="status-indicator"></span>
              <span style={{ color: '#00ff41' }}>Server: Ready</span>
            </div>
            <div className="status-item">
              <span className="status-dot connecting" data-testid="status-indicator"></span>
              <span style={{ color: '#ffb000' }}>Users: 0</span>
            </div>
          </div>
        </div>
      </div>

      {/* ローディング画面 */}
      {state.isLoading && (
        <div className="loading-screen active">
          <div className="loading-logo">AltMX</div>
          <div className="loading-bar">
            <div 
              className="loading-progress" 
              style={{ width: `${state.loadingProgress}%` }}
              data-testid="loading-progress"
            ></div>
          </div>
          <div className="loading-text">{state.loadingMessage}</div>
        </div>
      )}
    </div>
  )
}

export default OpeningScreen