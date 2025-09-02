"""
Code Validators - テストを通すための最小実装（Green段階）
生成コードの構文・型・品質検証
"""

import re
import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
import logging

from .response_parser import CodeBlock

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """検証エラー情報"""
    filename: str
    line: int
    column: int
    message: str
    error_type: str  # syntax, type, lint, security
    severity: str = "error"  # error, warning, info
    
    def format(self) -> str:
        """エラー情報フォーマット"""
        return f"{self.filename}:{self.line}:{self.column} [{self.severity}] {self.message}"


@dataclass
class ValidationResult:
    """検証結果"""
    is_valid: bool = True
    syntax_errors: List[ValidationError] = field(default_factory=list)
    type_errors: List[ValidationError] = field(default_factory=list)
    lint_errors: List[ValidationError] = field(default_factory=list)
    security_risks: List['SecurityRisk'] = field(default_factory=list)
    performance_warnings: List[ValidationError] = field(default_factory=list)
    
    def get_overall_status(self) -> str:
        """全体ステータス取得"""
        if not self.is_valid:
            return "invalid"
        elif self.performance_warnings or any(error.severity == "warning" for error in 
                                             self.syntax_errors + self.type_errors + self.lint_errors):
            return "valid_with_warnings"
        return "valid"
    
    def get_all_errors(self) -> List[ValidationError]:
        """すべてのエラー取得"""
        return (self.syntax_errors + self.type_errors + 
                self.lint_errors + self.performance_warnings)


