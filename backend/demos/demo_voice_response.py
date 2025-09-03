"""
AI-TTS統合デモ：実際の音声応答生成
札幌なまりの音声応答をテスト
"""

import asyncio
from ai_service import AIService


async def demo_voice_response():
    """音声応答デモ"""
    print("=== AltMX 音声応答デモ ===")
    
    # AIService初期化
    service = AIService()
    
    # デモメッセージ
    demo_messages = [
        "こんにちは！元気ですか？",
        "プログラミングで困ってることある？",
        "一緒にWebアプリ作ってみない？"
    ]
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n【デモ {i}】ユーザー: {message}")
        
        try:
            # 音声応答生成
            result = await service.generate_voice_response(
                message=message,
                use_sapporo_dialect=True
            )
            
            # テキスト応答表示
            print(f"AltMX: {result['text_response']}")
            
            # 音声ファイル保存
            if result['audio_data'] is not None:
                audio_file = f"demo_response_{i}.mp3"
                service.save_voice_response_to_file(result['audio_data'], audio_file)
                print(f"[AUDIO] 音声ファイル保存: {audio_file}")
                print(f"[INFO] 音声サイズ: {len(result['audio_data'].audio_content)} bytes")
            else:
                print("[WARN] 音声データなし")
                
        except Exception as e:
            print(f"[ERROR] エラー: {e}")
    
    # セッション統計表示
    print("\n" + "="*50)
    print("[STATS] セッション統計")
    print("="*50)
    
    stats = service.get_session_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n[SUCCESS] デモ完了！")


if __name__ == "__main__":
    asyncio.run(demo_voice_response())