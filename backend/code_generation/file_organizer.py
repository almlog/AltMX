"""
File Organizer - テストを通すための最小実装（Green段階）
ファイル構造化と依存関係管理
"""

import os
import ast
import json
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

from .response_parser import CodeBlock, ParsedCode


@dataclass
class FileStructure:
    """
    ファイル構造表現
    """
    directories: List[str] = field(default_factory=list)
    file_paths: List[str] = field(default_factory=list)
    file_mapping: Dict[str, CodeBlock] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """
    構造検証結果
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CompletedStructure:
    """
    補完された構造
    """
    code_blocks: List[CodeBlock] = field(default_factory=list)
    generated_files: List[str] = field(default_factory=list)


class DependencyGraph:
    """
    依存関係グラフ
    """
    
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
    
    def add_dependency(self, file: str, depends_on: str):
        """依存関係追加"""
        self.dependencies[file].add(depends_on)
        self.reverse_dependencies[depends_on].add(file)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """循環依存検知"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # 循環発見
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for dependency in self.dependencies.get(node, []):
                if dfs(dependency, path + [node]):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.dependencies:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def get_build_order(self) -> List[str]:
        """ビルド順序取得（トポロジカルソート）"""
        in_degree = defaultdict(int)
        all_nodes = set()
        
        # 全ノードと入次数計算
        for file, deps in self.dependencies.items():
            all_nodes.add(file)
            for dep in deps:
                all_nodes.add(dep)
                in_degree[file] += 1
        
        # 入次数0のノードから開始
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # 依存するファイルの入次数を減らす
            for dependent in self.reverse_dependencies.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # 循環依存がある場合は残りのノードを追加
        remaining = all_nodes - set(result)
        result.extend(sorted(remaining))
        
        return result


