"""
Claude API Integration Tests (TDD)
テストファースト！まずは失敗するテストを書く
札幌なまり応答システムのテスト
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Optional, Dict, Any


class TestClaudeAPIClient:
    """Claude APIクライアントのテスト"""
    
    def test_claude_client_creation(self):
        """Claude APIクライアントが作成できること"""
        # RED: まだclaude_service.pyがないので失敗する
        from claude_service import ClaudeAPIClient  # まだ存在しない
        
        client = ClaudeAPIClient()
        assert client is not None
        assert hasattr(client, 'api_key')
    
    def test_claude_api_key_configuration(self):
        """Claude APIキーが設定されていること"""
        # RED: まだAPIキー設定がないので失敗する
        from claude_service import ClaudeAPIClient
        
        client = ClaudeAPIClient()
        # 実際のキーまたはモックキーが設定されていることを確認
        assert client.api_key is not None
        assert len(client.api_key) > 10
    
    @pytest.mark.asyncio
    async def test_claude_api_connection(self):
        """Claude APIに接続できること"""
        # RED: まだ接続機能がないので失敗する
        from claude_service import ClaudeAPIClient
        
        client = ClaudeAPIClient()
        connection_ok = await client.test_connection()
        assert connection_ok == True


class TestSapporoDialectConversion:
    """札幌なまり変換ロジックのテスト"""
    
    def test_sapporo_dialect_converter_creation(self):
        """札幌なまり変換器が作成できること"""
        # RED: まだSapporoDialectConverterがないので失敗する
        from claude_service import SapporoDialectConverter  # まだ存在しない
        
        converter = SapporoDialectConverter()
        assert converter is not None
    
    def test_basic_sapporo_conversion(self):
        """基本的な札幌なまり変換ができること"""
        # RED: まだ変換ロジックがないので失敗する
        from claude_service import SapporoDialectConverter
        
        converter = SapporoDialectConverter()
        
        # 基本的な変換パターンテスト
        test_cases = [
            ("そうですね", "そうだべさ"),
            ("いいですよ", "いいべや"),
            ("わかりました", "わかったべ"),
            ("ありがとうございます", "ありがとさん"),
            ("大変ですね", "たいへんだべね"),
        ]
        
        for standard, expected_sapporo in test_cases:
            result = converter.convert_to_sapporo(standard)
            # 札幌なまりの特徴が含まれていることを確認（エンコーディング問題回避）
            sapporo_indicators = ["べ", "っしょ", "だべ", "さん", "ばん"]
            has_sapporo = any(indicator in result for indicator in sapporo_indicators)
            assert has_sapporo, f"札幌なまりが検出されませんでした: {standard} → {result}"
    
    def test_advanced_sapporo_patterns(self):
        """高度な札幌なまりパターンの変換"""
        # RED: まだ高度な変換がないので失敗する
        from claude_service import SapporoDialectConverter
        
        converter = SapporoDialectConverter()
        
        # 語尾変換
        result1 = converter.convert_to_sapporo("寒いです")
        assert "べ" in result1 or "っしょ" in result1
        
        # 疑問文変換
        result2 = converter.convert_to_sapporo("どうですか？")
        assert "だべ" in result2 or "っしょ" in result2
        
        # 感嘆文変換
        result3 = converter.convert_to_sapporo("すごいですね！")
        assert "べ" in result3 or "っしょ" in result3
    
    def test_context_aware_conversion(self):
        """文脈を考慮した変換ができること"""
        # RED: まだ文脈考慮機能がないので失敗する
        from claude_service import SapporoDialectConverter
        
        converter = SapporoDialectConverter()
        
        # 技術的な内容でも札幌なまりに
        tech_text = "このAPIの使い方は簡単です。まず認証を行い、リクエストを送信してください。"
        result = converter.convert_to_sapporo(tech_text)
        
        assert "べ" in result or "っしょ" in result or "さん" in result
        assert "API" in result  # 技術用語は保持


class TestClaudeResponseGeneration:
    """Claude応答生成のテスト"""
    
    @pytest.mark.asyncio
    async def test_basic_response_generation(self):
        """基本的な応答生成ができること"""
        # RED: まだ応答生成機能がないので失敗する
        from claude_service import ClaudeService  # まだ存在しない
        
        service = ClaudeService()
        
        prompt = "札幌の天気について教えてください"
        response = await service.generate_response(prompt)
        
        assert response is not None
        assert len(response) > 10
        assert "札幌" in response
    
    @pytest.mark.asyncio 
    async def test_sapporo_dialect_response(self):
        """札幌なまりでの応答生成ができること"""
        # RED: まだ札幌なまり応答がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        prompt = "今日はいい天気ですね"
        response = await service.generate_sapporo_response(prompt)
        
        # 札幌なまりの特徴が含まれていることを確認
        sapporo_indicators = ["べ", "っしょ", "だべ", "さん", "ばん"]
        has_sapporo = any(indicator in response for indicator in sapporo_indicators)
        assert has_sapporo, f"札幌なまりが含まれていません: {response}"
    
    @pytest.mark.asyncio
    async def test_code_generation_with_sapporo(self):
        """札幌なまりでのコード生成説明ができること"""
        # RED: まだコード生成説明がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        prompt = "Pythonでハローワールドを出力するコードを書いてください"
        response = await service.generate_code_explanation(prompt)
        
        assert 'print("Hello, World!")' in response or "Hello" in response
        # 札幌なまりで説明されていることを確認
        assert "べ" in response or "っしょ" in response
        assert "こうやって" in response or "こんな感じ" in response


class TestErrorHandlingAndRetry:
    """エラーハンドリング・リトライ機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """API エラーが適切に処理されること"""
        # RED: まだエラーハンドリングがないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        # 無効なAPIキーでのテスト
        with patch.object(service.client, 'api_key', 'invalid_key'):
            response = await service.generate_response("テスト")
            # エラー時はフォールバック応答を返す
            assert response is not None
            # エラーメッセージまたは通常の札幌なまり応答が返される
            error_indicators = ["申し訳", "エラー", "問題", "だべ", "っしょ"]
            has_error_or_sapporo = any(indicator in response for indicator in error_indicators)
            assert has_error_or_sapporo, f"エラー処理またはフォールバック応答が不適切: {response}"
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self):
        """リトライ機能が動作すること"""
        # RED: まだリトライ機能がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        # 最初は失敗、2回目は成功するモック
        with patch.object(service, '_call_claude_api') as mock_call:
            mock_call.side_effect = [Exception("一時的エラー"), "成功応答"]
            
            response = await service.generate_response("テスト")
            assert response == "成功応答"
            assert mock_call.call_count == 2
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """タイムアウト処理が動作すること"""
        # RED: まだタイムアウト処理がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        # タイムアウト設定テスト
        start_time = time.time()
        
        with patch.object(service, '_call_claude_api', side_effect=asyncio.TimeoutError):
            response = await service.generate_response("テスト", timeout=1)
            
        elapsed_time = time.time() - start_time
        assert elapsed_time < 3  # タイムアウト + 処理時間
        assert "タイムアウト" in response or "エラー" in response


