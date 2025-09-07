"""
Google Cloud Speech-to-Text API Integration Tests (TDD)
テストファースト！まずは失敗するテストを書く
リアルタイム音声認識とノイズキャンセリング機能
"""

import pytest
import asyncio
import time
import io
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, Optional, AsyncIterator
import wave


class TestGoogleSTTSetup:
    """Google STT API設定とクライアント作成テスト"""
    
    def test_google_stt_client_creation(self):
        """Google STT APIクライアントが作成できること"""
        # RED: まだ高度なSTTクライアントがないので失敗する
        from stt_service import AdvancedSTTService  # まだ存在しない
        
        service = AdvancedSTTService()
        assert service is not None
        assert hasattr(service, 'speech_client')
        assert hasattr(service, 'streaming_config')
    
    def test_google_stt_credentials_setup(self):
        """Google STT認証情報が適切に設定されていること"""
        # RED: まだ認証設定チェックがないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        credentials_valid = service.validate_credentials()
        
        assert credentials_valid == True
        assert service.get_quota_status()["remaining"] > 0
    
    def test_streaming_recognition_config(self):
        """ストリーミング認識設定が正しく構成されること"""
        # RED: まだストリーミング設定がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        config = service.get_streaming_config()
        
        assert config["language_code"] == "ja-JP"
        assert config["sample_rate_hertz"] == 16000
        assert config["audio_channel_count"] == 1
        assert config["enable_automatic_punctuation"] == True


class TestStreamingAudioRecognition:
    """ストリーミング音声認識テスト"""
    
    @pytest.mark.asyncio
    async def test_basic_streaming_recognition(self):
        """基本的なストリーミング音声認識機能"""
        # RED: まだストリーミング認識がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # モック音声データ（WAV形式）
        audio_data = self._create_mock_audio_data("こんにちは札幌")
        
        # ストリーミング認識実行
        recognized_text = await service.stream_recognize(audio_data)
        
        assert recognized_text is not None
        assert "こんにちは" in recognized_text
        assert len(recognized_text) > 0
    
    @pytest.mark.asyncio
    async def test_realtime_transcription(self):
        """リアルタイム文字起こし機能"""
        # RED: まだリアルタイム処理がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # リアルタイム文字起こし開始
        transcription_stream = service.start_realtime_transcription()
        
        # 音声データを段階的に送信
        audio_chunks = [
            self._create_mock_audio_data("こんにちは"),
            self._create_mock_audio_data("今日の"),
            self._create_mock_audio_data("天気はどうですか")
        ]
        
        results = []
        for chunk in audio_chunks:  # audio_chunksはlistなので通常のfor文を使用
            partial_result = await transcription_stream.process_audio_chunk(chunk)
            results.append(partial_result)
        
        # 最終結果取得
        final_text = await transcription_stream.finalize()
        
        assert len(results) == 3
        assert "こんにちは今日の天気はどうですか" in final_text
    
    @pytest.mark.asyncio
    async def test_streaming_with_confidence_scores(self):
        """信頼度スコア付きストリーミング認識"""
        # RED: まだ信頼度スコアがないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        audio_data = self._create_mock_audio_data("札幌の天気は晴れです")
        
        # 信頼度スコア付き認識
        result = await service.stream_recognize_with_confidence(audio_data)
        
        assert "text" in result
        assert "confidence" in result
        assert result["confidence"] >= 0.0
        assert result["confidence"] <= 1.0
        assert "札幌" in result["text"]
    
    def _create_mock_audio_data(self, text_content: str) -> bytes:
        """モック音声データ作成（テスト用）"""
        # WAVフォーマットのモックデータ作成
        sample_rate = 16000
        duration = 2.0  # 2秒
        
        # 簡単なWAVヘッダー + データ
        import struct
        
        data_size = int(sample_rate * duration * 2)  # 16-bit mono
        
        # WAV header
        header = struct.pack('<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16,
            1, 1, sample_rate, sample_rate * 2, 2, 16,
            b'data', data_size
        )
        
        # 音声データ（サイン波でモック）
        import math
        audio_samples = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))  # 440Hz tone
            audio_samples.append(struct.pack('<h', value))
        
        return header + b''.join(audio_samples)


