/**
 * AltMX - 表示モード切り替えタブ
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'

interface ViewTabsProps {
  currentView: 'code' | 'tree' | 'file' | 'preview'
  onViewChange: (view: 'code' | 'tree' | 'file' | 'preview') => void
}

const ViewTabs: FC<ViewTabsProps> = ({ currentView, onViewChange }) => {
  const tabs = [
    {
      id: 'code' as const,
      label: 'CODE',
      icon: '⚡',
      description: 'リアルタイムコード生成'
    },
    {
      id: 'tree' as const,
      label: 'TREE',
      icon: '🌳',
      description: 'プロジェクト構造'
    },
    {
      id: 'file' as const,
      label: 'FILE',
      icon: '📄',
      description: '個別ファイル詳細'
    },
    {
      id: 'preview' as const,
      label: 'PREVIEW',
      icon: '🚀',
      description: '実行結果プレビュー'
    }
  ]

  const handleTabClick = (tabId: typeof currentView) => {
    if (tabId !== currentView) {
      onViewChange(tabId)
    }
  }

  return (
    <div className="view-tabs">
      <div className="tabs-container">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${currentView === tab.id ? 'active' : ''}`}
            onClick={() => handleTabClick(tab.id)}
            aria-label={tab.description}
          >
            <div className="tab-content">
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </div>
            
            {/* アクティブタブのインジケーター */}
            {currentView === tab.id && (
              <div className="tab-indicator">
                <div className="indicator-glow"></div>
                <div className="indicator-line"></div>
              </div>
            )}

            {/* ホバーエフェクト */}
            <div className="tab-hover-effect"></div>
            
            {/* リップルエフェクト */}
            <div className="tab-ripple"></div>
          </button>
        ))}
      </div>

      {/* 背景グロー */}
      <div className="tabs-background-glow"></div>
      
      {/* スキャンライン */}
      <div className="tabs-scanline"></div>
    </div>
  )
}

export default ViewTabs