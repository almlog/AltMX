"""
Response Parser - テストを通すための最小実装（Green段階）
AI生成レスポンスの解析とコードブロック抽出
"""

import re
import ast
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field


@dataclass
class CodeBlock:
    """
    コードブロック表現
    """
    content: str
    filename: str = ""
    language: str = ""
    description: str = ""
    
    def detect_language(self) -> str:
        """言語自動判定"""
        if self.language:
            return self.language
        
        # ファイル拡張子から判定
        if self.filename:
            if self.filename.endswith(('.tsx', '.ts')):
                return "typescript"
            elif self.filename.endswith(('.jsx', '.js')):
                return "javascript"
            elif self.filename.endswith('.css'):
                return "css"
            elif self.filename.endswith('.json'):
                return "json"
            elif self.filename.endswith('.html'):
                return "html"
        
        # コンテンツから判定
        if "import React" in self.content or "from 'react'" in self.content:
            if "interface " in self.content or ": string" in self.content:
                return "typescript"
            return "javascript"
        
        if self.content.strip().startswith('{') and '"' in self.content:
            return "json"
        
        if any(keyword in self.content for keyword in [".class", "color:", "background:", "margin:"]):
            return "css"
        
        return "typescript"  # デフォルト
    
    def get_features(self) -> Set[str]:
        """コードブロック特徴抽出"""
        features = set()
        
        # React関連
        if "import React" in self.content:
            features.add("react_imports")
        
        if any(hook in self.content for hook in ["useState", "useEffect", "useCallback", "useMemo"]):
            features.add("react_hooks")
        
        if "<" in self.content and ">" in self.content and ("return" in self.content or "=>" in self.content):
            features.add("jsx_syntax")
        
        # TypeScript関連
        if (any(ts_feature in self.content for ts_feature in ["interface ", ": string", ": number", "type ", ": React."])
            or self.filename.endswith(('.tsx', '.ts'))):
            features.add("typescript")
        
        # Tailwind CSS関連
        tailwind_patterns = ["className=", "class=", "bg-", "text-", "p-", "m-", "flex", "grid"]
        if any(pattern in self.content for pattern in tailwind_patterns):
            features.add("tailwind")
        
        # UI/Component imports
        if any(ui_import in self.content for ui_import in ["@/components", "./components", "../components"]):
            features.add("component_imports")
        
        return features


@dataclass
class ParsedCode:
    """
    解析されたコード全体
    """
    code_blocks: List[CodeBlock] = field(default_factory=list)
    main_component: str = ""
    dependencies: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    
    def get_files_by_type(self, file_type: str) -> List[CodeBlock]:
        """ファイル種別でフィルタリング"""
        return [block for block in self.code_blocks if block.detect_language() == file_type]
    
    def get_file_by_name(self, filename: str) -> Optional[CodeBlock]:
        """ファイル名で検索"""
        for block in self.code_blocks:
            if block.filename == filename or filename in block.filename:
                return block
        return None


