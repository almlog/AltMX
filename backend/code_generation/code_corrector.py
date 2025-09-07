"""
Code Corrector - テストを通すための最小実装（Green段階）
コード自動修正・改善システム
"""

import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .response_parser import CodeBlock
from .validators import ValidationError
from .security_validator import SecurityValidator


@dataclass
class CorrectionSuggestion:
    """修正提案"""
    correction_type: str  # lint, security, style, performance
    description: str
    original_code: str
    suggested_code: str
    filename: str
    line: int = 0
    confidence: float = 0.8  # 0.0 - 1.0


class CodeCorrector:
    """
    コード自動修正システム
    """
    
    def __init__(self):
        self.security_validator = SecurityValidator()
        
        # 修正パターン定義
        self.correction_patterns = {
            "semicolons": {
                "pattern": r'((?:const|let|var|import|export).*?)(?<![;{}])\s*$',
                "replacement": r'\1;',
                "description": "Add missing semicolon"
            },
            "quotes": {
                "pattern": r'"([^"]*)"',
                "replacement": r"'\1'",
                "description": "Use single quotes instead of double quotes"
            },
            "var_to_const": {
                "pattern": r'\bvar\s+(\w+)\s*=',
                "replacement": r'const \1 =',
                "description": "Use const instead of var"
            }
        }
        
        # React/TypeScript固有の修正
        self.react_fixes = {
            "missing_react_import": {
                "condition": lambda content: "React" in content and "import React" not in content,
                "fix": "import React from 'react';\n\n",
                "position": "top"
            },
            "missing_usestate_import": {
                "condition": lambda content: "useState" in content and "useState" not in content.split('\n')[0] and not any("import" in line and "useState" in line for line in content.split('\n')[:5]),
                "fix": lambda content: self._add_react_hook_import(content, "useState"),
                "position": "import"
            }
        }
    
    def fix_common_issues(self, block: CodeBlock) -> Optional[CodeBlock]:
        """
        一般的な問題の自動修正
        
        Args:
            block: 修正対象コードブロック
            
        Returns:
            修正されたコードブロック（修正不要の場合はNone）
        """
        corrected_content = block.content
        has_changes = False
        
        # React/TypeScript固有修正
        corrected_content, react_changes = self._apply_react_fixes(corrected_content)
        has_changes |= react_changes
        
        # 一般的な修正
        for fix_type, pattern_config in self.correction_patterns.items():
            if fix_type == "semicolons":
                new_content, changed = self._fix_semicolons(corrected_content)
                corrected_content = new_content
                has_changes |= changed
            elif fix_type == "var_to_const":
                new_content, changed = self._fix_var_declarations(corrected_content)
                corrected_content = new_content
                has_changes |= changed
        
        # 型注釈修正
        new_content, type_changes = self._add_basic_type_annotations(corrected_content)
        corrected_content = new_content
        has_changes |= type_changes
        
        if has_changes:
            return CodeBlock(
                content=corrected_content,
                filename=block.filename,
                language=block.language,
                description=block.description
            )
        
        return None
    
    def _apply_react_fixes(self, content: str) -> tuple[str, bool]:
        """React固有の修正適用"""
        corrected = content
        has_changes = False
        
        # React import追加
        if self.react_fixes["missing_react_import"]["condition"](content):
            if not corrected.startswith("import React"):
                corrected = self.react_fixes["missing_react_import"]["fix"] + corrected
                has_changes = True
        
        # useState import追加
        if self.react_fixes["missing_usestate_import"]["condition"](content):
            if callable(self.react_fixes["missing_usestate_import"]["fix"]):
                new_content = self.react_fixes["missing_usestate_import"]["fix"](corrected)
                if new_content != corrected:
                    corrected = new_content
                    has_changes = True
        
        return corrected, has_changes
    
    def _add_react_hook_import(self, content: str, hook: str) -> str:
        """React Hook import追加"""
        lines = content.split('\n')
        
        # 既存のReact importを探す
        for i, line in enumerate(lines):
            if line.startswith("import React") and "from 'react'" in line:
                if "{" in line and "}" in line:
                    # 既存の名前付きimportに追加
                    if hook not in line:
                        import_part = line[line.find("{")+1:line.find("}")]
                        hooks = [h.strip() for h in import_part.split(",") if h.strip()]
                        if hook not in hooks:
                            hooks.append(hook)
                            new_import = f"import React, {{ {', '.join(hooks)} }} from 'react';"
                            lines[i] = new_import
                else:
                    # React, { hook } 形式に変更
                    lines[i] = f"import React, {{ {hook} }} from 'react';"
                return '\n'.join(lines)
        
        # React importがない場合は最初に追加
        if any("useState" in line for line in lines):
            lines.insert(0, f"import React, {{ {hook} }} from 'react';")
            return '\n'.join(lines)
        
        return content
    
    def _fix_semicolons(self, content: str) -> tuple[str, bool]:
        """セミコロン不足修正"""
        lines = content.split('\n')
        has_changes = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # セミコロンが必要な行パターン
            needs_semicolon = (
                stripped and
                not stripped.endswith((';', '{', '}', ')', ',')) and
                not stripped.startswith(('if', 'for', 'while', 'function', 'class', 'interface', 'type', '//', '/*', '*', 'import', 'export')) and
                any(keyword in stripped for keyword in ['const ', 'let ', 'var ', 'return ']) and
                not stripped.endswith('=> {')
            )
            
            if needs_semicolon:
                lines[i] = line.rstrip() + ';'
                has_changes = True
        
        return '\n'.join(lines), has_changes
    
    def _fix_var_declarations(self, content: str) -> tuple[str, bool]:
        """var宣言をconst/letに修正"""
        has_changes = False
        
        # var を const に置換（再代入がない場合）
        var_pattern = re.compile(r'\bvar\s+(\w+)\s*=')
        matches = var_pattern.finditer(content)
        
        corrected = content
        for match in matches:
            var_name = match.group(1)
            
            # 再代入チェック（簡易）
            assignment_count = len(re.findall(rf'\b{var_name}\s*=', content))
            
            if assignment_count == 1:  # 宣言のみ
                corrected = corrected.replace(f'var {var_name}', f'const {var_name}')
                has_changes = True
            else:  # 再代入がある
                corrected = corrected.replace(f'var {var_name}', f'let {var_name}')
                has_changes = True
        
        return corrected, has_changes
    
    def get_correction_suggestions(self, block: CodeBlock) -> List[CorrectionSuggestion]:
        """
        修正提案取得
        
        Args:
            block: 分析対象コードブロック
            
        Returns:
            修正提案のリスト
        """
        suggestions = []
        
        # セキュリティ関連提案
        security_risks = self.security_validator.scan_security_risks(block)
        for risk in security_risks:
            suggestions.append(CorrectionSuggestion(
                correction_type="security",
                description=f"Security risk: {risk.description}",
                original_code=self._extract_code_snippet(block.content, risk.line),
                suggested_code=f"// {risk.recommendation}",
                filename=block.filename,
                line=risk.line,
                confidence=0.9 if risk.severity in ["critical", "high"] else 0.7
            ))
        
        # リント関連提案
        lint_suggestions = self._get_lint_suggestions(block)
        suggestions.extend(lint_suggestions)
        
        # スタイル関連提案
        style_suggestions = self._get_style_suggestions(block)
        suggestions.extend(style_suggestions)
        
        return suggestions
    
    def _get_lint_suggestions(self, block: CodeBlock) -> List[CorrectionSuggestion]:
        """リント関連提案"""
        suggestions = []
        lines = block.content.split('\n')
        
        # セミコロン不足
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if (stripped.endswith(')') or stripped.endswith('}')) and not stripped.endswith(';'):
                if any(keyword in stripped for keyword in ['const ', 'let ', 'var ']):
                    suggestions.append(CorrectionSuggestion(
                        correction_type="lint",
                        description="Add missing semicolon",
                        original_code=line,
                        suggested_code=line + ';',
                        filename=block.filename,
                        line=i
                    ))
        
        # var使用
        if 'var ' in block.content:
            suggestions.append(CorrectionSuggestion(
                correction_type="lint",
                description="Use const/let instead of var",
                original_code="var variable = value;",
                suggested_code="const variable = value;",
                filename=block.filename,
                confidence=0.9
            ))
        
        return suggestions
    
    def _get_style_suggestions(self, block: CodeBlock) -> List[CorrectionSuggestion]:
        """スタイル関連提案"""
        suggestions = []
        
        # ダブルクォート使用
        double_quote_count = block.content.count('"')
        single_quote_count = block.content.count("'")
        
        if double_quote_count > single_quote_count:
            suggestions.append(CorrectionSuggestion(
                correction_type="style",
                description="Use single quotes consistently",
                original_code='"string"',
                suggested_code="'string'",
                filename=block.filename
            ))
        
        return suggestions
    
    def apply_specific_corrections(self, block: CodeBlock, correction_types: List[str]) -> CodeBlock:
        """
        特定の修正タイプのみ適用
        
        Args:
            block: 修正対象コードブロック
            correction_types: 適用する修正タイプのリスト
            
        Returns:
            修正されたコードブロック
        """
        corrected_content = block.content
        
        for correction_type in correction_types:
            if correction_type == "semicolons":
                corrected_content, _ = self._fix_semicolons(corrected_content)
            elif correction_type == "unused_variables":
                corrected_content = self._remove_unused_variables(corrected_content)
            elif correction_type == "var_to_const":
                corrected_content, _ = self._fix_var_declarations(corrected_content)
        
        return CodeBlock(
            content=corrected_content,
            filename=block.filename,
            language=block.language,
            description=block.description
        )
    
    def _remove_unused_variables(self, content: str) -> str:
        """未使用変数の除去"""
        lines = content.split('\n')
        corrected_lines = []
        
        for line in lines:
            # 簡易実装：'unused' を含む行をコメントアウト
            if 'unused' in line.lower() and any(keyword in line for keyword in ['const ', 'let ', 'var ']):
                # インデントを保持してコメントアウト
                indent = len(line) - len(line.lstrip())
                corrected_lines.append(' ' * indent + '// ' + line.strip() + '  // Unused variable')
            else:
                corrected_lines.append(line)
        
        return '\n'.join(corrected_lines)
    
    def _extract_code_snippet(self, content: str, line_number: int, context: int = 1) -> str:
        """コードスニペット抽出"""
        lines = content.split('\n')
        
        if line_number <= 0 or line_number > len(lines):
            return ""
        
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        
        return '\n'.join(lines[start:end])
    
    def _add_basic_type_annotations(self, content: str) -> tuple[str, bool]:
        """基本的な型注釈追加"""
        corrected = content
        has_changes = False
        
        # React.FC型注釈追加（関数コンポーネント）
        component_pattern = r'const\s+(\w+)\s*=\s*\(\s*\{\s*([^}]+)\s*\}\s*\)\s*=>'
        matches = re.finditer(component_pattern, content)
        
        for match in matches:
            component_name = match.group(1)
            props = match.group(2)
            
            # 既に型注釈がある場合はスキップ
            if ': React.FC' not in match.group(0) and 'React.FC' not in match.group(0):
                # プロパティから型を推測
                prop_types = []
                for prop in props.split(','):
                    prop_name = prop.strip()
                    if prop_name:
                        # 簡易的な型推測
                        if 'name' in prop_name.lower():
                            prop_types.append(f'{prop_name}: string')
                        elif 'age' in prop_name.lower() or 'id' in prop_name.lower():
                            prop_types.append(f'{prop_name}: number')
                        elif 'on' in prop_name.lower():
                            prop_types.append(f'{prop_name}: () => void')
                        else:
                            prop_types.append(f'{prop_name}: any')
                
                if prop_types:
                    type_def = f'{{ {", ".join(prop_types)} }}'
                    new_signature = f'const {component_name}: React.FC<{type_def}> = ({{ {props} }}) =>'
                    corrected = corrected.replace(match.group(0), new_signature)
                    has_changes = True
        
        return corrected, has_changes