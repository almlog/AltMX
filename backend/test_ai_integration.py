"""
AI Integration Tests (TDD)
テストファースト！まずは失敗するテストを書く
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from config import config, AIProvider


class TestConfigValidation:
    """設定の検証テスト"""
    
    def test_gemini_api_key_is_set(self):
        """Gemini APIキーが設定されていること"""
        assert config.GEMINI_API_KEY is not None
        assert len(config.GEMINI_API_KEY) > 20  # 適切な長さ
        assert config.GEMINI_API_KEY != "your_actual_gemini_api_key_here"
    
    def test_primary_provider_is_gemini(self):
        """プライマリプロバイダーがGeminiであること"""
        assert config.PRIMARY_AI_PROVIDER == "gemini"
        assert config.get_active_provider() == AIProvider.GEMINI
    
    def test_fallback_is_enabled(self):
        """フォールバック機能が有効であること"""
        assert config.ENABLE_FALLBACK == True
    
    def test_config_validation_passes(self):
        """設定の検証が通ること"""
        assert config.validate() == True


class TestGeminiAPIIntegration:
    """Gemini API統合テスト"""
    
    @pytest.mark.asyncio
    async def test_gemini_connection(self):
        """Gemini APIに接続できること"""
        from ai_service import AIService  # まだ存在しない
        
        service = AIService()
        result = await service.test_connection(AIProvider.GEMINI)
        assert result == True
    
    @pytest.mark.asyncio
    async def test_gemini_simple_response(self):
        """Geminiから基本的な応答を得られること"""
        from ai_service import AIService
        
        service = AIService()
        response = await service.generate_response(
            "こんにちは",
            provider=AIProvider.GEMINI
        )
        
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_sapporo_dialect_in_response(self):
        """札幌なまりで応答すること"""
        from ai_service import AIService
        
        service = AIService()
        response = await service.generate_response(
            "元気ですか？",
            use_sapporo_dialect=True
        )
        
        # 札幌なまりの特徴的な表現を含むか
        sapporo_keywords = ["だべ", "っしょ", "なんまら", "そだね"]
        assert any(keyword in response for keyword in sapporo_keywords)


class TestAIServiceFallback:
    """フォールバック機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_fallback_to_claude_on_gemini_error(self):
        """Geminiエラー時にClaudeへフォールバックすること"""
        from ai_service import AIService
        
        service = AIService()
        
        # Geminiを意図的に失敗させる
        with patch.object(service, '_call_gemini', side_effect=Exception("API Error")):
            response = await service.generate_response("テスト")
            
            # 応答が返ってくる（Claudeから）
            assert response is not None
            assert len(response) > 0
    
    @pytest.mark.asyncio  
    async def test_fallback_disabled_when_configured(self):
        """フォールバックが無効時はエラーを伝播すること"""
        from ai_service import AIService
        
        # フォールバックを一時的に無効化
        original = config.ENABLE_FALLBACK
        config.ENABLE_FALLBACK = False
        
        try:
            service = AIService()
            
            with patch.object(service, '_call_gemini', side_effect=Exception("API Error")):
                with pytest.raises(Exception) as exc_info:
                    await service.generate_response("テスト")
                
                assert "API Error" in str(exc_info.value)
        finally:
            config.ENABLE_FALLBACK = original


class TestCostMonitoring:
    """コスト監視機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_token_counting(self):
        """トークン数がカウントされること"""
        from ai_service import AIService
        
        service = AIService()
        response = await service.generate_response("短いテスト")
        
        assert service.get_session_stats()["total_tokens"] > 0
        assert service.get_session_stats()["api_calls"] == 1
    
    @pytest.mark.asyncio
    async def test_cost_estimation_for_claude(self):
        """Claude使用時のコスト推定が機能すること"""
        from ai_service import AIService
        
        service = AIService()
        
        # Claudeを強制的に使用
        response = await service.generate_response(
            "テスト",
            provider=AIProvider.CLAUDE
        )
        
        stats = service.get_session_stats()
        assert "estimated_cost_jpy" in stats
        assert stats["estimated_cost_jpy"] >= 0


if __name__ == "__main__":
    # 設定の確認から始める
    print("=== AI Integration Test Suite ===")
    print(f"Primary Provider: {config.PRIMARY_AI_PROVIDER}")
    print(f"Gemini API Key: {'OK' if config.GEMINI_API_KEY else 'Not Set'}")
    print(f"Claude API Key: {'OK' if config.CLAUDE_API_KEY else 'Not Set'}")
    print("")
    
    # pytest実行
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])