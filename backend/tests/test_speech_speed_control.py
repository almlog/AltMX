"""
音声再生スピード調整機能テスト (TDD)
speaking_rate, pitchをスライダーで動的調整
"""

import pytest
import asyncio
from ai_service import AIService
from tts_service import TTSService, VoiceConfig


class TestSpeechSpeedControl:
    """音声速度調整機能テスト"""
    
    @pytest.mark.asyncio
    async def test_voice_speed_adjustment_basic(self):
        """基本的な音声速度調整"""
        service = AIService()
        
        # 通常速度
        result_normal = await service.generate_voice_response(
            message="速度テスト",
            voice_speed=1.0  # 通常速度
        )
        
        # 高速
        result_fast = await service.generate_voice_response(
            message="速度テスト",
            voice_speed=1.5  # 1.5倍速
        )
        
        # 低速
        result_slow = await service.generate_voice_response(
            message="速度テスト",
            voice_speed=0.7  # 0.7倍速
        )
        
        # 全て成功
        assert result_normal["audio_data"] is not None
        assert result_fast["audio_data"] is not None
        assert result_slow["audio_data"] is not None
        
        # 速度に応じて音声サイズが変わる（目安）
        normal_size = len(result_normal["audio_data"].audio_content)
        fast_size = len(result_fast["audio_data"].audio_content)
        slow_size = len(result_slow["audio_data"].audio_content)
        
        # 高速は通常より短く、低速は長くなる傾向
        assert fast_size <= normal_size * 1.1  # 多少の差は許容
        assert slow_size >= normal_size * 0.9
    
    @pytest.mark.asyncio
    async def test_voice_pitch_adjustment(self):
        """音声ピッチ調整"""
        service = AIService()
        
        # 通常ピッチ
        result_normal = await service.generate_voice_response(
            message="ピッチテスト",
            voice_pitch=0.0  # 通常
        )
        
        # 高ピッチ
        result_high = await service.generate_voice_response(
            message="ピッチテスト", 
            voice_pitch=5.0  # +5
        )
        
        # 低ピッチ
        result_low = await service.generate_voice_response(
            message="ピッチテスト",
            voice_pitch=-5.0  # -5
        )
        
        # 全て成功
        assert result_normal["audio_data"] is not None
        assert result_high["audio_data"] is not None
        assert result_low["audio_data"] is not None
    
    @pytest.mark.asyncio
    async def test_combined_speed_and_pitch(self):
        """速度とピッチの組み合わせ調整"""
        service = AIService()
        
        result = await service.generate_voice_response(
            message="速度とピッチの組み合わせテスト",
            voice_speed=1.2,  # 1.2倍速
            voice_pitch=2.0   # +2ピッチ
        )
        
        assert result["audio_data"] is not None
        assert result["text_response"] is not None
    
    @pytest.mark.asyncio
    async def test_speed_range_validation(self):
        """音声速度の範囲検証"""
        service = AIService()
        
        # 有効範囲内
        valid_speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        
        for speed in valid_speeds:
            result = await service.generate_voice_response(
                message=f"速度{speed}テスト",
                voice_speed=speed
            )
            assert result["audio_data"] is not None
    
    @pytest.mark.asyncio
    async def test_pitch_range_validation(self):
        """音声ピッチの範囲検証"""
        service = AIService()
        
        # 有効範囲内
        valid_pitches = [-10.0, -5.0, 0.0, 5.0, 10.0]
        
        for pitch in valid_pitches:
            result = await service.generate_voice_response(
                message=f"ピッチ{pitch}テスト",
                voice_pitch=pitch
            )
            assert result["audio_data"] is not None
    
    @pytest.mark.asyncio
    async def test_invalid_speed_handling(self):
        """無効な速度値のハンドリング"""
        service = AIService()
        
        # 範囲外の値はデフォルトに調整される
        result = await service.generate_voice_response(
            message="無効速度テスト",
            voice_speed=10.0  # 範囲外
        )
        
        # エラーではなく調整される
        assert result["audio_data"] is not None


class TestTTSServiceSpeedControl:
    """TTSService単体での速度調整テスト"""
    
    @pytest.mark.asyncio
    async def test_tts_custom_voice_config(self):
        """カスタム音声設定でのTTS"""
        # カスタム設定
        custom_config = VoiceConfig(
            speaking_rate=1.5,  # 1.5倍速
            pitch=3.0,         # +3ピッチ
            volume_gain_db=2.0  # 音量+2dB
        )
        
        tts_service = TTSService(voice_config=custom_config)
        
        result = await tts_service.synthesize_speech(
            text="カスタム設定テストだべ",
            use_sapporo_style=True
        )
        
        assert result is not None
        assert len(result.audio_content) > 0
    
    @pytest.mark.asyncio
    async def test_dynamic_voice_config_override(self):
        """動的音声設定の上書き"""
        tts_service = TTSService()
        
        # 動的設定でオーバーライド
        result = await tts_service.synthesize_speech_with_config(
            text="動的設定テスト",
            speaking_rate=0.8,
            pitch=-2.0,
            use_sapporo_style=True
        )
        
        assert result is not None
        assert len(result.audio_content) > 0


class TestVoiceConfigPresets:
    """音声設定プリセット機能テスト"""
    
    def test_voice_preset_creation(self):
        """音声プリセット作成"""
        service = AIService()
        
        # プリセット作成
        service.create_voice_preset("高速札幌", {
            "speaking_rate": 1.8,
            "pitch": 1.0,
            "volume_gain_db": 1.0
        })
        
        service.create_voice_preset("ゆっくり札幌", {
            "speaking_rate": 0.6,
            "pitch": -3.0,
            "volume_gain_db": 0.0
        })
        
        # プリセット取得
        presets = service.get_voice_presets()
        
        assert "高速札幌" in presets
        assert "ゆっくり札幌" in presets
        assert presets["高速札幌"]["speaking_rate"] == 1.8
        assert presets["ゆっくり札幌"]["speaking_rate"] == 0.6
    
    @pytest.mark.asyncio
    async def test_voice_preset_usage(self):
        """音声プリセット使用"""
        service = AIService()
        
        # プリセット作成
        service.create_voice_preset("テスト用", {
            "speaking_rate": 1.3,
            "pitch": 2.5,
            "volume_gain_db": 1.5
        })
        
        # プリセット使用
        result = await service.generate_voice_response(
            message="プリセットテストだべ〜",
            voice_preset="テスト用"
        )
        
        assert result["audio_data"] is not None


if __name__ == "__main__":
    print("=== 音声速度調整機能テストスイート (TDD) ===")
    print("Red段階: 失敗するテストを実行")
    
    # pytest実行
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])