class TestNoiseCancellation:
    """ノイズキャンセリング機能テスト"""
    
    @pytest.mark.asyncio
    async def test_noise_reduction_processing(self):
        """ノイズ除去処理機能"""
        # RED: まだノイズ除去がないので失敗する
        from stt_service import AudioNoiseReducer  # まだ存在しない
        
        reducer = AudioNoiseReducer()
        
        # ノイズの多い音声データ
        noisy_audio = self._create_noisy_audio_data()
        
        # ノイズ除去処理
        cleaned_audio = await reducer.reduce_noise(noisy_audio)
        
        assert len(cleaned_audio) > 0
        assert cleaned_audio != noisy_audio  # 処理されて変化している
        
        # ノイズ除去品質チェック
        noise_level_before = reducer.calculate_noise_level(noisy_audio)
        noise_level_after = reducer.calculate_noise_level(cleaned_audio)
        
        assert noise_level_after < noise_level_before
    
    @pytest.mark.asyncio
    async def test_adaptive_noise_cancellation(self):
        """適応的ノイズキャンセリング機能"""
        # RED: まだ適応的処理がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 環境ノイズを含む音声
        audio_with_noise = self._create_noisy_audio_data()
        
        # 適応的ノイズキャンセリング付き認識
        result = await service.recognize_with_noise_cancellation(
            audio_with_noise,
            adaptive=True,
            noise_sensitivity=0.8
        )
        
        assert result["text"] is not None
        assert result["noise_reduction_applied"] == True
        assert result["original_noise_level"] > result["processed_noise_level"]
    
    @pytest.mark.asyncio  
    async def test_multiple_noise_types_handling(self):
        """複数種類ノイズ対応テスト"""
        # RED: まだ複数ノイズ対応がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 異なる種類のノイズパターン
        noise_patterns = {
            "traffic": self._create_traffic_noise(),
            "office": self._create_office_noise(),
            "wind": self._create_wind_noise()
        }
        
        for noise_type, noisy_audio in noise_patterns.items():
            result = await service.recognize_with_adaptive_filtering(
                noisy_audio,
                noise_profile=noise_type
            )
            
            assert result["recognized_text"] is not None
            assert result["noise_type_detected"] == noise_type
    
    def _create_noisy_audio_data(self) -> bytes:
        """ノイズありモック音声データ"""
        # 基本音声 + ノイズのモック
        clean_audio = self._create_mock_audio_data("テストメッセージ")
        
        # ノイズ追加（簡単な実装）
        import random
        noise_data = bytearray(clean_audio)
        
        # ランダムノイズ追加（バイト範囲を正しく処理）
        for i in range(len(noise_data)):
            if i % 4 == 0:  # 4バイトごとにノイズ
                original_value = noise_data[i]
                noise = random.randint(-20, 20)
                new_value = original_value + noise
                # 0-255の範囲に収める
                noise_data[i] = max(0, min(255, new_value))
        
        return bytes(noise_data)
    
    def _create_traffic_noise(self) -> bytes:
        """交通ノイズモック"""
        return self._create_noisy_audio_data()
    
    def _create_office_noise(self) -> bytes:
        """オフィスノイズモック"""
        return self._create_noisy_audio_data()
    
    def _create_wind_noise(self) -> bytes:
        """風ノイズモック"""
        return self._create_noisy_audio_data()
    
    def _create_mock_audio_data(self, text_content: str) -> bytes:
        """基本音声データ作成"""
        # 前のテストクラスと同じ実装
        sample_rate = 16000
        duration = 2.0
        
        import struct
        data_size = int(sample_rate * duration * 2)
        
        header = struct.pack('<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16,
            1, 1, sample_rate, sample_rate * 2, 2, 16,
            b'data', data_size
        )
        
        import math
        audio_samples = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            audio_samples.append(struct.pack('<h', value))
        
        return header + b''.join(audio_samples)


