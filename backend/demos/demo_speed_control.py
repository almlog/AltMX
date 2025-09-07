"""
音声速度調整機能デモ
スライダー風パラメータで速度・ピッチ調整
"""

import asyncio
from ai_service import AIService


async def demo_speed_control():
    """音声速度調整デモ"""
    print("=== AltMX 音声速度調整デモ ===")
    
    service = AIService()
    
    # テスト用メッセージ
    message = "なんまら良い天気だべ〜！今日も札幌は寒いっしょ。"
    
    # 1. 通常速度
    print("\n[デモ1] 通常速度")
    result1 = await service.generate_voice_response(
        message=message,
        voice_speed=0.9,  # 通常速度
        voice_pitch=-2.0  # 通常ピッチ
    )
    service.save_voice_response_to_file(result1['audio_data'], "demo_normal_speed.mp3")
    print(f"通常速度 - サイズ: {len(result1['audio_data'].audio_content)} bytes")
    
    # 2. 高速
    print("\n[デモ2] 1.5倍速")
    result2 = await service.generate_voice_response(
        message=message,
        voice_speed=1.5,  # 1.5倍速
        voice_pitch=0.0   # やや高いピッチ
    )
    service.save_voice_response_to_file(result2['audio_data'], "demo_fast_speed.mp3")
    print(f"高速 - サイズ: {len(result2['audio_data'].audio_content)} bytes")
    
    # 3. 低速
    print("\n[デモ3] 0.7倍速")
    result3 = await service.generate_voice_response(
        message=message,
        voice_speed=0.7,   # 0.7倍速
        voice_pitch=-5.0   # 低いピッチ
    )
    service.save_voice_response_to_file(result3['audio_data'], "demo_slow_speed.mp3")
    print(f"低速 - サイズ: {len(result3['audio_data'].audio_content)} bytes")
    
    # 4. プリセット使用
    print("\n[デモ4] プリセット「高速」使用")
    result4 = await service.generate_voice_response(
        message=message,
        voice_preset="高速"
    )
    service.save_voice_response_to_file(result4['audio_data'], "demo_preset_fast.mp3")
    print(f"プリセット高速 - サイズ: {len(result4['audio_data'].audio_content)} bytes")
    
    # 5. カスタムプリセット作成・使用
    print("\n[デモ5] カスタムプリセット")
    service.create_voice_preset("超高速札幌", {
        "speaking_rate": 2.0,
        "pitch": 3.0,
        "volume_gain_db": 2.0
    })
    
    result5 = await service.generate_voice_response(
        message=message,
        voice_preset="超高速札幌"
    )
    service.save_voice_response_to_file(result5['audio_data'], "demo_custom_preset.mp3")
    print(f"カスタムプリセット - サイズ: {len(result5['audio_data'].audio_content)} bytes")
    
    # プリセット一覧表示
    print("\n[利用可能なプリセット]")
    presets = service.get_voice_presets()
    for name, config in presets.items():
        print(f"- {name}: 速度={config['speaking_rate']}, ピッチ={config['pitch']}")
    
    # セッション統計
    print("\n[セッション統計]")
    stats = service.get_session_stats()
    print(f"音声応答数: {stats['voice_responses']}")
    print(f"TTS呼び出し数: {stats['tts_calls']}")
    print(f"総音声データ: {stats['total_audio_bytes']} bytes")
    
    print("\n[SUCCESS] 音声速度調整機能デモ完了！")


if __name__ == "__main__":
    asyncio.run(demo_speed_control())