"""
Code Generation Cache - Green段階（テストを通すための実装）
Redis基盤のキャッシュシステム
"""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """キャッシュエントリ"""
    data: Any
    created_at: float
    ttl: int = 3600  # デフォルト1時間
    
    def is_expired(self) -> bool:
        """有効期限切れチェック"""
        if self.ttl <= 0:  # TTL無効
            return False
        return time.time() > (self.created_at + self.ttl)


@dataclass
class CacheStats:
    """キャッシュ統計"""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    cache_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """ヒット率"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests


class CodeGenerationCache:
    """
    コード生成キャッシュシステム
    Redis基盤（フォールバック：インメモリ）
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, use_redis: bool = True):
        self.config = self._init_config(config)
        self.use_redis = use_redis
        
        # 統計情報
        self._stats = CacheStats()
        self._stats_lock = threading.Lock()
        
        # インメモリキャッシュ（Redis無効時・フォールバック用）
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._memory_lock = threading.Lock()
        
        # Redis接続
        self._redis = None
        if use_redis:
            try:
                self._init_redis()
            except Exception as e:
                logger.warning(f"Redis connection failed, using memory cache: {e}")
                self.use_redis = False
        
        logger.info(f"CodeGenerationCache initialized (Redis: {self.use_redis})")
    
    def _init_config(self, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """設定初期化"""
        default_config = {
            "default_ttl": 3600,  # 1時間
            "max_cache_size": 10000,
            "enable_stats": True,
            "redis_url": "redis://localhost:6379",
            "redis_db": 0,
            "key_prefix": "altmx:codegen:"
        }
        
        if custom_config:
            default_config.update(custom_config)
        
        return default_config
    
    def _init_redis(self):
        """Redis初期化"""
        try:
            import redis
            
            self._redis = redis.Redis.from_url(
                self.config["redis_url"],
                db=self.config["redis_db"],
                decode_responses=False  # バイナリデータ対応
            )
            
            # 接続テスト
            self._redis.ping()
            logger.info("Redis connection established")
            
        except ImportError:
            logger.warning("redis package not installed, using memory cache")
            raise
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def generate_prompt_hash(
        self,
        user_prompt: str,
        complexity: str = "medium",
        include_security: bool = True,
        **kwargs
    ) -> str:
        """
        プロンプトハッシュ生成
        
        Args:
            user_prompt: ユーザープロンプト
            complexity: 複雑度
            include_security: セキュリティ含む
            **kwargs: 追加パラメータ
            
        Returns:
            ハッシュ文字列
        """
        # ハッシュ対象データ作成
        hash_data = {
            "prompt": user_prompt.strip(),
            "complexity": complexity,
            "security": include_security
        }
        
        # 追加パラメータも含める
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (str, int, bool, float)):
                hash_data[key] = value
        
        # JSON文字列化してハッシュ
        json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        
        return hash_obj.hexdigest()[:32]  # 32文字に短縮
    
    def _make_key(self, key: str) -> str:
        """キー名生成（プレフィックス付き）"""
        return f"{self.config['key_prefix']}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから取得
        
        Args:
            key: キー
            
        Returns:
            キャッシュされたデータ（なければNone）
        """
        with self._stats_lock:
            self._stats.total_requests += 1
        
        try:
            if self.use_redis and self._redis:
                return self._redis_get(key)
            else:
                return self._memory_get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            with self._stats_lock:
                self._stats.misses += 1
            return None
    
    def _redis_get(self, key: str) -> Optional[Any]:
        """Redis取得"""
        redis_key = self._make_key(key)
        
        try:
            data = self._redis.get(redis_key)
            if data is None:
                with self._stats_lock:
                    self._stats.misses += 1
                return None
            
            # JSONデシリアライズ
            result = json.loads(data.decode('utf-8'))
            
            with self._stats_lock:
                self._stats.hits += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            with self._stats_lock:
                self._stats.misses += 1
            return None
    
    def _memory_get(self, key: str) -> Optional[Any]:
        """インメモリ取得"""
        with self._memory_lock:
            if key not in self._memory_cache:
                with self._stats_lock:
                    self._stats.misses += 1
                return None
            
            entry = self._memory_cache[key]
            
            # 有効期限チェック
            if entry.is_expired():
                del self._memory_cache[key]
                with self._stats_lock:
                    self._stats.misses += 1
                    self._stats.cache_size = len(self._memory_cache)
                return None
            
            with self._stats_lock:
                self._stats.hits += 1
            
            return entry.data
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        キャッシュに保存
        
        Args:
            key: キー
            data: データ
            ttl: 有効期限（秒）
            
        Returns:
            成功フラグ
        """
        if ttl is None:
            ttl = self.config["default_ttl"]
        
        try:
            if self.use_redis and self._redis:
                return self._redis_set(key, data, ttl)
            else:
                return self._memory_set(key, data, ttl)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def _redis_set(self, key: str, data: Any, ttl: int) -> bool:
        """Redis保存"""
        redis_key = self._make_key(key)
        
        try:
            # JSONシリアライズ
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Redis保存
            if ttl > 0:
                result = self._redis.setex(redis_key, ttl, json_data.encode('utf-8'))
            else:
                result = self._redis.set(redis_key, json_data.encode('utf-8'))
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def _memory_set(self, key: str, data: Any, ttl: int) -> bool:
        """インメモリ保存"""
        with self._memory_lock:
            # サイズ制限チェック
            if (len(self._memory_cache) >= self.config["max_cache_size"] and 
                key not in self._memory_cache):
                self._evict_lru()
            
            # エントリ作成
            entry = CacheEntry(
                data=data,
                created_at=time.time(),
                ttl=ttl
            )
            
            self._memory_cache[key] = entry
            
            with self._stats_lock:
                self._stats.cache_size = len(self._memory_cache)
            
            return True
    
    def _evict_lru(self):
        """LRU削除（簡易実装）"""
        if not self._memory_cache:
            return
        
        # 最古のエントリを削除
        oldest_key = min(self._memory_cache.keys(), 
                        key=lambda k: self._memory_cache[k].created_at)
        del self._memory_cache[oldest_key]
    
    def delete(self, key: str) -> bool:
        """
        キャッシュから削除
        
        Args:
            key: キー
            
        Returns:
            削除成功フラグ
        """
        try:
            if self.use_redis and self._redis:
                redis_key = self._make_key(key)
                result = self._redis.delete(redis_key)
                return bool(result)
            else:
                with self._memory_lock:
                    if key in self._memory_cache:
                        del self._memory_cache[key]
                        with self._stats_lock:
                            self._stats.cache_size = len(self._memory_cache)
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        キャッシュ全クリア
        
        Returns:
            成功フラグ
        """
        try:
            if self.use_redis and self._redis:
                pattern = self._make_key("*")
                keys = self._redis.keys(pattern)
                if keys:
                    self._redis.delete(*keys)
            else:
                with self._memory_lock:
                    self._memory_cache.clear()
                    with self._stats_lock:
                        self._stats.cache_size = 0
            
            # 統計リセット
            with self._stats_lock:
                self._stats = CacheStats()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        キャッシュ統計取得
        
        Returns:
            統計情報辞書
        """
        with self._stats_lock:
            # インメモリキャッシュのサイズ更新
            if not self.use_redis:
                self._stats.cache_size = len(self._memory_cache)
            
            return {
                "hits": self._stats.hits,
                "misses": self._stats.misses,
                "total_requests": self._stats.total_requests,
                "hit_rate": self._stats.hit_rate,
                "cache_size": self._stats.cache_size,
                "using_redis": self.use_redis,
                "config": self.config
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        ヘルスチェック
        
        Returns:
            ヘルス情報
        """
        try:
            if self.use_redis and self._redis:
                # Redis接続確認
                self._redis.ping()
                redis_status = "healthy"
            else:
                redis_status = "disabled"
            
            return {
                "status": "healthy",
                "redis_status": redis_status,
                "cache_backend": "redis" if self.use_redis else "memory",
                "stats": self.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "cache_backend": "memory",  # フォールバック
                "stats": self.get_stats()
            }