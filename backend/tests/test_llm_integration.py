"""
Test suite for LLM Integration - TDD実装
Gemini/Claude API統合とフォールバック機能のテスト
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
from ai_integration.llm_client import LLMClient, AIProvider, LLMResponse
from ai_integration.circuit_breaker import CircuitBreaker, CircuitBreakerState


class TestLLMResponse:
    """LLMResponseクラスのテスト"""
    
    def test_llm_response_creation(self):
        """LLMResponse作成テスト"""
        response = LLMResponse(
            text="Generated code here",
            provider=AIProvider.GEMINI,
            tokens_used=150,
            response_time_ms=2000,
            success=True
        )
        
        assert response.text == "Generated code here"
        assert response.provider == AIProvider.GEMINI
        assert response.tokens_used == 150
        assert response.response_time_ms == 2000
        assert response.success is True
    
    def test_llm_response_failure(self):
        """LLMResponse失敗ケース作成テスト"""
        response = LLMResponse(
            text="",
            provider=AIProvider.CLAUDE,
            tokens_used=0,
            response_time_ms=0,
            success=False,
            error_message="API connection failed"
        )
        
        assert response.text == ""
        assert response.success is False
        assert response.error_message == "API connection failed"


class TestCircuitBreaker:
    """CircuitBreakerクラスのテスト"""
    
    @pytest.fixture
    def circuit_breaker(self):
        """テスト用CircuitBreaker"""
        return CircuitBreaker(
            failure_threshold=3,
            timeout_seconds=5.0,
            success_threshold=2
        )
    
    def test_circuit_breaker_initial_state(self, circuit_breaker):
        """CircuitBreaker初期状態テスト"""
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.success_count == 0
    
    def test_circuit_breaker_failure_tracking(self, circuit_breaker):
        """失敗回数追跡テスト"""
        # 失敗を記録
        circuit_breaker.record_failure()
        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        
        # 閾値まで失敗を重ねる
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        
        assert circuit_breaker.failure_count == 3
        assert circuit_breaker.state == CircuitBreakerState.OPEN
    
    def test_circuit_breaker_success_reset(self, circuit_breaker):
        """成功時のリセットテスト"""
        # 失敗を記録
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.failure_count == 2
        
        # 成功を記録
        circuit_breaker.record_success()
        assert circuit_breaker.failure_count == 0  # リセットされる
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_circuit_breaker_half_open_transition(self, circuit_breaker):
        """HALF_OPEN状態遷移テスト"""
        # OPENまで持っていく
        for _ in range(3):
            circuit_breaker.record_failure()
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # タイムアウト時間経過をシミュレート
        circuit_breaker.last_failure_time = time.time() - 10  # 10秒前
        
        # can_executeでHALF_OPENに遷移
        can_execute = circuit_breaker.can_execute()
        assert can_execute is True
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN
    
    def test_circuit_breaker_half_open_success_recovery(self, circuit_breaker):
        """HALF_OPEN状態から成功による回復テスト"""
        # HALF_OPEN状態に設定
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        circuit_breaker.success_count = 0
        
        # 成功を記録（閾値まで）
        circuit_breaker.record_success()
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN
        
        circuit_breaker.record_success()
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.success_count == 0  # リセット
        assert circuit_breaker.failure_count == 0


class TestLLMClient:
    """LLMClientクラスのテスト"""
    
    @pytest.fixture
    def llm_client(self):
        """テスト用LLMClient"""
        return LLMClient()
    
    @pytest.mark.asyncio
    async def test_gemini_api_call_success(self, llm_client):
        """Gemini API成功呼び出しテスト"""
        with patch.object(llm_client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini:
            mock_gemini.return_value = LLMResponse(
                text="Generated React component",
                provider=AIProvider.GEMINI,
                tokens_used=200,
                response_time_ms=1500,
                success=True
            )
            
            result = await llm_client.generate_code(
                prompt="Create a login form",
                provider=AIProvider.GEMINI
            )
            
            assert result.success is True
            assert result.text == "Generated React component"
            assert result.provider == AIProvider.GEMINI
            mock_gemini.assert_called_once()
    
    @pytest.mark.asyncio  
    async def test_claude_api_call_success(self, llm_client):
        """Claude API成功呼び出しテスト"""
        with patch.object(llm_client, '_call_claude_api', new_callable=AsyncMock) as mock_claude:
            mock_claude.return_value = LLMResponse(
                text="Generated TypeScript component",
                provider=AIProvider.CLAUDE,
                tokens_used=180,
                response_time_ms=1200,
                success=True
            )
            
            result = await llm_client.generate_code(
                prompt="Create a dashboard",
                provider=AIProvider.CLAUDE
            )
            
            assert result.success is True
            assert result.text == "Generated TypeScript component"
            assert result.provider == AIProvider.CLAUDE
            mock_claude.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_failure_circuit_breaker_activation(self, llm_client):
        """API失敗時のCircuitBreaker起動テスト"""
        with patch.object(llm_client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini, \
             patch.object(llm_client, '_call_claude_api', new_callable=AsyncMock) as mock_claude:
            # 両方のAPI失敗をシミュレート
            mock_gemini.side_effect = Exception("API connection failed")
            mock_claude.side_effect = Exception("API connection failed")
            
            # 失敗を閾値まで繰り返す（フォールバック無効）
            for i in range(3):
                result = await llm_client.generate_code(
                    prompt="Test prompt",
                    provider=AIProvider.GEMINI,
                    enable_fallback=False
                )
                assert result.success is False
            
            # CircuitBreakerがOPENになることを確認
            assert llm_client.gemini_circuit_breaker.state == CircuitBreakerState.OPEN
    
    @pytest.mark.asyncio
    async def test_automatic_fallback_to_claude(self, llm_client):
        """Gemini失敗時のClaude自動フォールバックテスト"""
        with patch.object(llm_client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini, \
             patch.object(llm_client, '_call_claude_api', new_callable=AsyncMock) as mock_claude:
            
            # Gemini失敗を設定
            mock_gemini.side_effect = Exception("Gemini API failed")
            
            # Claude成功を設定
            mock_claude.return_value = LLMResponse(
                text="Fallback response from Claude",
                provider=AIProvider.CLAUDE,
                tokens_used=150,
                response_time_ms=1800,
                success=True
            )
            
            # フォールバック有効で実行
            result = await llm_client.generate_code(
                prompt="Create a component",
                provider=AIProvider.GEMINI,
                enable_fallback=True
            )
            
            # Claudeからの応答を受け取ることを確認
            assert result.success is True
            assert result.text == "Fallback response from Claude"
            assert result.provider == AIProvider.CLAUDE
            
            # 両方のAPIが呼ばれたことを確認（Geminiはリトライ含む）
            assert mock_gemini.call_count >= 1
            mock_claude.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_blocks_requests(self, llm_client):
        """CircuitBreakerによるリクエストブロックテスト"""
        # CircuitBreakerをOPEN状態に設定
        llm_client.gemini_circuit_breaker.state = CircuitBreakerState.OPEN
        llm_client.gemini_circuit_breaker.last_failure_time = time.time()
        
        with patch.object(llm_client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini:
            result = await llm_client.generate_code(
                prompt="Test prompt",
                provider=AIProvider.GEMINI,
                enable_fallback=False
            )
            
            # リクエストがブロックされることを確認
            assert result.success is False
            assert "Circuit breaker is OPEN" in result.error_message
            mock_gemini.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, llm_client):
        """リトライメカニズムテスト"""
        with patch.object(llm_client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini:
            # 最初の2回は失敗、3回目は成功
            mock_gemini.side_effect = [
                Exception("Temporary failure"),
                Exception("Another temporary failure"),
                LLMResponse(
                    text="Success on retry",
                    provider=AIProvider.GEMINI,
                    tokens_used=100,
                    response_time_ms=1000,
                    success=True
                )
            ]
            
            result = await llm_client.generate_code(
                prompt="Test retry",
                provider=AIProvider.GEMINI,
                max_retries=3
            )
            
            assert result.success is True
            assert result.text == "Success on retry"
            assert mock_gemini.call_count == 3
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, llm_client):
        """タイムアウト処理テスト"""
        with patch.object(llm_client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini, \
             patch.object(llm_client, '_call_claude_api', new_callable=AsyncMock) as mock_claude:
            # 両方のAPIでタイムアウト
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(10)  # 10秒待機
                return LLMResponse(text="Late response", provider=AIProvider.GEMINI, success=True)
            
            mock_gemini.side_effect = slow_response
            mock_claude.side_effect = slow_response
            
            result = await llm_client.generate_code(
                prompt="Test timeout",
                provider=AIProvider.GEMINI,
                timeout_seconds=2  # 2秒でタイムアウト
            )
            
            assert result.success is False
            assert "timeout" in result.error_message.lower()
    
    def test_get_provider_statistics(self, llm_client):
        """プロバイダー統計情報取得テスト"""
        stats = llm_client.get_provider_statistics()
        
        # 統計情報の構造確認
        assert "gemini" in stats
        assert "claude" in stats
        
        for provider_stats in stats.values():
            assert "total_requests" in provider_stats
            assert "successful_requests" in provider_stats
            assert "failed_requests" in provider_stats
            assert "average_response_time_ms" in provider_stats
            assert "circuit_breaker_state" in provider_stats


# 統合テスト
class TestLLMIntegrationFlow:
    """LLM統合フロー全体のテスト"""
    
    @pytest.mark.asyncio
    async def test_full_failover_scenario(self):
        """完全なフェイルオーバーシナリオテスト"""
        client = LLMClient()
        
        with patch.object(client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini, \
             patch.object(client, '_call_claude_api', new_callable=AsyncMock) as mock_claude:
            
            # Gemini完全失敗
            mock_gemini.side_effect = Exception("Gemini service down")
            
            # Claude成功
            mock_claude.return_value = LLMResponse(
                text="Claude backup response",
                provider=AIProvider.CLAUDE,
                tokens_used=200,
                response_time_ms=2000,
                success=True
            )
            
            # 複数回実行してフェイルオーバー確認
            for i in range(5):
                result = await client.generate_code(
                    prompt=f"Test request {i}",
                    provider=AIProvider.GEMINI,
                    enable_fallback=True
                )
                
                assert result.success is True
                assert result.provider == AIProvider.CLAUDE
            
            # 統計確認
            stats = client.get_provider_statistics()
            assert stats["gemini"]["failed_requests"] == 5
            assert stats["claude"]["successful_requests"] == 5
    
    @pytest.mark.asyncio
    async def test_load_balancing_behavior(self):
        """負荷分散動作テスト"""
        client = LLMClient()
        
        with patch.object(client, '_call_gemini_api', new_callable=AsyncMock) as mock_gemini, \
             patch.object(client, '_call_claude_api', new_callable=AsyncMock) as mock_claude:
            
            # 両方とも成功レスポンス
            mock_gemini.return_value = LLMResponse(
                text="Gemini response", provider=AIProvider.GEMINI, success=True
            )
            mock_claude.return_value = LLMResponse(
                text="Claude response", provider=AIProvider.CLAUDE, success=True
            )
            
            # プロバイダーを指定せずに複数回実行
            gemini_count = 0
            claude_count = 0
            
            for _ in range(10):
                result = await client.generate_code(
                    prompt="Load balance test",
                    provider=None  # 自動選択
                )
                
                if result.provider == AIProvider.GEMINI:
                    gemini_count += 1
                elif result.provider == AIProvider.CLAUDE:
                    claude_count += 1
            
            # 両方のプロバイダーが使用されることを確認
            assert gemini_count > 0
            assert claude_count > 0
            assert gemini_count + claude_count == 10