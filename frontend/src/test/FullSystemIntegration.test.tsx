/**
 * Full System Integration Test - 完全な動作確認テスト
 * TDD Red段階 - これらのテストは失敗するはず
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import userEvent from '@testing-library/user-event'

// 実際に統合されるべきコンポーネント
import VaporwaveMainScreen from '../components/VaporwaveMainScreen'

// Mock API
vi.mock('../services/codeGenerationApi', () => ({
  generateCode: vi.fn().mockResolvedValue({
    success: true,
    generated_files: [{
      filename: 'TodoApp.tsx',
      content: `import React, { useState } from 'react';

const TodoApp = () => {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  const addTodo = () => {
    if (input.trim()) {
      setTodos([...todos, { id: Date.now(), text: input, done: false }]);
      setInput('');
    }
  };

  return (
    <div className="todo-app">
      <h1>TODO アプリ</h1>
      <div>
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          placeholder="タスクを入力"
        />
        <button onClick={addTodo}>追加</button>
      </div>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>{todo.text}</li>
        ))}
      </ul>
    </div>
  );
};

export default TodoApp;`,
      language: 'typescript',
      description: 'React TODO アプリケーション'
    }]
  })
}))

describe('Full System Integration - TODOアプリ生成フロー', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
    
    // scrollIntoViewをモック
    Element.prototype.scrollIntoView = vi.fn()
  })

  it('メイン画面にコード生成タブが表示される', async () => {
    render(<VaporwaveMainScreen />)
    
    // タブが表示されているか（特定のタブメニューボタン）
    const buttons = screen.getAllByText('コード生成')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('コード生成タブをクリックすると生成フォームが表示される', async () => {
    render(<VaporwaveMainScreen />)
    
    // まずタブメニューのコード生成ボタンを見つける
    const allButtons = screen.getAllByText('コード生成')
    const tabButton = allButtons.find(button => button.tagName === 'BUTTON')
    
    if (tabButton) {
      await user.click(tabButton)
    }
    
    // フォームが表示される
    await waitFor(() => {
      expect(screen.getByLabelText(/プロンプト入力/i)).toBeInTheDocument()
    })
    expect(screen.getByRole('button', { name: /生成開始/i })).toBeInTheDocument()
  })

  it('TODOアプリのリクエストを送信できる', async () => {
    render(<VaporwaveMainScreen />)
    
    // コード生成タブをクリック
    const allButtons = screen.getAllByText('コード生成')
    const tabButton = allButtons.find(button => button.tagName === 'BUTTON')
    
    if (tabButton) {
      await user.click(tabButton)
    }
    
    // プロンプト入力
    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    await user.type(promptInput, 'TODOアプリを作ってください')
    
    // 生成ボタンをクリック
    const generateButton = screen.getByRole('button', { name: /生成開始/i })
    await user.click(generateButton)
    
    // 生成中の状態確認（ボタンが無効化される）
    await waitFor(() => {
      expect(generateButton).toBeDisabled()
    })
  })

  it('生成されたコードがプレビューパネルに表示される', async () => {
    render(<VaporwaveMainScreen />)
    
    // コード生成タブをクリック
    const allButtons = screen.getAllByText('コード生成')
    const tabButton = allButtons.find(button => button.tagName === 'BUTTON')
    
    if (tabButton) {
      await user.click(tabButton)
    }
    
    // プロンプト入力
    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    await user.type(promptInput, 'TODOアプリを作ってください')
    
    // 生成実行
    const generateButton = screen.getByRole('button', { name: /生成開始/i })
    await user.click(generateButton)
    
    // 生成完了を待つ（ファイル名が表示される）
    await waitFor(() => {
      expect(screen.getByText('TodoApp.tsx')).toBeInTheDocument()
    }, { timeout: 3000 })
    
    // プレビューパネルのタブが表示される（PreviewPanel内のボタン）
    const codeButtons = screen.getAllByRole('button', { name: /コード/i })
    const liveButtons = screen.getAllByRole('button', { name: /ライブ/i })
    
    expect(codeButtons.length).toBeGreaterThan(0)
    expect(liveButtons.length).toBeGreaterThan(0)
  })

  it('ライブプレビューボタンでReactコンポーネントがプレビューできる', async () => {
    render(<VaporwaveMainScreen />)
    
    // コード生成タブをクリック
    const allButtons = screen.getAllByText('コード生成')
    const tabButton = allButtons.find(button => button.tagName === 'BUTTON')
    
    if (tabButton) {
      await user.click(tabButton)
    }
    
    // 生成実行
    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    await user.type(promptInput, 'TODOアプリを作ってください')
    
    const generateButton = screen.getByRole('button', { name: /生成開始/i })
    await user.click(generateButton)
    
    // 生成完了を待つ
    await waitFor(() => {
      expect(screen.getByText('TodoApp.tsx')).toBeInTheDocument()
    })
    
    // ライブプレビューボタンをクリック
    const liveButton = screen.getByText(/ライブ/i)
    await user.click(liveButton)
    
    // iframeが表示される
    expect(screen.getByTitle('live-preview')).toBeInTheDocument()
  })

  it('エラーが発生した場合、適切なエラーメッセージが表示される', async () => {
    // APIをエラーモックに変更
    const { generateCode } = await import('../services/codeGenerationApi')
    vi.mocked(generateCode).mockRejectedValueOnce(new Error('生成に失敗しました'))
    
    render(<VaporwaveMainScreen />)
    
    // コード生成タブをクリック
    const allButtons = screen.getAllByText('コード生成')
    const tabButton = allButtons.find(button => button.tagName === 'BUTTON')
    
    if (tabButton) {
      await user.click(tabButton)
    }
    
    // 生成実行
    const promptInput = screen.getByLabelText(/プロンプト入力/i)
    await user.type(promptInput, 'エラーテスト')
    
    const generateButton = screen.getByRole('button', { name: /生成開始/i })
    await user.click(generateButton)
    
    // エラーメッセージが表示される
    await waitFor(() => {
      expect(screen.getByText(/生成に失敗しました/i)).toBeInTheDocument()
    })
  })

  it('チャットと同時に使用できる', async () => {
    render(<VaporwaveMainScreen />)
    
    // チャットタブをクリック
    const allChatButtons = screen.getAllByText('チャット')
    const chatTabButton = allChatButtons.find(button => button.tagName === 'BUTTON')
    
    if (chatTabButton) {
      await user.click(chatTabButton)
    }
    
    // チャット入力
    const chatInput = screen.getByPlaceholderText(/Message to AltMX/i)
    expect(chatInput).toBeInTheDocument()
    
    // コード生成タブに切り替え
    const allCodeGenButtons = screen.getAllByText('コード生成')
    const codeGenTabButton = allCodeGenButtons.find(button => button.tagName === 'BUTTON')
    
    if (codeGenTabButton) {
      await user.click(codeGenTabButton)
    }
    
    // コード生成フォームが表示される
    expect(screen.getByLabelText(/プロンプト入力/i)).toBeInTheDocument()
    
    // チャットタブに戻る
    await user.click(chatTabButton)
    
    // チャットが保持されている
    expect(chatInput).toBeInTheDocument()
  })
})