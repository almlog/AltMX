"""
Test suite for Code Validation System - TDD実装
生成コードの構文・型・品質検証のテスト
"""

import pytest
from unittest.mock import Mock, patch, call
import tempfile
import os
from code_generation.validators import CodeValidator, ValidationResult, ValidationError
from code_generation.security_validator import SecurityValidator, SecurityRisk
from code_generation.code_corrector import CodeCorrector, CorrectionSuggestion
from code_generation.response_parser import CodeBlock


class TestValidationResult:
    """ValidationResultクラスのテスト"""
    
    def test_validation_result_creation(self):
        """ValidationResult作成テスト"""
        result = ValidationResult(
            is_valid=True,
            syntax_errors=[],
            type_errors=[],
            lint_errors=["Missing semicolon"],
            security_risks=[],
            performance_warnings=["Unused variable"]
        )
        
        assert result.is_valid is True
        assert len(result.syntax_errors) == 0
        assert len(result.lint_errors) == 1
        assert result.lint_errors[0] == "Missing semicolon"
        assert len(result.performance_warnings) == 1
    
    def test_validation_result_overall_validity(self):
        """全体的な有効性判定テスト"""
        # 有効なケース
        valid_result = ValidationResult(is_valid=True)
        assert valid_result.get_overall_status() == "valid"
        
        # 警告ありケース
        warning_result = ValidationResult(is_valid=True, performance_warnings=["Warning"])
        assert warning_result.get_overall_status() == "valid_with_warnings"
        
        # エラーありケース
        error_result = ValidationResult(is_valid=False, syntax_errors=["Error"])
        assert error_result.get_overall_status() == "invalid"


class TestValidationError:
    """ValidationErrorクラスのテスト"""
    
    def test_validation_error_creation(self):
        """ValidationError作成テスト"""
        error = ValidationError(
            filename="App.tsx",
            line=10,
            column=5,
            message="Unexpected token",
            error_type="syntax",
            severity="error"
        )
        
        assert error.filename == "App.tsx"
        assert error.line == 10
        assert error.column == 5
        assert error.message == "Unexpected token"
        assert error.error_type == "syntax"
        assert error.severity == "error"
    
    def test_validation_error_formatting(self):
        """ValidationError文字列フォーマットテスト"""
        error = ValidationError(
            filename="utils.ts",
            line=15,
            column=8,
            message="Variable 'x' is never used",
            error_type="lint",
            severity="warning"
        )
        
        formatted = error.format()
        assert "utils.ts:15:8" in formatted
        assert "Variable 'x' is never used" in formatted
        assert "warning" in formatted.lower()


