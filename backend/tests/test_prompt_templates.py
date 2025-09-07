"""
Test suite for PromptTemplate system - TDD実装
コード生成用プロンプトテンプレート管理のテスト
"""

import pytest
from unittest.mock import Mock, patch
from code_generation.prompt_templates import PromptTemplate, PromptTemplateManager
from code_generation.prompt_optimizer import PromptOptimizer


class TestPromptTemplate:
    """PromptTemplateクラスのテスト"""
    
    def test_template_initialization(self):
        """テンプレート初期化の検証"""
        template = PromptTemplate(
            name="test_form",
            description="Test form template",
            base_prompt="Generate a form component: {user_prompt}",
            complexity_adjustments={
                'simple': 'Make it basic',
                'medium': 'Add validation',
                'complex': 'Include advanced features'
            }
        )
        
        assert template.name == "test_form"
        assert template.description == "Test form template"
        assert "{user_prompt}" in template.base_prompt
        assert len(template.complexity_adjustments) == 3
    
    def test_template_format_simple(self):
        """シンプルなプロンプト生成テスト"""
        template = PromptTemplate(
            name="form",
            description="Form template",
            base_prompt="Generate a {component_type} component: {user_prompt}",
            complexity_adjustments={'simple': 'Keep it simple'}
        )
        
        result = template.format_prompt(
            user_prompt="contact form",
            complexity="simple",
            component_type="React"
        )
        
        assert "Generate a React component: contact form" in result
        assert "Keep it simple" in result
    
    def test_template_format_with_security_requirements(self):
        """セキュリティ要件込みプロンプト生成テスト"""
        template = PromptTemplate(
            name="form",
            description="Form template", 
            base_prompt="Generate: {user_prompt}",
            complexity_adjustments={'simple': 'basic'}
        )
        
        result = template.format_prompt(
            user_prompt="login form",
            complexity="simple",
            include_security=True
        )
        
        # セキュリティ要件が含まれているかチェック
        assert "XSS" in result or "security" in result.lower()
        assert "sanitize" in result.lower() or "validate" in result.lower()


class TestPromptTemplateManager:
    """PromptTemplateManagerクラスのテスト"""
    
    @pytest.fixture
    def template_manager(self):
        """テスト用TemplateManager"""
        return PromptTemplateManager()
    
    def test_get_available_templates(self, template_manager):
        """利用可能テンプレート一覧取得テスト"""
        templates = template_manager.get_available_templates()
        
        # 基本テンプレートが存在することを確認
        template_names = [t.name for t in templates]
        assert "form" in template_names
        assert "dashboard" in template_names
        assert "list" in template_names
        
        # 各テンプレートが必要な要素を持つことを確認
        for template in templates:
            assert hasattr(template, 'name')
            assert hasattr(template, 'description')
            assert hasattr(template, 'base_prompt')
            assert hasattr(template, 'complexity_adjustments')
    
    def test_get_template_by_name(self, template_manager):
        """名前によるテンプレート取得テスト"""
        form_template = template_manager.get_template("form")
        
        assert form_template is not None
        assert form_template.name == "form"
        assert "form" in form_template.description.lower()
        assert "React" in form_template.base_prompt
        assert "TypeScript" in form_template.base_prompt
    
    def test_get_template_nonexistent(self, template_manager):
        """存在しないテンプレート取得時の例外テスト"""
        with pytest.raises(ValueError, match="Template not found"):
            template_manager.get_template("nonexistent_template")
    
    def test_detect_template_type_from_prompt(self, template_manager):
        """プロンプトからのテンプレート種別自動判定テスト"""
        # フォーム系プロンプト
        form_prompts = [
            "Create a contact form with validation",
            "Build a login form component", 
            "Generate user registration form"
        ]
        
        for prompt in form_prompts:
            detected = template_manager.detect_template_type(prompt)
            assert detected == "form"
        
        # ダッシュボード系プロンプト
        dashboard_prompts = [
            "Create a dashboard with charts",
            "Build an admin dashboard",
            "Generate analytics dashboard"
        ]
        
        for prompt in dashboard_prompts:
            detected = template_manager.detect_template_type(prompt)
            assert detected == "dashboard"
        
        # リスト系プロンプト
        list_prompts = [
            "Create a todo list component",
            "Build a user list with CRUD",
            "Generate product catalog"
        ]
        
        for prompt in list_prompts:
            detected = template_manager.detect_template_type(prompt)
            assert detected == "list"
    
    def test_detect_template_type_fallback(self, template_manager):
        """テンプレート種別判定のフォールバックテスト"""
        ambiguous_prompt = "Create something cool"
        detected = template_manager.detect_template_type(ambiguous_prompt)
        
        # フォールバックで "form" が返されることを確認
        assert detected == "form"