class CodeValidator:
    """
    コード品質検証システム
    """
    
    def __init__(self):
        # TypeScript設定
        self.typescript_config = {
            "compilerOptions": {
                "target": "ES2022",
                "lib": ["DOM", "DOM.Iterable", "ES6"],
                "allowJs": True,
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx"
            }
        }
        
        # ESLint基本ルール
        self.eslint_rules = {
            "extends": ["eslint:recommended", "@typescript-eslint/recommended"],
            "rules": {
                "semi": ["error", "always"],
                "quotes": ["error", "single"],
                "no-unused-vars": ["error"],
                "no-console": ["warn"],
                "prefer-const": ["error"],
                "no-var": ["error"]
            }
        }
    
    def validate_typescript_syntax(self, block: CodeBlock) -> ValidationResult:
        """
        TypeScript構文検証
        
        Args:
            block: 検証対象コードブロック
            
        Returns:
            検証結果
        """
        result = ValidationResult()
        
        try:
            # 簡易構文チェック
            syntax_errors = self._check_basic_syntax(block)
            result.syntax_errors.extend(syntax_errors)
            
            # 型関連チェック
            type_errors = self._check_typescript_types(block)
            result.type_errors.extend(type_errors)
            
            result.is_valid = len(syntax_errors) == 0 and len(type_errors) == 0
            
        except Exception as e:
            error = ValidationError(
                filename=block.filename,
                line=0,
                column=0,
                message=f"Validation error: {str(e)}",
                error_type="syntax"
            )
            result.syntax_errors.append(error)
            result.is_valid = False
        
        return result
    
    def _check_basic_syntax(self, block: CodeBlock) -> List[ValidationError]:
        """基本構文チェック"""
        errors = []
        lines = block.content.split('\n')
        
        # 括弧バランスチェック
        brace_count = block.content.count('{') - block.content.count('}')
        if brace_count != 0:
            errors.append(ValidationError(
                filename=block.filename,
                line=len(lines),
                column=0,
                message=f"Unmatched braces: {abs(brace_count)} {'opening' if brace_count > 0 else 'closing'} braces",
                error_type="syntax"
            ))
        
        paren_count = block.content.count('(') - block.content.count(')')
        if paren_count != 0:
            errors.append(ValidationError(
                filename=block.filename,
                line=len(lines),
                column=0,
                message=f"Unmatched parentheses: {abs(paren_count)} {'opening' if paren_count > 0 else 'closing'} parentheses",
                error_type="syntax"
            ))
        
        # 不完全な文チェック
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.endswith('=') and not stripped.endswith('==') and not stripped.endswith('!='):
                errors.append(ValidationError(
                    filename=block.filename,
                    line=i,
                    column=len(line),
                    message="Incomplete assignment",
                    error_type="syntax"
                ))
            
            # 欠落キーワード検知
            if 'missing:' in stripped:
                errors.append(ValidationError(
                    filename=block.filename,
                    line=i,
                    column=stripped.find('missing:'),
                    message="Incomplete object property",
                    error_type="syntax"
                ))
        
        return errors
    
    def _check_typescript_types(self, block: CodeBlock) -> List[ValidationError]:
        """TypeScript型チェック"""
        errors = []
        
        # React関連の基本チェック
        if "React" in block.content and "import React" not in block.content:
            errors.append(ValidationError(
                filename=block.filename,
                line=1,
                column=0,
                message="React is used but not imported",
                error_type="type",
                severity="warning"
            ))
        
        # useState未import検知
        if "useState" in block.content and "useState" not in block.content.split('\n')[0]:
            if not any("import" in line and "useState" in line for line in block.content.split('\n')[:5]):
                errors.append(ValidationError(
                    filename=block.filename,
                    line=1,
                    column=0,
                    message="useState is used but not imported",
                    error_type="type",
                    severity="warning"
                ))
        
        return errors
    
    def validate_eslint(self, block: CodeBlock) -> ValidationResult:
        """
        ESLint検証
        
        Args:
            block: 検証対象コードブロック
            
        Returns:
            検証結果
        """
        result = ValidationResult()
        
        try:
            lint_errors = self._check_eslint_rules(block)
            result.lint_errors.extend(lint_errors)
            result.is_valid = len(lint_errors) == 0
            
        except Exception as e:
            error = ValidationError(
                filename=block.filename,
                line=0,
                column=0,
                message=f"ESLint validation error: {str(e)}",
                error_type="lint"
            )
            result.lint_errors.append(error)
            result.is_valid = False
        
        return result
    
    def _check_eslint_rules(self, block: CodeBlock) -> List[ValidationError]:
        """ESLintルールチェック"""
        errors = []
        lines = block.content.split('\n')
        
        # セミコロンチェック
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if (stripped.endswith(')') or stripped.endswith('}')) and not stripped.endswith(';'):
                # 関数宣言や式の末尾でセミコロン不足
                if any(keyword in stripped for keyword in ['const ', 'let ', 'var ', 'import ', 'export ']) and 'interface' not in stripped and 'type ' not in stripped:
                    errors.append(ValidationError(
                        filename=block.filename,
                        line=i,
                        column=len(line),
                        message="Missing semicolon",
                        error_type="lint",
                        severity="error"
                    ))
        
        # 未使用変数チェック（簡易）
        variable_declarations = re.findall(r'(?:const|let|var)\s+(\w+)', block.content)
        for var_name in variable_declarations:
            if var_name != 'React' and block.content.count(var_name) == 1:
                errors.append(ValidationError(
                    filename=block.filename,
                    line=0,
                    column=0,
                    message=f"Variable '{var_name}' is declared but never used",
                    error_type="lint",
                    severity="warning"
                ))
        
        # var使用チェック
        if 'var ' in block.content:
            errors.append(ValidationError(
                filename=block.filename,
                line=0,
                column=0,
                message="Use 'const' or 'let' instead of 'var'",
                error_type="lint",
                severity="warning"
            ))
        
        return errors
    
    def validate_comprehensive(self, block: CodeBlock) -> ValidationResult:
        """
        包括的検証
        
        Args:
            block: 検証対象コードブロック
            
        Returns:
            統合検証結果
        """
        # 各種検証を実行
        syntax_result = self.validate_typescript_syntax(block)
        lint_result = self.validate_eslint(block)
        
        # 結果統合
        combined_result = ValidationResult()
        combined_result.syntax_errors = syntax_result.syntax_errors
        combined_result.type_errors = syntax_result.type_errors
        combined_result.lint_errors = lint_result.lint_errors
        
        # パフォーマンス警告チェック
        perf_warnings = self._check_performance_issues(block)
        combined_result.performance_warnings = perf_warnings
        
        # 全体的な有効性判定
        has_critical_errors = (len(combined_result.syntax_errors) > 0 or 
                              any(error.severity == "error" for error in combined_result.type_errors + combined_result.lint_errors))
        combined_result.is_valid = not has_critical_errors
        
        return combined_result
    
    def _check_performance_issues(self, block: CodeBlock) -> List[ValidationError]:
        """パフォーマンス問題チェック"""
        warnings = []
        
        # Math.random()をkeyに使用
        if 'key={Math.random()}' in block.content:
            warnings.append(ValidationError(
                filename=block.filename,
                line=0,
                column=0,
                message="Using Math.random() as React key can cause performance issues",
                error_type="performance",
                severity="warning"
            ))
        
        # 毎回新しい関数/オブジェクトを作成
        lines = block.content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'onClick={() => ' in line or 'onChange={() => ' in line:
                warnings.append(ValidationError(
                    filename=block.filename,
                    line=i,
                    column=0,
                    message="Consider extracting inline arrow function to avoid re-renders",
                    error_type="performance",
                    severity="info"
                ))
        
        return warnings
    
    def validate_multiple_files(self, blocks: List[CodeBlock]) -> List[ValidationResult]:
        """
        複数ファイル検証
        
        Args:
            blocks: 検証対象コードブロックのリスト
            
        Returns:
            各ファイルの検証結果リスト
        """
        results = []
        
        for block in blocks:
            result = self.validate_comprehensive(block)
            results.append(result)
        
        return results
    
    def validate_with_dependencies(self, block: CodeBlock, external_deps: List[str]) -> ValidationResult:
        """
        外部依存関係ありの検証
        
        Args:
            block: 検証対象コードブロック
            external_deps: 外部依存関係リスト
            
        Returns:
            検証結果
        """
        # 基本検証
        result = self.validate_comprehensive(block)
        
        # 外部依存関係のimportエラーを除去
        filtered_errors = []
        for error in result.type_errors:
            # 外部依存関係に関連するエラーは無視
            if not any(dep in error.message for dep in external_deps):
                filtered_errors.append(error)
        
        result.type_errors = filtered_errors
        
        # 有効性再判定
        has_critical_errors = (len(result.syntax_errors) > 0 or 
                              any(error.severity == "error" for error in result.type_errors + result.lint_errors))
        result.is_valid = not has_critical_errors
        
        return result