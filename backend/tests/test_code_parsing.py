"""
Test suite for Code Parsing System - TDD実装
AI生成レスポンスの解析とファイル構造化のテスト
"""

import pytest
from unittest.mock import Mock, patch
import ast
import re
from code_generation.response_parser import ResponseParser, CodeBlock, ParsedCode
from code_generation.file_organizer import FileOrganizer, FileStructure, DependencyGraph


class TestCodeBlock:
    """CodeBlockクラスのテスト"""
    
    def test_code_block_creation(self):
        """CodeBlock作成テスト"""
        block = CodeBlock(
            language="typescript",
            content="const hello = 'world';",
            filename="hello.ts",
            description="Simple constant declaration"
        )
        
        assert block.language == "typescript"
        assert block.content == "const hello = 'world';"
        assert block.filename == "hello.ts"
        assert block.description == "Simple constant declaration"
    
    def test_code_block_auto_detect_language(self):
        """言語自動判定テスト"""
        # TypeScript/JSX判定
        tsx_content = "import React from 'react';\nconst Component = () => <div>Hello</div>;"
        block = CodeBlock(content=tsx_content, filename="Component.tsx")
        
        assert block.detect_language() == "typescript"
        assert "import React" in block.content
        assert "jsx_syntax" in block.get_features() or "typescript" in block.get_features()
    
    def test_code_block_get_features(self):
        """コードブロック特徴抽出テスト"""
        react_content = """
        import React, { useState } from 'react';
        import { Button } from '@/components/ui/button';
        
        const MyComponent = () => {
          const [count, setCount] = useState(0);
          return <Button onClick={() => setCount(c => c + 1)}>{count}</Button>;
        };
        
        export default MyComponent;
        """
        
        block = CodeBlock(content=react_content, filename="MyComponent.tsx")
        features = block.get_features()
        
        assert "react_hooks" in features  # useState使用
        assert "react_imports" in features  # React import
        assert "jsx_syntax" in features  # JSX記法
        assert "typescript" in features  # TypeScript
        assert "tailwind" in features or "component_imports" in features  # UIコンポーネント


class TestParsedCode:
    """ParsedCodeクラスのテスト"""
    
    def test_parsed_code_creation(self):
        """ParsedCode作成テスト"""
        blocks = [
            CodeBlock(language="typescript", content="const a = 1;", filename="app.tsx"),
            CodeBlock(language="css", content=".class { color: red; }", filename="styles.css")
        ]
        
        parsed = ParsedCode(
            code_blocks=blocks,
            main_component="app.tsx",
            dependencies=["react", "typescript"],
            features=["react_hooks", "typescript"]
        )
        
        assert len(parsed.code_blocks) == 2
        assert parsed.main_component == "app.tsx"
        assert "react" in parsed.dependencies
        assert "typescript" in parsed.dependencies
        assert "react_hooks" in parsed.features
    
    def test_parsed_code_get_files_by_type(self):
        """ファイル種別フィルタリングテスト"""
        blocks = [
            CodeBlock(language="typescript", content="const a = 1;", filename="App.tsx"),
            CodeBlock(language="typescript", content="interface Props {}", filename="types.ts"),
            CodeBlock(language="css", content=".red { color: red; }", filename="app.css"),
            CodeBlock(language="json", content='{"name": "test"}', filename="package.json")
        ]
        
        parsed = ParsedCode(code_blocks=blocks)
        
        ts_files = parsed.get_files_by_type("typescript")
        assert len(ts_files) == 2
        assert any(f.filename == "App.tsx" for f in ts_files)
        assert any(f.filename == "types.ts" for f in ts_files)
        
        css_files = parsed.get_files_by_type("css")
        assert len(css_files) == 1
        assert css_files[0].filename == "app.css"