class ResponseParser:
    """
    AI応答解析システム
    """
    
    def __init__(self):
        # コードブロック抽出パターン
        self.code_block_pattern = re.compile(
            r'```(\w+)?\s*\n(.*?)\n```',
            re.DOTALL | re.MULTILINE
        )
        
        # ファイル名抽出パターン
        self.filename_pattern = re.compile(
            r'\*\*([^*]+\.(tsx?|jsx?|css|html|json))\*\*|//\s*([^/\n]+\.(tsx?|jsx?|css|html|json))',
            re.IGNORECASE
        )
    
    def extract_code_blocks(self, response: str) -> List[CodeBlock]:
        """
        AIレスポンスからコードブロック抽出
        
        Args:
            response: AI生成レスポンステキスト
            
        Returns:
            抽出されたコードブロックのリスト
        """
        blocks = []
        
        # ファイル名付きブロックパターン
        filename_blocks = re.findall(
            r'\*\*([^*]+\.(tsx?|jsx?|css|html|json))\*\*\s*```(\w+)?\n(.*?)```',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        # 処理済み位置記録
        processed_positions = set()
        
        # ファイル名付きブロック処理
        for match in filename_blocks:
            filename, ext, language, content = match
            if content.strip():
                block = CodeBlock(
                    content=content.strip(),
                    filename=filename.strip(),
                    language=self._normalize_language(language or ext)
                )
                blocks.append(block)
        
        # 通常のMarkdownコードブロック抽出
        matches = self.code_block_pattern.findall(response)
        
        for i, (language, content) in enumerate(matches):
            if not content.strip():
                continue
            
            # 既に処理済みかチェック
            if any(content.strip() in block.content for block in blocks):
                continue
            
            # ファイル名検出
            filename = self._extract_filename_from_content(content) or self._generate_filename(content, language, i)
            
            # 言語正規化
            normalized_language = self._normalize_language(language)
            
            block = CodeBlock(
                content=content.strip(),
                filename=filename,
                language=normalized_language
            )
            
            blocks.append(block)
        
        return blocks
    
    def _extract_filename_from_content(self, content: str) -> Optional[str]:
        """コンテンツからファイル名抽出"""
        lines = content.split('\n')
        
        # 最初の数行をチェック
        for line in lines[:3]:
            # コメント形式のファイル名
            if line.strip().startswith('//') and '.' in line:
                filename = line.replace('//', '').strip()
                if any(ext in filename for ext in ['.tsx', '.ts', '.jsx', '.js', '.css', '.json', '.html']):
                    return filename
            
            # ファイル拡張子を含む行
            if any(ext in line for ext in ['.tsx', '.ts', '.jsx', '.js', '.css', '.json']):
                parts = line.split()
                for part in parts:
                    if '.' in part and any(ext in part for ext in ['.tsx', '.ts', '.jsx', '.js', '.css', '.json']):
                        return part.strip('(),"\' ')
        
        return None
    
    def _generate_filename(self, content: str, language: str, index: int) -> str:
        """ファイル名自動生成"""
        # コンテンツから推測
        if "function App" in content or "const App" in content:
            return "App.tsx"
        elif "export default" in content and "Component" in content:
            return f"Component{index}.tsx"
        elif "interface " in content or "type " in content:
            return "types.ts"
        elif language == "css" or any(css_prop in content for css_prop in ["{", "color:", "background:"]):
            return "styles.css"
        elif language == "json" or (content.strip().startswith('{') and '"' in content):
            return "package.json"
        else:
            ext = self._get_extension_from_language(language)
            return f"file{index}{ext}"
    
    def _normalize_language(self, language: str) -> str:
        """言語名正規化"""
        lang_map = {
            'tsx': 'typescript',
            'ts': 'typescript', 
            'jsx': 'javascript',
            'js': 'javascript',
            'typescript': 'typescript',
            'javascript': 'javascript',
            'css': 'css',
            'json': 'json',
            'html': 'html'
        }
        return lang_map.get(language.lower(), 'typescript')
    
    def _get_extension_from_language(self, language: str) -> str:
        """言語から拡張子取得"""
        ext_map = {
            'typescript': '.tsx',
            'javascript': '.jsx',
            'css': '.css',
            'json': '.json',
            'html': '.html'
        }
        return ext_map.get(language.lower(), '.tsx')
    
    def detect_main_component(self, blocks: List[CodeBlock]) -> str:
        """メインコンポーネント判定"""
        # 優先順位でチェック
        priorities = [
            lambda b: b.filename.lower() == "app.tsx",
            lambda b: b.filename.lower() == "app.jsx",
            lambda b: b.filename.lower() == "index.tsx", 
            lambda b: b.filename.lower() == "index.jsx",
            lambda b: "function App" in b.content or "const App" in b.content,
            lambda b: "export default" in b.content and b.detect_language() == "typescript"
        ]
        
        for priority_check in priorities:
            for block in blocks:
                if priority_check(block):
                    return block.filename
        
        # フォールバック：最初のTypeScriptファイル
        for block in blocks:
            if block.detect_language() in ["typescript", "javascript"]:
                return block.filename
        
        return blocks[0].filename if blocks else ""
    
    def detect_dependencies(self, blocks: List[CodeBlock]) -> List[str]:
        """依存関係検出"""
        dependencies = set()
        
        # npm package patterns
        npm_package_pattern = re.compile(r"from ['\"]([^'\"./][^'\"]*)['\"]")
        relative_import_pattern = re.compile(r"import.*from ['\"]([^'\"]*)['\"]")
        
        for block in blocks:
            # npm packages
            npm_matches = npm_package_pattern.findall(block.content)
            for match in npm_matches:
                # スコープパッケージも対応
                if match.startswith('@'):
                    dependencies.add(match.split('/')[0] + '/' + match.split('/')[1] if '/' in match else match)
                else:
                    dependencies.add(match.split('/')[0])
            
        # 基本的なReact依存関係
        if any("React" in block.content for block in blocks):
            dependencies.add("react")
            
        if any("ReactDOM" in block.content or "react-dom" in block.content for block in blocks):
            dependencies.add("react-dom")
            
        # TypeScript
        if any(block.detect_language() == "typescript" for block in blocks):
            dependencies.add("typescript")
        
        return sorted(list(dependencies))
    
    def detect_features(self, blocks: List[CodeBlock]) -> List[str]:
        """機能特徴検出"""
        features = set()
        
        all_content = " ".join(block.content for block in blocks)
        
        # React Hooks
        if any(hook in all_content for hook in ["useState", "useEffect", "useCallback", "useMemo", "useContext"]):
            features.add("react_hooks")
        
        # Form関連
        if any(form_keyword in all_content for form_keyword in ["<form", "onSubmit", "input", "required"]):
            features.add("form_validation")
        
        # Tailwind CSS
        tailwind_classes = ["bg-", "text-", "p-", "m-", "flex", "grid", "w-", "h-", "border"]
        if any(tw_class in all_content for tw_class in tailwind_classes):
            features.add("tailwind_css")
        
        # レスポンシブデザイン
        if any(responsive in all_content for responsive in ["@media", "sm:", "md:", "lg:", "xl:", "grid-cols"]):
            features.add("responsive_design")
        
        # TypeScript
        if any(block.detect_language() == "typescript" for block in blocks):
            features.add("typescript")
        
        # API呼び出し
        if any(api_keyword in all_content for api_keyword in ["fetch(", "axios", "api", "endpoint"]):
            features.add("api_integration")
        
        return sorted(list(features))
    
    def parse_response(self, ai_response: str) -> ParsedCode:
        """
        AIレスポンス解析メイン処理
        
        Args:
            ai_response: AI生成レスポンス
            
        Returns:
            解析されたコード構造
        """
        # 1. コードブロック抽出
        blocks = self.extract_code_blocks(ai_response)
        
        if not blocks:
            return ParsedCode()
        
        # 2. メインコンポーネント判定
        main_component = self.detect_main_component(blocks)
        
        # 3. 依存関係検出
        dependencies = self.detect_dependencies(blocks)
        
        # 4. 機能特徴検出
        features = self.detect_features(blocks)
        
        return ParsedCode(
            code_blocks=blocks,
            main_component=main_component,
            dependencies=dependencies,
            features=features
        )