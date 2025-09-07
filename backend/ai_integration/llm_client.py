"""
LLM Client - テストを通すための最小実装（Green段階）
Gemini/Claude API統合とフォールバック機能
"""

import asyncio
import time
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

from .circuit_breaker import CircuitBreaker, CircuitBreakerState

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI Provider種別"""
    GEMINI = "gemini"
    CLAUDE = "claude"


@dataclass
class LLMResponse:
    """
    LLM API レスポンス
    """
    text: str
    provider: AIProvider
    tokens_used: int = 0
    response_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None


class LLMClient:
    """
    LLM統合クライアント（Gemini + Claude + フォールバック）
    """
    
    def __init__(self):
        # Circuit Breaker設定
        self.gemini_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout_seconds=30.0,
            success_threshold=2
        )
        
        self.claude_circuit_breaker = CircuitBreaker(
            failure_threshold=3, 
            timeout_seconds=30.0,
            success_threshold=2
        )
        
        # 統計情報管理
        self.statistics = {
            "gemini": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_response_time_ms": 0,
                "average_response_time_ms": 0,
                "circuit_breaker_state": CircuitBreakerState.CLOSED
            },
            "claude": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_response_time_ms": 0,
                "average_response_time_ms": 0,
                "circuit_breaker_state": CircuitBreakerState.CLOSED
            }
        }
    
    async def generate_code(
        self,
        prompt: str,
        provider: Optional[AIProvider] = None,
        enable_fallback: bool = True,
        max_retries: int = 1,
        timeout_seconds: float = 30.0
    ) -> LLMResponse:
        """
        コード生成メイン処理
        
        Args:
            prompt: 生成プロンプト
            provider: 使用するAIプロバイダー（Noneで自動選択）
            enable_fallback: フォールバック有効
            max_retries: リトライ回数
            timeout_seconds: タイムアウト時間
            
        Returns:
            LLM応答
        """
        # プロバイダー自動選択
        if provider is None:
            provider = self._select_best_provider()
        
        # 主プロバイダーでの実行試行
        result = await self._execute_with_provider(
            prompt=prompt,
            provider=provider,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            allow_fallback=enable_fallback
        )
        
        return result
    
    async def _execute_with_provider(
        self,
        prompt: str,
        provider: AIProvider,
        max_retries: int,
        timeout_seconds: float,
        allow_fallback: bool = True
    ) -> LLMResponse:
        """
        指定プロバイダーでの実行
        """
        circuit_breaker = self._get_circuit_breaker(provider)
        
        # Circuit Breaker確認
        if not circuit_breaker.can_execute():
            self._update_statistics(provider, success=False, response_time_ms=0)
            
            # フォールバック試行
            if allow_fallback:
                fallback_provider = self._get_fallback_provider(provider)
                if fallback_provider:
                    logger.info(f"Circuit breaker OPEN for {provider.value}, falling back to {fallback_provider.value}")
                    return await self._execute_with_provider(
                        prompt=prompt,
                        provider=fallback_provider,
                        max_retries=max_retries,
                        timeout_seconds=timeout_seconds,
                        allow_fallback=False  # 無限ループ防止
                    )
            
            return LLMResponse(
                text="",
                provider=provider,
                success=False,
                error_message=f"Circuit breaker is OPEN for {provider.value}"
            )
        
        # リトライ処理
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                # タイムアウト付きAPI呼び出し
                result = await asyncio.wait_for(
                    self._call_provider_api(prompt, provider),
                    timeout=timeout_seconds
                )
                
                # 成功時
                circuit_breaker.record_success()
                self._update_statistics(provider, success=True, response_time_ms=result.response_time_ms)
                return result
                
            except asyncio.TimeoutError:
                last_exception = Exception(f"Request timeout after {timeout_seconds}s")
                
            except Exception as e:
                last_exception = e
            
            # 最後の試行でない場合は少し待機
            if attempt < max_retries:
                await asyncio.sleep(1.0 * (attempt + 1))  # 指数バックオフ
        
        # すべて失敗
        circuit_breaker.record_failure()
        self._update_statistics(provider, success=False, response_time_ms=0)
        
        # フォールバック試行
        if allow_fallback:
            fallback_provider = self._get_fallback_provider(provider)
            if fallback_provider:
                logger.info(f"Primary {provider.value} failed, falling back to {fallback_provider.value}")
                return await self._execute_with_provider(
                    prompt=prompt,
                    provider=fallback_provider,
                    max_retries=max_retries,
                    timeout_seconds=timeout_seconds,
                    allow_fallback=False  # 無限ループ防止
                )
        
        return LLMResponse(
            text="",
            provider=provider,
            success=False,
            error_message=str(last_exception)
        )
    
    async def _call_provider_api(self, prompt: str, provider: AIProvider) -> LLMResponse:
        """
        プロバイダー固有のAPI呼び出し
        """
        if provider == AIProvider.GEMINI:
            return await self._call_gemini_api(prompt)
        elif provider == AIProvider.CLAUDE:
            return await self._call_claude_api(prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _call_gemini_api(self, prompt: str) -> LLMResponse:
        """
        Gemini API呼び出し（最小実装）
        """
        start_time = time.time()
        
        # 実際のGemini API呼び出し実装
        # テスト時はmockされるため、ここは基本実装のみ
        try:
            # 実装予定: google.generativeai使用
            await asyncio.sleep(0.1)  # API呼び出しシミュレーション
            
            response_time = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                text="// Mock Gemini response\nimport React from 'react';\n\nconst Component = () => {\n  return <div>Generated by Gemini</div>;\n};\n\nexport default Component;",
                provider=AIProvider.GEMINI,
                tokens_used=150,
                response_time_ms=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            raise e
    
    async def _call_claude_api(self, prompt: str) -> LLMResponse:
        """
        Claude API呼び出し（最小実装）
        """
        start_time = time.time()
        
        try:
            # 実装予定: Anthropic Claude API使用
            await asyncio.sleep(0.1)  # API呼び出しシミュレーション
            
            response_time = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                text="// Mock Claude response\nimport React from 'react';\n\nconst Component = () => {\n  return <div>Generated by Claude</div>;\n};\n\nexport default Component;",
                provider=AIProvider.CLAUDE,
                tokens_used=120,
                response_time_ms=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            raise e
    
    def _select_best_provider(self) -> AIProvider:
        """
        最適なプロバイダー選択（負荷分散）
        """
        gemini_stats = self.statistics["gemini"]
        claude_stats = self.statistics["claude"]
        
        # Circuit Breakerが開いていない方を優先
        if self.gemini_circuit_breaker.state == CircuitBreakerState.OPEN:
            return AIProvider.CLAUDE
        
        if self.claude_circuit_breaker.state == CircuitBreakerState.OPEN:
            return AIProvider.GEMINI
        
        # 初期状態では簡単な分散（リクエスト数ベース）
        total_gemini = gemini_stats["total_requests"]
        total_claude = claude_stats["total_requests"]
        
        # リクエスト数が少ない方を選択（負荷分散）
        if total_gemini <= total_claude:
            return AIProvider.GEMINI
        else:
            return AIProvider.CLAUDE
    
    def _get_fallback_provider(self, primary: AIProvider) -> Optional[AIProvider]:
        """
        フォールバックプロバイダー取得
        """
        if primary == AIProvider.GEMINI:
            return AIProvider.CLAUDE
        elif primary == AIProvider.CLAUDE:
            return AIProvider.GEMINI
        return None
    
    def _get_circuit_breaker(self, provider: AIProvider) -> CircuitBreaker:
        """
        プロバイダーのCircuit Breaker取得
        """
        if provider == AIProvider.GEMINI:
            return self.gemini_circuit_breaker
        elif provider == AIProvider.CLAUDE:
            return self.claude_circuit_breaker
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _update_statistics(self, provider: AIProvider, success: bool, response_time_ms: int):
        """
        統計情報更新
        """
        stats = self.statistics[provider.value]
        stats["total_requests"] += 1
        
        if success:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
        
        stats["total_response_time_ms"] += response_time_ms
        stats["average_response_time_ms"] = (
            stats["total_response_time_ms"] / stats["total_requests"]
        )
        
        # Circuit Breaker状態更新
        stats["circuit_breaker_state"] = self._get_circuit_breaker(provider).get_state()
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """
        プロバイダー統計情報取得
        """
        # 現在のCircuit Breaker状態で更新
        self.statistics["gemini"]["circuit_breaker_state"] = self.gemini_circuit_breaker.get_state()
        self.statistics["claude"]["circuit_breaker_state"] = self.claude_circuit_breaker.get_state()
        
        return self.statistics.copy()
    
    def reset_statistics(self):
        """統計情報リセット"""
        for provider_stats in self.statistics.values():
            provider_stats["total_requests"] = 0
            provider_stats["successful_requests"] = 0
            provider_stats["failed_requests"] = 0
            provider_stats["total_response_time_ms"] = 0
            provider_stats["average_response_time_ms"] = 0
        
        # Circuit Breaker もリセット
        self.gemini_circuit_breaker.reset()
        self.claude_circuit_breaker.reset()