class TestCodeValidator:
    """CodeValidatorクラスのテスト"""
    
    @pytest.fixture
    def validator(self):
        """テスト用CodeValidator"""
        return CodeValidator()
    
    def test_typescript_syntax_validation_success(self, validator):
        """TypeScript構文検証成功テスト"""
        valid_code = """
        import React from 'react';
        
        interface Props {
          name: string;
          age: number;
        }
        
        const Component: React.FC<Props> = ({ name, age }) => {
          return <div>Hello {name}, you are {age} years old</div>;
        };
        
        export default Component;
        """
        
        block = CodeBlock(content=valid_code, filename="Component.tsx", language="typescript")
        result = validator.validate_typescript_syntax(block)
        
        assert result.is_valid is True
        assert len(result.syntax_errors) == 0
        assert len(result.type_errors) == 0
    
    def test_typescript_syntax_validation_failure(self, validator):
        """TypeScript構文検証失敗テスト"""
        invalid_code = """
        import React from 'react';
        
        const Component = () => {
          const unclosed = {
            name: "test"
            // missing closing brace
          return <div>Hello</div>;
        };
        """
        
        block = CodeBlock(content=invalid_code, filename="Invalid.tsx", language="typescript")
        result = validator.validate_typescript_syntax(block)
        
        assert result.is_valid is False
        assert len(result.syntax_errors) > 0
        assert any("brace" in error.message.lower() or "}" in error.message for error in result.syntax_errors)
    
    def test_eslint_validation_success(self, validator):
        """ESLint検証成功テスト"""
        clean_code = """
        import React from 'react';
        
        const CleanComponent = () => {
          return <div>Clean code</div>;
        };
        
        export default CleanComponent;
        """
        
        block = CodeBlock(content=clean_code, filename="Clean.tsx", language="typescript")
        result = validator.validate_eslint(block)
        
        assert result.is_valid is True
        assert len(result.lint_errors) == 0
    
    def test_eslint_validation_failure(self, validator):
        """ESLint検証失敗テスト"""
        messy_code = """
        import React from 'react'
        
        const MessyComponent = () => {
          const unusedVariable = 'never used';
          var oldStyle = 'should use const/let';
          
          return <div>Messy code</div>
        }
        
        export default MessyComponent
        """
        
        block = CodeBlock(content=messy_code, filename="Messy.tsx", language="typescript")
        result = validator.validate_eslint(block)
        
        assert result.is_valid is False
        assert len(result.lint_errors) > 0
        assert any("unused" in error.message.lower() or "semicolon" in error.message.lower() for error in result.lint_errors)
    
    def test_comprehensive_validation(self, validator):
        """包括的検証テスト"""
        code_block = CodeBlock(
            content="""
            import React, { useState } from 'react';
            
            const App = () => {
              const [count, setCount] = useState(0);
              
              return (
                <div>
                  <h1>Count: {count}</h1>
                  <button onClick={() => setCount(count + 1)}>Increment</button>
                </div>
              );
            };
            
            export default App;
            """,
            filename="App.tsx",
            language="typescript"
        )
        
        result = validator.validate_comprehensive(code_block)
        
        assert result.is_valid is True
        assert len(result.syntax_errors) == 0
        assert len(result.type_errors) == 0
        # 軽微なlint警告があっても全体は有効
    
    def test_multiple_files_validation(self, validator):
        """複数ファイル検証テスト"""
        blocks = [
            CodeBlock(
                content="export interface User { id: number; name: string; }",
                filename="types.ts",
                language="typescript"
            ),
            CodeBlock(
                content="""
                import React from 'react';
                import { User } from './types';
                
                const UserComponent: React.FC<{ user: User }> = ({ user }) => (
                  <div>{user.name}</div>
                );
                
                export default UserComponent;
                """,
                filename="UserComponent.tsx",
                language="typescript"
            )
        ]
        
        results = validator.validate_multiple_files(blocks)
        
        assert len(results) == 2
        for result in results:
            assert result.is_valid is True
    
    def test_validation_with_external_dependencies(self, validator):
        """外部依存関係ありの検証テスト"""
        code_with_deps = """
        import React from 'react';
        import axios from 'axios';
        import { clsx } from 'clsx';
        
        const ApiComponent = () => {
          const fetchData = async () => {
            const response = await axios.get('/api/data');
            return response.data;
          };
          
          return (
            <div className={clsx('container', 'active')}>
              API Component
            </div>
          );
        };
        
        export default ApiComponent;
        """
        
        block = CodeBlock(content=code_with_deps, filename="ApiComponent.tsx", language="typescript")
        
        # 外部依存関係を考慮した検証
        result = validator.validate_with_dependencies(block, ['axios', 'clsx'])
        
        assert result.is_valid is True
        # 外部依存関係のimportエラーが発生しないことを確認


