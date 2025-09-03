"""
Google Cloud Text-to-Speech API 接続テスト
認証とAPI疎通確認
"""

import os
import sys
from google.cloud import texttospeech
from dotenv import load_dotenv

def test_tts_connection():
    """TTS API接続テスト"""
    print("=== Google Cloud TTS 接続テスト ===")
    
    # 環境変数読み込み
    load_dotenv()
    
    # 環境変数確認
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"Project ID: {project_id}")
    print(f"Credentials Path: {credentials_path}")
    
    # 認証情報ファイル確認
    if not os.path.exists(credentials_path):
        print(f"[ERROR] 認証ファイルが見つかりません: {credentials_path}")
        return False
    
    print("[OK] 認証ファイル確認OK")
    
    try:
        # TTS Client初期化
        print("\n[INFO] TTS Client初期化中...")
        client = texttospeech.TextToSpeechClient()
        
        # 利用可能な音声一覧取得テスト
        print("[INFO] 利用可能な音声一覧取得中...")
        voices = client.list_voices()
        
        # 日本語音声のカウント
        japanese_voices = [voice for voice in voices.voices if 'ja-JP' in voice.language_codes]
        print(f"[OK] 日本語音声数: {len(japanese_voices)}種類")
        
        # 音声の詳細表示
        print("\n[INFO] 利用可能な日本語音声:")
        for voice in japanese_voices[:5]:  # 最初の5つのみ表示
            print(f"  - {voice.name} ({voice.ssml_gender})")
        
        # 簡単な音声合成テスト
        print("\n[INFO] 音声合成テスト中...")
        
        synthesis_input = texttospeech.SynthesisInput(text="こんにちは、なんまらいい天気だべ！")
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name="ja-JP-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,
            pitch=-2.0
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        print(f"[OK] 音声合成成功！音声データサイズ: {len(response.audio_content)} bytes")
        
        # テスト音声ファイル保存
        test_audio_path = "test_sapporo_voice.mp3"
        with open(test_audio_path, "wb") as out:
            out.write(response.audio_content)
        
        print(f"[INFO] テスト音声保存: {test_audio_path}")
        print("[SUCCESS] Google Cloud TTS接続テスト完全成功！")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] TTS接続エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_tts_connection()
    sys.exit(0 if success else 1)