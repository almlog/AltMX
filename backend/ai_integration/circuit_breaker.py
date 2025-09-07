"""
Circuit Breaker Pattern - テストを通すための最小実装（Green段階）
AI API障害時の自動フォールバック制御
"""

import time
from enum import Enum
from typing import Optional


class CircuitBreakerState(Enum):
    """Circuit Breaker状態"""
    CLOSED = "closed"      # 正常状態
    OPEN = "open"          # 障害状態（リクエスト遮断）
    HALF_OPEN = "half_open"  # 試行状態（一部リクエスト許可）


class CircuitBreaker:
    """
    Circuit Breaker実装
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0,
        success_threshold: int = 3
    ):
        """
        Circuit Breaker初期化
        
        Args:
            failure_threshold: OPEN状態に移行する失敗回数
            timeout_seconds: OPEN→HALF_OPEN移行までの待機時間
            success_threshold: HALF_OPEN→CLOSED移行に必要な成功回数
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        
        # 状態管理
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
    
    def can_execute(self) -> bool:
        """
        リクエスト実行可能判定
        
        Returns:
            実行可能な場合True
        """
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # タイムアウト時間経過後はHALF_OPENに移行
            if (self.last_failure_time and 
                time.time() - self.last_failure_time >= self.timeout_seconds):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        
        # HALF_OPEN状態では実行許可
        return True
    
    def record_success(self) -> None:
        """
        成功記録
        """
        self.failure_count = 0
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.success_threshold:
                # CLOSED状態に復帰
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
        else:
            self.state = CircuitBreakerState.CLOSED
    
    def record_failure(self) -> None:
        """
        失敗記録
        """
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
        
        # HALF_OPEN状態での失敗はOPENに戻る
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0
    
    def get_state(self) -> CircuitBreakerState:
        """現在の状態取得"""
        return self.state
    
    def reset(self) -> None:
        """状態リセット"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None