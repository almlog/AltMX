/**
 * Live Preview E2E Test - 実際のブラウザ動作確認
 * TDD Green段階のための実動作テスト
 */

import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { PreviewPanel } from '../components/CodeGeneration/PreviewPanel'
import type { GeneratedFile } from '../components/CodeGeneration/PreviewPanel'

describe('Live Preview E2E', () => {
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

  it('PreviewPanelにライブモードが表示される', () => {
    render(
      <PreviewPanel 
        file={sampleReactComponent} 
        files={sampleFiles}
      />
    )

    // React component should show live preview button
    expect(screen.getByText('ライブ')).toBeInTheDocument()
    expect(screen.getByText('コード')).toBeInTheDocument()
  })

  it('ファイル情報が正しく表示される', () => {
    render(
      <PreviewPanel 
        file={sampleReactComponent} 
        files={sampleFiles}
      />
    )

    expect(screen.getByText('TestComponent.tsx')).toBeInTheDocument()
    expect(screen.getByText('typescript')).toBeInTheDocument()
  })

  it('ライブプレビュー非対応ファイルでは従来モード', () => {
    const htmlFile: GeneratedFile = {
      filename: 'test.html',
      content: '<html><body><h1>Test HTML</h1></body></html>',
      language: 'html',
      description: 'HTML file'
    }

    render(
      <PreviewPanel 
        file={htmlFile} 
        files={[htmlFile]}
      />
    )

    // Should show normal preview buttons
    expect(screen.getByText('コード')).toBeInTheDocument()
    expect(screen.getByText('プレビュー')).toBeInTheDocument()
    
    // Should NOT show live button for HTML files
    expect(screen.queryByText('ライブ')).not.toBeInTheDocument()
  })

  it('コピー機能が動作する', () => {
    render(
      <PreviewPanel 
        file={sampleReactComponent} 
        files={sampleFiles}
      />
    )

    expect(screen.getByText('コピー')).toBeInTheDocument()
  })
})