class TestRecognitionAccuracy:
    """音声認識精度テスト"""
    
    @pytest.mark.asyncio
    async def test_recognition_accuracy_measurement(self):
        """認識精度測定機能"""
        # RED: まだ精度測定がないので失敗する
        from stt_service import RecognitionAccuracyTester  # まだ存在しない
        
        tester = RecognitionAccuracyTester()
        
        # テストデータセット
        test_cases = [
            ("こんにちは", self._create_mock_audio_data("こんにちは")),
            ("札幌の天気", self._create_mock_audio_data("札幌の天気")),
            ("ありがとうございます", self._create_mock_audio_data("ありがとうございます"))
        ]
        
        # 精度テスト実行
        accuracy_results = await tester.run_accuracy_test(test_cases)
        
        assert "overall_accuracy" in accuracy_results
        assert accuracy_results["overall_accuracy"] >= 0.8  # 80%以上
        assert "test_results" in accuracy_results
        assert len(accuracy_results["test_results"]) == 3
    
    @pytest.mark.asyncio
    async def test_dialect_recognition_accuracy(self):
        """札幌方言認識精度テスト"""
        # RED: まだ方言認識がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 札幌方言のテストケース
        dialect_tests = [
            "なんまらいい天気だべ",
            "そだね〜、めんこいね",
            "ザンギ食べたっしょ？"
        ]
        
        results = []
        for dialect_text in dialect_tests:
            audio = self._create_mock_audio_data(dialect_text)
            result = await service.recognize_sapporo_dialect(audio)
            results.append({
                "expected": dialect_text,
                "recognized": result["text"],
                "confidence": result["confidence"]
            })
        
        # 方言認識精度チェック
        for result in results:
            assert result["confidence"] >= 0.7  # 70%以上の信頼度
            # 主要な方言単語が認識されているか
            if "なんまら" in result["expected"]:
                assert "なんまら" in result["recognized"]
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """負荷下での性能テスト"""
        # RED: まだ負荷テストがないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 並行音声認識テスト
        concurrent_tasks = []
        test_audio = self._create_mock_audio_data("パフォーマンステスト")
        
        start_time = time.time()
        
        # 10個の並行認識タスク
        for i in range(10):
            task = service.stream_recognize(test_audio)
            concurrent_tasks.append(task)
        
        results = await asyncio.gather(*concurrent_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # パフォーマンス要件チェック
        assert total_time < 5.0  # 5秒以内
        assert len(results) == 10
        assert all(result is not None for result in results)
    
    @pytest.mark.asyncio
    async def test_continuous_recognition_stability(self):
        """連続認識安定性テスト"""
        # RED: まだ連続認識がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 長時間連続認識シミュレーション
        continuous_session = await service.start_continuous_recognition()
        
        # 30回連続で音声を処理
        results = []
        for i in range(30):
            audio_chunk = self._create_mock_audio_data(f"テスト{i}")
            result = await continuous_session.process_chunk(audio_chunk)
            results.append(result)
            
            # 短い間隔をシミュレート
            await asyncio.sleep(0.1)
        
        await continuous_session.stop()
        
        # 安定性チェック
        assert len(results) == 30
        successful_recognitions = [r for r in results if r is not None]
        success_rate = len(successful_recognitions) / len(results)
        
        assert success_rate >= 0.9  # 90%以上の成功率
    
    def _create_mock_audio_data(self, text_content: str) -> bytes:
        """モック音声データ作成"""
        # 同じ実装を再利用
        sample_rate = 16000
        duration = 2.0
        
        import struct
        data_size = int(sample_rate * duration * 2)
        
        header = struct.pack('<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16,
            1, 1, sample_rate, sample_rate * 2, 2, 16,
            b'data', data_size
        )
        
        import math
        audio_samples = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            audio_samples.append(struct.pack('<h', value))
        
        return header + b''.join(audio_samples)


class TestAdvancedSTTFeatures:
    """高度なSTT機能テスト"""
    
    @pytest.mark.asyncio
    async def test_language_detection(self):
        """言語検出機能"""
        # RED: まだ言語検出がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 複数言語のテストケース
        test_audios = {
            "ja": self._create_mock_audio_data("こんにちは"),
            "en": self._create_mock_audio_data("hello"),
            "ko": self._create_mock_audio_data("안녕하세요")
        }
        
        for expected_lang, audio in test_audios.items():
            result = await service.detect_and_recognize(audio)
            
            assert result["detected_language"] == expected_lang
            assert result["confidence"] >= 0.7
    
    @pytest.mark.asyncio
    async def test_speaker_identification(self):
        """話者識別機能"""
        # RED: まだ話者識別がないので失敗する
        from stt_service import AdvancedSTTService
        
        service = AdvancedSTTService()
        
        # 話者登録
        speaker1_audio = self._create_mock_audio_data("話者1のテスト音声")
        speaker2_audio = self._create_mock_audio_data("話者2のテスト音声")
        
        await service.register_speaker("speaker1", speaker1_audio)
        await service.register_speaker("speaker2", speaker2_audio)
        
        # 話者識別テスト
        test_audio = self._create_mock_audio_data("識別テスト")
        result = await service.recognize_with_speaker_id(test_audio)
        
        assert "speaker_id" in result
        assert "text" in result
        assert result["speaker_id"] in ["speaker1", "speaker2", "unknown"]
    
    @pytest.mark.asyncio
    async def test_emotion_detection_in_speech(self):
        """音声感情検出機能"""
        # RED: まだ感情検出がないので失敗する
        from stt_service import SpeechEmotionAnalyzer  # まだ存在しない
        
        analyzer = SpeechEmotionAnalyzer()
        
        # 感情別音声データ
        emotions_audio = {
            "happy": self._create_mock_audio_data("うれしい！"),
            "sad": self._create_mock_audio_data("悲しいです..."),
            "angry": self._create_mock_audio_data("なんで！？")
        }
        
        for expected_emotion, audio in emotions_audio.items():
            result = await analyzer.detect_emotion(audio)
            
            assert result["primary_emotion"] == expected_emotion
            assert result["confidence"] >= 0.6
            assert "emotion_scores" in result
    
    def _create_mock_audio_data(self, text_content: str) -> bytes:
        """モック音声データ作成"""
        sample_rate = 16000
        duration = 2.0
        
        import struct
        data_size = int(sample_rate * duration * 2)
        
        header = struct.pack('<4sI4s4sIHHIIHH4sI',
            b'RIFF', 36 + data_size, b'WAVE', b'fmt ', 16,
            1, 1, sample_rate, sample_rate * 2, 2, 16,
            b'data', data_size
        )
        
        import math
        audio_samples = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            audio_samples.append(struct.pack('<h', value))
        
        return header + b''.join(audio_samples)


if __name__ == "__main__":
    # TDD Red段階確認のためテスト実行
    print("=== Google STT Integration Test Suite (RED Stage) ===")
    print("These tests should FAIL initially - that's the point of TDD!")
    print("リアルタイム音声認識とノイズキャンセリング機能のテスト開始")
    print("")
    
    # pytest実行
    pytest.main([__file__, "-v", "--tb=short"])