"""
File Management Tests - Red段階（失敗するテスト）
一時ファイル管理・プレビューシステムテスト
"""

import pytest
import os
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# 実装済みモジュールインポート
from code_generation.file_manager import FileManager, FileEntry, PreviewSession
from code_generation.preview_server import PreviewServer


@pytest.fixture
def temp_dir():
    """テスト用一時ディレクトリ"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def file_manager(temp_dir):
    """ファイルマネージャーインスタンス"""
    config = {
        "temp_root": temp_dir,
        "default_ttl": 3600,  # 1時間
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "cleanup_interval": 60  # 1分
    }
    return FileManager(config)


@pytest.fixture
def sample_files():
    """サンプルファイルデータ"""
    return [
        {
            "filename": "App.tsx",
            "content": "import React from 'react';\n\nconst App = () => {\n  return <div>Hello World</div>;\n};\n\nexport default App;",
            "language": "typescript"
        },
        {
            "filename": "styles.css",
            "content": ".container {\n  padding: 20px;\n  background: #f0f0f0;\n}\n\n.title {\n  color: #333;\n  font-size: 24px;\n}",
            "language": "css"
        },
        {
            "filename": "package.json",
            "content": "{\n  \"name\": \"my-app\",\n  \"version\": \"1.0.0\",\n  \"dependencies\": {\n    \"react\": \"^18.0.0\"\n  }\n}",
            "language": "json"
        }
    ]


class TestFileManager:
    """ファイルマネージャーテスト"""
    
    def test_file_manager_initialization(self, file_manager, temp_dir):
        """ファイルマネージャー初期化テスト"""
        assert file_manager is not None
        assert file_manager.temp_root == temp_dir
        assert hasattr(file_manager, 'create_session')
        assert hasattr(file_manager, 'save_files')
        assert hasattr(file_manager, 'get_session')
        assert hasattr(file_manager, 'cleanup_expired')
    
    def test_session_creation(self, file_manager):
        """セッション作成テスト"""
        session_id = file_manager.create_session()
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # セッション取得
        session = file_manager.get_session(session_id)
        assert session is not None
        assert session.session_id == session_id
        assert session.created_at > 0
        assert isinstance(session.files, list)
    
    def test_file_saving(self, file_manager, sample_files):
        """ファイル保存テスト"""
        session_id = file_manager.create_session()
        
        # ファイル保存
        result = file_manager.save_files(session_id, sample_files)
        
        assert result["success"] is True
        assert "files_saved" in result
        assert result["files_saved"] == len(sample_files)
        
        # セッション内容確認
        session = file_manager.get_session(session_id)
        assert len(session.files) == len(sample_files)
        
        # ファイル内容確認
        for file_entry in session.files:
            assert file_entry.filename in [f["filename"] for f in sample_files]
            assert file_entry.content is not None
            assert len(file_entry.content) > 0
    
    def test_file_directory_structure(self, file_manager, sample_files):
        """ファイルディレクトリ構造テスト"""
        session_id = file_manager.create_session()
        file_manager.save_files(session_id, sample_files)
        
        session = file_manager.get_session(session_id)
        
        # ディレクトリが作成されている
        session_dir = Path(file_manager.temp_root) / session_id
        assert session_dir.exists()
        assert session_dir.is_dir()
        
        # ファイルが実際に保存されている
        for file_entry in session.files:
            file_path = session_dir / file_entry.filename
            assert file_path.exists()
            assert file_path.is_file()
            
            # ファイル内容確認
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content == file_entry.content
    
    def test_session_expiration(self, file_manager, sample_files):
        """セッション有効期限テスト"""
        # 短い有効期限でセッション作成
        short_ttl_config = file_manager.config.copy()
        short_ttl_config["default_ttl"] = 1  # 1秒
        short_ttl_manager = FileManager(short_ttl_config)
        
        session_id = short_ttl_manager.create_session()
        short_ttl_manager.save_files(session_id, sample_files)
        
        # 即座に取得（まだ有効）
        session = short_ttl_manager.get_session(session_id)
        assert session is not None
        
        # 有効期限切れを待つ
        time.sleep(2)
        
        # 期限切れで取得できない
        expired_session = short_ttl_manager.get_session(session_id)
        assert expired_session is None
    
    def test_file_size_limits(self, file_manager):
        """ファイルサイズ制限テスト"""
        # 大きなファイル作成
        large_content = "x" * (15 * 1024 * 1024)  # 15MB（制限の10MBを超過）
        large_file = [{"filename": "large.txt", "content": large_content, "language": "text"}]
        
        session_id = file_manager.create_session()
        result = file_manager.save_files(session_id, large_file)
        
        # サイズ制限でエラー
        assert result["success"] is False
        error_msg = result.get("error", "").lower()
        assert "large" in error_msg or "size" in error_msg
    
    def test_cleanup_expired_sessions(self, file_manager, sample_files):
        """期限切れセッションクリーンアップテスト"""
        # 通常セッション
        normal_session = file_manager.create_session()
        file_manager.save_files(normal_session, sample_files)
        
        # 期限切れセッション（手動で古い日付設定）
        expired_session = file_manager.create_session()
        file_manager.save_files(expired_session, sample_files)
        
        # 期限切れにするため時刻を操作
        session_obj = file_manager.get_session(expired_session)
        session_obj.created_at = time.time() - 7200  # 2時間前
        
        # クリーンアップ実行
        cleaned_count = file_manager.cleanup_expired()
        
        # 期限切れセッションが削除された
        assert cleaned_count >= 1
        assert file_manager.get_session(expired_session) is None
        assert file_manager.get_session(normal_session) is not None


class TestPreviewServer:
    """プレビューサーバーテスト"""
    
    @pytest.fixture
    def preview_server(self, file_manager):
        """プレビューサーバーインスタンス"""
        return PreviewServer(file_manager)
    
    def test_preview_server_initialization(self, preview_server):
        """プレビューサーバー初期化テスト"""
        assert preview_server is not None
        assert hasattr(preview_server, 'generate_preview_url')
        assert hasattr(preview_server, 'serve_file')
        assert hasattr(preview_server, 'get_session_info')
    
    def test_preview_url_generation(self, preview_server, file_manager, sample_files):
        """プレビューURL生成テスト"""
        session_id = file_manager.create_session()
        file_manager.save_files(session_id, sample_files)
        
        # プレビューURL生成
        preview_url = preview_server.generate_preview_url(session_id)
        
        assert preview_url is not None
        assert isinstance(preview_url, str)
        assert session_id in preview_url
        assert preview_url.startswith("http")
    
    def test_file_serving(self, preview_server, file_manager, sample_files):
        """ファイル配信テスト"""
        session_id = file_manager.create_session()
        file_manager.save_files(session_id, sample_files)
        
        # ファイル配信
        for file_data in sample_files:
            response = preview_server.serve_file(session_id, file_data["filename"])
            
            assert response is not None
            assert response["success"] is True
            assert response["content"] == file_data["content"]
            assert response["mimetype"] is not None
    
    def test_security_access_control(self, preview_server, file_manager, sample_files):
        """セキュリティアクセス制御テスト"""
        session_id = file_manager.create_session()
        file_manager.save_files(session_id, sample_files)
        
        # 不正なセッションID
        invalid_response = preview_server.serve_file("invalid_session", "App.tsx")
        assert invalid_response["success"] is False
        
        # パストラバーサル攻撃
        malicious_response = preview_server.serve_file(session_id, "../../../etc/passwd")
        assert malicious_response["success"] is False
        
        # 存在しないファイル
        notfound_response = preview_server.serve_file(session_id, "nonexistent.txt")
        assert notfound_response["success"] is False


class TestFileIntegration:
    """ファイル管理統合テスト"""
    
    def test_end_to_end_file_workflow(self, file_manager, sample_files):
        """エンドツーエンドファイルワークフローテスト"""
        # 1. セッション作成
        session_id = file_manager.create_session()
        assert session_id is not None
        
        # 2. ファイル保存
        save_result = file_manager.save_files(session_id, sample_files)
        assert save_result["success"] is True
        
        # 3. セッション情報取得
        session = file_manager.get_session(session_id)
        assert session is not None
        assert len(session.files) == len(sample_files)
        
        # 4. プレビューサーバー初期化
        preview_server = PreviewServer(file_manager)
        
        # 5. プレビューURL生成
        preview_url = preview_server.generate_preview_url(session_id)
        assert preview_url is not None
        
        # 6. ファイル配信確認
        for file_data in sample_files:
            response = preview_server.serve_file(session_id, file_data["filename"])
            assert response["success"] is True
            assert response["content"] == file_data["content"]
    
    def test_concurrent_sessions(self, file_manager, sample_files):
        """同時セッションテスト"""
        import threading
        
        sessions_created = []
        errors = []
        
        def create_and_save_session():
            try:
                session_id = file_manager.create_session()
                result = file_manager.save_files(session_id, sample_files)
                if result["success"]:
                    sessions_created.append(session_id)
                else:
                    errors.append(result.get("error", "Unknown error"))
            except Exception as e:
                errors.append(str(e))
        
        # 同時セッション作成
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_and_save_session)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # エラーなく複数セッション作成
        assert len(errors) == 0
        assert len(sessions_created) == 5
        
        # 各セッションが独立している
        for session_id in sessions_created:
            session = file_manager.get_session(session_id)
            assert session is not None
            assert len(session.files) == len(sample_files)


class TestFileSecurity:
    """ファイルセキュリティテスト"""
    
    def test_path_traversal_prevention(self, file_manager):
        """パストラバーサル攻撃防止テスト"""
        malicious_files = [
            {"filename": "../../../malicious.txt", "content": "malicious", "language": "text"},
            {"filename": "..\\..\\windows.txt", "content": "windows path", "language": "text"},
            {"filename": "/etc/passwd", "content": "absolute path", "language": "text"}
        ]
        
        session_id = file_manager.create_session()
        result = file_manager.save_files(session_id, malicious_files)
        
        # 悪意のあるファイル名は拒否される
        if result["success"]:
            # 成功した場合、ファイル名がサニタイズされている
            session = file_manager.get_session(session_id)
            for file_entry in session.files:
                assert not file_entry.filename.startswith("/")
                assert ".." not in file_entry.filename
                assert not file_entry.filename.startswith("\\")
        else:
            # またはエラーで拒否される
            assert "security" in result.get("error", "").lower() or "invalid" in result.get("error", "").lower()
    
    def test_file_content_validation(self, file_manager):
        """ファイル内容検証テスト"""
        # 怪しい内容を含むファイル
        suspicious_files = [
            {"filename": "script.js", "content": "<script>alert('xss')</script>", "language": "javascript"},
            {"filename": "data.txt", "content": "SELECT * FROM users WHERE id = 1; DROP TABLE users;", "language": "text"}
        ]
        
        session_id = file_manager.create_session()
        result = file_manager.save_files(session_id, suspicious_files)
        
        # 基本的には保存されるが、配信時にエスケープ等の処理が必要
        assert result["success"] is True
        
        # プレビューサーバーでの配信時にセキュリティ処理確認
        preview_server = PreviewServer(file_manager)
        response = preview_server.serve_file(session_id, "script.js")
        
        assert response["success"] is True
        # セキュリティ処理（エスケープ等）が行われている
        assert response.get("escaped", False) is True or response.get("sanitized", False) is True


class TestFilePerformance:
    """ファイル処理パフォーマンステスト"""
    
    def test_large_file_handling(self, file_manager):
        """大容量ファイル処理テスト"""
        # 大きなファイルセット
        large_files = []
        for i in range(50):
            content = f"// File {i}\n" + "x" * 10000  # 10KB each
            large_files.append({
                "filename": f"file_{i}.js",
                "content": content,
                "language": "javascript"
            })
        
        start_time = time.time()
        
        session_id = file_manager.create_session()
        result = file_manager.save_files(session_id, large_files)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert result["success"] is True
        assert processing_time < 10.0  # 10秒以内
        
        # ファイル数確認
        session = file_manager.get_session(session_id)
        assert len(session.files) == 50
    
    def test_cleanup_performance(self, file_manager, sample_files):
        """クリーンアップパフォーマンステスト"""
        # 多数のセッション作成
        session_ids = []
        for i in range(20):
            session_id = file_manager.create_session()
            file_manager.save_files(session_id, sample_files)
            session_ids.append(session_id)
        
        # 半分を期限切れにする
        for i in range(0, 10):
            session = file_manager.get_session(session_ids[i])
            session.created_at = time.time() - 7200  # 2時間前
        
        # クリーンアップ性能測定
        start_time = time.time()
        cleaned_count = file_manager.cleanup_expired()
        cleanup_time = time.time() - start_time
        
        assert cleaned_count >= 10
        assert cleanup_time < 5.0  # 5秒以内


if __name__ == "__main__":
    pytest.main([__file__, "-v"])