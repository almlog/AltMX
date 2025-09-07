/**
 * AgentModePanel TDD Test Suite
 * Red-Green-Refactor サイクルに従った厳密なテスト
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import AgentModePanel from '../AgentModePanel'

// Mock fetch for API calls - with proper typing
const mockFetch = vi.fn()
global.fetch = mockFetch as any

describe('AgentModePanel - TDD Test Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock successful API responses
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        message: 'Mode changed successfully',
        current_mode: 'coding',
        system_prompt: 'Test prompt',
        configuration: {
          mode: 'coding',
          quality_level: 'development',
          personality: 'professional'
        }
      })
    })
  })

  // RED: 最初に失敗するテスト群
  describe('RED Phase - Initial failing tests', () => {
    it('should render all 8 agent modes with icons and names when expanded', () => {
      render(<AgentModePanel />)
      
      // 初期状態では現在のモード（Chat）のみ表示される
      expect(screen.getByText('Chat')).toBeInTheDocument()
      expect(screen.getByText('💬')).toBeInTheDocument()
      
      // パネルを展開
      const header = screen.getByText('Chat').closest('.mode-header')!
      fireEvent.click(header)
      
      // 展開後、8つのモード全てが表示されること
      expect(screen.getAllByText('Chat')).toHaveLength(2) // Header + Toggle row
      expect(screen.getByText('Coding')).toBeInTheDocument()
      expect(screen.getByText('Live')).toBeInTheDocument()
      expect(screen.getByText('Production')).toBeInTheDocument()
      expect(screen.getByText('Review')).toBeInTheDocument()
      expect(screen.getByText('Debug')).toBeInTheDocument()
      expect(screen.getByText('Teaching')).toBeInTheDocument()
      expect(screen.getByText('Architecture')).toBeInTheDocument()
      
      // アイコンが表示されること（Header + Toggle rows）
      expect(screen.getAllByText('💬')).toHaveLength(2)
      expect(screen.getByText('💻')).toBeInTheDocument()
      expect(screen.getByText('🎥')).toBeInTheDocument()
      expect(screen.getByText('🏭')).toBeInTheDocument()
      expect(screen.getByText('🔍')).toBeInTheDocument()
      expect(screen.getByText('🐛')).toBeInTheDocument()
      expect(screen.getByText('👨‍🏫')).toBeInTheDocument()
      expect(screen.getByText('🏗️')).toBeInTheDocument()
    })

    it('should show tooltips on hover with detailed explanations', async () => {
      render(<AgentModePanel />)
      
      // パネルを展開
      const header = screen.getByText('Chat').closest('.mode-header')!
      fireEvent.click(header)
      
      // Chatトグル行のツールチップを確認
      const chatRows = screen.getAllByText('Chat')
      const chatToggleRow = chatRows.find(el => 
        el.closest('.mode-toggle-row') && 
        el.closest('.mode-toggle-row').hasAttribute('title')
      )?.closest('.mode-toggle-row')
      
      expect(chatToggleRow).toHaveAttribute('title', expect.stringContaining('一般的な質問や会話に適したモード'))
    })

    it('should expand and collapse when header is clicked', () => {
      render(<AgentModePanel />)
      
      // 初期状態では折りたたまれている
      expect(screen.queryByText('AI Agent Mode Settings')).not.toBeInTheDocument()
      
      // ヘッダークリックで展開
      const header = screen.getByText('Chat').closest('.mode-header')
      fireEvent.click(header)
      expect(screen.getByText('AI Agent Mode Settings')).toBeInTheDocument()
      
      // 再度クリックで折りたたみ
      fireEvent.click(header)
      expect(screen.queryByText('AI Agent Mode Settings')).not.toBeInTheDocument()
    })

    it('should have radio buttons for mode selection', () => {
      render(<AgentModePanel />)
      
      // パネルを展開
      const header = screen.getByText('Chat').closest('.mode-header')!
      fireEvent.click(header)
      
      // 全てのラジオボタンが存在すること
      const radioButtons = screen.getAllByRole('radio')
      expect(radioButtons).toHaveLength(8)
      
      // 初期状態でChatが選択されていること
      const chatRadio = screen.getByDisplayValue('chat')
      expect(chatRadio).toBeChecked()
    })

    it('should call API when mode is changed', async () => {
      const mockOnModeChange = vi.fn()
      render(<AgentModePanel onModeChange={mockOnModeChange} />)
      
      // パネルを展開
      const header = screen.getByText('Chat').closest('.mode-header')!
      fireEvent.click(header)
      
      // Codingモードを選択
      const codingRadio = screen.getByDisplayValue('coding')
      fireEvent.click(codingRadio)
      
      // API呼び出しが実行されること
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/agent/declare-mode', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            mode: 'coding',
            quality_level: 'development',
            personality: 'professional',
            focus_areas: [],
            constraints: [],
            session_goals: [],
            audience: 'general'
          })
        })
      })
      
      // コールバックが呼ばれること
      expect(mockOnModeChange).toHaveBeenCalledWith('coding')
    })

    it('should show loading state during API call', async () => {
      // 遅延レスポンスをモック
      mockFetch.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: async () => ({ success: true, current_mode: 'coding', message: 'Success' })
          }), 100)
        )
      )
      
      render(<AgentModePanel />)
      
      // パネルを展開
      const header = screen.getByText('Chat').closest('.mode-header')!
      fireEvent.click(header)
      
      // Codingモードを選択
      const codingRadio = screen.getByDisplayValue('coding')
      fireEvent.click(codingRadio)
      
      // ローディング状態が表示されること
      expect(screen.getByText('モード変更中...')).toBeInTheDocument()
      
      // ローディング終了を待機
      await waitFor(() => {
        expect(screen.queryByText('モード変更中...')).not.toBeInTheDocument()
      }, { timeout: 200 })
    })

    it('should handle API errors gracefully', async () => {
      // エラーレスポンスをモック（current-mode APIもエラーにする）
      mockFetch.mockImplementation((url: string) => {
        if (url === '/api/agent/current-mode') {
          return Promise.reject(new Error('Network error'))
        }
        if (url === '/api/agent/declare-mode') {
          return Promise.reject(new Error('Network error'))
        }
        return Promise.resolve({ ok: false })
      })
      
      render(<AgentModePanel />)
      
      // パネルを展開
      const header = screen.getByText('Chat').closest('.mode-header')!
      fireEvent.click(header)
      
      // Codingモードを選択
      const codingRadio = screen.getByDisplayValue('coding')
      fireEvent.click(codingRadio)
      
      // エラーメッセージが表示されること
      await waitFor(() => {
        expect(screen.getByText('通信エラーが発生しました')).toBeInTheDocument()
      })
    })

    it('should fetch current mode on mount', async () => {
      // 現在のモード取得APIをモック
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          mode: 'production'
        })
      })
      
      render(<AgentModePanel />)
      
      // マウント時に現在のモード取得APIが呼ばれること
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/agent/current-mode')
      })
    })
  })
})