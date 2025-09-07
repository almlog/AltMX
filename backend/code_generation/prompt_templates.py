"""
PromptTemplate System - テストを通すための最小実装（Green段階）
React/TypeScript コード生成用プロンプトテンプレート管理
"""

from typing import Dict, List, Optional, Any
import re


class PromptTemplate:
    """
    コード生成用プロンプトテンプレート
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        base_prompt: str,
        complexity_adjustments: Dict[str, str]
    ):
        self.name = name
        self.description = description
        self.base_prompt = base_prompt
        self.complexity_adjustments = complexity_adjustments
    
    def format_prompt(
        self,
        user_prompt: str,
        complexity: str,
        include_security: bool = False,
        include_accessibility: bool = False,
        **kwargs
    ) -> str:
        """
        プロンプトフォーマット生成
        
        Args:
            user_prompt: ユーザーの要求
            complexity: 複雑度（simple/medium/complex）
            include_security: セキュリティ要件含む
            include_accessibility: アクセシビリティ要件含む
            **kwargs: 追加パラメータ
            
        Returns:
            フォーマットされたプロンプト文字列
        """
        # 基本プロンプトにユーザー入力を適用
        formatted = self.base_prompt.format(user_prompt=user_prompt, **kwargs)
        
        # 複雑度調整を追加
        if complexity in self.complexity_adjustments:
            formatted += f"\n\nComplexity Adjustment: {self.complexity_adjustments[complexity]}"
        
        # セキュリティ要件追加
        if include_security:
            security_reqs = """

Security Requirements:
- Prevent XSS attacks by sanitizing all user inputs
- Validate all form data before processing
- Use proper CSRF protection for forms
- Avoid using innerHTML directly
- Sanitize any dynamic content rendering"""
            formatted += security_reqs
        
        # アクセシビリティ要件追加
        if include_accessibility:
            a11y_reqs = """

Accessibility Requirements:
- Add proper aria-label attributes to interactive elements
- Use semantic HTML structure with appropriate roles
- Ensure keyboard navigation support
- Provide screen reader friendly content
- Use proper contrast ratios for text and backgrounds"""
            formatted += a11y_reqs
        
        return formatted


class PromptTemplateManager:
    """
    プロンプトテンプレート管理システム
    """
    
    def __init__(self):
        self._templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """
        デフォルトテンプレートの初期化
        """
        templates = {}
        
        # フォームテンプレート
        templates["form"] = PromptTemplate(
            name="form",
            description="React form component with validation",
            base_prompt="""You are an expert React/TypeScript developer. Generate a production-ready form component.

Requirements:
- Use React 18 with TypeScript 5.x
- Apply Tailwind CSS for styling
- Include proper form validation
- Make the component responsive and accessible
- Use modern React patterns (hooks, functional components)

User Request: {user_prompt}

Generate complete, executable React/TypeScript code with proper imports and exports.""",
            complexity_adjustments={
                "simple": "Keep form fields basic with HTML5 validation only",
                "medium": "Add custom validation logic and error handling", 
                "complex": "Include advanced features like multi-step forms, async validation, and state management"
            }
        )
        
        # ダッシュボードテンプレート  
        templates["dashboard"] = PromptTemplate(
            name="dashboard",
            description="React dashboard component with data visualization",
            base_prompt="""You are an expert React/TypeScript developer. Generate a production-ready dashboard component.

Requirements:
- Use React 18 with TypeScript 5.x
- Apply Tailwind CSS for responsive layout
- Include data visualization components
- Use proper TypeScript interfaces for data
- Make the dashboard responsive and accessible

User Request: {user_prompt}

Generate complete, executable React/TypeScript code with mock data and proper component structure.""",
            complexity_adjustments={
                "simple": "Create basic dashboard with simple cards and mock data",
                "medium": "Add charts, filters, and interactive elements",
                "complex": "Include real-time updates, advanced analytics, and customizable layouts"
            }
        )
        
        # リストテンプレート
        templates["list"] = PromptTemplate(
            name="list",
            description="React list component with CRUD operations",
            base_prompt="""You are an expert React/TypeScript developer. Generate a production-ready list component.

Requirements:
- Use React 18 with TypeScript 5.x  
- Apply Tailwind CSS for styling
- Include CRUD operations (Create, Read, Update, Delete)
- Implement search and filter functionality
- Use proper TypeScript types for data

User Request: {user_prompt}

Generate complete, executable React/TypeScript code with state management and proper component structure.""",
            complexity_adjustments={
                "simple": "Basic list display with add/remove functionality",
                "medium": "Add search, sort, and inline editing capabilities", 
                "complex": "Include pagination, bulk operations, and advanced filtering"
            }
        )
        
        return templates
    
    def get_available_templates(self) -> List[PromptTemplate]:
        """
        利用可能なテンプレート一覧取得
        
        Returns:
            テンプレートのリスト
        """
        return list(self._templates.values())
    
    def get_template(self, name: str) -> PromptTemplate:
        """
        名前によるテンプレート取得
        
        Args:
            name: テンプレート名
            
        Returns:
            指定されたテンプレート
            
        Raises:
            ValueError: テンプレートが見つからない場合
        """
        if name not in self._templates:
            raise ValueError(f"Template not found: {name}")
        
        return self._templates[name]
    
    def list_templates(self) -> list[str]:
        """
        利用可能なテンプレート名一覧取得
        
        Returns:
            テンプレート名のリスト
        """
        return list(self._templates.keys())
    
    def detect_template_type(self, user_prompt: str) -> str:
        """
        ユーザープロンプトからテンプレート種別を自動判定
        
        Args:
            user_prompt: ユーザーのプロンプト
            
        Returns:
            判定されたテンプレート種別
        """
        prompt_lower = user_prompt.lower()
        
        # フォーム系キーワード判定
        form_keywords = ["form", "login", "register", "contact", "signup", "input", "validation"]
        if any(keyword in prompt_lower for keyword in form_keywords):
            return "form"
        
        # ダッシュボード系キーワード判定
        dashboard_keywords = ["dashboard", "analytics", "chart", "graph", "admin", "statistics", "metrics"]
        if any(keyword in prompt_lower for keyword in dashboard_keywords):
            return "dashboard"
        
        # リスト系キーワード判定
        list_keywords = ["list", "table", "crud", "todo", "catalog", "inventory", "manage", "collection"]
        if any(keyword in prompt_lower for keyword in list_keywords):
            return "list"
        
        # デフォルトはフォーム
        return "form"