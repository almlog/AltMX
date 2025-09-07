/**
 * Live Preview Engine Tests - TDD Red-Green-Refactor
 * ライブプレビューエンジンの動作テスト
 */

import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { LivePreviewEngine } from '../components/CodeGeneration/LivePreviewEngine'
import type { GeneratedFile } from '../components/CodeGeneration/PreviewPanel'

// Mock the browser APIs
Object.defineProperty(window, 'ts', {
  writable: true,
  value: undefined
});

describe('LivePreviewEngine', () => {
  const mockOnError = vi.fn()
  const mockOnCompileSuccess = vi.fn()

  const sampleReactComponent: GeneratedFile = {
    filename: 'TestComponent.tsx',
    content: `import React from 'react';

const TestComponent = () => {
  return (
    <div data-testid="generated-component">
      <h1>Generated Component Test</h1>
      <p>This is a test component</p>
    </div>
  );
};

export default TestComponent;`,
    language: 'typescript',
    description: 'Test React component'
  }

  const sampleFiles: GeneratedFile[] = [sampleReactComponent]

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset TypeScript compiler mock
    window.ts = undefined
  })

  it('コンポーネントが正しく表示される', () => {
    render(
      <LivePreviewEngine
        files={sampleFiles}
        selectedFile={sampleReactComponent}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    expect(screen.getByText('ライブプレビュー - TestComponent.tsx')).toBeInTheDocument()
  })

  it('TypeScriptコンパイラーが初期化される', async () => {
    render(
      <LivePreviewEngine
        files={sampleFiles}
        selectedFile={sampleReactComponent}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    // TypeScript compiler script should be added to the head
    await waitFor(() => {
      const scripts = document.querySelectorAll('script[src*="typescript"]')
      expect(scripts.length).toBeGreaterThan(0)
    })
  })

  it('初期コンパイル状態が表示される', async () => {
    const brokenComponent: GeneratedFile = {
      filename: 'BrokenComponent.tsx',
      content: `import React from 'react';

const BrokenComponent = () => {
  return (
    <div>
      <h1>Broken Component</h1>
      <p>This component has syntax error
    </div>
  );
};`,
      language: 'typescript',
      description: 'Broken component for testing'
    }

    render(
      <LivePreviewEngine
        files={[brokenComponent]}
        selectedFile={brokenComponent}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    // Should show preview header
    expect(screen.getByText('ライブプレビュー - BrokenComponent.tsx')).toBeInTheDocument()
  })

  it('非TypeScriptファイルでは従来通りの表示', () => {
    const htmlFile: GeneratedFile = {
      filename: 'test.html',
      content: '<html><body><h1>Test HTML</h1></body></html>',
      language: 'html',
      description: 'HTML file'
    }

    render(
      <LivePreviewEngine
        files={[htmlFile]}
        selectedFile={htmlFile}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    expect(screen.getByText('ライブプレビュー - test.html')).toBeInTheDocument()
  })

  it('ファイル未選択時の状態', () => {
    render(
      <LivePreviewEngine
        files={sampleFiles}
        selectedFile={null}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    expect(screen.getByText('ファイル未選択')).toBeInTheDocument()
  })

  it('ホットリロード機能が動作する', async () => {
    vi.useFakeTimers()
    
    const { rerender } = render(
      <LivePreviewEngine
        files={sampleFiles}
        selectedFile={sampleReactComponent}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    const iframe = screen.getByTitle('live-preview') as HTMLIFrameElement
    expect(iframe).toBeInTheDocument()

    // Update the component
    const updatedComponent: GeneratedFile = {
      ...sampleReactComponent,
      content: sampleReactComponent.content.replace('Generated Component Test', 'Updated Component Test')
    }

    rerender(
      <LivePreviewEngine
        files={[updatedComponent]}
        selectedFile={updatedComponent}
        onError={mockOnError}
        onCompileSuccess={mockOnCompileSuccess}
      />
    )

    // Fast forward timers to trigger debounced compilation
    vi.advanceTimersByTime(300)

    await waitFor(() => {
      // The iframe should be reset for recompilation
      expect(iframe.src).toEqual('about:blank')
    })
    
    vi.useRealTimers()
  })
})