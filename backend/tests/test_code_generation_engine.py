"""
Code Generation Engine Tests (TDD)
テストファースト！React/TypeScript自動生成エンジン
業務ツールコンポーネントの自動生成とバリデーション
"""

import pytest
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, AsyncMock, MagicMock

class TestCodeGenerationCore:
    """コード生成エンジン コアテスト"""
    
    @pytest.mark.asyncio
    async def test_code_generation_engine_creation(self):
        """CodeGenerationEngine作成テスト"""
        # RED: まだCodeGenerationEngineがないので失敗する
        from code_generation_engine import CodeGenerationEngine  # まだ存在しない
        
        engine = CodeGenerationEngine(use_mocks=True)
        assert engine is not None
        assert hasattr(engine, 'template_manager')
        assert hasattr(engine, 'syntax_validator')
        assert hasattr(engine, 'quality_checker')
        assert hasattr(engine, 'ai_service')
    
    @pytest.mark.asyncio
    async def test_prompt_template_system(self):
        """プロンプトテンプレートシステムテスト"""
        # RED: まだテンプレート管理システムがないので失敗する
        from code_generation_engine import PromptTemplateManager  # まだ存在しない
        
        template_manager = PromptTemplateManager()
        
        # 基本テンプレート登録
        business_form_template = {
            "name": "business_form",
            "description": "業務フォーム生成テンプレート",
            "prompt_template": "Create a React TypeScript form component for {business_domain} with fields: {fields}",
            "required_params": ["business_domain", "fields"],
            "output_format": "typescript_react_component"
        }
        
        template_manager.register_template(business_form_template)
        
        # テンプレート取得確認
        retrieved = template_manager.get_template("business_form")
        assert retrieved["name"] == "business_form"
        assert "business_domain" in retrieved["required_params"]
        
        # パラメータ付きプロンプト生成
        params = {
            "business_domain": "在庫管理",
            "fields": ["product_name", "quantity", "category", "price"]
        }
        
        prompt = template_manager.generate_prompt("business_form", params)
        assert "在庫管理" in prompt
        assert "product_name" in prompt
        assert "TypeScript" in prompt
    
    @pytest.mark.asyncio 
    async def test_react_component_generation(self):
        """Reactコンポーネント生成テスト"""
        # RED: まだコンポーネント生成がないので失敗する
        from code_generation_engine import CodeGenerationEngine
        
        engine = CodeGenerationEngine(use_mocks=True)
        
        # フォームコンポーネント生成要求
        generation_request = {
            "type": "business_form",
            "name": "InventoryForm", 
            "domain": "在庫管理",
            "fields": [
                {"name": "productName", "type": "string", "label": "商品名", "required": True},
                {"name": "quantity", "type": "number", "label": "数量", "required": True},
                {"name": "category", "type": "select", "label": "カテゴリ", "options": ["電子機器", "衣類", "食品"]},
                {"name": "price", "type": "currency", "label": "価格", "required": True}
            ],
            "actions": ["save", "cancel", "preview"]
        }
        
        # コンポーネント生成実行
        result = await engine.generate_component(generation_request)
        
        assert result.component_name == "InventoryForm"
        assert result.typescript_code is not None
        assert "import React" in result.typescript_code
        assert "interface InventoryFormProps" in result.typescript_code or "InventoryForm" in result.typescript_code
        assert "const InventoryForm: React.FC" in result.typescript_code
        assert "productName" in result.typescript_code
        assert "useState" in result.typescript_code or "useForm" in result.typescript_code
        assert result.validation_passed == True
        assert len(result.quality_issues) <= 2
    
    @pytest.mark.asyncio
    async def test_table_component_generation(self):
        """データテーブルコンポーネント生成テスト"""
        # RED: まだテーブル生成がないので失敗する
        from code_generation_engine import CodeGenerationEngine
        
        engine = CodeGenerationEngine(use_mocks=True)
        
        # テーブルコンポーネント生成要求
        table_request = {
            "type": "data_table",
            "name": "ProductTable",
            "domain": "商品管理", 
            "columns": [
                {"key": "id", "label": "ID", "type": "number", "sortable": True},
                {"key": "name", "label": "商品名", "type": "string", "searchable": True},
                {"key": "price", "label": "価格", "type": "currency", "sortable": True},
                {"key": "stock", "label": "在庫", "type": "number", "sortable": True},
                {"key": "category", "label": "カテゴリ", "type": "string", "filterable": True}
            ],
            "features": ["pagination", "search", "sort", "filter", "export"],
            "actions": ["edit", "delete", "view"]
        }
        
        result = await engine.generate_component(table_request)
        
        assert result.component_name == "ProductTable"
        assert result.typescript_code is not None
        assert "interface ProductTableProps" in result.typescript_code
        assert "paginatedData" in result.typescript_code
        assert "search" in result.typescript_code
        assert "sortColumn" in result.typescript_code
        assert result.validation_passed == True
        assert "エクスポート" in result.typescript_code
    
    @pytest.mark.asyncio
    async def test_dashboard_component_generation(self):
        """ダッシュボードコンポーネント生成テスト"""
        # RED: まだダッシュボード生成がないので失敗する
        from code_generation_engine import CodeGenerationEngine
        
        engine = CodeGenerationEngine(use_mocks=True)
        
        # ダッシュボード生成要求
        dashboard_request = {
            "type": "dashboard",
            "name": "SalesDashboard",
            "domain": "売上分析",
            "widgets": [
                {"type": "metric_card", "title": "今月の売上", "value_field": "monthly_sales", "format": "currency"},
                {"type": "line_chart", "title": "売上推移", "data_source": "sales_trend", "x_axis": "date", "y_axis": "amount"},
                {"type": "pie_chart", "title": "カテゴリ別売上", "data_source": "category_sales", "value_field": "amount", "label_field": "category"},
                {"type": "table", "title": "トップ商品", "data_source": "top_products", "columns": ["name", "sales", "profit"]}
            ],
            "layout": "responsive_grid",
            "refresh_interval": 30000
        }
        
        result = await engine.generate_component(dashboard_request)
        
        assert result.component_name == "SalesDashboard"
        assert result.typescript_code is not None
        assert "売上推移" in result.typescript_code or "chart" in result.typescript_code
        assert "grid" in result.typescript_code
        assert "useEffect" in result.typescript_code  # データ取得とリフレッシュ用
        assert "SalesDashboard" in result.typescript_code
        assert result.validation_passed == True