class TestSecurityValidator:
    """SecurityValidatorクラスのテスト"""
    
    @pytest.fixture
    def security_validator(self):
        """テスト用SecurityValidator"""
        return SecurityValidator()
    
    def test_xss_detection(self, security_validator):
        """XSS脆弱性検知テスト"""
        vulnerable_code = """
        import React from 'react';
        
        const UnsafeComponent = ({ userInput }) => {
          return (
            <div dangerouslySetInnerHTML={{ __html: userInput }} />
          );
        };
        """
        
        block = CodeBlock(content=vulnerable_code, filename="Unsafe.tsx")
        risks = security_validator.scan_security_risks(block)
        
        assert len(risks) > 0
        xss_risk = next((risk for risk in risks if risk.risk_type == "xss"), None)
        assert xss_risk is not None
        assert xss_risk.severity in ["high", "critical"]
        assert "dangerouslySetInnerHTML" in xss_risk.recommendation
    
    def test_sql_injection_detection(self, security_validator):
        """SQLインジェクション検知テスト"""
        vulnerable_code = """
        const executeQuery = (userId) => {
          const query = `SELECT * FROM users WHERE id = ${userId}`;
          return database.query(query);
        };
        """
        
        block = CodeBlock(content=vulnerable_code, filename="database.ts")
        risks = security_validator.scan_security_risks(block)
        
        sql_injection_risk = next((risk for risk in risks if risk.risk_type == "sql_injection"), None)
        assert sql_injection_risk is not None
        assert sql_injection_risk.severity in ["high", "critical"]
    
    def test_eval_usage_detection(self, security_validator):
        """eval使用検知テスト"""
        dangerous_code = """
        const processUserCode = (code) => {
          return eval(code); // Dangerous!
        };
        
        const createFunction = (body) => {
          return new Function('return ' + body)(); // Also dangerous!
        };
        """
        
        block = CodeBlock(content=dangerous_code, filename="dangerous.js")
        risks = security_validator.scan_security_risks(block)
        
        eval_risks = [risk for risk in risks if risk.risk_type == "code_injection"]
        assert len(eval_risks) >= 1  # eval and Function constructor
    
    def test_safe_code_no_risks(self, security_validator):
        """安全なコードでリスクなしテスト"""
        safe_code = """
        import React from 'react';
        
        const SafeComponent = ({ name, email }) => {
          const handleSubmit = (e) => {
            e.preventDefault();
            // Safe form handling
          };
          
          return (
            <form onSubmit={handleSubmit}>
              <input type="text" value={name} readOnly />
              <input type="email" value={email} readOnly />
              <button type="submit">Submit</button>
            </form>
          );
        };
        """
        
        block = CodeBlock(content=safe_code, filename="Safe.tsx")
        risks = security_validator.scan_security_risks(block)
        
        critical_risks = [risk for risk in risks if risk.severity == "critical"]
        assert len(critical_risks) == 0
    
    def test_comprehensive_security_scan(self, security_validator):
        """包括的セキュリティスキャンテスト"""
        mixed_code = """
        import React from 'react';
        
        const MixedComponent = ({ userHtml, userScript }) => {
          // XSS risk
          const dangerousDiv = <div dangerouslySetInnerHTML={{ __html: userHtml }} />;
          
          // Code injection risk
          const result = eval(userScript);
          
          // Safe operations
          const safeDiv = <div>{userHtml}</div>; // Escaped by React
          
          return (
            <div>
              {dangerousDiv}
              {safeDiv}
            </div>
          );
        };
        """
        
        block = CodeBlock(content=mixed_code, filename="Mixed.tsx")
        risks = security_validator.scan_security_risks(block)
        
        assert len(risks) >= 2  # XSS + Code injection
        risk_types = {risk.risk_type for risk in risks}
        assert "xss" in risk_types
        assert "code_injection" in risk_types


class TestCodeCorrector:
    """CodeCorrectorクラスのテスト"""
    
    @pytest.fixture
    def corrector(self):
        """テスト用CodeCorrector"""
        return CodeCorrector()
    
    def test_fix_missing_semicolons(self, corrector):
        """セミコロン不足修正テスト"""
        code_without_semicolons = """
        const name = 'John'
        const age = 30
        const greeting = `Hello, ${name}`
        
        function greet() {
          return greeting
        }
        """
        
        block = CodeBlock(content=code_without_semicolons, filename="nosemi.ts")
        corrected = corrector.fix_common_issues(block)
        
        assert corrected is not None
        assert corrected.content.count(';') > 0
        # 各行の終わりにセミコロンが追加されていることを確認
        lines = corrected.content.split('\n')
        declaration_lines = [line for line in lines if line.strip() and not line.strip().startswith('}')]
        assert any(line.strip().endswith(';') for line in declaration_lines)
    
    def test_fix_missing_imports(self, corrector):
        """import不足修正テスト"""
        code_missing_imports = """
        const Component = () => {
          const [count, setCount] = useState(0);
          
          return (
            <div>
              <h1>Count: {count}</h1>
              <button onClick={() => setCount(count + 1)}>Click</button>
            </div>
          );
        };
        """
        
        block = CodeBlock(content=code_missing_imports, filename="missing_imports.tsx")
        corrected = corrector.fix_common_issues(block)
        
        assert corrected is not None
        assert "import React" in corrected.content
        assert "useState" in corrected.content
        # ReactとuseStateのimportが追加されていることを確認
    
    def test_fix_type_annotations(self, corrector):
        """型注釈修正テスト"""
        code_missing_types = """
        const Component = ({ name, age, onSave }) => {
          const handleClick = (event) => {
            onSave({ name, age });
          };
          
          return <button onClick={handleClick}>Save {name}</button>;
        };
        """
        
        block = CodeBlock(content=code_missing_types, filename="no_types.tsx")
        corrected = corrector.fix_common_issues(block)
        
        assert corrected is not None
        # 基本的な型注釈が追加されていることを確認
        assert ": React.FC" in corrected.content or "React.ComponentProps" in corrected.content or "interface" in corrected.content
    
    def test_get_correction_suggestions(self, corrector):
        """修正提案取得テスト"""
        problematic_code = """
        import React from 'react'
        
        const BadComponent = ({ data }) => {
          var oldStyleVar = 'bad'
          const unused = 'never used'
          
          return <div dangerouslySetInnerHTML={{__html: data}} />
        }
        """
        
        block = CodeBlock(content=problematic_code, filename="bad.tsx")
        suggestions = corrector.get_correction_suggestions(block)
        
        assert len(suggestions) > 0
        
        # 各種修正提案があることを確認
        suggestion_types = {s.correction_type for s in suggestions}
        expected_types = {"lint", "security", "style"}
        assert len(suggestion_types.intersection(expected_types)) > 0
        
        # セキュリティ関連の提案があることを確認
        security_suggestions = [s for s in suggestions if s.correction_type == "security"]
        assert len(security_suggestions) > 0
    
    def test_apply_corrections_selectively(self, corrector):
        """選択的修正適用テスト"""
        code = """
        const component = ({ name }) => {
          const unused = 'variable'
          return <div>{name}</div>
        }
        """
        
        block = CodeBlock(content=code, filename="selective.tsx")
        
        # セミコロンのみ修正
        corrected = corrector.apply_specific_corrections(block, ["semicolons"])
        assert corrected.content.count(';') > 0
        assert "unused" in corrected.content  # unused variable は修正されない
        
        # 未使用変数のみ修正
        corrected2 = corrector.apply_specific_corrections(block, ["unused_variables"])
        assert "// const unused" in corrected2.content  # コメントアウトされている


