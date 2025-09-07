"""
Code Generation Cache Tests - Red段階（失敗するテスト）
Redis基盤のキャッシュシステムテスト
"""

import pytest
import time
import hashlib
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional

# 実装済みモジュールインポート
from code_generation.cache import CodeGenerationCache, CacheEntry, CacheStats


@pytest.fixture
def cache():
    """キャッシュインスタンス（Redisなしでテスト）"""
    return CodeGenerationCache(use_redis=False)


@pytest.fixture
def sample_generation_result():
    """サンプル生成結果"""
    return {
        "success": True,
        "generated_files": [
            {
                "filename": "LoginForm.tsx",
                "content": "import React from 'react';\n\nconst LoginForm = () => {\n  return <div>Login</div>;\n};",
                "language": "typescript"
            }
        ],
        "errors": [],
        "warnings": [],
        "performance_metrics": {"total_time": 5.2}
    }


@pytest.fixture
def cache_key():
    """テスト用キャッシュキー"""
    return "test_prompt_hash_12345"


class TestCodeGenerationCache:
    """コード生成キャッシュテスト"""
    
    def test_cache_initialization(self, cache):
        """キャッシュ初期化テスト"""
        assert cache is not None
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'delete')
        assert hasattr(cache, 'clear')
        assert hasattr(cache, 'get_stats')
    
    def test_cache_set_and_get(self, cache, cache_key, sample_generation_result):
        """キャッシュ設定・取得テスト"""
        # キャッシュに保存
        cache.set(cache_key, sample_generation_result, ttl=3600)
        
        # キャッシュから取得
        cached_result = cache.get(cache_key)
        
        assert cached_result is not None
        assert cached_result["success"] == sample_generation_result["success"]
        assert len(cached_result["generated_files"]) == len(sample_generation_result["generated_files"])
    
    def test_cache_miss(self, cache):
        """キャッシュミステスト"""
        result = cache.get("non_existent_key")
        assert result is None
    
    def test_cache_expiration(self, cache, cache_key, sample_generation_result):
        """キャッシュ有効期限テスト"""
        # 短い有効期限でキャッシュ設定
        cache.set(cache_key, sample_generation_result, ttl=1)
        
        # 即座に取得（まだ有効）
        result = cache.get(cache_key)
        assert result is not None
        
        # 有効期限切れを待つ
        time.sleep(2)
        
        # 期限切れで取得できない
        expired_result = cache.get(cache_key)
        assert expired_result is None
    
    def test_cache_delete(self, cache, cache_key, sample_generation_result):
        """キャッシュ削除テスト"""
        # キャッシュ設定
        cache.set(cache_key, sample_generation_result)
        
        # 削除前は存在
        assert cache.get(cache_key) is not None
        
        # 削除
        cache.delete(cache_key)
        
        # 削除後は存在しない
        assert cache.get(cache_key) is None
    
    def test_cache_clear(self, cache, sample_generation_result):
        """キャッシュクリアテスト"""
        # 複数エントリ追加
        cache.set("key1", sample_generation_result)
        cache.set("key2", sample_generation_result)
        
        # クリア前は存在
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        
        # 全クリア
        cache.clear()
        
        # クリア後は存在しない
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestPromptHashing:
    """プロンプトハッシュ化テスト"""
    
    def test_prompt_hash_generation(self, cache):
        """プロンプトハッシュ生成テスト"""
        prompt = "Create a React login form"
        complexity = "medium"
        include_security = True
        
        hash1 = cache.generate_prompt_hash(prompt, complexity, include_security)
        hash2 = cache.generate_prompt_hash(prompt, complexity, include_security)
        
        # 同じ条件では同じハッシュ
        assert hash1 == hash2
        assert len(hash1) > 0
        assert isinstance(hash1, str)
    
    def test_different_prompts_different_hashes(self, cache):
        """異なるプロンプトでは異なるハッシュ"""
        hash1 = cache.generate_prompt_hash("Create a login form", "medium", True)
        hash2 = cache.generate_prompt_hash("Create a dashboard", "medium", True)
        
        assert hash1 != hash2
    
    def test_different_parameters_different_hashes(self, cache):
        """異なるパラメータでは異なるハッシュ"""
        prompt = "Create a React form"
        
        hash1 = cache.generate_prompt_hash(prompt, "medium", True)
        hash2 = cache.generate_prompt_hash(prompt, "high", True)
        hash3 = cache.generate_prompt_hash(prompt, "medium", False)
        
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3


