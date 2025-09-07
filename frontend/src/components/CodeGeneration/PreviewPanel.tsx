/**
 * Preview Panel - Green段階（テストを通すための実装）
 * プレビューパネルコンポーネント
 */

import React, { useState, useCallback, useRef } from 'react'
import { LivePreviewEngine } from './LivePreviewEngine'

export interface GeneratedFile {
  filename: string
  content: string
  language: string
  description?: string
}

export interface PreviewPanelProps {
  file: GeneratedFile | null
  files?: GeneratedFile[]
  className?: string
}

type ViewMode = 'code' | 'preview' | 'live'

export const PreviewPanel: React.FC<PreviewPanelProps> = ({
  file,
  files = [],
  className = ''
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('code')
  const [copySuccess, setCopySuccess] = useState(false)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // ファイルコピー機能
  const handleCopy = useCallback(async () => {
    if (!file?.content) return

    try {
      await navigator.clipboard.writeText(file.content)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }, [file?.content])

  // コードのシンタックスハイライト
  const getHighlightedCode = useCallback((content: string, language: string) => {
    // 簡単なシンタックスハイライト実装
    // 実際の実装ではPrism.jsやhighlight.jsを使用することが多い
    const lines = content.split('\n')
    return lines.map((line, index) => (
      <div key={index} className="flex">
        <span className="text-gray-400 text-sm w-8 text-right pr-2 select-none">
          {index + 1}
        </span>
        <span className="flex-1">
          <code className={`language-${language}`}>{line || ' '}</code>
        </span>
      </div>
    ))
  }, [])

  // プレビュー用HTML生成
  const generatePreviewHtml = useCallback((file: GeneratedFile): string => {
    if (file.language === 'html' || file.filename.endsWith('.html')) {
      return file.content
    }

    if (file.language === 'css') {
      return `
        <!DOCTYPE html>
        <html>
          <head>
            <style>
              ${file.content}
            </style>
          </head>
          <body>
            <div class="preview-container">
              <h1>CSS Preview</h1>
              <p>This is a CSS preview.</p>
              <button>Sample Button</button>
              <div class="sample-div">Sample Div</div>
            </div>
          </body>
        </html>
      `
    }

    if (file.language === 'javascript' || file.language === 'typescript') {
      return `
        <!DOCTYPE html>
        <html>
          <head>
            <title>${file.filename}</title>
          </head>
          <body>
            <div id="root"></div>
            <script>
              ${file.content}
            </script>
          </body>
        </html>
      `
    }

    // その他のファイルタイプはテキストプレビュー
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${file.filename}</title>
          <style>
            body { font-family: monospace; padding: 20px; white-space: pre-wrap; }
          </style>
        </head>
        <body>${file.content}</body>
      </html>
    `
  }, [])

  // ファイルタイプアイコン取得
  const getFileTypeIcon = useCallback((filename: string, language: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase()
    
    const iconMap: Record<string, string> = {
      'ts': '🟦',
      'tsx': '⚛️',
      'js': '🟨',
      'jsx': '⚛️',
      'css': '🎨',
      'html': '🌐',
      'json': '📋',
      'md': '📝'
    }

    return iconMap[ext || ''] || '📄'
  }, [])

  // プレビュー可能かチェック
  const isPreviewable = useCallback((file: GeneratedFile): boolean => {
    return ['html', 'css', 'javascript', 'typescript'].includes(file.language) ||
           file.filename.endsWith('.html')
  }, [])

  // ライブプレビュー可能かチェック（React/TypeScriptコンポーネント）
  const isLivePreviewable = useCallback((file: GeneratedFile): boolean => {
    return file.language === 'typescript' && file.filename.endsWith('.tsx')
  }, [])

  if (!file) {
    return (
      <div className={`bg-white border border-gray-200 rounded-lg p-8 text-center ${className}`}>
        <div className="text-gray-400 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
        </div>
        <p className="text-gray-500">ファイルを選択してください</p>
        <p className="text-sm text-gray-400 mt-2">
          左側のファイルツリーからファイルを選択すると、こちらにプレビューが表示されます
        </p>
      </div>
    )
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg flex flex-col ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <span className="text-xl">{getFileTypeIcon(file.filename, file.language)}</span>
          <div>
            <h3 className="font-medium text-gray-900">{file.filename}</h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">
                {file.language}
              </span>
              <span>{new Blob([file.content]).size} bytes</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* ビューモード切り替え */}
          {(isPreviewable(file) || isLivePreviewable(file)) && (
            <div className="flex rounded-md overflow-hidden border border-gray-300">
              <button
                onClick={() => setViewMode('code')}
                className={`px-3 py-1 text-sm font-medium transition-colors ${
                  viewMode === 'code'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                コード
              </button>
              {isPreviewable(file) && (
                <button
                  onClick={() => setViewMode('preview')}
                  className={`px-3 py-1 text-sm font-medium transition-colors ${
                    viewMode === 'preview'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  プレビュー
                </button>
              )}
              {isLivePreviewable(file) && (
                <button
                  onClick={() => setViewMode('live')}
                  className={`px-3 py-1 text-sm font-medium transition-colors ${
                    viewMode === 'live'
                      ? 'bg-green-500 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  ライブ
                </button>
              )}
            </div>
          )}

          {/* コピーボタン */}
          <button
            onClick={handleCopy}
            className={`px-3 py-1.5 text-sm font-medium rounded-md border transition-colors ${
              copySuccess
                ? 'bg-green-50 text-green-700 border-green-200'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {copySuccess ? '✓ コピー済み' : 'コピー'}
          </button>
        </div>
      </div>

      {/* ファイル説明 */}
      {file.description && (
        <div className="px-4 py-2 bg-blue-50 border-b border-gray-200">
          <p className="text-sm text-blue-800">{file.description}</p>
        </div>
      )}

      {/* コンテンツエリア */}
      <div className="flex-1 overflow-auto">
        {viewMode === 'code' ? (
          /* コードビュー */
          <div className="p-4">
            <pre className="bg-gray-50 rounded-lg p-4 text-sm overflow-x-auto">
              <div role="code" className={`language-${file.language}`}>
                {getHighlightedCode(file.content, file.language)}
              </div>
            </pre>
          </div>
        ) : viewMode === 'live' ? (
          /* ライブプレビュービュー */
          <div className="p-4">
            <LivePreviewEngine
              files={files}
              selectedFile={file}
              onError={(error) => console.error('Live preview error:', error)}
              onCompileSuccess={() => console.log('Live preview compiled successfully')}
            />
          </div>
        ) : (
          /* 静的プレビュービュー */
          <div className="p-4">
            <div className="border border-gray-300 rounded-lg overflow-hidden">
              <div className="bg-gray-100 px-3 py-2 text-sm text-gray-600 border-b border-gray-300">
                プレビュー - {file.filename}
              </div>
              <iframe
                ref={iframeRef}
                title="preview"
                className="w-full h-96 border-0"
                srcDoc={generatePreviewHtml(file)}
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          </div>
        )}
      </div>

      {/* フッター統計 */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
        <div className="flex justify-between">
          <span>
            {file.content.split('\n').length} 行, {file.content.split(/\s+/).length} 単語
          </span>
          <span>
            最終更新: {new Date().toLocaleDateString('ja-JP')}
          </span>
        </div>
      </div>
    </div>
  )
}