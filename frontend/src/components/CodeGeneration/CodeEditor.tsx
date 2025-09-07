/**
 * Code Editor - Green段階（テストを通すための実装）
 * コードエディターコンポーネント
 */

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react'

export interface CodeEditorProps {
  value: string
  language: string
  onChange: (value: string) => void
  readOnly?: boolean
  showLineNumbers?: boolean
  theme?: 'light' | 'dark'
  className?: string
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  language,
  onChange,
  readOnly = false,
  showLineNumbers = true,
  theme = 'light',
  className = ''
}) => {
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>(theme)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // テーマ切り替え
  const toggleTheme = useCallback(() => {
    setCurrentTheme(prev => prev === 'light' ? 'dark' : 'light')
  }, [])

  // テキストエリアの高さ自動調整
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.max(textarea.scrollHeight, 200)}px`
    }
  }, [])

  // 値変更時の処理
  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value)
    adjustHeight()
  }, [onChange, adjustHeight])

  // キーボードショートカット処理
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget
    
    // Tab キーでインデント挿入
    if (e.key === 'Tab') {
      e.preventDefault()
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const newValue = value.substring(0, start) + '  ' + value.substring(end)
      onChange(newValue)
      
      // カーソル位置を調整
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 2
      }, 0)
    }
    
    // Ctrl+/ または Cmd+/ でコメントトグル
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
      e.preventDefault()
      const lines = value.split('\n')
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      
      // 選択範囲の行番号を取得
      const startLine = value.substring(0, start).split('\n').length - 1
      const endLine = value.substring(0, end).split('\n').length - 1
      
      // コメント文字列を言語に応じて決定
      const commentMap: Record<string, string> = {
        typescript: '//',
        javascript: '//',
        css: '/*',
        html: '<!--',
        json: '',
        python: '#',
      }
      
      const commentStr = commentMap[language] || '//'
      
      if (commentStr) {
        const newLines = lines.map((line, index) => {
          if (index >= startLine && index <= endLine) {
            if (line.trim().startsWith(commentStr)) {
              return line.replace(new RegExp(`^\\s*${commentStr.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s?`), '')
            } else {
              return `${commentStr} ${line}`
            }
          }
          return line
        })
        
        onChange(newLines.join('\n'))
      }
    }
  }, [value, onChange, language])

  // 行番号生成
  const lineNumbers = useMemo(() => {
    const lines = value.split('\n')
    return Array.from({ length: lines.length }, (_, i) => i + 1)
  }, [value])

  // 初期化時に高さ調整
  useEffect(() => {
    adjustHeight()
  }, [adjustHeight])

  // テーマスタイル
  const themeStyles = {
    light: {
      container: 'bg-white border-gray-300',
      textarea: 'bg-white text-gray-900',
      lineNumbers: 'bg-gray-50 text-gray-400 border-gray-300',
      syntax: 'text-gray-900'
    },
    dark: {
      container: 'bg-gray-900 border-gray-600',
      textarea: 'bg-gray-900 text-gray-100',
      lineNumbers: 'bg-gray-800 text-gray-500 border-gray-600',
      syntax: 'text-gray-100'
    }
  }

  const currentStyles = themeStyles[currentTheme]

  // 言語別のシンタックスハイライト用クラス
  const getSyntaxHighlightClass = useCallback((language: string): string => {
    const classMap: Record<string, string> = {
      typescript: 'language-typescript',
      javascript: 'language-javascript',
      css: 'language-css',
      html: 'language-html',
      json: 'language-json',
      python: 'language-python'
    }
    return classMap[language] || 'language-text'
  }, [])

  return (
    <div className={`code-editor ${getSyntaxHighlightClass(language)} theme-${currentTheme} ${className}`}>
      {/* ヘッダー */}
      <div className={`flex items-center justify-between p-3 border-b ${currentStyles.container}`}>
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-gray-700">
            {language.charAt(0).toUpperCase() + language.slice(1)} Editor
          </span>
          {readOnly && (
            <span className="px-2 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">
              読み取り専用
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* テーマ切り替えボタン */}
          <button
            onClick={toggleTheme}
            className="p-1.5 text-gray-500 hover:text-gray-700 rounded"
            title="テーマ切り替え"
          >
            {currentTheme === 'light' ? '🌙' : '☀️'}
          </button>
          
          {/* その他のツールバーボタン */}
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <span>{value.split('\n').length} 行</span>
            <span>•</span>
            <span>{value.length} 文字</span>
          </div>
        </div>
      </div>

      {/* エディター本体 */}
      <div className={`relative border rounded-b-lg overflow-hidden ${currentStyles.container}`}>
        <div className="flex">
          {/* 行番号 */}
          {showLineNumbers && (
            <div className={`flex-shrink-0 p-3 border-r select-none ${currentStyles.lineNumbers}`}>
              <div className="text-sm font-mono leading-6">
                {lineNumbers.map(num => (
                  <div key={num} className="text-right">
                    {num}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* テキストエリア */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              role="textbox"
              value={value}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              readOnly={readOnly}
              className={`w-full p-3 font-mono text-sm leading-6 resize-none border-0 focus:outline-none focus:ring-0 ${currentStyles.textarea}`}
              style={{ 
                minHeight: '200px',
                background: 'transparent',
                overflow: 'hidden'
              }}
              spellCheck={false}
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              data-gramm="false" // Grammarly無効化
              {...(readOnly && { readOnly: true })}
            />
            
            {/* シンタックスハイライトオーバーレイ（簡易版） */}
            <div 
              className="absolute inset-0 p-3 font-mono text-sm leading-6 pointer-events-none whitespace-pre-wrap break-words"
              style={{ 
                color: 'transparent',
                background: 'transparent',
                zIndex: -1
              }}
              aria-hidden="true"
            >
              {/* 実際の実装では、より高度なシンタックスハイライトライブラリを使用 */}
            </div>
          </div>
        </div>
      </div>

      {/* フッター */}
      <div className={`flex items-center justify-between px-3 py-2 text-xs border-t ${currentStyles.container}`}>
        <div className="flex items-center space-x-4 text-gray-500">
          <span>言語: {language}</span>
          <span>エンコーディング: UTF-8</span>
          <span>改行: LF</span>
        </div>
        
        <div className="flex items-center space-x-4 text-gray-500">
          {!readOnly && (
            <span>Ctrl+/ でコメント</span>
          )}
          <span>
            カーソル位置: {textareaRef.current?.selectionStart || 0}
          </span>
        </div>
      </div>
    </div>
  )
}