class TestResponseParser:
    """ResponseParserクラスのテスト"""
    
    @pytest.fixture
    def parser(self):
        """テスト用Parser"""
        return ResponseParser()
    
    def test_extract_code_blocks_markdown(self, parser):
        """Markdownコードブロック抽出テスト"""
        ai_response = """
        Here's a React component:
        
        ```tsx
        // App.tsx
        import React from 'react';
        
        const App = () => {
          return <div className="min-h-screen">Hello World</div>;
        };
        
        export default App;
        ```
        
        And here's the CSS:
        
        ```css
        /* app.css */
        .min-h-screen {
          min-height: 100vh;
        }
        ```
        """
        
        blocks = parser.extract_code_blocks(ai_response)
        
        assert len(blocks) == 2
        
        # TSXブロック確認
        tsx_block = blocks[0]
        assert tsx_block.language == "tsx"
        assert "import React" in tsx_block.content
        assert "App.tsx" in tsx_block.content or tsx_block.filename == "App.tsx"
        
        # CSSブロック確認
        css_block = blocks[1]
        assert css_block.language == "css"
        assert "min-h-screen" in css_block.content
        assert "app.css" in css_block.content or css_block.filename == "app.css"
    
    def test_extract_code_blocks_with_filenames(self, parser):
        """ファイル名付きコードブロック抽出テスト"""
        ai_response = """
        Here are the files:
        
        **components/Button.tsx**
        ```typescript
        import React from 'react';
        interface ButtonProps {
          children: React.ReactNode;
          onClick: () => void;
        }
        
        const Button = ({ children, onClick }: ButtonProps) => (
          <button onClick={onClick} className="btn">{children}</button>
        );
        export default Button;
        ```
        
        **utils/helpers.ts**
        ```typescript
        export const formatDate = (date: Date): string => {
          return date.toISOString().split('T')[0];
        };
        ```
        """
        
        blocks = parser.extract_code_blocks(ai_response)
        
        assert len(blocks) == 2
        assert blocks[0].filename == "components/Button.tsx"
        assert blocks[1].filename == "utils/helpers.ts"
        assert "ButtonProps" in blocks[0].content
        assert "formatDate" in blocks[1].content
    
    def test_detect_main_component(self, parser):
        """メインコンポーネント判定テスト"""
        blocks = [
            CodeBlock(content="export const Header = () => <header>Header</header>;", filename="Header.tsx"),
            CodeBlock(content="import React from 'react';\nimport Header from './Header';\n\nfunction App() { return <div><Header /></div>; }\nexport default App;", filename="App.tsx"),
            CodeBlock(content="export interface User { id: number; }", filename="types.ts")
        ]
        
        main_component = parser.detect_main_component(blocks)
        assert main_component == "App.tsx"
    
    def test_detect_dependencies(self, parser):
        """依存関係検出テスト"""
        blocks = [
            CodeBlock(content="import React, { useState, useEffect } from 'react';\nimport axios from 'axios';", filename="App.tsx"),
            CodeBlock(content="import { clsx } from 'clsx';\nimport { twMerge } from 'tailwind-merge';", filename="utils.ts")
        ]
        
        dependencies = parser.detect_dependencies(blocks)
        
        assert "react" in dependencies
        assert "axios" in dependencies
        assert "clsx" in dependencies
        assert "tailwind-merge" in dependencies
    
    def test_detect_features(self, parser):
        """機能特徴検出テスト"""
        blocks = [
            CodeBlock(content="const [state, setState] = useState(0);\nuse useEffect(() => {}, []);", filename="hooks.tsx"),
            CodeBlock(content="<form onSubmit={handleSubmit}><input type='email' required /></form>", filename="form.tsx"),
            CodeBlock(content="className='grid grid-cols-2 gap-4 p-6'", filename="layout.tsx")
        ]
        
        features = parser.detect_features(blocks)
        
        assert "react_hooks" in features
        assert "form_validation" in features
        assert "tailwind_css" in features
        assert "responsive_design" in features
    
    def test_parse_response_full_flow(self, parser):
        """レスポンス解析フルフローテスト"""
        ai_response = """
        Here's a complete React application:
        
        ```tsx
        // App.tsx
        import React, { useState } from 'react';
        import './App.css';
        
        const App = () => {
          const [count, setCount] = useState(0);
          
          return (
            <div className="container mx-auto p-4">
              <h1 className="text-3xl font-bold">Counter: {count}</h1>
              <button 
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                onClick={() => setCount(c => c + 1)}
              >
                Increment
              </button>
            </div>
          );
        };
        
        export default App;
        ```
        
        ```css
        /* App.css */
        .container {
          max-width: 1200px;
        }
        
        @media (max-width: 768px) {
          .container {
            padding: 1rem;
          }
        }
        ```
        
        ```json
        {
          "name": "counter-app",
          "version": "1.0.0",
          "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
          }
        }
        ```
        """
        
        parsed = parser.parse_response(ai_response)
        
        # 基本構造確認
        assert len(parsed.code_blocks) == 3
        assert parsed.main_component == "App.tsx"
        
        # 依存関係確認
        assert "react" in parsed.dependencies
        assert "react-dom" in parsed.dependencies
        
        # 機能確認
        assert "react_hooks" in parsed.features
        assert "tailwind_css" in parsed.features
        assert "responsive_design" in parsed.features


