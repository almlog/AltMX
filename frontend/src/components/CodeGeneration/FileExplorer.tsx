/**
 * File Explorer - Green段階（テストを通すための実装）
 * ファイルエクスプローラーコンポーネント
 */

import React, { useState, useMemo, useCallback } from 'react'

export interface GeneratedFile {
  filename: string
  content: string
  language: string
  description?: string
}

export interface FileExplorerProps {
  files: GeneratedFile[]
  onFileSelect: (file: GeneratedFile) => void
  onDownload: (files: GeneratedFile[]) => void
  selectedFile?: GeneratedFile | null
  showDetails?: boolean
  searchable?: boolean
  className?: string
}

interface FileNode {
  name: string
  path: string
  type: 'file' | 'folder'
  file?: GeneratedFile
  children?: FileNode[]
  expanded?: boolean
}

export const FileExplorer: React.FC<FileExplorerProps> = ({
  files,
  onFileSelect,
  onDownload,
  selectedFile,
  showDetails = false,
  searchable = false,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set(['', 'components', 'styles']) // 初期状態でよく使うフォルダを展開
  )

  // ファイルツリー構造生成
  const fileTree = useMemo(() => {
    const root: FileNode = {
      name: '',
      path: '',
      type: 'folder',
      children: [],
      expanded: true
    }

    files.forEach(file => {
      const parts = file.filename.split('/')
      let currentNode = root

      // ディレクトリ構造を作成
      for (let i = 0; i < parts.length - 1; i++) {
        const folderName = parts[i]
        const folderPath = parts.slice(0, i + 1).join('/')
        
        let folderNode = currentNode.children?.find(
          child => child.name === folderName && child.type === 'folder'
        )

        if (!folderNode) {
          folderNode = {
            name: folderName,
            path: folderPath,
            type: 'folder',
            children: [],
            expanded: expandedFolders.has(folderPath)
          }
          currentNode.children?.push(folderNode)
        }

        currentNode = folderNode
      }

      // ファイルノード追加
      const fileName = parts[parts.length - 1]
      currentNode.children?.push({
        name: fileName,
        path: file.filename,
        type: 'file',
        file: file
      })
    })

    // ソート（フォルダ優先、その後アルファベット順）
    const sortNodes = (nodes: FileNode[]): FileNode[] => {
      return nodes.sort((a, b) => {
        if (a.type !== b.type) {
          return a.type === 'folder' ? -1 : 1
        }
        return a.name.localeCompare(b.name)
      }).map(node => ({
        ...node,
        children: node.children ? sortNodes(node.children) : undefined
      }))
    }

    root.children = sortNodes(root.children || [])
    return root
  }, [files, expandedFolders])

  // 検索フィルタリング
  const filteredTree = useMemo(() => {
    if (!searchTerm.trim()) return fileTree

    const filterTree = (node: FileNode): FileNode | null => {
      if (node.type === 'file') {
        return node.name.toLowerCase().includes(searchTerm.toLowerCase()) ? node : null
      }

      const filteredChildren = node.children
        ?.map(child => filterTree(child))
        .filter(child => child !== null) as FileNode[]

      if (filteredChildren.length > 0) {
        return {
          ...node,
          children: filteredChildren,
          expanded: true // 検索時は展開
        }
      }

      return null
    }

    return filterTree(fileTree) || fileTree
  }, [fileTree, searchTerm])

  // フォルダ展開/折りたたみ
  const toggleFolder = useCallback((folderPath: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev)
      if (newSet.has(folderPath)) {
        newSet.delete(folderPath)
      } else {
        newSet.add(folderPath)
      }
      return newSet
    })
  }, [])

  // ファイルアイコン取得
  const getFileIcon = useCallback((filename: string, language: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase()
    
    const iconMap: Record<string, string> = {
      // TypeScript/JavaScript
      'ts': '🟦',
      'tsx': '⚛️',
      'js': '🟨',
      'jsx': '⚛️',
      // Styles
      'css': '🎨',
      'scss': '🎨',
      'sass': '🎨',
      'less': '🎨',
      // Config
      'json': '📋',
      'xml': '📋',
      'yaml': '📋',
      'yml': '📋',
      'toml': '📋',
      // Web
      'html': '🌐',
      'htm': '🌐',
      'md': '📝',
      'txt': '📄',
      // Images
      'png': '🖼️',
      'jpg': '🖼️',
      'jpeg': '🖼️',
      'gif': '🖼️',
      'svg': '🖼️',
    }

    return iconMap[ext || ''] || '📄'
  }, [])

  // フォルダアイコン取得
  const getFolderIcon = useCallback((expanded: boolean): string => {
    return expanded ? '📂' : '📁'
  }, [])

  // ファイルサイズ計算
  const getFileSize = useCallback((content: string): string => {
    const bytes = new Blob([content]).size
    if (bytes < 1024) return `${bytes}B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  }, [])

  // ダウンロード処理
  const handleDownload = useCallback(() => {
    onDownload(files)
  }, [onDownload, files])

  // ファイルノードレンダリング
  const renderFileNode = useCallback((node: FileNode, depth: number = 0): React.ReactElement => {
    const isSelected = selectedFile && node.file && selectedFile.filename === node.file.filename
    const isExpanded = expandedFolders.has(node.path)
    const isHidden = searchTerm && !node.name.toLowerCase().includes(searchTerm.toLowerCase()) && node.type === 'file'

    if (node.type === 'folder' && node.children?.length === 0) {
      return <React.Fragment key={node.path} />
    }

    return (
      <div key={node.path} className={`file-tree-node ${isHidden ? 'hidden' : ''}`}>
        {node.type === 'folder' ? (
          <div>
            <div
              className="flex items-center py-1 px-2 cursor-pointer hover:bg-gray-100 rounded"
              style={{ paddingLeft: `${depth * 16 + 8}px` }}
              onClick={() => toggleFolder(node.path)}
            >
              <span className="mr-2 text-sm">
                {getFolderIcon(isExpanded)}
              </span>
              <span className="text-sm font-medium text-gray-700">
                {node.name}
              </span>
            </div>
            {isExpanded && node.children && (
              <div>
                {node.children.map(child => renderFileNode(child, depth + 1))}
              </div>
            )}
          </div>
        ) : (
          <div
            className={`file-item flex items-center py-1 px-2 cursor-pointer hover:bg-gray-100 rounded transition-colors ${
              isSelected ? 'selected bg-blue-100 border-l-4 border-blue-500' : ''
            }`}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => node.file && onFileSelect(node.file)}
          >
            <span className="mr-2 text-sm">
              {getFileIcon(node.name, node.file?.language || '')}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-900 truncate">
                  {node.name}
                </span>
                {showDetails && node.file && (
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <span className="px-2 py-0.5 bg-gray-100 rounded">
                      {node.file.language}
                    </span>
                    <span>{getFileSize(node.file.content)}</span>
                  </div>
                )}
              </div>
              {showDetails && node.file?.description && (
                <p className="text-xs text-gray-500 truncate mt-0.5">
                  {node.file.description}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }, [
    selectedFile,
    expandedFolders,
    searchTerm,
    showDetails,
    onFileSelect,
    toggleFolder,
    getFolderIcon,
    getFileIcon,
    getFileSize
  ])

  return (
    <div className={`bg-white border border-gray-200 rounded-lg ${className}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">
          ファイル ({files.length})
        </h3>
        <button
          type="button"
          onClick={handleDownload}
          className="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          ダウンロード
        </button>
      </div>

      {/* 検索バー */}
      {searchable && (
        <div className="p-4 border-b border-gray-200">
          <input
            type="text"
            placeholder="ファイルを検索..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      )}

      {/* ファイルツリー */}
      <div className="max-h-96 overflow-y-auto">
        {files.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-2">📁</div>
            <p>ファイルがありません</p>
          </div>
        ) : (
          <div className="p-2">
            {filteredTree.children?.map(child => renderFileNode(child))}
          </div>
        )}
      </div>

      {/* フッター統計 */}
      {files.length > 0 && (
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
          <div className="flex justify-between">
            <span>
              {files.filter(f => f.language === 'typescript').length} TypeScript, {' '}
              {files.filter(f => f.language === 'css').length} CSS, {' '}
              {files.filter(f => f.language === 'json').length} JSON
            </span>
            <span>
              総サイズ: {getFileSize(files.map(f => f.content).join(''))}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}