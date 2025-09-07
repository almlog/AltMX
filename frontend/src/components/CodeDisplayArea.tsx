/**
 * AltMX - コード表示エリア（4つの表示モード切替）
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'
import ViewTabs from './ViewTabs'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  path: string
  children?: FileNode[]
}

interface CodeContent {
  currentCode: string
  fileTree: FileNode[]
  selectedFile: string
  previewUrl: string
}

interface CodeDisplayAreaProps {
  currentView: 'code' | 'tree' | 'file' | 'preview'
  codeContent: CodeContent
  onViewChange: (view: 'code' | 'tree' | 'file' | 'preview') => void
}

const CodeDisplayArea: FC<CodeDisplayAreaProps> = ({
  currentView,
  codeContent,
  onViewChange
}) => {
  const renderCodeView = () => (
    <div className="code-view">
      <div className="code-editor">
        <div className="editor-header">
          <span className="editor-title">リアルタイムコード生成</span>
          <div className="editor-controls">
            <button className="control-btn">Copy</button>
            <button className="control-btn">Format</button>
          </div>
        </div>
        <div className="editor-content">
          <pre className="code-block">
            <code>{codeContent.currentCode}</code>
          </pre>
        </div>
      </div>
    </div>
  )

  const renderTreeView = () => (
    <div className="tree-view">
      <div className="tree-header">
        <span className="tree-title">プロジェクト構造</span>
        <div className="tree-controls">
          <button className="control-btn">Expand All</button>
          <button className="control-btn">Collapse</button>
        </div>
      </div>
      <div className="tree-content">
        {renderFileTree(codeContent.fileTree)}
      </div>
    </div>
  )

  const renderFileTree = (nodes: FileNode[], level = 0) => (
    <ul className="file-tree" style={{ paddingLeft: `${level * 20}px` }}>
      {nodes.map((node, index) => (
        <li key={index} className={`tree-node ${node.type}`}>
          <div className="node-content">
            <span className={`node-icon ${node.type}`}>
              {node.type === 'folder' ? '📁' : '📄'}
            </span>
            <span className="node-name">{node.name}</span>
          </div>
          {node.children && renderFileTree(node.children, level + 1)}
        </li>
      ))}
    </ul>
  )

  const renderFileView = () => (
    <div className="file-view">
      <div className="file-header">
        <span className="file-title">個別ファイル詳細</span>
        <span className="file-path">{codeContent.selectedFile}</span>
      </div>
      <div className="file-content">
        <div className="file-editor">
          <div className="line-numbers">
            {codeContent.currentCode.split('\n').map((_, index) => (
              <span key={index} className="line-number">
                {index + 1}
              </span>
            ))}
          </div>
          <div className="file-code">
            <pre>
              <code>{codeContent.currentCode}</code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  )

  const renderPreviewView = () => (
    <div className="preview-view">
      <div className="preview-header">
        <span className="preview-title">実行結果プレビュー</span>
        <div className="preview-controls">
          <button className="control-btn">Refresh</button>
          <button className="control-btn">Full Screen</button>
        </div>
      </div>
      <div className="preview-content">
        {codeContent.previewUrl ? (
          <iframe 
            src={codeContent.previewUrl}
            className="preview-frame"
            title="Preview"
          />
        ) : (
          <div className="preview-placeholder">
            <div className="placeholder-icon">🚀</div>
            <div className="placeholder-text">
              <h3>プレビュー準備中</h3>
              <p>コード生成後にプレビューが表示されます</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  const renderCurrentView = () => {
    switch (currentView) {
      case 'code': return renderCodeView()
      case 'tree': return renderTreeView()
      case 'file': return renderFileView()
      case 'preview': return renderPreviewView()
      default: return renderCodeView()
    }
  }

  return (
    <div className="code-display-area neon-panel">
      {/* タブ切り替え */}
      <ViewTabs 
        currentView={currentView}
        onViewChange={onViewChange}
      />

      {/* コンテンツエリア */}
      <div className="display-content">
        {renderCurrentView()}
      </div>
    </div>
  )
}

export default CodeDisplayArea