class TestFileOrganizer:
    """FileOrganizerクラスのテスト"""
    
    @pytest.fixture
    def organizer(self):
        """テスト用FileOrganizer"""
        return FileOrganizer()
    
    def test_organize_files_structure(self, organizer):
        """ファイル構造化テスト"""
        blocks = [
            CodeBlock(content="import React from 'react';", filename="App.tsx"),
            CodeBlock(content="export interface User {}", filename="types.ts"),
            CodeBlock(content=".btn { padding: 8px; }", filename="components/Button.css"),
            CodeBlock(content="export const Button = () => {}", filename="components/Button.tsx"),
            CodeBlock(content='{"name": "test"}', filename="package.json")
        ]
        
        structure = organizer.organize_files(blocks)
        
        # ディレクトリ構造確認
        assert "src/" in structure.directories
        assert "src/components/" in structure.directories
        
        # ファイル配置確認
        assert "src/App.tsx" in structure.file_paths
        assert "src/types.ts" in structure.file_paths
        assert "src/components/Button.tsx" in structure.file_paths
        assert "src/components/Button.css" in structure.file_paths
        assert "package.json" in structure.file_paths  # ルート配置
    
    def test_create_dependency_graph(self, organizer):
        """依存関係グラフ作成テスト"""
        blocks = [
            CodeBlock(content="import { Button } from './components/Button';\nimport { User } from './types';", filename="App.tsx"),
            CodeBlock(content="export const Button = () => {};", filename="components/Button.tsx"),
            CodeBlock(content="export interface User { id: number; }", filename="types.ts")
        ]
        
        graph = organizer.create_dependency_graph(blocks)
        
        # 依存関係確認
        assert "App.tsx" in graph.dependencies
        assert "Button.tsx" in graph.dependencies["App.tsx"]
        assert "types.ts" in graph.dependencies["App.tsx"]
        
        # 順序確認（依存される側が先）
        order = graph.get_build_order()
        assert order.index("types.ts") < order.index("App.tsx")
        assert order.index("Button.tsx") < order.index("App.tsx")
    
    def test_validate_file_structure(self, organizer):
        """ファイル構造検証テスト"""
        valid_blocks = [
            CodeBlock(content="import React from 'react';\nexport default App;", filename="App.tsx"),
            CodeBlock(content="export const utils = {};", filename="utils.ts")
        ]
        
        invalid_blocks = [
            CodeBlock(content="import { NonExistent } from './missing';", filename="App.tsx"),  # 存在しないimport
            CodeBlock(content="const incomplete = ", filename="invalid.ts")  # 構文エラー
        ]
        
        # 有効な構造
        valid_result = organizer.validate_structure(valid_blocks)
        assert valid_result.is_valid is True
        assert len(valid_result.errors) == 0
        
        # 無効な構造
        invalid_result = organizer.validate_structure(invalid_blocks)
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) > 0
    
    def test_generate_missing_files(self, organizer):
        """不足ファイル生成テスト"""
        blocks = [
            CodeBlock(content="import React from 'react';\nimport './App.css';\nconst App = () => <div>Hello</div>;", filename="App.tsx")
        ]
        
        # package.jsonとindex.htmlが自動生成されることを期待
        completed_structure = organizer.complete_structure(blocks)
        
        # 生成されたファイル確認
        file_names = [block.filename for block in completed_structure.code_blocks]
        assert "package.json" in file_names
        assert "index.html" in file_names or "public/index.html" in file_names
        
        # package.json内容確認
        package_json_block = next(block for block in completed_structure.code_blocks if "package.json" in block.filename)
        package_content = package_json_block.content
        assert "react" in package_content
        assert "react-dom" in package_content