class TestCacheStats:
    """キャッシュ統計テスト"""
    
    def test_hit_rate_calculation(self, cache, sample_generation_result):
        """ヒット率計算テスト"""
        # 初期状態
        stats = cache.get_stats()
        assert stats["hit_rate"] == 0.0
        assert stats["total_requests"] == 0
        
        # キャッシュミス
        cache.get("non_existent")
        stats = cache.get_stats()
        assert stats["hit_rate"] == 0.0
        assert stats["total_requests"] == 1
        assert stats["misses"] == 1
        
        # キャッシュ設定してヒット
        cache.set("test_key", sample_generation_result)
        cache.get("test_key")
        
        stats = cache.get_stats()
        assert stats["hit_rate"] == 0.5  # 1 hit, 1 miss
        assert stats["total_requests"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    def test_cache_size_tracking(self, cache, sample_generation_result):
        """キャッシュサイズ追跡テスト"""
        # 初期状態
        stats = cache.get_stats()
        assert stats["cache_size"] == 0
        
        # エントリ追加
        cache.set("key1", sample_generation_result)
        cache.set("key2", sample_generation_result)
        
        stats = cache.get_stats()
        assert stats["cache_size"] == 2
        
        # エントリ削除
        cache.delete("key1")
        stats = cache.get_stats()
        assert stats["cache_size"] == 1


class TestCacheIntegration:
    """キャッシュ統合テスト"""
    
    def test_engine_cache_integration(self, cache):
        """エンジンとキャッシュの統合テスト"""
        from code_generation.engine import CodeGenerationEngine, GenerationRequest
        
        # キャッシュ付きエンジン作成
        engine = CodeGenerationEngine(cache=cache)
        
        request = GenerationRequest(
            user_prompt="Simple React component",
            complexity="simple"
        )
        
        # 最初の生成（キャッシュミス）
        result1 = engine.generate_code_with_cache(request)
        
        # 同じリクエストで生成（キャッシュヒット）
        result2 = engine.generate_code_with_cache(request)
        
        # 結果は同じだがキャッシュから取得
        assert result1["success"] == result2["success"]
        
        # キャッシュ統計確認
        stats = cache.get_stats()
        assert stats["hits"] >= 1
    
    @patch('redis.Redis')
    def test_redis_integration(self, mock_redis, sample_generation_result):
        """Redis統合テスト"""
        # Redisモック設定
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        
        # Redis有効でキャッシュ作成
        redis_cache = CodeGenerationCache(use_redis=True)
        
        # Redisメソッドが呼ばれることを確認
        redis_cache.set("test_key", sample_generation_result, ttl=3600)
        
        # Redis set操作が呼ばれる
        assert mock_redis_instance.setex.called or mock_redis_instance.set.called
    
    def test_cache_serialization(self, cache, sample_generation_result):
        """キャッシュシリアライゼーションテスト"""
        # 複雑なデータ構造をキャッシュ
        complex_data = {
            "nested": {
                "data": ["list", "items"],
                "number": 42,
                "boolean": True
            },
            "files": sample_generation_result["generated_files"]
        }
        
        cache.set("complex_key", complex_data)
        retrieved = cache.get("complex_key")
        
        assert retrieved is not None
        assert retrieved["nested"]["data"] == ["list", "items"]
        assert retrieved["nested"]["number"] == 42
        assert retrieved["nested"]["boolean"] is True


class TestCachePerformance:
    """キャッシュパフォーマンステスト"""
    
    def test_large_data_caching(self, cache):
        """大容量データキャッシュテスト"""
        # 大きなコード生成結果をシミュレート
        large_result = {
            "success": True,
            "generated_files": [
                {
                    "filename": f"Component{i}.tsx",
                    "content": "import React from 'react';\n" * 1000,  # 大きなコンテンツ
                    "language": "typescript"
                }
                for i in range(10)
            ]
        }
        
        # 大容量データのキャッシュ設定・取得
        start_time = time.time()
        cache.set("large_key", large_result)
        set_time = time.time() - start_time
        
        start_time = time.time()
        retrieved = cache.get("large_key")
        get_time = time.time() - start_time
        
        # パフォーマンス検証（妥当な時間内）
        assert set_time < 1.0  # 1秒以内
        assert get_time < 0.5  # 0.5秒以内
        assert retrieved is not None
        assert len(retrieved["generated_files"]) == 10
    
    def test_concurrent_cache_access(self, cache, sample_generation_result):
        """同時キャッシュアクセステスト"""
        import threading
        
        results = []
        errors = []
        
        def cache_operation(key_suffix):
            try:
                key = f"concurrent_key_{key_suffix}"
                cache.set(key, sample_generation_result)
                result = cache.get(key)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 同時アクセステスト
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # エラーなく実行完了
        assert len(errors) == 0
        assert len(results) == 10
        
        # すべての結果が正しい
        for result in results:
            assert result["success"] is True


class TestCacheConfiguration:
    """キャッシュ設定テスト"""
    
    def test_cache_with_custom_config(self):
        """カスタム設定キャッシュテスト"""
        config = {
            "default_ttl": 7200,  # 2時間
            "max_cache_size": 1000,
            "enable_stats": True,
            "redis_url": "redis://localhost:6379"
        }
        
        cache = CodeGenerationCache(config=config, use_redis=False)
        
        assert cache.config["default_ttl"] == 7200
        assert cache.config["max_cache_size"] == 1000
        assert cache.config["enable_stats"] is True
    
    def test_cache_size_limit(self, sample_generation_result):
        """キャッシュサイズ制限テスト"""
        # 小さなキャッシュサイズ制限
        cache = CodeGenerationCache(config={"max_cache_size": 2}, use_redis=False)
        
        # 制限を超えてエントリ追加
        cache.set("key1", sample_generation_result)
        cache.set("key2", sample_generation_result)
        cache.set("key3", sample_generation_result)  # 制限超過
        
        stats = cache.get_stats()
        
        # 最大サイズを超えない
        assert stats["cache_size"] <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])