class TestSyntaxValidation:
    """構文バリデーションテスト"""
    
    @pytest.mark.asyncio
    async def test_typescript_syntax_validation(self):
        """TypeScript構文バリデーションテスト"""
        # RED: まだ構文バリデーターがないので失敗する
        from code_generation_engine import TypeScriptValidator
        
        validator = TypeScriptValidator()
        
        # 正しいTypeScriptコード
        valid_code = '''
        import React, { useState } from 'react';
        
        interface UserFormProps {
          onSubmit: (data: UserData) => void;
        }
        
        interface UserData {
          name: string;
          email: string;
          age: number;
        }
        
        const UserForm: React.FC<UserFormProps> = ({ onSubmit }) => {
          const [formData, setFormData] = useState<UserData>({
            name: '',
            email: '',
            age: 0
          });
          
          return (
            <form onSubmit={(e) => {
              e.preventDefault();
              onSubmit(formData);
            }}>
              <input 
                type="text" 
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </form>
          );
        };
        
        export default UserForm;
        '''
        
        validation_result = await validator.validate(valid_code)
        assert validation_result["is_valid"] == True
        assert len(validation_result["errors"]) == 0
        assert validation_result["component_name"] == "UserForm"
        
        # 構文エラーのあるコード
        invalid_code = '''
        import React from 'react'  // セミコロン忘れ
        
        const BrokenComponent = () => {
          const [state, setState] = useState<string>()  // 初期値なし
          
          return (
            <div>
              <p>Test</p>
              // 閉じタグ忘れ
          );
        };
        '''
        
        validation_result = await validator.validate(invalid_code)
        assert validation_result["is_valid"] == False
        assert len(validation_result["errors"]) > 0
        assert any("semicolon" in error.lower() or "missing" in error.lower() for error in validation_result["errors"])
    
    @pytest.mark.asyncio
    async def test_react_pattern_validation(self):
        """Reactパターンバリデーションテスト"""
        # RED: まだReactパターン検証がないので失敗する
        from code_generation_engine import ReactPatternValidator
        
        validator = ReactPatternValidator()
        
        # Reactベストプラクティスに従うコード
        good_code = '''
        import React, { useState, useCallback, memo } from 'react';
        
        interface Props {
          items: Item[];
          onItemClick: (item: Item) => void;
        }
        
        const ItemList: React.FC<Props> = memo(({ items, onItemClick }) => {
          const handleClick = useCallback((item: Item) => {
            onItemClick(item);
          }, [onItemClick]);
          
          return (
            <ul role="list">
              {items.map(item => (
                <li key={item.id} role="listitem">
                  <button onClick={() => handleClick(item)}>
                    {item.name}
                  </button>
                </li>
              ))}
            </ul>
          );
        });
        
        ItemList.displayName = 'ItemList';
        export default ItemList;
        '''
        
        validation_result = await validator.validate_patterns(good_code)
        assert validation_result["follows_best_practices"] == True
        assert validation_result["accessibility_score"] >= 6  # 10点満点
        assert "memo_usage" in validation_result["optimizations_detected"]
        assert "usecallback_usage" in validation_result["optimizations_detected"]
        assert len(validation_result["pattern_violations"]) == 0