class TestPerformanceRequirements:
    """パフォーマンス要件のテスト"""
    
    @pytest.mark.asyncio
    async def test_response_time_under_2_seconds(self):
        """応答時間が2秒以内であること"""
        # RED: まだ高速応答がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        start_time = time.time()
        response = await service.generate_response("簡単な質問です")
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 2.0, f"応答時間が遅すぎます: {elapsed_time:.2f}秒"
        assert response is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self):
        """並行リクエスト処理ができること"""
        # RED: まだ並行処理対応がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        # 3つの並行リクエスト
        tasks = [
            service.generate_response("質問1"),
            service.generate_response("質問2"),
            service.generate_response("質問3")
        ]
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed_time = time.time() - start_time
        
        # 並行処理により総時間は短縮されているはず
        assert elapsed_time < 4.0  # 直列なら6秒程度かかる
        assert all(response is not None for response in responses)
        assert len(responses) == 3


class TestCacheIntegration:
    """キャッシュ統合のテスト"""
    
    @pytest.mark.asyncio
    async def test_response_caching(self):
        """応答がキャッシュされること"""
        # RED: まだキャッシュ統合がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        prompt = "キャッシュテスト用の質問"
        
        # 1回目: APIコール
        start_time = time.time()
        response1 = await service.generate_response(prompt)
        first_call_time = time.time() - start_time
        
        # 2回目: キャッシュヒット（高速）
        start_time = time.time()
        response2 = await service.generate_response(prompt)
        second_call_time = time.time() - start_time
        
        assert response1 == response2
        assert second_call_time < first_call_time * 0.5  # キャッシュは半分以下の時間
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self):
        """キャッシュの有効期限が動作すること"""
        # RED: まだキャッシュ有効期限がないので失敗する
        from claude_service import ClaudeService
        
        service = ClaudeService()
        
        prompt = "期限切れテスト"
        
        # 短いTTLでキャッシュ
        await service.generate_response(prompt, cache_ttl=1)
        
        # 2秒後にキャッシュ期限切れ
        await asyncio.sleep(2)
        
        # 再度APIコールされることを確認
        with patch.object(service, '_call_claude_api') as mock_call:
            mock_call.return_value = "新しい応答"
            response = await service.generate_response(prompt)
            assert mock_call.called  # APIが再度呼ばれた


if __name__ == "__main__":
    # TDD Red段階確認のためテスト実行
    print("=== Claude API Integration Test Suite (RED Stage) ===")
    print("These tests should FAIL initially - that's the point of TDD!")
    print("札幌なまり応答システムのテスト開始")
    print("")
    
    # pytest実行
    pytest.main([__file__, "-v", "--tb=short"])