class TestDependencyGraph:
    """DependencyGraphクラスのテスト"""
    
    def test_dependency_graph_creation(self):
        """依存関係グラフ作成テスト"""
        graph = DependencyGraph()
        
        graph.add_dependency("App.tsx", "Button.tsx")
        graph.add_dependency("App.tsx", "utils.ts")
        graph.add_dependency("Button.tsx", "types.ts")
        
        assert "App.tsx" in graph.dependencies
        assert "Button.tsx" in graph.dependencies["App.tsx"]
        assert "utils.ts" in graph.dependencies["App.tsx"]
        assert "types.ts" in graph.dependencies["Button.tsx"]
    
    def test_circular_dependency_detection(self):
        """循環依存検知テスト"""
        graph = DependencyGraph()
        
        graph.add_dependency("A.tsx", "B.tsx")
        graph.add_dependency("B.tsx", "C.tsx")
        graph.add_dependency("C.tsx", "A.tsx")  # 循環依存
        
        circular_deps = graph.detect_circular_dependencies()
        assert len(circular_deps) > 0
        assert any("A.tsx" in cycle for cycle in circular_deps)
    
    def test_build_order_generation(self):
        """ビルド順序生成テスト"""
        graph = DependencyGraph()
        
        # 依存関係: App -> Button -> types, App -> utils
        graph.add_dependency("App.tsx", "Button.tsx")
        graph.add_dependency("App.tsx", "utils.ts")
        graph.add_dependency("Button.tsx", "types.ts")
        
        build_order = graph.get_build_order()
        
        # 依存される順序確認
        assert build_order.index("types.ts") < build_order.index("Button.tsx")
        assert build_order.index("Button.tsx") < build_order.index("App.tsx")
        assert build_order.index("utils.ts") < build_order.index("App.tsx")


