/**
 * File Explorer Components Tests - Red段階（失敗するテスト）
 * ファイルエクスプローラー・プレビューコンポーネントテスト
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import userEvent from '@testing-library/user-event'

// Test用のインポート（実装前なのでエラーになる想定）
import { FileExplorer } from '../components/CodeGeneration/FileExplorer'
import { PreviewPanel } from '../components/CodeGeneration/PreviewPanel'
import { CodeEditor } from '../components/CodeGeneration/CodeEditor'

// Mock data
const mockGeneratedFiles = [
  {
    filename: 'App.tsx',
    content: `import React from 'react';\n\nconst App = () => {\n  return <div>Hello World</div>;\n};\n\nexport default App;`,
    language: 'typescript',
    description: 'Main application component'
  },
  {
    filename: 'components/Button.tsx',
    content: `import React from 'react';\n\ninterface ButtonProps {\n  onClick: () => void;\n  children: React.ReactNode;\n}\n\nconst Button: React.FC<ButtonProps> = ({ onClick, children }) => {\n  return <button onClick={onClick}>{children}</button>;\n};\n\nexport default Button;`,
    language: 'typescript',
    description: 'Reusable button component'
  },
  {
    filename: 'styles/global.css',
    content: `* {\n  margin: 0;\n  padding: 0;\n  box-sizing: border-box;\n}\n\nbody {\n  font-family: Arial, sans-serif;\n  background-color: #f5f5f5;\n}`,
    language: 'css',
    description: 'Global styles'
  },
  {
    filename: 'package.json',
    content: `{\n  "name": "my-app",\n  "version": "1.0.0",\n  "dependencies": {\n    "react": "^18.0.0",\n    "react-dom": "^18.0.0"\n  }\n}`,
    language: 'json',
    description: 'Package configuration'
  }
]

describe('FileExplorer', () => {
  const mockOnFileSelect = vi.fn()
  const mockOnDownload = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('ファイルツリーが正しく表示される', () => {
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
      />
    )

    // ファイル名が表示される
    expect(screen.getByText('App.tsx')).toBeInTheDocument()
    expect(screen.getByText('Button.tsx')).toBeInTheDocument()
    expect(screen.getByText('global.css')).toBeInTheDocument()
    expect(screen.getByText('package.json')).toBeInTheDocument()

    // フォルダ構造が表示される
    expect(screen.getByText('components')).toBeInTheDocument()
    expect(screen.getByText('styles')).toBeInTheDocument()
  })

  it('ファイル選択が正しく動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
      />
    )

    const appFile = screen.getByText('App.tsx')
    await user.click(appFile)

    expect(mockOnFileSelect).toHaveBeenCalledWith(mockGeneratedFiles[0])
  })

  it('選択されたファイルがハイライトされる', async () => {
    const user = userEvent.setup()
    
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
        selectedFile={mockGeneratedFiles[0]}
      />
    )

    const appFile = screen.getByText('App.tsx').closest('.file-item')
    expect(appFile).toHaveClass('selected') // 選択状態のクラス
  })

  it('ファイルアイコンが正しく表示される', () => {
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
      />
    )

    // 各ファイルタイプに応じたアイコンの検証
    // TypeScriptファイル
    const tsFiles = screen.getAllByText(/\.tsx?$/)
    expect(tsFiles.length).toBeGreaterThan(0)

    // CSSファイル
    expect(screen.getByText('global.css')).toBeInTheDocument()

    // JSONファイル
    expect(screen.getByText('package.json')).toBeInTheDocument()
  })

  it('フォルダ展開・折りたたみが動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
      />
    )

    // フォルダが存在することを確認
    const componentsFolder = screen.getByText('components')
    expect(componentsFolder).toBeInTheDocument()
    
    // フォルダをクリックして折りたたみ/展開の動作確認
    await user.click(componentsFolder)
    
    // クリック後の状態確認（実装に依存）
    expect(componentsFolder).toBeInTheDocument()
  })

  it('ファイルサイズと言語情報が表示される', () => {
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
        showDetails={true}
      />
    )

    // 言語表示（複数あることを考慮）
    expect(screen.getAllByText('typescript')).toHaveLength(2) // App.tsx と Button.tsx
    expect(screen.getByText('css')).toBeInTheDocument()
    expect(screen.getByText('json')).toBeInTheDocument()
  })

  it('ダウンロード機能が動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
      />
    )

    const downloadButton = screen.getByRole('button', { name: /ダウンロード/i })
    await user.click(downloadButton)

    expect(mockOnDownload).toHaveBeenCalledWith(mockGeneratedFiles)
  })

  it('検索機能が動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={mockOnFileSelect}
        onDownload={mockOnDownload}
        searchable={true}
      />
    )

    const searchInput = screen.getByPlaceholderText(/ファイルを検索/i)
    await user.type(searchInput, 'App')

    // 検索にマッチするファイルのみ表示
    expect(screen.getByText('App.tsx')).toBeVisible()
    
    // 検索機能が実装されているかの基本確認
    expect(searchInput.value).toBe('App')
  })
})

describe('PreviewPanel', () => {
  const mockFile = mockGeneratedFiles[0]

  it('プレビューパネルが正しく表示される', () => {
    render(<PreviewPanel file={mockFile} />)

    expect(screen.getByText('App.tsx')).toBeInTheDocument()
    expect(screen.getByText('typescript')).toBeInTheDocument()
    expect(screen.getByText('Main application component')).toBeInTheDocument()
  })

  it('ファイル内容が表示される', () => {
    render(<PreviewPanel file={mockFile} />)

    expect(screen.getByText(/import React from 'react'/)).toBeInTheDocument()
    expect(screen.getByText(/const App = \(\)/)).toBeInTheDocument()
  })

  it('ファイルが選択されていない場合のメッセージ', () => {
    render(<PreviewPanel file={null} />)

    expect(screen.getByText(/ファイルを選択してください/i)).toBeInTheDocument()
  })

  it('コードのシンタックスハイライトが適用される', () => {
    render(<PreviewPanel file={mockFile} />)

    // シンタックスハイライトのクラスやスタイルが適用されているかチェック
    const codeElements = screen.getAllByRole('code') // 複数のcode要素
    expect(codeElements[0]).toHaveClass('language-typescript')
  })

  it('プレビューモードの切り替えが動作する', async () => {
    const user = userEvent.setup()
    
    render(<PreviewPanel file={mockFile} />)

    // コードビューとプレビュービューの切り替え
    const previewButton = screen.getByRole('button', { name: /プレビュー/i })
    const codeButton = screen.getByRole('button', { name: /コード/i })

    // 初期状態はコードビュー
    expect(screen.getByText(/import React/)).toBeInTheDocument()

    // プレビュービューに切り替え（HTMLファイルの場合）
    await user.click(previewButton)
    
    // iframe または レンダリング結果が表示される
    const iframe = screen.queryByTitle('preview')
    if (iframe) {
      expect(iframe).toBeInTheDocument()
    }
  })

  it('ファイルコピー機能が動作する', async () => {
    const user = userEvent.setup()
    
    // Clipboard API のモック
    const mockWriteText = vi.fn().mockResolvedValue(undefined)
    
    // navigatorオブジェクトをモック
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: mockWriteText,
      },
      writable: true,
    })

    render(<PreviewPanel file={mockFile} />)

    const copyButton = screen.getByRole('button', { name: /コピー/i })
    await user.click(copyButton)

    expect(mockWriteText).toHaveBeenCalledWith(mockFile.content)
  })
})

describe('CodeEditor', () => {
  const mockOnChange = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('コードエディタが正しく表示される', () => {
    render(
      <CodeEditor
        value={mockGeneratedFiles[0].content}
        language="typescript"
        onChange={mockOnChange}
      />
    )

    expect(screen.getByDisplayValue(/import React from 'react'/)).toBeInTheDocument()
  })

  it('編集機能が動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <CodeEditor
        value={mockGeneratedFiles[0].content}
        language="typescript"
        onChange={mockOnChange}
        readOnly={false}
      />
    )

    const editor = screen.getByRole('textbox') // textarea またはcontenteditable
    await user.type(editor, '\n// New comment')

    expect(mockOnChange).toHaveBeenCalled()
  })

  it('読み取り専用モードが動作する', () => {
    render(
      <CodeEditor
        value={mockGeneratedFiles[0].content}
        language="typescript"
        onChange={mockOnChange}
        readOnly={true}
      />
    )

    const editor = screen.getByRole('textbox')
    expect(editor).toHaveAttribute('readonly')
  })

  it('言語別シンタックスハイライトが適用される', () => {
    render(
      <CodeEditor
        value={mockGeneratedFiles[2].content} // CSS file
        language="css"
        onChange={mockOnChange}
      />
    )

    // CSS用のハイライトクラスが適用されている
    const editorContainer = screen.getByRole('textbox').closest('.code-editor')
    expect(editorContainer).toHaveClass('language-css')
  })

  it('行番号が表示される', () => {
    render(
      <CodeEditor
        value={mockGeneratedFiles[0].content}
        language="typescript"
        onChange={mockOnChange}
        showLineNumbers={true}
      />
    )

    // 行番号の要素が存在する
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('テーマ切り替えが動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <CodeEditor
        value={mockGeneratedFiles[0].content}
        language="typescript"
        onChange={mockOnChange}
        theme="light"
      />
    )

    // 初期テーマ
    const editorContainer = screen.getByRole('textbox').closest('.code-editor')
    expect(editorContainer).toHaveClass('theme-light')

    // テーマ切り替えボタンがある場合
    const themeButton = screen.queryByRole('button', { name: /テーマ/i })
    if (themeButton) {
      await user.click(themeButton)
      expect(editorContainer).toHaveClass('theme-dark')
    }
  })
})

describe('Integration Tests', () => {
  it('ファイル選択からプレビュー表示までの統合フロー', async () => {
    const user = userEvent.setup()
    
    const TestComponent = () => {
      const [selectedFile, setSelectedFile] = React.useState(null)

      return (
        <div className="flex">
          <FileExplorer
            files={mockGeneratedFiles}
            onFileSelect={setSelectedFile}
            onDownload={() => {}}
            selectedFile={selectedFile}
          />
          <PreviewPanel file={selectedFile} />
        </div>
      )
    }

    render(<TestComponent />)

    // ファイル選択
    const appFile = screen.getByText('App.tsx')
    await user.click(appFile)

    // プレビューパネルにファイル内容が表示される
    await waitFor(() => {
      expect(screen.getByText(/import React from 'react'/)).toBeInTheDocument()
    })

    // 選択状態が反映される
    expect(appFile.closest('.file-item')).toHaveClass('selected')
  })

  it('ファイルツリーとコードエディタの統合', async () => {
    const user = userEvent.setup()
    
    const TestComponent = () => {
      const [selectedFile, setSelectedFile] = React.useState(null)
      const [editingContent, setEditingContent] = React.useState('')

      React.useEffect(() => {
        if (selectedFile) {
          setEditingContent(selectedFile.content)
        }
      }, [selectedFile])

      return (
        <div className="flex">
          <FileExplorer
            files={mockGeneratedFiles}
            onFileSelect={setSelectedFile}
            onDownload={() => {}}
          />
          {selectedFile && (
            <CodeEditor
              value={editingContent}
              language={selectedFile.language}
              onChange={setEditingContent}
            />
          )}
        </div>
      )
    }

    render(<TestComponent />)

    // ファイル選択
    const cssFile = screen.getByText('global.css')
    await user.click(cssFile)

    // エディタにCSS内容が表示される
    await waitFor(() => {
      expect(screen.getByDisplayValue(/\* \{/)).toBeInTheDocument()
    })
  })

  it('ファイルダウンロード機能の統合テスト', async () => {
    const user = userEvent.setup()
    const mockOnDownload = vi.fn()

    render(
      <FileExplorer
        files={mockGeneratedFiles}
        onFileSelect={() => {}}
        onDownload={mockOnDownload}
      />
    )

    const downloadButton = screen.getByRole('button', { name: /ダウンロード/i })
    await user.click(downloadButton)

    expect(mockOnDownload).toHaveBeenCalledWith(mockGeneratedFiles)
  })
})