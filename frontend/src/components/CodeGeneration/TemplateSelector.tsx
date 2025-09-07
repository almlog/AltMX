/**
 * Template Selector - Green段階（テストを通すための実装）
 * テンプレート選択コンポーネント
 */

import React, { useState, useEffect, useCallback } from 'react'
import { getTemplates } from '../../services/codeGenerationApi'

export interface Template {
  name: string
  description: string
  complexity_levels: string[]
}

export interface TemplateSelectorProps {
  onSelect: (templateName: string) => void
  selectedTemplate?: string
  className?: string
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  onSelect,
  selectedTemplate,
  className = ''
}) => {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadTemplates = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await getTemplates()
      setTemplates(response.templates)
    } catch (err) {
      console.error('Failed to load templates:', err)
      setError('テンプレートの読み込みに失敗しました')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTemplates()
  }, [loadTemplates])

  const handleTemplateClick = useCallback((templateName: string) => {
    onSelect(templateName)
  }, [onSelect])

  const getTemplateIcon = useCallback((templateName: string): string => {
    const iconMap: Record<string, string> = {
      form: '📝',
      dashboard: '📊',
      list: '📋',
      navigation: '🧭',
      auth: '🔐',
      data: '💾',
      chart: '📈',
      layout: '🏗️'
    }
    return iconMap[templateName] || '⚡'
  }, [])

  const getComplexityBadgeColor = useCallback((level: string): string => {
    const colorMap: Record<string, string> = {
      simple: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800'
    }
    return colorMap[level] || 'bg-gray-100 text-gray-800'
  }, [])

  if (loading) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">読み込み中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          <p className="font-medium">{error}</p>
        </div>
        <button
          onClick={loadTemplates}
          className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          再試行
        </button>
      </div>
    )
  }

  if (templates.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <p>利用可能なテンプレートがありません</p>
      </div>
    )
  }

  return (
    <div className={className}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">テンプレート選択</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => (
          <button
            key={template.name}
            onClick={() => handleTemplateClick(template.name)}
            className={`p-4 border-2 rounded-lg text-left transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              selectedTemplate === template.name
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">{getTemplateIcon(template.name)}</span>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 capitalize mb-1">
                  {template.name}
                </h4>
                <p className="text-sm text-gray-600 mb-3">
                  {template.description}
                </p>
                <div className="flex flex-wrap gap-1">
                  {template.complexity_levels.map((level) => (
                    <span
                      key={level}
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getComplexityBadgeColor(level)}`}
                    >
                      {level === 'simple' && 'シンプル'}
                      {level === 'medium' && '標準'}
                      {level === 'high' && '高度'}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            {selectedTemplate === template.name && (
              <div className="mt-2 flex items-center text-blue-600">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-xs font-medium">選択中</span>
              </div>
            )}
          </button>
        ))}
      </div>
      
      {selectedTemplate && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            <span className="font-medium">選択中:</span> {templates.find(t => t.name === selectedTemplate)?.description}
          </p>
        </div>
      )}
    </div>
  )
}