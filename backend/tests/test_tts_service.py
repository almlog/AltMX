"""
TTS Service Tests (TDD)
テストファースト！まずは失敗するテストを書く
"""

import pytest
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceConfig:
    """音声設定データクラス"""
    language_code: str = "ja-JP"
    name: str = "ja-JP-Standard-A"
    ssml_gender: str = "FEMALE"
    speaking_rate: float = 0.9
    pitch: float = -2.0
    volume_gain_db: float = 0.0


@dataclass 
class AudioData:
    """音声データ"""
    audio_content: bytes
    format: str
    sample_rate: int


class TestTTSServiceBasics:
    """TTSService基本機能テスト"""
    
    def test_tts_service_import(self):
        """TTSServiceがインポートできること"""
        from tts_service import TTSService
        assert TTSService is not None
    
    def test_tts_service_initialization(self):
        """TTSServiceが正しく初期化されること"""
        from tts_service import TTSService
        
        service = TTSService()
        assert service is not None
        assert hasattr(service, 'client')
        assert hasattr(service, 'voice_config')
    
    def test_voice_config_default_values(self):
        """VoiceConfigのデフォルト値が正しいこと"""
        from tts_service import VoiceConfig
        
        config = VoiceConfig()
        assert config.language_code == "ja-JP"
        assert config.name == "ja-JP-Standard-A"
        assert config.ssml_gender == "FEMALE"
        assert config.speaking_rate == 0.9
        assert config.pitch == -2.0


class TestTTSServiceSynthesis:
    """音声合成機能テスト"""
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_basic(self):
        """基本的な音声合成が動作すること"""
        from tts_service import TTSService, AudioData
        
        service = TTSService()
        
        # 基本的なテキスト合成
        result = await service.synthesize_speech(
            text="こんにちは",
            use_sapporo_style=False
        )
        
        assert result is not None
        assert isinstance(result, AudioData)
        assert len(result.audio_content) > 0
        assert result.format in ["MP3", "WAV"]
    
    @pytest.mark.asyncio
    async def test_synthesize_speech_with_sapporo_style(self):
        """札幌なまりスタイルでの音声合成"""
        from tts_service import TTSService, AudioData
        
        service = TTSService()
        
        result = await service.synthesize_speech(
            text="なんまらいい天気だべ",
            use_sapporo_style=True
        )
        
        assert result is not None
        assert isinstance(result, AudioData)
        assert len(result.audio_content) > 0
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """空のテキストのハンドリング"""
        from tts_service import TTSService
        
        service = TTSService()
        
        with pytest.raises(ValueError) as exc_info:
            await service.synthesize_speech("")
        
        assert "テキストが空です" in str(exc_info.value)


class TestSSMLEnhancement:
    """SSML強化機能テスト"""
    
    def test_create_ssml_markup_basic(self):
        """基本的なSSMLマークアップ生成"""
        from tts_service import TTSService
        
        service = TTSService()
        
        ssml = service._create_ssml_markup("こんにちは")
        
        assert ssml.startswith('<speak>')
        assert ssml.endswith('</speak>')
        assert 'こんにちは' in ssml
    
    def test_enhance_sapporo_pronunciation(self):
        """札幌なまり発音強化テスト"""
        from tts_service import TTSService
        
        service = TTSService()
        
        # 札幌なまり特有の表現をテスト
        test_cases = [
            ("なんまらいい", "emphasis"),
            ("そだね〜", "prosody"),
            ("だべさ", "phoneme"),
            ("っしょ", "phoneme")
        ]
        
        for text, expected_tag in test_cases:
            ssml = service._create_ssml_markup(text, enhance_sapporo=True)
            assert expected_tag in ssml.lower()
    
    def test_ssml_escaping(self):
        """SSML特殊文字のエスケープ処理"""
        from tts_service import TTSService
        
        service = TTSService()
        
        text_with_special_chars = "A&B < C > D"
        ssml = service._create_ssml_markup(text_with_special_chars)
        
        assert "&amp;" in ssml
        assert "&lt;" in ssml
        assert "&gt;" in ssml


class TestVoiceConfiguration:
    """音声設定テスト"""
    
    def test_get_voice_config_default(self):
        """デフォルト音声設定取得"""
        from tts_service import TTSService
        
        service = TTSService()
        config = service._get_voice_config()
        
        assert config.language_code == "ja-JP"
        assert config.speaking_rate == 0.9
        assert config.pitch == -2.0
    
    def test_voice_config_customization(self):
        """カスタム音声設定"""
        from tts_service import TTSService
        
        custom_config = VoiceConfig(
            name="ja-JP-Standard-B",
            speaking_rate=1.0,
            pitch=0.0
        )
        
        service = TTSService(voice_config=custom_config)
        config = service._get_voice_config()
        
        assert config.name == "ja-JP-Standard-B"
        assert config.speaking_rate == 1.0
        assert config.pitch == 0.0


class TestErrorHandling:
    """エラーハンドリングテスト"""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """API エラーのハンドリング"""
        from tts_service import TTSService
        
        service = TTSService()
        
        # API エラーをシミュレート
        with patch.object(service, '_call_tts_api', side_effect=Exception("API Error")):
            with pytest.raises(Exception) as exc_info:
                await service.synthesize_speech("テスト")
            
            assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self):
        """ネットワークタイムアウトのハンドリング"""
        from tts_service import TTSService
        
        service = TTSService()
        
        # タイムアウトをシミュレート
        with patch.object(service, '_call_tts_api', side_effect=asyncio.TimeoutError()):
            with pytest.raises(asyncio.TimeoutError):
                await service.synthesize_speech("テスト")


class TestPerformance:
    """パフォーマンステスト"""
    
    @pytest.mark.asyncio
    async def test_synthesis_response_time(self):
        """音声合成のレスポンス時間テスト"""
        import time
        from tts_service import TTSService
        
        service = TTSService()
        
        start_time = time.time()
        result = await service.synthesize_speech("短いテスト")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 1秒以内での応答を要求
        assert response_time < 1.0
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_long_text_handling(self):
        """長いテキストのハンドリング"""
        from tts_service import TTSService
        
        service = TTSService()
        
        long_text = "札幌なまりで話すAIエンジニアです。" * 50
        
        result = await service.synthesize_speech(long_text)
        
        assert result is not None
        assert len(result.audio_content) > 0


if __name__ == "__main__":
    print("=== TTS Service Test Suite (TDD) ===")
    print("Red段階: 失敗するテストを実行")
    
    # pytest実行
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])