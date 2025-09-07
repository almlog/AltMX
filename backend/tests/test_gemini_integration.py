"""
Gemini API Integration & Fallback Tests (TDD)
テストファースト！まずは失敗するテストを書く
Claude障害時のフォールバックシステム
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Optional, Dict, Any


class TestGeminiAPIClient:
    """Gemini APIクライアントのテスト"""
    
    def test_gemini_client_creation(self):
        """Gemini APIクライアントが作成できること"""
        # RED: まだgemini_service.pyがないので失敗する
        from gemini_service import GeminiAPIClient  # まだ存在しない
        
        client = GeminiAPIClient()
        assert client is not None
        assert hasattr(client, 'api_key')
    
    def test_gemini_api_key_configuration(self):
        """Gemini APIキーが設定されていること"""
        # RED: まだAPIキー設定がないので失敗する
        from gemini_service import GeminiAPIClient
        
        client = GeminiAPIClient()
        assert client.api_key is not None
        assert len(client.api_key) > 10
    
    @pytest.mark.asyncio
    async def test_gemini_api_connection(self):
        """Gemini APIに接続できること"""
        # RED: まだ接続機能がないので失敗する
        from gemini_service import GeminiAPIClient
        
        client = GeminiAPIClient()
        connection_ok = await client.test_connection()
        assert connection_ok == True
    
    @pytest.mark.asyncio
    async def test_gemini_response_generation(self):
        """Gemini APIで応答生成ができること"""
        # RED: まだ応答生成機能がないので失敗する
        from gemini_service import GeminiAPIClient
        
        client = GeminiAPIClient()
        response = await client.generate_response("テスト質問")
        
        assert response is not None
        assert len(response) > 5
        assert isinstance(response, str)


class TestCircuitBreakerPattern:
    """Circuit Breakerパターンのテスト"""
    
    def test_circuit_breaker_creation(self):
        """Circuit Breakerが作成できること"""
        # RED: まだCircuitBreakerがないので失敗する
        from ai_service import CircuitBreaker  # まだ存在しない
        
        breaker = CircuitBreaker(failure_threshold=3, timeout=60)
        assert breaker is not None
        assert breaker.failure_threshold == 3
        assert breaker.timeout == 60
    
    def test_circuit_breaker_closed_state(self):
        """Circuit Breaker初期状態（Closed）のテスト"""
        # RED: まだ状態管理がないので失敗する
        from ai_service import CircuitBreaker, CircuitBreakerState
        
        breaker = CircuitBreaker(failure_threshold=3, timeout=60)
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.can_execute() == True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_failure_counting(self):
        """Circuit Breakerの失敗回数カウントテスト"""
        # RED: まだ失敗カウント機能がないので失敗する
        from ai_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=2, timeout=60)
        
        # 1回目の失敗
        await breaker.record_failure()
        assert breaker.failure_count == 1
        assert breaker.can_execute() == True
        
        # 2回目の失敗でOpen状態に
        await breaker.record_failure()
        assert breaker.failure_count == 2
        assert breaker.can_execute() == False  # Open状態
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_success_reset(self):
        """Circuit Breaker成功時のリセットテスト"""
        # RED: まだ成功時リセット機能がないので失敗する
        from ai_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=3, timeout=60)
        
        # 失敗をカウント
        await breaker.record_failure()
        assert breaker.failure_count == 1
        
        # 成功でカウントリセット
        await breaker.record_success()
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_timeout_recovery(self):
        """Circuit Breakerタイムアウト後の回復テスト"""
        # RED: まだタイムアウト回復機能がないので失敗する
        from ai_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=1, timeout=1)  # 1秒タイムアウト
        
        # 失敗でOpen状態に
        await breaker.record_failure()
        assert breaker.can_execute() == False
        
        # 1.5秒後にHalf-Open状態に
        await asyncio.sleep(1.5)
        assert breaker.can_execute() == True  # Half-Open状態では実行可能


class TestAIServiceIntegration:
    """AI サービス統合のテスト"""
    
    def test_ai_service_creation(self):
        """統合AIサービスが作成できること"""
        # RED: まだAIServiceがないので失敗する
        from ai_service import AIService  # まだ存在しない
        
        service = AIService()
        assert service is not None
        assert hasattr(service, 'claude_client')
        assert hasattr(service, 'gemini_client')
        assert hasattr(service, 'circuit_breaker')
    
    @pytest.mark.asyncio
    async def test_primary_provider_claude(self):
        """プライマリプロバイダー（Claude）での応答生成"""
        # RED: まだプライマリプロバイダー機能がないので失敗する
        from ai_service import AIService
        
        service = AIService(primary_provider="claude")
        response = await service.generate_response("こんにちは")
        
        assert response is not None
        # Claudeが使用されたことを確認
        assert "べ" in response or "っしょ" in response  # 札幌なまり
    
    @pytest.mark.asyncio
    async def test_fallback_to_gemini(self):
        """Claude障害時のGeminiフォールバック"""
        # RED: まだフォールバック機能がないので失敗する
        from ai_service import AIService
        
        service = AIService(primary_provider="claude")
        
        # Claudeを無効化
        with patch.object(service.claude_client, 'generate_response', side_effect=Exception("Claude障害")):
            response = await service.generate_response("テスト")
            
            assert response is not None
            # Geminiにフォールバックされた
            assert service.current_provider == "gemini"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Circuit BreakerとAI統合のテスト"""
        # RED: まだCircuit Breaker統合がないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        # 複数回の失敗でCircuit Breakerが作動
        with patch.object(service.claude_client, 'generate_response', side_effect=Exception("API障害")):
            # 失敗を重ねる
            for i in range(3):
                try:
                    await service.generate_response("テスト")
                except:
                    pass
            
            # Circuit BreakerがOpen状態
            assert service.circuit_breaker.can_execute() == False
            
            # 自動的にGeminiにフォールバック
            response = await service.generate_response("テスト")
            assert response is not None
            assert service.current_provider == "gemini"