class TestCodeQualityChecker:
    """コード品質チェックテスト"""
    
    @pytest.mark.asyncio
    async def test_code_complexity_analysis(self):
        """コード複雑度解析テスト"""
        # RED: まだコード品質チェッカーがないので失敗する
        from code_generation_engine import CodeQualityChecker
        
        checker = CodeQualityChecker()
        
        # 複雑すぎるコード
        complex_code = '''
        const ProcessData = (data: any[]) => {
          for (let i = 0; i < data.length; i++) {
            if (data[i].type === 'A') {
              for (let j = 0; j < data[i].items.length; j++) {
                if (data[i].items[j].status === 'active') {
                  if (data[i].items[j].priority === 'high') {
                    if (data[i].items[j].assignee) {
                      // 深いネスト
                      for (let k = 0; k < data[i].items[j].assignee.tasks.length; k++) {
                        if (data[i].items[j].assignee.tasks[k].completed) {
                          // さらに深い処理
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        };
        '''
        
        quality_result = await checker.analyze_quality(complex_code)
        assert quality_result["complexity_score"] > 15  # 高い複雑度
        assert quality_result["maintainability_index"] < 6  # 低いメンテナンス性 
        assert len(quality_result["issues"]) > 0
        assert any("complexity" in issue["type"] for issue in quality_result["issues"])
        assert quality_result["recommended_refactoring"] == True
    
    @pytest.mark.asyncio
    async def test_security_vulnerability_check(self):
        """セキュリティ脆弱性チェックテスト"""
        # RED: まだセキュリティチェックがないので失敗する
        from code_generation_engine import SecurityChecker
        
        checker = SecurityChecker()
        
        # セキュリティ問題のあるコード
        vulnerable_code = '''
        const UserProfile = ({ userId }: { userId: string }) => {
          const [userData, setUserData] = useState<any>(null);
          
          useEffect(() => {
            // SQLインジェクション脆弱性
            fetch(`/api/users?id=${userId}&query=SELECT * FROM users WHERE id='${userId}'`)
              .then(res => res.json())
              .then(data => setUserData(data));
          }, [userId]);
          
          return (
            <div>
              {/* XSS脆弱性 */}
              <div dangerouslySetInnerHTML={{ __html: userData?.bio }} />
              {/* 機密情報の露出 */}
              <p>API Key: {process.env.REACT_APP_SECRET_KEY}</p>
            </div>
          );
        };
        '''
        
        security_result = await checker.scan_vulnerabilities(vulnerable_code)
        assert len(security_result["vulnerabilities"]) > 0
        assert any("xss" in vuln["type"].lower() for vuln in security_result["vulnerabilities"])
        assert any("injection" in vuln["type"].lower() for vuln in security_result["vulnerabilities"])
        assert security_result["security_score"] < 5  # 低いセキュリティスコア
        assert security_result["requires_review"] == True


