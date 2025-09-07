/**
 * Code Generation Components Tests - Red段階（失敗するテスト）
 * React コード生成フォーム・コンポーネントテスト
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import userEvent from '@testing-library/user-event'

// Test用のインポート（実装前なのでエラーになる想定）
import { CodeGenerationForm } from '../components/CodeGeneration/RequestForm'
import { TemplateSelector } from '../components/CodeGeneration/TemplateSelector'
import { ProgressIndicator } from '../components/CodeGeneration/ProgressIndicator'

// Mock API calls
vi.mock('../services/codeGenerationApi', () => ({
  generateCode: vi.fn(),
  getTemplates: vi.fn(),
  validateCode: vi.fn()
}))

import { generateCode, getTemplates } from '../services/codeGenerationApi'
const mockGenerateCode = vi.mocked(generateCode)
const mockGetTemplates = vi.mocked(getTemplates)

describe('CodeGenerationForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('フォームが正しく表示される', () => {
    render(
      <CodeGenerationForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel}
        isGenerating={false}
      />
    )

    expect(screen.getByLabelText(/プロンプト入力/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/複雑度選択/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /生成開始/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /キャンセル/i })).toBeInTheDocument()
  })

  it('プロンプト入力の検証が機能する', async () => {
    render(
      <CodeGenerationForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel}
        isGenerating={false}
      />
    )

    const submitButton = screen.getByRole('button', { name: /生成開始/i })
    
    // 空のプロンプトで送信
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/プロンプトを入力してください/i)).toBeInTheDocument()
    })
    
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('フォーム送信が正しく動作する', async () => {
    const user = userEvent.setup()
    
    render(
      <CodeGenerationForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel}
        isGenerating={false}
      />
    )

    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    const complexitySelect = screen.getByLabelText(/複雑度選択/i)
    const submitButton = screen.getByRole('button', { name: /生成開始/i })

    // フォーム入力
    await user.type(promptInput, 'Create a React login form')
    await user.selectOptions(complexitySelect, 'medium')
    
    // 送信
    await user.click(submitButton)

    expect(mockOnSubmit).toHaveBeenCalledWith({
      user_prompt: 'Create a React login form',
      complexity: 'medium',
      include_security: true,
      include_accessibility: false,
      target_framework: 'react',
      max_files: 10,
      timeout: 60
    })
  })

  it('生成中状態でフォームが無効化される', () => {
    render(
      <CodeGenerationForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel}
        isGenerating={true}
      />
    )

    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    const submitButton = screen.getByRole('button', { name: /生成中.../i })

    expect(promptInput).toBeDisabled()
    expect(submitButton).toBeDisabled()
    expect(screen.getByRole('button', { name: /キャンセル/i })).toBeEnabled()
  })

  it('エラー表示機能が動作する', () => {
    const errorMessage = 'API呼び出しでエラーが発生しました'
    
    render(
      <CodeGenerationForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel}
        isGenerating={false}
        error={errorMessage}
      />
    )

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})

describe('TemplateSelector', () => {
  const mockTemplates = [
    {
      name: 'form',
      description: 'フォームコンポーネント',
      complexity_levels: ['simple', 'medium', 'high']
    },
    {
      name: 'dashboard',
      description: 'ダッシュボードレイアウト',
      complexity_levels: ['medium', 'high']
    },
    {
      name: 'list',
      description: 'リストコンポーネント',
      complexity_levels: ['simple', 'medium']
    }
  ]

  const mockOnSelect = vi.fn()

  beforeEach(() => {
    mockGetTemplates.mockResolvedValue({ templates: mockTemplates })
  })

  it('テンプレート一覧が表示される', async () => {
    render(<TemplateSelector onSelect={mockOnSelect} />)

    await waitFor(() => {
      expect(screen.getByText('フォームコンポーネント')).toBeInTheDocument()
      expect(screen.getByText('ダッシュボードレイアウト')).toBeInTheDocument()
      expect(screen.getByText('リストコンポーネント')).toBeInTheDocument()
    })
  })

  it('テンプレート選択が動作する', async () => {
    const user = userEvent.setup()
    
    render(<TemplateSelector onSelect={mockOnSelect} />)

    await waitFor(() => {
      expect(screen.getByText('フォームコンポーネント')).toBeInTheDocument()
    })

    const formTemplate = screen.getByText('フォームコンポーネント').closest('button')
    await user.click(formTemplate!)

    expect(mockOnSelect).toHaveBeenCalledWith('form')
  })

  it('ローディング状態が表示される', () => {
    mockGetTemplates.mockImplementation(() => new Promise(() => {})) // 永続的なpending
    
    render(<TemplateSelector onSelect={mockOnSelect} />)

    expect(screen.getByText(/読み込み中.../i)).toBeInTheDocument()
  })

  it('エラー状態が表示される', async () => {
    mockGetTemplates.mockRejectedValue(new Error('API Error'))
    
    render(<TemplateSelector onSelect={mockOnSelect} />)

    await waitFor(() => {
      expect(screen.getByText(/テンプレートの読み込みに失敗/i)).toBeInTheDocument()
    })
  })
})

describe('ProgressIndicator', () => {
  it('進捗段階が正しく表示される', () => {
    const stages = [
      { name: '検証', status: 'completed' as const },
      { name: '準備', status: 'completed' as const },
      { name: 'AI生成', status: 'in_progress' as const },
      { name: '解析', status: 'pending' as const },
      { name: '完了', status: 'pending' as const }
    ]

    render(<ProgressIndicator stages={stages} />)

    // 完了段階
    expect(screen.getByText('検証')).toBeInTheDocument()
    expect(screen.getByText('準備')).toBeInTheDocument()
    
    // 進行中段階
    expect(screen.getByText('AI生成')).toBeInTheDocument()
    
    // 待機中段階
    expect(screen.getByText('解析')).toBeInTheDocument()
    expect(screen.getByText('完了')).toBeInTheDocument()
  })

  it('進捗率が計算される', () => {
    const stages = [
      { name: '検証', status: 'completed' as const },
      { name: '準備', status: 'completed' as const },
      { name: 'AI生成', status: 'in_progress' as const },
      { name: '解析', status: 'pending' as const },
      { name: '完了', status: 'pending' as const }
    ]

    render(<ProgressIndicator stages={stages} />)

    // 2/5完了 + 1/5進行中 = 50%
    expect(screen.getByText('50%')).toBeInTheDocument()
  })

  it('キャンセル機能が動作する', async () => {
    const mockOnCancel = vi.fn()
    const user = userEvent.setup()

    const stages = [
      { name: 'AI生成', status: 'in_progress' as const }
    ]

    render(
      <ProgressIndicator 
        stages={stages} 
        onCancel={mockOnCancel}
        cancellable={true}
      />
    )

    const cancelButton = screen.getByRole('button', { name: /キャンセル/i })
    await user.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('エラー状態が表示される', () => {
    const stages = [
      { name: '検証', status: 'completed' as const },
      { name: 'AI生成', status: 'error' as const, error: 'API呼び出しエラー' }
    ]

    render(<ProgressIndicator stages={stages} />)

    expect(screen.getAllByText('API呼び出しエラー')).toHaveLength(2) // エラーメッセージとステージエラー
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})

describe('Integration Tests', () => {
  it('フォーム送信から進捗表示までの統合フロー', async () => {
    const user = userEvent.setup()
    
    const TestComponent = () => {
      const [isGenerating, setIsGenerating] = React.useState(false)
      const [stages, setStages] = React.useState([
        { name: '検証', status: 'pending' as const },
        { name: 'AI生成', status: 'pending' as const },
        { name: '完了', status: 'pending' as const }
      ])

      const handleSubmit = (data: any) => {
        setIsGenerating(true)
        // 進捗シミュレーション
        setTimeout(() => {
          setStages(prev => prev.map((stage, i) => 
            i === 0 ? { ...stage, status: 'completed' } : stage
          ))
        }, 100)
      }

      return (
        <div>
          <CodeGenerationForm 
            onSubmit={handleSubmit}
            onCancel={() => setIsGenerating(false)}
            isGenerating={isGenerating}
          />
          {isGenerating && <ProgressIndicator stages={stages} />}
        </div>
      )
    }

    render(<TestComponent />)

    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    const submitButton = screen.getByRole('button', { name: /生成開始/i })

    await user.type(promptInput, 'Create a dashboard')
    await user.click(submitButton)

    // フォームが無効化される
    expect(screen.getByLabelText(/プロンプト入力/i)).toBeDisabled()

    // 進捗表示が現れる
    expect(screen.getByText('検証')).toBeInTheDocument()

    // 進捗更新を待機
    await waitFor(() => {
      expect(screen.getByText('33%')).toBeInTheDocument() // 1/3完了
    }, { timeout: 200 })
  })
})