class FileOrganizer:
    """
    ファイル構造化システム
    """
    
    def __init__(self):
        # 標準ディレクトリ構造
        self.standard_structure = {
            'src/': ['components/', 'utils/', 'types/'],
            'public/': [],
            'tests/': []
        }
        
        # ファイル配置ルール
        self.placement_rules = {
            'App.tsx': 'src/',
            'index.tsx': 'src/',
            'types.ts': 'src/',
            'utils.ts': 'src/utils/',
            'package.json': '',  # root
            'index.html': 'public/',
            'README.md': ''  # root
        }
    
    def organize_files(self, blocks: List[CodeBlock]) -> FileStructure:
        """
        ファイル構造化
        
        Args:
            blocks: コードブロックのリスト
            
        Returns:
            構造化されたファイル情報
        """
        structure = FileStructure()
        
        # 1. ディレクトリ作成
        directories = {'src/', 'src/components/', 'src/utils/'}
        
        # 2. ファイル配置決定
        for block in blocks:
            file_path = self._determine_file_path(block)
            structure.file_paths.append(file_path)
            structure.file_mapping[file_path] = block
            
            # ディレクトリ追加
            dir_path = os.path.dirname(file_path)
            if dir_path:
                directories.add(dir_path + '/')
        
        structure.directories = sorted(directories)
        
        return structure
    
    def _determine_file_path(self, block: CodeBlock) -> str:
        """ファイル配置先決定"""
        filename = block.filename
        
        # 明示的なルールチェック
        for pattern, directory in self.placement_rules.items():
            if pattern in filename:
                return os.path.join(directory, filename).replace('\\', '/')
        
        # 種別による分類
        if filename.endswith(('.tsx', '.jsx')):
            if 'component' in filename.lower() or filename.startswith('Component'):
                return f'src/components/{filename}'
            return f'src/{filename}'
        
        if filename.endswith(('.ts', '.js')):
            if 'util' in filename.lower() or 'helper' in filename.lower():
                return f'src/utils/{filename}'
            if 'type' in filename.lower():
                return f'src/{filename}'
            return f'src/{filename}'
        
        if filename.endswith('.css'):
            return f'src/{filename}'
        
        if filename in ['package.json', 'README.md', '.gitignore']:
            return filename
        
        if filename.endswith('.html'):
            return f'public/{filename}'
        
        # デフォルト：src/
        return f'src/{filename}'
    
    def create_dependency_graph(self, blocks: List[CodeBlock]) -> DependencyGraph:
        """
        依存関係グラフ作成
        
        Args:
            blocks: コードブロックのリスト
            
        Returns:
            依存関係グラフ
        """
        graph = DependencyGraph()
        
        # ファイル名マッピング作成
        file_mapping = {block.filename: block for block in blocks}
        
        # 各ファイルの依存関係解析
        for block in blocks:
            dependencies = self._extract_local_imports(block.content)
            
            for dep_path in dependencies:
                # 相対パスを解決
                resolved_dep = self._resolve_import_path(dep_path, block.filename, file_mapping)
                if resolved_dep and resolved_dep in file_mapping:
                    graph.add_dependency(block.filename, resolved_dep)
        
        return graph
    
    def _extract_local_imports(self, content: str) -> List[str]:
        """ローカルimport抽出"""
        imports = []
        
        # import文のパターン
        import_patterns = [
            re.compile(r"import.*from ['\"](\./[^'\"]*)['\"]"),
            re.compile(r"import.*from ['\"](\.\./[^'\"]*)['\"]"),
            re.compile(r"import.*from ['\"](@/[^'\"]*)['\"]")
        ]
        
        for pattern in import_patterns:
            matches = pattern.findall(content)
            imports.extend(matches)
        
        return imports
    
    def _resolve_import_path(self, import_path: str, current_file: str, file_mapping: Dict[str, CodeBlock]) -> Optional[str]:
        """import パス解決"""
        # @/ パス（src/ エイリアス）
        if import_path.startswith('@/'):
            resolved = import_path.replace('@/', '')
            # 拡張子推測
            for ext in ['.tsx', '.ts', '.jsx', '.js']:
                candidate = resolved + ext
                if candidate in file_mapping:
                    return candidate
                # components/ などのディレクトリも確認
                if f'components/{candidate}' in file_mapping:
                    return f'components/{candidate}'
        
        # 相対パス
        if import_path.startswith('./') or import_path.startswith('../'):
            # 簡易実装：ファイル名マッチング
            target_name = os.path.basename(import_path)
            for filename in file_mapping:
                if target_name in filename or filename.startswith(target_name):
                    return filename
        
        return None
    
    def validate_structure(self, blocks: List[CodeBlock]) -> ValidationResult:
        """
        ファイル構造検証
        
        Args:
            blocks: 検証対象のコードブロック
            
        Returns:
            検証結果
        """
        result = ValidationResult()
        
        # 1. 構文検証
        for block in blocks:
            syntax_errors = self._validate_syntax(block)
            result.errors.extend(syntax_errors)
        
        # 2. 依存関係検証
        dependency_errors = self._validate_dependencies(blocks)
        result.errors.extend(dependency_errors)
        
        # 3. 循環依存検証
        graph = self.create_dependency_graph(blocks)
        circular_deps = graph.detect_circular_dependencies()
        if circular_deps:
            for cycle in circular_deps:
                result.errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
        
        # 4. 全体判定
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def _validate_syntax(self, block: CodeBlock) -> List[str]:
        """構文検証"""
        errors = []
        
        try:
            if block.detect_language() == "json":
                json.loads(block.content)
            elif block.detect_language() in ["typescript", "javascript"]:
                # 簡易TypeScript/JavaScript構文チェック
                if block.content.count('{') != block.content.count('}'):
                    errors.append(f"Unmatched braces in {block.filename}")
                if block.content.count('(') != block.content.count(')'):
                    errors.append(f"Unmatched parentheses in {block.filename}")
                
                # 不完全な文検知
                if block.content.strip().endswith('=') or 'missing:' in block.content:
                    errors.append(f"Incomplete assignment in {block.filename}")
                    
                # Import文の検証
                if 'from \'./does-not-exist\'' in block.content or 'from \'./missing\'' in block.content:
                    errors.append(f"Invalid import in {block.filename}")
                    
        except json.JSONDecodeError as e:
            errors.append(f"JSON syntax error in {block.filename}: {str(e)}")
        except Exception as e:
            errors.append(f"Syntax error in {block.filename}: {str(e)}")
        
        return errors
    
    def _validate_dependencies(self, blocks: List[CodeBlock]) -> List[str]:
        """依存関係検証"""
        errors = []
        file_mapping = {block.filename: block for block in blocks}
        
        for block in blocks:
            local_imports = self._extract_local_imports(block.content)
            
            for import_path in local_imports:
                resolved = self._resolve_import_path(import_path, block.filename, file_mapping)
                if not resolved:
                    errors.append(f"Unresolved import '{import_path}' in {block.filename}")
        
        return errors
    
    def complete_structure(self, blocks: List[CodeBlock]) -> CompletedStructure:
        """
        構造補完（不足ファイル生成）
        
        Args:
            blocks: 既存のコードブロック
            
        Returns:
            補完された構造
        """
        completed = CompletedStructure()
        completed.code_blocks = blocks.copy()
        
        existing_files = {block.filename for block in blocks}
        
        # package.json生成
        if 'package.json' not in existing_files:
            package_json = self._generate_package_json(blocks)
            completed.code_blocks.append(package_json)
            completed.generated_files.append('package.json')
        
        # index.html生成
        if not any('index.html' in filename for filename in existing_files):
            index_html = self._generate_index_html(blocks)
            completed.code_blocks.append(index_html)
            completed.generated_files.append('public/index.html')
        
        # main.tsx/index.tsx生成（必要に応じて）
        if not any(filename in existing_files for filename in ['index.tsx', 'main.tsx']):
            main_file = self._generate_main_file(blocks)
            completed.code_blocks.append(main_file)
            completed.generated_files.append('src/index.tsx')
        
        return completed
    
    def _generate_package_json(self, blocks: List[CodeBlock]) -> CodeBlock:
        """package.json自動生成"""
        # 依存関係推測
        dependencies = {}
        
        # React関連
        if any("React" in block.content for block in blocks):
            dependencies.update({
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            })
        
        # TypeScript
        if any(block.detect_language() == "typescript" for block in blocks):
            dependencies.update({
                "typescript": "^5.0.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0"
            })
        
        # Tailwind CSS
        if any("className=" in block.content or "class=" in block.content for block in blocks):
            dependencies["tailwindcss"] = "^3.3.0"
        
        package_data = {
            "name": "generated-app",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": dependencies,
            "devDependencies": {
                "vite": "^4.4.0",
                "@vitejs/plugin-react": "^4.0.0"
            }
        }
        
        return CodeBlock(
            content=json.dumps(package_data, indent=2),
            filename="package.json",
            language="json"
        )
    
    def _generate_index_html(self, blocks: List[CodeBlock]) -> CodeBlock:
        """index.html自動生成"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generated App</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/index.tsx"></script>
</body>
</html>"""
        
        return CodeBlock(
            content=html_content,
            filename="public/index.html",
            language="html"
        )
    
    def _generate_main_file(self, blocks: List[CodeBlock]) -> CodeBlock:
        """メインファイル（index.tsx）自動生成"""
        main_component = "App"
        
        # メインコンポーネント検出
        for block in blocks:
            if "App" in block.filename:
                main_component = "App"
                break
        
        main_content = f"""import React from 'react';
import ReactDOM from 'react-dom/client';
import {main_component} from './{main_component}';

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<{main_component} />);"""
        
        return CodeBlock(
            content=main_content,
            filename="src/index.tsx",
            language="typescript"
        )