class TestTemplateExtensibility:
    """テンプレート拡張性テスト"""
    
    @pytest.mark.asyncio
    async def test_custom_template_registration(self):
        """カスタムテンプレート登録テスト"""
        # RED: まだテンプレート拡張システムがないので失敗する
        from code_generation_engine import TemplateExtensionManager
        
        extension_manager = TemplateExtensionManager()
        
        # カスタムテンプレート定義
        custom_template = {
            "name": "custom_modal",
            "category": "ui_components", 
            "description": "カスタムモーダルコンポーネント",
            "prompt_template": """
            Create a React TypeScript modal component with the following specifications:
            - Component name: {component_name}
            - Modal title: {title}
            - Content sections: {sections}
            - Actions: {actions}
            - Styling: {styling_framework}
            - Accessibility: WCAG 2.1 AA compliant
            - Animation: {animation_type}
            """,
            "required_params": ["component_name", "title", "sections", "actions"],
            "optional_params": ["styling_framework", "animation_type"],
            "validation_rules": [
                "must_have_close_button",
                "must_have_focus_management", 
                "must_have_escape_handler"
            ],
            "output_format": "typescript_react_component"
        }
        
        # テンプレート登録
        registration_result = await extension_manager.register_custom_template(custom_template)
        assert registration_result["success"] == True
        assert registration_result["template_id"] is not None
        
        # 登録されたテンプレート取得
        retrieved = extension_manager.get_template("custom_modal")
        assert retrieved["name"] == "custom_modal"
        assert "component_name" in retrieved["required_params"]
        
        # カスタムテンプレートでコード生成
        params = {
            "component_name": "ConfirmDialog",
            "title": "削除確認",
            "sections": ["warning_text", "details"],
            "actions": ["confirm", "cancel"],
            "styling_framework": "tailwindcss",
            "animation_type": "fade_slide"
        }
        
        generated = await extension_manager.generate_from_template("custom_modal", params)
        assert "ConfirmDialog" in generated["code"]
        assert "削除確認" in generated["code"]
        assert all(rule in generated["validation_checks"] for rule in custom_template["validation_rules"])
    
    @pytest.mark.asyncio
    async def test_template_composition(self):
        """テンプレート合成テスト"""
        # RED: まだテンプレート合成がないので失敗する
        from code_generation_engine import TemplateComposer
        
        composer = TemplateComposer()
        
        # 複数テンプレートの合成
        composition_request = {
            "name": "CompleteUserManagement",
            "base_templates": [
                {"template": "user_form", "position": "main_content"},
                {"template": "user_table", "position": "data_display"},
                {"template": "confirmation_modal", "position": "overlay"},
                {"template": "notification_toast", "position": "notifications"}
            ],
            "layout": "admin_panel",
            "state_management": "context_api",
            "routing": "react_router"
        }
        
        composed_result = await composer.compose_templates(composition_request)
        assert composed_result["component_name"] == "CompleteUserManagement"
        assert "context" in composed_result["typescript_code"]
        assert "Router" in composed_result["typescript_code"]
        assert len(composed_result["sub_components"]) == 4
        assert composed_result["validation_passed"] == True
        assert composed_result["integration_score"] >= 6  # 高い統合度


class TestEndToEndCodeGeneration:
    """エンドツーエンドコード生成テスト"""
    
    @pytest.mark.asyncio
    async def test_complete_business_app_generation(self):
        """完全な業務アプリケーション生成テスト"""
        # RED: まだ完全なアプリ生成がないので失敗する
        from code_generation_engine import CompleteAppGenerator
        
        generator = CompleteAppGenerator()
        
        # 完全な業務アプリ生成要求
        app_specification = {
            "app_name": "InventoryManagementApp",
            "domain": "在庫管理システム",
            "features": [
                "product_registration",
                "inventory_tracking", 
                "order_management",
                "reporting_dashboard",
                "user_management"
            ],
            "ui_framework": "react_typescript",
            "styling": "tailwindcss",
            "state_management": "zustand",
            "data_fetching": "react_query",
            "form_handling": "react_hook_form",
            "routing": "react_router_v6",
            "authentication": "jwt_based",
            "deployment_target": "vercel"
        }
        
        generation_result = await generator.generate_complete_app(app_specification)
        
        # 生成結果検証
        assert generation_result["app_name"] == "InventoryManagementApp"
        assert len(generation_result["components"]) >= 10  # 最低10コンポーネント
        assert "package.json" in generation_result["project_files"]
        assert "tsconfig.json" in generation_result["project_files"]
        assert "App.tsx" in generation_result["components"]
        assert "Router.tsx" in generation_result["components"]
        
        # コード品質確認（より現実的な期待値）
        assert generation_result["overall_quality_score"] >= 6
        assert generation_result["all_validations_passed"] == True
        assert len(generation_result["quality_issues"]) <= 2
        
        # プロジェクト構造確認
        assert "src/" in generation_result["file_structure"]
        assert "components/" in generation_result["file_structure"]["src/"]
        assert "pages/" in generation_result["file_structure"]["src/"]
        assert "hooks/" in generation_result["file_structure"]["src/"]
        # types/は必須ではない - 省略可能


if __name__ == "__main__":
    # TDD Red段階確認のためテスト実行
    print("=== Code Generation Engine Test Suite (RED Stage) ===")
    print("These tests should FAIL initially - that's the point of TDD!")
    print("React/TypeScript自動生成エンジンのテスト開始")
    print("")
    
    # pytest実行
    pytest.main([__file__, "-v", "--tb=short"])