/**
 * Progress Indicator - Green段階（テストを通すための実装）
 * コード生成進捗表示コンポーネント
 */

import React, { useMemo, useCallback } from 'react'

export type ProgressStatus = 'pending' | 'in_progress' | 'completed' | 'error'

export interface ProgressStage {
  name: string
  status: ProgressStatus
  error?: string
  startTime?: number
  endTime?: number
}

export interface ProgressIndicatorProps {
  stages: ProgressStage[]
  onCancel?: () => void
  cancellable?: boolean
  className?: string
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  stages,
  onCancel,
  cancellable = false,
  className = ''
}) => {
  // 進捗率計算
  const progressPercentage = useMemo(() => {
    if (stages.length === 0) return 0

    const completedCount = stages.filter(stage => stage.status === 'completed').length
    const inProgressCount = stages.filter(stage => stage.status === 'in_progress').length
    
    // 完了分 + 進行中の半分を進捗とする
    const progress = (completedCount + inProgressCount * 0.5) / stages.length
    return Math.round(progress * 100)
  }, [stages])

  // エラーステージの取得
  const errorStage = useMemo(() => {
    return stages.find(stage => stage.status === 'error')
  }, [stages])

  // ステージアイコンの取得
  const getStageIcon = useCallback((status: ProgressStatus): React.ReactElement => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )
      case 'in_progress':
        return (
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        )
      case 'error':
        return (
          <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        )
      default: // pending
        return (
          <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />
        )
    }
  }, [])

  // ステージスタイルの取得
  const getStageStyle = useCallback((status: ProgressStatus): string => {
    const baseStyle = "flex items-center space-x-3 p-3 rounded-lg"
    
    switch (status) {
      case 'completed':
        return `${baseStyle} bg-green-50 border border-green-200`
      case 'in_progress':
        return `${baseStyle} bg-blue-50 border border-blue-200`
      case 'error':
        return `${baseStyle} bg-red-50 border border-red-200`
      default:
        return `${baseStyle} bg-gray-50 border border-gray-200`
    }
  }, [])

  // 実行時間の計算
  const getExecutionTime = useCallback((stage: ProgressStage): string | null => {
    if (stage.startTime && stage.endTime) {
      const duration = stage.endTime - stage.startTime
      return `${(duration / 1000).toFixed(1)}秒`
    }
    return null
  }, [])

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">生成進捗</h3>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-600">{progressPercentage}%</span>
          {cancellable && onCancel && (
            <button
              onClick={onCancel}
              className="px-3 py-1 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              キャンセル
            </button>
          )}
        </div>
      </div>

      {/* 進捗バー */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progressPercentage}%` }}
        />
      </div>

      {/* エラー表示 */}
      {errorStage && (
        <div role="alert" className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-medium">エラーが発生しました</h4>
              {errorStage.error && (
                <p className="mt-1 text-sm">{errorStage.error}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ステージ一覧 */}
      <div className="space-y-3">
        {stages.map((stage, index) => (
          <div key={`${stage.name}-${index}`} className={getStageStyle(stage.status)}>
            <div className="flex-shrink-0">
              {getStageIcon(stage.status)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-900">
                  {stage.name}
                </h4>
                {getExecutionTime(stage) && (
                  <span className="text-xs text-gray-500">
                    {getExecutionTime(stage)}
                  </span>
                )}
              </div>
              {stage.status === 'in_progress' && (
                <p className="text-xs text-blue-600 mt-1">実行中...</p>
              )}
              {stage.status === 'error' && stage.error && (
                <p className="text-xs text-red-600 mt-1">{stage.error}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 完了メッセージ */}
      {progressPercentage === 100 && !errorStage && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
          <div className="flex">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-medium">生成完了</h4>
              <p className="mt-1 text-sm">コードの生成が正常に完了しました。</p>
            </div>
          </div>
        </div>
      )}

      {/* 進行中の詳細情報 */}
      {stages.some(stage => stage.status === 'in_progress') && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          処理には数十秒かかる場合があります...
        </div>
      )}
    </div>
  )
}