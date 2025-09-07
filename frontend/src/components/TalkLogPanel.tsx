/**
 * AltMX - トークログ表示パネル
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'
import { useRef, useEffect, useState } from 'react'

interface TalkLogPanelProps {
  talkLog: Array<{
    type: 'user' | 'ai'
    message: string
    timestamp: Date
  }>
  onSendMessage: (message: string) => void
}

const TalkLogPanel: FC<TalkLogPanelProps> = ({ talkLog, onSendMessage }) => {
  const logEndRef = useRef<HTMLDivElement>(null)
  const [inputMessage, setInputMessage] = useState('')

  // 新しいメッセージが追加されたら自動スクロール
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [talkLog])

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('ja-JP', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="talk-log-panel neon-panel">
      <h3 className="panel-title">TALK LOG</h3>
      
      <div className="log-container">
        {talkLog.length === 0 ? (
          <div className="log-empty">
            <span>ログなし</span>
          </div>
        ) : (
          talkLog.map((log, index) => (
            <div 
              key={index} 
              className={`log-entry ${log.type === 'ai' ? 'ai-message' : 'user-message'}`}
            >
              <div className="log-header">
                <span className="log-sender">
                  {log.type === 'ai' ? 'AltMX' : 'USER'}
                </span>
                <span className="log-time">
                  {formatTime(log.timestamp)}
                </span>
              </div>
              <div className="log-message">
                {log.message}
              </div>
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>

      {/* スクロールインジケーター */}
      <div className="scroll-indicator">
        <div className="scroll-track">
          <div className="scroll-thumb"></div>
        </div>
      </div>

      {/* チャット入力 */}
      <div className="chat-input-container">
        <div className="input-wrapper">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && inputMessage.trim()) {
                onSendMessage(inputMessage.trim())
                setInputMessage('')
              }
            }}
            placeholder="Message to AltMX..."
            className="chat-input"
          />
          <button
            onClick={() => {
              if (inputMessage.trim()) {
                onSendMessage(inputMessage.trim())
                setInputMessage('')
              }
            }}
            className="send-button"
            disabled={!inputMessage.trim()}
          >
            <span className="send-icon">⚡</span>
          </button>
        </div>
        <div className="input-glow"></div>
      </div>
    </div>
  )
}

export default TalkLogPanel