"""
AI Service + TTS Integration Tests (TDD)
AIServiceとTTSServiceの統合テスト
"""

import pytest
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass


class TestAITTSIntegration:
    """AI-TTS統合テスト"""
    
    @pytest.mark.asyncio
    async def test_ai_service_has_tts_capability(self):
        """AIServiceにTTS機能が追加されていること"""
        from ai_service import AIService
        
        service = AIService()
        
        # TTS関連のメソッドが存在することを確認
        assert hasattr(service, 'generate_voice_response')
        assert hasattr(service, 'tts_service')
    
    @pytest.mark.asyncio
    async def test_generate_voice_response_basic(self):
        """基本的な音声応答生成が動作すること"""
        from ai_service import AIService
        
        service = AIService()
        
        # テキスト応答と音声の両方を取得
        result = await service.generate_voice_response(
            message="こんにちは",
            use_sapporo_dialect=True
        )
        
        assert result is not None
        assert "text_response" in result
        assert "audio_data" in result
        assert len(result["text_response"]) > 0
        assert result["audio_data"] is not None
    
    @pytest.mark.asyncio
    async def test_sapporo_dialect_voice_pipeline(self):
        """札幌なまりの音声パイプラインテスト"""
        from ai_service import AIService
        
        service = AIService()
        
        result = await service.generate_voice_response(
            message="元気ですか？",
            use_sapporo_dialect=True
        )
        
        # テキスト応答に札幌なまりが含まれる
        sapporo_keywords = ["だべ", "っしょ", "なんまら", "そだね"]
        text_response = result["text_response"]
        
        assert any(keyword in text_response for keyword in sapporo_keywords)
        
        # 音声データが生成されている
        assert result["audio_data"] is not None
        assert len(result["audio_data"].audio_content) > 0
    
    @pytest.mark.asyncio
    async def test_text_only_vs_voice_response_consistency(self):
        """テキストのみと音声応答の一貫性テスト"""
        from ai_service import AIService
        
        service = AIService()
        
        # 同じメッセージでテキストのみの応答
        text_only = await service.generate_response(
            message="プログラミングについて教えて",
            use_sapporo_dialect=True
        )
        
        # 音声付き応答
        voice_result = await service.generate_voice_response(
            message="プログラミングについて教えて",
            use_sapporo_dialect=True
        )
        
        # テキスト内容が同じ（キャッシュ利用）
        assert text_only == voice_result["text_response"]
    
    @pytest.mark.asyncio
    async def test_tts_service_initialization(self):
        """TTSServiceが正しく初期化されること"""
        from ai_service import AIService
        
        service = AIService()
        
        # TTSServiceが初期化されている
        assert service.tts_service is not None
        assert hasattr(service.tts_service, 'synthesize_speech')
    
    @pytest.mark.asyncio
    async def test_voice_response_performance(self):
        """音声応答のパフォーマンステスト"""
        import time
        from ai_service import AIService
        
        service = AIService()
        
        start_time = time.time()
        
        result = await service.generate_voice_response(
            message="短いテスト",
            use_sapporo_dialect=True
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 3秒以内での応答（AI応答+音声合成）
        assert response_time < 3.0
        assert result is not None


class TestTTSErrorHandling:
    """TTS統合時のエラーハンドリングテスト"""
    
    @pytest.mark.asyncio
    async def test_tts_failure_fallback(self):
        """TTS失敗時のフォールバック処理"""
        from ai_service import AIService
        
        service = AIService()
        
        # TTSを意図的に失敗させる
        with patch.object(service.tts_service, 'synthesize_speech', side_effect=Exception("TTS Error")):
            result = await service.generate_voice_response(
                message="テスト",
                fallback_to_text=True
            )
            
            # テキスト応答は返される
            assert result["text_response"] is not None
            assert len(result["text_response"]) > 0
            
            # 音声データはNone
            assert result["audio_data"] is None
    
    @pytest.mark.asyncio
    async def test_ai_failure_no_tts_call(self):
        """AI応答失敗時にTTSが呼ばれないこと"""
        from ai_service import AIService
        
        service = AIService()
        
        # AIを意図的に失敗させる
        with patch.object(service, 'generate_response', side_effect=Exception("AI Error")):
            with pytest.raises(Exception) as exc_info:
                await service.generate_voice_response("テスト")
            
            assert "AI Error" in str(exc_info.value)


class TestSessionStatistics:
    """セッション統計の拡張テスト"""
    
    @pytest.mark.asyncio
    async def test_voice_response_statistics(self):
        """音声応答統計が記録されること"""
        from ai_service import AIService
        
        service = AIService()
        
        # 音声応答を実行
        await service.generate_voice_response(
            message="統計テスト",
            use_sapporo_dialect=True
        )
        
        stats = service.get_session_stats()
        
        # TTS統計が追加されている
        assert "tts_calls" in stats
        assert "voice_responses" in stats
        assert "total_audio_bytes" in stats
        
        assert stats["tts_calls"] > 0
        assert stats["voice_responses"] > 0
        assert stats["total_audio_bytes"] > 0


class TestCacheIntegration:
    """キャッシュ統合テスト"""
    
    @pytest.mark.asyncio
    async def test_voice_response_caching(self):
        """音声応答のキャッシュ機能"""
        from ai_service import AIService
        
        service = AIService()
        
        # 初回リクエスト
        result1 = await service.generate_voice_response(
            message="キャッシュテスト",
            use_sapporo_dialect=True
        )
        
        # 同じリクエスト（キャッシュヒットするはず）
        result2 = await service.generate_voice_response(
            message="キャッシュテスト",
            use_sapporo_dialect=True
        )
        
        # テキスト応答が同じ
        assert result1["text_response"] == result2["text_response"]
        
        # 音声データも同じ
        assert result1["audio_data"].audio_content == result2["audio_data"].audio_content
        
        # キャッシュ統計が正しい
        stats = service.get_session_stats()
        assert stats["cache_hits"] > 0


if __name__ == "__main__":
    print("=== AI-TTS Integration Test Suite (TDD) ===")
    print("Red段階: 失敗するテストを実行")
    
    # pytest実行
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])