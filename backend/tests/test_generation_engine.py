"""
Code Generation Engine Tests - Red段階（失敗するテスト）
メインエンジン統合テスト
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass
from typing import List, Optional

# 実装済みモジュールインポート
from code_generation.engine import CodeGenerationEngine, GenerationRequest, GenerationResult
from code_generation.response_parser import CodeBlock, ParsedCode
from code_generation.validators import ValidationResult, ValidationError
from ai_integration.llm_client import LLMResponse




class TestCodeGenerationEngine:
    """メインエンジンテスト"""
    
    @pytest.fixture
    def engine(self):
        """エンジンインスタンス"""
        return CodeGenerationEngine()
    
    @pytest.fixture
    def sample_request(self):
        """サンプルリクエスト"""
        return GenerationRequest(
            user_prompt="Create a React login form with email and password validation",
            complexity="medium",
            include_security=True
        )
    
    def test_engine_initialization(self, engine):
        """エンジン初期化テスト"""
        assert engine is not None
        assert hasattr(engine, 'prompt_template')
        assert hasattr(engine, 'prompt_optimizer')
        assert hasattr(engine, 'llm_client')
        assert hasattr(engine, 'response_parser')
        assert hasattr(engine, 'validator')
        assert hasattr(engine, 'corrector')
        assert hasattr(engine, 'file_organizer')
    
    @pytest.mark.asyncio
    async def test_full_generation_pipeline_success(self, engine, sample_request):
        """完全な生成パイプライン成功テスト"""
        result = await engine.generate_code(sample_request)
        
        assert result.success is True
        assert len(result.generated_files) > 0
        assert result.errors == [] or result.errors is None
        
        # ファイル構造チェック
        filenames = [f['filename'] for f in result.generated_files]
        assert any('.tsx' in f for f in filenames)
        
        # 生成されたファイル内容チェック
        for file_info in result.generated_files:
            assert 'filename' in file_info
            assert 'content' in file_info
            assert 'language' in file_info
            assert file_info['content'].strip() != ""
    
    @pytest.mark.asyncio
    async def test_generation_with_validation_errors(self, engine):
        """バリデーションエラー付き生成テスト"""
        bad_request = GenerationRequest(
            user_prompt="Generate broken code with syntax errors",
            complexity="low"
        )
        
        result = await engine.generate_code(bad_request)
        
        # バリデーションエラーがあっても結果は返される
        assert result is not None
        if not result.success:
            assert len(result.errors) > 0
        else:
            # 自動修正が成功した場合
            assert result.warnings is not None
    
    @pytest.mark.asyncio
    async def test_complex_generation_request(self, engine):
        """複雑な生成リクエストテスト"""
        complex_request = GenerationRequest(
            user_prompt="Create a complete React dashboard with charts, data tables, user management, and API integration",
            complexity="high",
            include_security=True,
            include_accessibility=True
        )
        
        result = await engine.generate_code(complex_request)
        
        assert result is not None
        if result.success:
            assert len(result.generated_files) >= 3  # 複数ファイル期待
            assert result.performance_metrics is not None
        
    @pytest.mark.asyncio
    async def test_error_handling_ai_failure(self, engine, sample_request):
        """AI呼び出し失敗時のエラーハンドリング"""
        with patch('ai_integration.llm_client.LLMClient.generate_code') as mock_llm:
            mock_llm.side_effect = Exception("AI service unavailable")
            
            result = await engine.generate_code(sample_request)
            
            assert result.success is False
            assert "AI service" in str(result.errors) or "unavailable" in str(result.errors)
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, engine, sample_request):
        """パフォーマンス測定テスト"""
        result = await engine.generate_code(sample_request)
        
        if result.success:
            assert result.performance_metrics is not None
            assert 'total_time' in result.performance_metrics
            assert 'ai_generation_time' in result.performance_metrics
            assert 'validation_time' in result.performance_metrics
            assert 'parsing_time' in result.performance_metrics


class TestEngineIntegration:
    """エンジン統合テスト"""
    
    @pytest.fixture
    def engine(self):
        return CodeGenerationEngine()
    
    @pytest.mark.asyncio
    async def test_prompt_to_code_flow(self, engine):
        """プロンプト→コード変換フローテスト"""
        request = GenerationRequest(
            user_prompt="Simple React counter component"
        )
        
        result = await engine.generate_code(request)
        
        # 基本的なReactコンポーネント生成確認
        if result.success:
            generated_content = ' '.join([f['content'] for f in result.generated_files])
            assert 'React' in generated_content or 'useState' in generated_content
    
    @pytest.mark.asyncio
    async def test_security_validation_integration(self, engine):
        """セキュリティ検証統合テスト"""
        request = GenerationRequest(
            user_prompt="Create a component that uses dangerouslySetInnerHTML",
            include_security=True
        )
        
        result = await engine.generate_code(request)
        
        # セキュリティリスクがある場合は警告またはエラー
        if 'dangerouslySetInnerHTML' in str(result.generated_files):
            assert result.warnings is not None or not result.success
    
    @pytest.mark.asyncio 
    async def test_file_organization_integration(self, engine):
        """ファイル構成統合テスト"""
        request = GenerationRequest(
            user_prompt="Create a React app with multiple components and types"
        )
        
        result = await engine.generate_code(request)
        
        if result.success and len(result.generated_files) > 1:
            filenames = [f['filename'] for f in result.generated_files]
            
            # 適切なファイル名が生成されているか
            assert any('.tsx' in f or '.ts' in f for f in filenames)
            
            # 重複ファイル名がないか
            assert len(filenames) == len(set(filenames))


class TestEngineErrorHandling:
    """エンジンエラーハンドリングテスト"""
    
    @pytest.fixture
    def engine(self):
        return CodeGenerationEngine()
    
    @pytest.mark.asyncio
    async def test_invalid_request_handling(self, engine):
        """無効なリクエスト処理テスト"""
        invalid_request = GenerationRequest(user_prompt="")
        
        result = await engine.generate_code(invalid_request)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "prompt" in str(result.errors).lower() or "empty" in str(result.errors).lower()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, engine):
        """タイムアウト処理テスト"""
        timeout_request = GenerationRequest(
            user_prompt="Create extremely complex application with 50 components"
        )
        
        # タイムアウト設定でテスト
        result = await engine.generate_code(timeout_request, timeout=1)  # 1秒でタイムアウト
        
        # タイムアウトしても適切に処理される
        assert result is not None


class TestEngineLogging:
    """エンジンログテスト"""
    
    @pytest.fixture
    def engine(self):
        return CodeGenerationEngine()
    
    @pytest.mark.asyncio
    async def test_logging_integration(self, engine, caplog):
        """ログ統合テスト"""
        request = GenerationRequest(user_prompt="Simple component")
        
        await engine.generate_code(request)
        
        # ログが適切に出力されているか
        assert len(caplog.records) > 0
        log_messages = [record.message for record in caplog.records]
        assert any("generation" in msg.lower() for msg in log_messages)


class TestEngineConfiguration:
    """エンジン設定テスト"""
    
    def test_engine_with_custom_config(self):
        """カスタム設定エンジンテスト"""
        custom_config = {
            'max_file_count': 10,
            'enable_auto_correction': True,
            'timeout_seconds': 30
        }
        
        engine = CodeGenerationEngine(config=custom_config)
        
        assert engine.config['max_file_count'] == 10
        assert engine.config['enable_auto_correction'] is True
        assert engine.config['timeout_seconds'] == 30
    
    def test_default_configuration(self):
        """デフォルト設定テスト"""
        engine = CodeGenerationEngine()
        
        assert engine.config is not None
        assert 'max_file_count' in engine.config
        assert 'enable_auto_correction' in engine.config
        assert 'timeout_seconds' in engine.config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])