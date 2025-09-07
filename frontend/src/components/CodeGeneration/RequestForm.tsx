/**
 * Code Generation Request Form - Green段階（テストを通すための実装）
 * コード生成リクエストフォームコンポーネント
 */

import React, { useState, useCallback } from 'react'

export interface GenerationRequest {
  user_prompt: string
  complexity: string
  include_security: boolean
  include_accessibility: boolean
  target_framework: string
  max_files: number
  timeout: number
}

export interface CodeGenerationFormProps {
  onSubmit: (request: GenerationRequest) => void
  onCancel: () => void
  isGenerating: boolean
  error?: string
}

export const CodeGenerationForm: React.FC<CodeGenerationFormProps> = ({
  onSubmit,
  onCancel,
  isGenerating,
  error
}) => {
  const [formData, setFormData] = useState<GenerationRequest>({
    user_prompt: '',
    complexity: 'medium',
    include_security: true,
    include_accessibility: false,
    target_framework: 'react',
    max_files: 10,
    timeout: 60
  })
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {}

    // プロンプト必須チェック
    if (!formData.user_prompt.trim()) {
      errors.user_prompt = 'プロンプトを入力してください'
    } else if (formData.user_prompt.trim().length < 5) {
      errors.user_prompt = 'プロンプトは5文字以上で入力してください'
    } else if (formData.user_prompt.trim().length > 10000) {
      errors.user_prompt = 'プロンプトは10000文字以内で入力してください'
    }

    // 複雑度チェック
    if (!['simple', 'medium', 'high'].includes(formData.complexity)) {
      errors.complexity = '有効な複雑度を選択してください'
    }

    // ファイル数チェック
    if (formData.max_files < 1 || formData.max_files > 20) {
      errors.max_files = 'ファイル数は1-20の範囲で指定してください'
    }

    // タイムアウトチェック
    if (formData.timeout < 5 || formData.timeout > 300) {
      errors.timeout = 'タイムアウトは5-300秒の範囲で指定してください'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }, [formData])

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      onSubmit(formData)
    }
  }, [formData, validateForm, onSubmit])

  const handleInputChange = useCallback(<K extends keyof GenerationRequest>(
    field: K,
    value: GenerationRequest[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // エラーメッセージクリア
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const { [field]: removed, ...rest } = prev
        return rest
      })
    }
  }, [validationErrors])

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">コード生成リクエスト</h2>
      
      {error && (
        <div role="alert" className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          <strong className="font-medium">エラー:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* プロンプト入力 */}
        <div>
          <label 
            htmlFor="user_prompt" 
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            プロンプト入力 *
          </label>
          <textarea
            id="user_prompt"
            name="user_prompt"
            rows={4}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              validationErrors.user_prompt ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="例: ログイン機能付きの管理者ダッシュボードを作成してください"
            value={formData.user_prompt}
            onChange={(e) => handleInputChange('user_prompt', e.target.value)}
            disabled={isGenerating}
            aria-describedby={validationErrors.user_prompt ? "user_prompt_error" : undefined}
          />
          {validationErrors.user_prompt && (
            <p id="user_prompt_error" className="mt-1 text-sm text-red-600">
              {validationErrors.user_prompt}
            </p>
          )}
        </div>

        {/* 複雑度選択 */}
        <div>
          <label 
            htmlFor="complexity" 
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            複雑度選択 *
          </label>
          <select
            id="complexity"
            name="complexity"
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              validationErrors.complexity ? 'border-red-300' : 'border-gray-300'
            }`}
            value={formData.complexity}
            onChange={(e) => handleInputChange('complexity', e.target.value)}
            disabled={isGenerating}
          >
            <option value="simple">シンプル (基本機能のみ)</option>
            <option value="medium">標準 (バランス型)</option>
            <option value="high">高度 (高機能・複雑)</option>
          </select>
          {validationErrors.complexity && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.complexity}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* セキュリティ機能 */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={formData.include_security}
                onChange={(e) => handleInputChange('include_security', e.target.checked)}
                disabled={isGenerating}
              />
              <span className="ml-2 text-sm text-gray-700">セキュリティ機能を含める</span>
            </label>
          </div>

          {/* アクセシビリティ機能 */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={formData.include_accessibility}
                onChange={(e) => handleInputChange('include_accessibility', e.target.checked)}
                disabled={isGenerating}
              />
              <span className="ml-2 text-sm text-gray-700">アクセシビリティ対応</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 最大ファイル数 */}
          <div>
            <label 
              htmlFor="max_files" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              最大ファイル数
            </label>
            <input
              type="number"
              id="max_files"
              name="max_files"
              min="1"
              max="20"
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.max_files ? 'border-red-300' : 'border-gray-300'
              }`}
              value={formData.max_files}
              onChange={(e) => handleInputChange('max_files', parseInt(e.target.value, 10))}
              disabled={isGenerating}
            />
            {validationErrors.max_files && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.max_files}</p>
            )}
          </div>

          {/* タイムアウト */}
          <div>
            <label 
              htmlFor="timeout" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              タイムアウト (秒)
            </label>
            <input
              type="number"
              id="timeout"
              name="timeout"
              min="5"
              max="300"
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                validationErrors.timeout ? 'border-red-300' : 'border-gray-300'
              }`}
              value={formData.timeout}
              onChange={(e) => handleInputChange('timeout', parseInt(e.target.value, 10))}
              disabled={isGenerating}
            />
            {validationErrors.timeout && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.timeout}</p>
            )}
          </div>
        </div>

        {/* アクションボタン */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={false} // キャンセルは常に有効
          >
            キャンセル
          </button>
          <button
            type="submit"
            className={`px-4 py-2 text-sm font-medium text-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
              isGenerating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            disabled={isGenerating}
          >
            {isGenerating ? '生成中...' : '生成開始'}
          </button>
        </div>
      </form>
    </div>
  )
}