# 統合テスト
class TestCodeParsingIntegration:
    """コード解析システム統合テスト"""
    
    def test_full_parsing_pipeline(self):
        """完全な解析パイプラインテスト"""
        ai_response = """
        I'll create a React todo application:
        
        ```tsx
        // App.tsx
        import React, { useState } from 'react';
        import { TodoItem } from './components/TodoItem';
        import { Todo } from './types';
        import './App.css';
        
        const App = () => {
          const [todos, setTodos] = useState<Todo[]>([]);
          const [input, setInput] = useState('');
          
          const addTodo = () => {
            if (input.trim()) {
              setTodos([...todos, { id: Date.now(), text: input, completed: false }]);
              setInput('');
            }
          };
          
          return (
            <div className="container mx-auto p-4 max-w-md">
              <h1 className="text-2xl font-bold mb-4">Todo App</h1>
              <div className="flex mb-4">
                <input
                  className="flex-1 border border-gray-300 px-3 py-2 rounded-l"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Add a todo..."
                />
                <button
                  className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600"
                  onClick={addTodo}
                >
                  Add
                </button>
              </div>
              <div>
                {todos.map(todo => (
                  <TodoItem key={todo.id} todo={todo} setTodos={setTodos} />
                ))}
              </div>
            </div>
          );
        };
        
        export default App;
        ```
        
        ```tsx
        // components/TodoItem.tsx
        import React from 'react';
        import { Todo } from '../types';
        
        interface TodoItemProps {
          todo: Todo;
          setTodos: React.Dispatch<React.SetStateAction<Todo[]>>;
        }
        
        export const TodoItem = ({ todo, setTodos }: TodoItemProps) => {
          const toggleComplete = () => {
            setTodos(prev => prev.map(t => 
              t.id === todo.id ? { ...t, completed: !t.completed } : t
            ));
          };
          
          const deleteTodo = () => {
            setTodos(prev => prev.filter(t => t.id !== todo.id));
          };
          
          return (
            <div className="flex items-center p-2 border-b">
              <input
                type="checkbox"
                checked={todo.completed}
                onChange={toggleComplete}
                className="mr-3"
              />
              <span className={`flex-1 ${todo.completed ? 'line-through text-gray-500' : ''}`}>
                {todo.text}
              </span>
              <button
                onClick={deleteTodo}
                className="text-red-500 hover:text-red-700 px-2"
              >
                Delete
              </button>
            </div>
          );
        };
        ```
        
        ```typescript
        // types.ts
        export interface Todo {
          id: number;
          text: string;
          completed: boolean;
        }
        ```
        """
        
        # パイプライン実行
        parser = ResponseParser()
        organizer = FileOrganizer()
        
        # 1. レスポンス解析
        parsed = parser.parse_response(ai_response)
        
        # 2. ファイル構造化
        structure = organizer.organize_files(parsed.code_blocks)
        
        # 3. 依存関係グラフ作成
        graph = organizer.create_dependency_graph(parsed.code_blocks)
        
        # 4. 構造検証
        validation = organizer.validate_structure(parsed.code_blocks)
        
        # 結果確認
        assert len(parsed.code_blocks) == 3
        assert parsed.main_component == "App.tsx"
        assert "react" in parsed.dependencies
        assert "react_hooks" in parsed.features
        assert "tailwind_css" in parsed.features
        
        # ファイル構造確認
        assert "src/App.tsx" in structure.file_paths
        assert "src/components/TodoItem.tsx" in structure.file_paths
        assert "src/types.ts" in structure.file_paths
        
        # 依存関係確認
        build_order = graph.get_build_order()
        assert build_order.index("types.ts") < build_order.index("App.tsx")
        assert build_order.index("TodoItem.tsx") < build_order.index("App.tsx")
        
        # 検証結果確認
        assert validation.is_valid is True
        assert len(validation.errors) == 0
    
    def test_error_handling_robustness(self):
        """エラーハンドリング堅牢性テスト"""
        parser = ResponseParser()
        organizer = FileOrganizer()
        
        # 不完全なAI応答
        malformed_response = """
        Here's some code:
        
        ```typescript
        // 構文エラーを含むコード
        const broken = {
          missing: 
        };
        
        import { NonExistent } from './does-not-exist';
        ```
        
        ```tsx
        // ファイル名なし、不完全なReactコード
        const Component = () => {
          return <div>Missing imports</div>
        }
        """
        
        # エラーが発生しても処理が継続することを確認
        parsed = parser.parse_response(malformed_response)
        structure = organizer.organize_files(parsed.code_blocks)
        validation = organizer.validate_structure(parsed.code_blocks)
        
        # エラーが適切に捕捉されていることを確認
        assert validation.is_valid is False
        assert len(validation.errors) > 0
        assert any("syntax" in error.lower() or "import" in error.lower() for error in validation.errors)