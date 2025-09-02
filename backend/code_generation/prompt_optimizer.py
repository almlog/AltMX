"""
PromptOptimizer - テストを通すための最小実装（Green段階）
プロンプトの最適化・トークン管理システム
"""

from typing import List, Optional, Dict, Any
import re
from .prompt_templates import PromptTemplateManager


class PromptOptimizer:
    """
    プロンプト最適化システム
    """
    
    def __init__(self):
        self.template_manager = PromptTemplateManager()
        self.max_tokens = 4000  # AI API制限
    
    def optimize(
        self,
        user_prompt: str,
        complexity: str,
        template_type: str,
        include_security: bool = False,
        include_accessibility: bool = False,
        custom_requirements: Optional[List[str]] = None
    ) -> str:
        """
        プロンプト最適化メイン処理
        
        Args:
            user_prompt: ユーザーの要求
            complexity: 複雑度（simple/medium/complex）
            template_type: テンプレート種別
            include_security: セキュリティ要件含む
            include_accessibility: アクセシビリティ要件含む
            custom_requirements: カスタム要件リスト
            
        Returns:
            最適化されたプロンプト
            
        Raises:
            ValueError: 無効な入力パラメータの場合
        """
        # 入力検証
        if not user_prompt or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")
        
        if complexity not in ["simple", "medium", "complex"]:
            raise ValueError(f"Invalid complexity: {complexity}")
        
        try:
            template = self.template_manager.get_template(template_type)
        except ValueError:
            raise ValueError(f"Invalid template type: {template_type}")
        
        # 基本プロンプト生成
        optimized_prompt = template.format_prompt(
            user_prompt=user_prompt,
            complexity=complexity,
            include_security=include_security,
            include_accessibility=include_accessibility
        )
        
        # カスタム要件追加
        if custom_requirements:
            custom_section = "\n\nAdditional Requirements:\n"
            for req in custom_requirements:
                custom_section += f"- {req}\n"
            optimized_prompt += custom_section
        
        # トークン制限チェック・調整
        if self._get_token_count(optimized_prompt) > self.max_tokens:
            optimized_prompt = self._reduce_token_count(optimized_prompt)
        
        return optimized_prompt
    
    def _get_token_count(self, text: str) -> int:
        """
        概算トークン数計算（簡易実装）
        
        Args:
            text: 対象テキスト
            
        Returns:
            推定トークン数
        """
        # 簡易実装：単語数 * 1.3倍でトークン数推定
        words = len(text.split())
        return int(words * 1.3)
    
    def _reduce_token_count(self, prompt: str) -> str:
        """
        トークン数削減処理
        
        Args:
            prompt: 元のプロンプト
            
        Returns:
            短縮されたプロンプト
        """
        lines = prompt.split('\n')
        
        # 優先度に基づいて行を削除
        # 1. 空行削除
        lines = [line for line in lines if line.strip()]
        
        # 2. 冗長な説明行を短縮
        shortened_lines = []
        for line in lines:
            if len(line) > 100:  # 長い行を短縮
                shortened_line = line[:100] + "..."
                shortened_lines.append(shortened_line)
            else:
                shortened_lines.append(line)
        
        return '\n'.join(shortened_lines)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        最適化統計情報取得
        
        Returns:
            最適化に関する統計情報
        """
        return {
            "max_tokens": self.max_tokens,
            "available_templates": len(self.template_manager.get_available_templates()),
            "supported_complexities": ["simple", "medium", "complex"]
        }