class TestFallbackSwitching:
    """フォールバック自動切り替えのテスト"""
    
    @pytest.mark.asyncio
    async def test_automatic_provider_switching(self):
        """プロバイダーの自動切り替えテスト"""
        # RED: まだ自動切り替えがないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        # 初期はClaude
        assert service.current_provider == "claude"
        
        # Claude障害をシミュレート
        await service._switch_provider("gemini", reason="claude_failure")
        
        assert service.current_provider == "gemini"
    
    @pytest.mark.asyncio
    async def test_provider_recovery_detection(self):
        """プロバイダー回復の検出テスト"""
        # RED: まだ回復検出機能がないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        # Geminiにフォールバック
        await service._switch_provider("gemini", reason="claude_failure")
        
        # Claudeの回復をテスト
        recovery_ok = await service._test_provider_recovery("claude")
        
        if recovery_ok:
            # 自動的にClaude に復帰
            await service._switch_provider("claude", reason="recovery")
            assert service.current_provider == "claude"
    
    @pytest.mark.asyncio
    async def test_fallback_response_consistency(self):
        """フォールバック応答の一貫性テスト"""
        # RED: まだ応答一貫性機能がないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        prompt = "札幌の天気について教えてください"
        
        # Claude応答
        claude_response = await service._generate_with_claude(prompt)
        
        # Gemini応答
        gemini_response = await service._generate_with_gemini(prompt)
        
        # 両方とも札幌なまり応答であること
        assert "べ" in claude_response or "っしょ" in claude_response
        assert "べ" in gemini_response or "っしょ" in gemini_response
        
        # 内容が関連していること
        assert "札幌" in claude_response
        assert "札幌" in gemini_response or "天気" in gemini_response


class TestPerformanceAndReliability:
    """パフォーマンスと信頼性のテスト"""
    
    @pytest.mark.asyncio
    async def test_fallback_response_time(self):
        """フォールバック応答時間のテスト"""
        # RED: まだ高速フォールバックがないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        # Claude障害時の応答時間測定
        with patch.object(service.claude_client, 'generate_response', side_effect=Exception("障害")):
            start_time = time.time()
            response = await service.generate_response("テスト")
            elapsed_time = time.time() - start_time
            
            # フォールバック込みで3秒以内
            assert elapsed_time < 3.0
            assert response is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_failover_handling(self):
        """並行フェイルオーバー処理のテスト"""
        # RED: まだ並行フェイルオーバーがないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        # 複数の並行リクエスト中の障害
        with patch.object(service.claude_client, 'generate_response', side_effect=Exception("障害")):
            tasks = [
                service.generate_response(f"質問{i}")
                for i in range(5)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 全て正常に応答（Geminiフォールバック）
            for response in responses:
                assert not isinstance(response, Exception)
                assert response is not None
    
    @pytest.mark.asyncio
    async def test_error_rate_monitoring(self):
        """エラー率監視のテスト"""
        # RED: まだエラー率監視がないので失敗する
        from ai_service import AIService
        
        service = AIService()
        
        # エラー率統計の確認
        stats = await service.get_error_statistics()
        
        assert "claude_error_rate" in stats
        assert "gemini_error_rate" in stats
        assert "total_requests" in stats
        assert "successful_requests" in stats
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        """ヘルスチェック統合のテスト"""
        # RED: まだヘルスチェック統合がないので失敗する
        from ai_service import get_ai_service_health
        
        health = await get_ai_service_health()
        
        assert "claude_status" in health
        assert "gemini_status" in health
        assert "current_provider" in health
        assert "circuit_breaker_state" in health
        
        # 各ステータスは "healthy" または "unhealthy"
        assert health["claude_status"] in ["healthy", "unhealthy"]
        assert health["gemini_status"] in ["healthy", "unhealthy"]


if __name__ == "__main__":
    # TDD Red段階確認のためテスト実行
    print("=== Gemini API Integration & Fallback Test Suite (RED Stage) ===")
    print("These tests should FAIL initially - that's the point of TDD!")
    print("Claude障害時のフォールバックシステムテスト開始")
    print("")
    
    # pytest実行
    pytest.main([__file__, "-v", "--tb=short"])