class TestPromptOptimizer:
    """PromptOptimizerクラスのテスト"""
    
    @pytest.fixture
    def optimizer(self):
        """テスト用Optimizer"""
        return PromptOptimizer()
    
    def test_optimize_prompt_simple_complexity(self, optimizer):
        """シンプル複雑度でのプロンプト最適化テスト"""
        result = optimizer.optimize(
            user_prompt="Create a contact form",
            complexity="simple",
            template_type="form"
        )
        
        # 基本要件がプロンプトに含まれることを確認
        assert "React" in result
        assert "TypeScript" in result
        assert "Tailwind" in result
        assert "contact form" in result
        
        # シンプル複雑度特有の制約が含まれることを確認  
        assert "basic" in result.lower() or "simple" in result.lower()
    
    def test_optimize_prompt_complex_complexity(self, optimizer):
        """複雑な複雑度でのプロンプト最適化テスト"""
        result = optimizer.optimize(
            user_prompt="Create a user management dashboard",
            complexity="complex", 
            template_type="dashboard"
        )
        
        # 基本要件に加えて高度な機能要求が含まれることを確認
        assert "React" in result
        assert "TypeScript" in result
        assert "dashboard" in result.lower()
        assert "user management" in result
        
        # 複雑度特有の要求が含まれることを確認
        complex_features = ["validation", "authentication", "authorization", "advanced"]
        assert any(feature in result.lower() for feature in complex_features)
    
    def test_optimize_prompt_with_security_requirements(self, optimizer):
        """セキュリティ要件込み最適化テスト"""
        result = optimizer.optimize(
            user_prompt="Create a login form",
            complexity="medium",
            template_type="form",
            include_security=True
        )
        
        # セキュリティ関連の要件が追加されることを確認
        security_terms = ["XSS", "CSRF", "sanitize", "validate", "security"]
        assert any(term in result for term in security_terms)
    
    def test_optimize_prompt_accessibility_requirements(self, optimizer):
        """アクセシビリティ要件込み最適化テスト"""
        result = optimizer.optimize(
            user_prompt="Create a data table",
            complexity="medium",
            template_type="list",
            include_accessibility=True
        )
        
        # アクセシビリティ関連の要件が追加されることを確認
        a11y_terms = ["aria-label", "role", "accessibility", "screen reader", "keyboard"]
        assert any(term in result for term in a11y_terms)
    
    @patch('code_generation.prompt_optimizer.PromptOptimizer._get_token_count')
    def test_optimize_prompt_token_limit(self, mock_token_count, optimizer):
        """トークン制限下でのプロンプト最適化テスト"""
        # トークン数をモック
        mock_token_count.return_value = 5000  # 制限超過をシミュレート
        
        result = optimizer.optimize(
            user_prompt="Create a very complex application with many features",
            complexity="complex",
            template_type="dashboard"
        )
        
        # トークン制限により内容が短縮されることを確認
        assert len(result) < 10000  # 適切な長さに収まっている
        assert "Create a very complex application" in result  # 主要部分は保持
    
    def test_optimize_prompt_with_custom_requirements(self, optimizer):
        """カスタム要件でのプロンプト最適化テスト"""
        custom_reqs = [
            "Use React Hook Form for form handling",
            "Integrate with REST API", 
            "Support dark mode"
        ]
        
        result = optimizer.optimize(
            user_prompt="Create a user profile form",
            complexity="medium",
            template_type="form",
            custom_requirements=custom_reqs
        )
        
        # カスタム要件が含まれることを確認
        for req in custom_reqs:
            assert req in result or any(word in result for word in req.split())


# 統合テスト
class TestPromptSystemIntegration:
    """プロンプトシステム全体の統合テスト"""
    
    def test_full_prompt_generation_flow(self):
        """プロンプト生成フルフローテスト"""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer()
        
        # 1. テンプレート種別自動検出
        user_prompt = "Create a todo list with add/delete functionality"
        template_type = manager.detect_template_type(user_prompt)
        assert template_type == "list"
        
        # 2. プロンプト最適化
        optimized = optimizer.optimize(
            user_prompt=user_prompt,
            complexity="medium",
            template_type=template_type,
            include_security=True,
            include_accessibility=True
        )
        
        # 3. 結果検証
        assert "todo list" in optimized
        assert "React" in optimized
        assert "TypeScript" in optimized
        assert "add" in optimized and "delete" in optimized
        
        # セキュリティ・アクセシビリティ要件も含まれている
        assert any(term in optimized.lower() for term in ["security", "sanitize", "validate"])
        assert any(term in optimized for term in ["aria-label", "role", "accessibility"])
    
    def test_error_handling_robustness(self):
        """エラーハンドリングの堅牢性テスト"""
        manager = PromptTemplateManager()
        optimizer = PromptOptimizer()
        
        # 空のプロンプトテスト
        with pytest.raises(ValueError):
            optimizer.optimize(
                user_prompt="",
                complexity="simple", 
                template_type="form"
            )
        
        # 無効な複雑度テスト
        with pytest.raises(ValueError):
            optimizer.optimize(
                user_prompt="Create a form",
                complexity="invalid_complexity",
                template_type="form" 
            )
        
        # 無効なテンプレート種別テスト
        with pytest.raises(ValueError):
            optimizer.optimize(
                user_prompt="Create something",
                complexity="simple",
                template_type="invalid_template"
            )