class TestValidationIntegration:
    """検証システム統合テスト"""
    
    def test_full_validation_pipeline(self):
        """完全な検証パイプラインテスト"""
        validator = CodeValidator()
        security_validator = SecurityValidator()
        corrector = CodeCorrector()
        
        code_block = CodeBlock(
            content="""
            import React from 'react'
            
            const TodoApp = ({ initialTodos }) => {
              const [todos, setTodos] = useState(initialTodos)
              const [input, setInput] = useState('')
              
              const addTodo = () => {
                if (input.trim()) {
                  setTodos([...todos, { id: Date.now(), text: input, done: false }])
                  setInput('')
                }
              }
              
              return (
                <div className="todo-app">
                  <input value={input} onChange={e => setInput(e.target.value)} />
                  <button onClick={addTodo}>Add</button>
                  <ul>
                    {todos.map(todo => (
                      <li key={todo.id} className={todo.done ? 'done' : ''}>
                        {todo.text}
                      </li>
                    ))}
                  </ul>
                </div>
              )
            }
            
            export default TodoApp
            """,
            filename="TodoApp.tsx",
            language="typescript"
        )
        
        # 1. 基本検証
        validation_result = validator.validate_comprehensive(code_block)
        
        # 2. セキュリティスキャン
        security_risks = security_validator.scan_security_risks(code_block)
        
        # 3. 修正提案
        corrections = corrector.get_correction_suggestions(code_block)
        
        # 4. 自動修正適用
        corrected_block = corrector.fix_common_issues(code_block)
        
        # 結果確認
        assert validation_result is not None
        assert len(security_risks) == 0 or all(risk.severity != "critical" for risk in security_risks)
        assert corrected_block is not None
        assert len(corrected_block.content) > len(code_block.content)  # imports等が追加される
    
    def test_error_handling_robustness(self):
        """エラーハンドリング堅牢性テスト"""
        validator = CodeValidator()
        
        # 完全に壊れたコード
        broken_code = CodeBlock(
            content="This is not code at all!!! {{{{ invalid syntax",
            filename="broken.tsx",
            language="typescript"
        )
        
        # エラーが発生しても例外をスローしないことを確認
        result = validator.validate_comprehensive(broken_code)
        assert result is not None
        assert result.is_valid is False
        assert len(result.syntax_errors) > 0
    
    def test_performance_validation(self):
        """パフォーマンス検証テスト"""
        validator = CodeValidator()
        
        # パフォーマンス問題のあるコード
        performance_issues = CodeBlock(
            content="""
            import React from 'react';
            
            const SlowComponent = ({ items }) => {
              // 毎回新しいオブジェクトを作成（パフォーマンス問題）
              const expensiveComputation = () => {
                return items.map(item => ({
                  ...item,
                  processed: true
                }));
              };
              
              return (
                <div>
                  {items.map(item => (
                    <div key={Math.random()}> {/* 非効率なkey */}
                      <ExpensiveChild data={expensiveComputation()} />
                    </div>
                  ))}
                </div>
              );
            };
            """,
            filename="SlowComponent.tsx",
            language="typescript"
        )
        
        result = validator.validate_comprehensive(performance_issues)
        
        # パフォーマンス警告が含まれていることを確認
        assert len(result.performance_warnings) > 0
        warnings_text = ' '.join(w.message for w in result.performance_warnings)
        assert any(keyword in warnings_text.lower() for keyword in ["key", "computation", "optimization"])