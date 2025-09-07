/**
 * Live Preview Engine - Reactコンポーネントのリアルタイムプレビュー
 * TypeScript/JSXをブラウザでコンパイルして実行
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import type { FC } from 'react';
import type { GeneratedFile } from './PreviewPanel';

// TypeScript Compiler API (browser版)
declare global {
  interface Window {
    ts: any; // TypeScript compiler
  }
}

export interface LivePreviewEngineProps {
  files: GeneratedFile[];
  selectedFile?: GeneratedFile;
  onError?: (error: string) => void;
  onCompileSuccess?: () => void;
}

interface CompileError {
  message: string;
  line?: number;
  column?: number;
  file?: string;
}

export const LivePreviewEngine: FC<LivePreviewEngineProps> = ({
  files: _files,
  selectedFile,
  onError,
  onCompileSuccess
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [compileErrors, setCompileErrors] = useState<CompileError[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const compileTimeoutRef = useRef<number>();

  // TypeScript compiler初期化（CDN経由）
  useEffect(() => {
    if (!window.ts) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/typescript@5.0.0/lib/typescript.js';
      script.onload = () => {
        console.log('TypeScript compiler loaded');
      };
      document.head.appendChild(script);
    }
  }, []);

  // React/ReactDOM CDN読み込み用HTML
  const getReactRuntimeHtml = useCallback(() => {
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Live Preview</title>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    body { 
      margin: 0; 
      padding: 20px; 
      font-family: system-ui, sans-serif; 
    }
    .preview-container { 
      max-width: 800px; 
      margin: 0 auto; 
    }
    .error-display {
      background: #fee;
      border: 1px solid #fcc;
      padding: 15px;
      border-radius: 5px;
      margin: 10px 0;
      color: #c00;
    }
    .error-title {
      font-weight: bold;
      margin-bottom: 10px;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  <div id="error-boundary"></div>
  
  <script>
    // Global error handler
    window.addEventListener('error', (event) => {
      const errorDiv = document.getElementById('error-boundary');
      if (errorDiv) {
        errorDiv.innerHTML = \`
          <div class="error-display">
            <div class="error-title">実行時エラー:</div>
            <div>\${event.error ? event.error.message : event.message}</div>
            <div style="font-size: 0.9em; margin-top: 5px;">
              行: \${event.lineno || 'N/A'}, 列: \${event.colno || 'N/A'}
            </div>
          </div>
        \`;
      }
    });

    // React error boundary
    class ErrorBoundary extends React.Component {
      constructor(props) {
        super(props);
        this.state = { hasError: false };
      }

      static getDerivedStateFromError(error) {
        return { hasError: true, error };
      }

      componentDidCatch(error, errorInfo) {
        console.error('React Error Boundary:', error, errorInfo);
        const errorDiv = document.getElementById('error-boundary');
        if (errorDiv) {
          errorDiv.innerHTML = \`
            <div class="error-display">
              <div class="error-title">Reactエラー:</div>
              <div>\${error.message}</div>
            </div>
          \`;
        }
      }

      render() {
        if (this.state.hasError) {
          return React.createElement('div', { className: 'error-display' }, 
            React.createElement('div', { className: 'error-title' }, 'コンポーネントエラー'),
            React.createElement('div', null, this.state.error?.message || 'Unknown error')
          );
        }
        return this.props.children;
      }
    }

    // Render function
    function renderPreview(componentCode) {
      try {
        // Clear previous errors
        document.getElementById('error-boundary').innerHTML = '';
        
        // Transform JSX with Babel
        const transformedCode = Babel.transform(componentCode, {
          presets: ['react', 'typescript'],
          plugins: [
            ['transform-typescript', { isTSX: true, allExtensions: true }]
          ]
        }).code;

        // Create function from code
        const componentFunction = new Function('React', 'ReactDOM', transformedCode + '; return typeof GeneratedComponent !== "undefined" ? GeneratedComponent : (typeof FormComponent !== "undefined" ? FormComponent : (typeof ButtonComponent !== "undefined" ? ButtonComponent : (typeof ModalComponent !== "undefined" ? ModalComponent : null)));');
        
        const Component = componentFunction(React, ReactDOM);
        
        if (Component) {
          const root = ReactDOM.createRoot(document.getElementById('root'));
          root.render(
            React.createElement(ErrorBoundary, null,
              React.createElement('div', { className: 'preview-container' },
                React.createElement(Component, {})
              )
            )
          );
        } else {
          throw new Error('コンポーネントが見つかりません。エクスポートされたコンポーネント名を確認してください。');
        }
      } catch (error) {
        const errorDiv = document.getElementById('error-boundary');
        if (errorDiv) {
          errorDiv.innerHTML = \`
            <div class="error-display">
              <div class="error-title">コンパイルエラー:</div>
              <div>\${error.message}</div>
            </div>
          \`;
        }
      }
    }

    // Expose render function globally
    window.renderPreview = renderPreview;
  </script>
</body>
</html>`;
  }, []);

  // コンパイル・プレビュー生成
  const compileAndPreview = useCallback(async (targetFile: GeneratedFile) => {
    if (!targetFile) return;

    setIsLoading(true);
    setCompileErrors([]);

    try {
      // TypeScript/JSXファイルのみ処理
      if (targetFile.language === 'typescript' && targetFile.filename.endsWith('.tsx')) {
        const baseHtml = getReactRuntimeHtml();
        
        // コンポーネントコードを抽出・変換
        let componentCode = targetFile.content;
        
        // import文を削除（CDN版を使用するため）
        componentCode = componentCode
          .replace(/import\s+.*?\s+from\s+['"][^'"]+['"];?\s*/g, '')
          .replace(/import\s+type\s+.*?\s+from\s+['"][^'"]+['"];?\s*/g, '');
        
        // TypeScriptの型定義を削除
        componentCode = componentCode
          .replace(/:\s*FC<[^>]+>/g, '')
          .replace(/interface\s+\w+\s*{[^}]*}/g, '');

        // HTML with embedded component code
        const finalHtml = baseHtml.replace(
          '</body>',
          `
          <script>
            // Component code
            ${componentCode}
            
            // Auto-render after load
            setTimeout(() => {
              if (window.renderPreview) {
                window.renderPreview(\`${componentCode.replace(/`/g, '\\`')}\`);
              }
            }, 100);
          </script>
          </body>`
        );

        setPreviewHtml(finalHtml);
        onCompileSuccess?.();
      } else {
        // 非Reactファイルは従来通り
        setPreviewHtml(`
          <!DOCTYPE html>
          <html>
            <head>
              <title>${targetFile.filename}</title>
              <style>
                body { font-family: monospace; padding: 20px; white-space: pre-wrap; }
              </style>
            </head>
            <body>${targetFile.content}</body>
          </html>
        `);
      }
    } catch (error) {
      const compileError: CompileError = {
        message: error instanceof Error ? error.message : 'Unknown compile error',
        file: targetFile.filename
      };
      
      setCompileErrors([compileError]);
      onError?.(compileError.message);
    }

    setIsLoading(false);
  }, [getReactRuntimeHtml, onCompileSuccess, onError]);

  // Hot reload - ファイル変更時の自動再コンパイル
  useEffect(() => {
    if (selectedFile) {
      // デバウンス: 500ms後にコンパイル実行
      if (compileTimeoutRef.current) {
        clearTimeout(compileTimeoutRef.current);
      }

      compileTimeoutRef.current = window.setTimeout(() => {
        compileAndPreview(selectedFile);
      }, 300); // 300ms < 500ms requirement
    }

    return () => {
      if (compileTimeoutRef.current) {
        clearTimeout(compileTimeoutRef.current);
      }
    };
  }, [selectedFile, compileAndPreview]);

  // iframe更新
  useEffect(() => {
    if (iframeRef.current && previewHtml) {
      const iframe = iframeRef.current;
      
      // 高速更新のためdocument.writeを使用
      iframe.onload = () => {
        try {
          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
          if (iframeDoc) {
            iframeDoc.open();
            iframeDoc.write(previewHtml);
            iframeDoc.close();
          }
        } catch (error) {
          console.error('iframe update error:', error);
        }
      };
      
      // Trigger load
      iframe.src = 'about:blank';
    }
  }, [previewHtml]);

  return (
    <div className="live-preview-engine h-full flex flex-col">
      {/* エラー表示 */}
      {compileErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 p-3 mb-4 rounded">
          <h4 className="text-red-800 font-medium mb-2">コンパイルエラー</h4>
          {compileErrors.map((error, index) => (
            <div key={index} className="text-sm text-red-700">
              <div className="font-medium">{error.file}</div>
              <div>{error.message}</div>
              {error.line && (
                <div className="text-xs text-red-600">
                  行: {error.line}, 列: {error.column}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ローディング表示 */}
      {isLoading && (
        <div className="bg-blue-50 border border-blue-200 p-3 mb-4 rounded">
          <div className="flex items-center">
            <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full mr-2"></div>
            <span className="text-blue-800 text-sm">コンパイル中...</span>
          </div>
        </div>
      )}

      {/* プレビューiframe */}
      <div className="flex-1 border border-gray-300 rounded-lg overflow-hidden">
        <div className="bg-gray-100 px-3 py-2 text-sm text-gray-600 border-b border-gray-300 flex justify-between">
          <span>ライブプレビュー - {selectedFile?.filename || 'ファイル未選択'}</span>
          <span className="text-xs text-gray-500">
            {isLoading ? 'コンパイル中...' : 'リアルタイム更新'}
          </span>
        </div>
        <iframe
          ref={iframeRef}
          title="live-preview"
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin allow-forms"
        />
      </div>
    </div>
  );
};