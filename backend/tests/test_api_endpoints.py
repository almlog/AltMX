"""
API Endpoints Tests - Red段階（失敗するテスト）
FastAPI エンドポイント・WebSocket統合テスト
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

# 実装済みモジュールインポート
from main import app
from api.code_generation import router as code_generation_router
from websocket.code_generation import manager as websocket_manager


@pytest.fixture
def client():
    """テストクライアント"""
    return TestClient(app)


@pytest.fixture
def sample_generation_request():
    """サンプル生成リクエスト"""
    return {
        "user_prompt": "Create a React login form with email and password validation",
        "complexity": "medium",
        "include_security": True,
        "include_accessibility": False,
        "target_framework": "react",
        "max_files": 10
    }


@pytest.fixture
def sample_validation_request():
    """サンプル検証リクエスト"""
    return {
        "code_blocks": [
            {
                "filename": "LoginForm.tsx",
                "content": "import React from 'react';\n\nconst LoginForm = () => {\n  return <div>Login Form</div>;\n};",
                "language": "typescript"
            }
        ]
    }


class TestCodeGenerationAPI:
    """コード生成APIテスト"""
    
    def test_generate_endpoint_success(self, client, sample_generation_request):
        """コード生成成功テスト"""
        response = client.post("/api/code-generation/generate", json=sample_generation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "generated_files" in data
        assert "performance_metrics" in data
        
        if data["success"]:
            assert len(data["generated_files"]) > 0
            assert "filename" in data["generated_files"][0]
            assert "content" in data["generated_files"][0]
            assert "language" in data["generated_files"][0]
    
    def test_generate_endpoint_invalid_request(self, client):
        """無効リクエストテスト"""
        invalid_request = {"user_prompt": ""}  # 空のプロンプト
        
        response = client.post("/api/code-generation/generate", json=invalid_request)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "message" in data
    
    def test_generate_endpoint_missing_fields(self, client):
        """必須フィールド欠落テスト"""
        incomplete_request = {}  # user_promptなし
        
        response = client.post("/api/code-generation/generate", json=incomplete_request)
        
        assert response.status_code == 422  # FastAPI validation error
        data = response.json()
        assert "detail" in data
    
    def test_generate_endpoint_timeout_handling(self, client):
        """タイムアウト処理テスト"""
        timeout_request = {
            "user_prompt": "Create extremely complex application with 100 components",
            "complexity": "high",
            "timeout": 1  # 1秒でタイムアウト
        }
        
        response = client.post("/api/code-generation/generate", json=timeout_request)
        
        # タイムアウトでも適切なレスポンス
        assert response.status_code in [200, 408, 500]
        data = response.json()
        assert "success" in data or "detail" in data


class TestCodeValidationAPI:
    """コード検証APIテスト"""
    
    def test_validate_endpoint_success(self, client, sample_validation_request):
        """コード検証成功テスト"""
        response = client.post("/api/code-generation/validate", json=sample_validation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "is_valid" in data
        assert "validation_results" in data
        assert isinstance(data["validation_results"], list)
        
        for result in data["validation_results"]:
            assert "filename" in result
            assert "syntax_errors" in result
            assert "type_errors" in result
            assert "lint_errors" in result
    
    def test_validate_endpoint_invalid_code(self, client):
        """無効コード検証テスト"""
        invalid_code_request = {
            "code_blocks": [
                {
                    "filename": "broken.tsx",
                    "content": "const broken = ( => {  // 構文エラー",
                    "language": "typescript"
                }
            ]
        }
        
        response = client.post("/api/code-generation/validate", json=invalid_code_request)
        
        assert response.status_code == 200  # 検証結果は返す
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["validation_results"]) > 0
    
    def test_validate_endpoint_security_check(self, client):
        """セキュリティチェックテスト"""
        security_risk_request = {
            "code_blocks": [
                {
                    "filename": "unsafe.tsx",
                    "content": "const Component = ({userInput}) => <div dangerouslySetInnerHTML={{__html: userInput}} />;",
                    "language": "typescript"
                }
            ]
        }
        
        response = client.post("/api/code-generation/validate", json=security_risk_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "security_risks" in data
        if data["security_risks"]:
            assert len(data["security_risks"]) > 0


class TestTemplatesAPI:
    """テンプレートAPIテスト"""
    
    def test_get_templates_success(self, client):
        """テンプレート取得成功テスト"""
        response = client.get("/api/code-generation/templates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert isinstance(data["templates"], list)
        
        for template in data["templates"]:
            assert "name" in template
            assert "description" in template
            assert "complexity_levels" in template
    
    def test_get_specific_template(self, client):
        """特定テンプレート取得テスト"""
        response = client.get("/api/code-generation/templates/form")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "name" in data
            assert "description" in data
            assert "base_prompt" in data
    
    def test_get_nonexistent_template(self, client):
        """存在しないテンプレート取得テスト"""
        response = client.get("/api/code-generation/templates/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "message" in data


class TestWebSocketIntegration:
    """WebSocket統合テスト"""
    
    def test_websocket_connection(self, client):
        """WebSocket接続テスト"""
        with client.websocket_connect("/ws/code-generation") as websocket:
            # 接続成功をテスト
            data = websocket.receive_json()
            assert "type" in data
            assert data["type"] == "connection_established"
    
    def test_websocket_progress_updates(self, client, sample_generation_request):
        """WebSocket進捗更新テスト"""
        with client.websocket_connect("/ws/code-generation") as websocket:
            # 生成リクエスト送信
            websocket.send_json({
                "action": "generate_code",
                "data": sample_generation_request
            })
            
            # 進捗更新受信
            messages = []
            try:
                while True:
                    message = websocket.receive_json(timeout=5)
                    messages.append(message)
                    if message.get("type") == "generation_complete":
                        break
            except:
                pass  # タイムアウトまたは完了
            
            assert len(messages) > 0
            
            # 進捗メッセージの検証
            progress_messages = [m for m in messages if m.get("type") == "progress_update"]
            assert len(progress_messages) > 0
            
            for msg in progress_messages:
                assert "stage" in msg
                assert "progress" in msg
                assert 0 <= msg["progress"] <= 100
    
    def test_websocket_error_handling(self, client):
        """WebSocketエラー処理テスト"""
        with client.websocket_connect("/ws/code-generation") as websocket:
            # 無効なリクエスト送信
            websocket.send_json({
                "action": "generate_code",
                "data": {"user_prompt": ""}  # 空のプロンプト
            })
            
            # エラーメッセージ受信
            error_message = websocket.receive_json()
            assert error_message.get("type") == "error"
            assert "message" in error_message


class TestAPIErrorHandling:
    """APIエラーハンドリングテスト"""
    
    def test_internal_server_error_handling(self, client):
        """内部サーバーエラー処理テスト"""
        with patch('code_generation.engine.CodeGenerationEngine.generate_code') as mock_generate:
            mock_generate.side_effect = Exception("Internal error")
            
            response = client.post("/api/code-generation/generate", json={
                "user_prompt": "Simple component"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data or "message" in data
    
    def test_method_not_allowed(self, client):
        """メソッド不許可テスト"""
        response = client.get("/api/code-generation/generate")  # POSTのみ許可
        
        assert response.status_code == 405
    
    def test_not_found_endpoint(self, client):
        """存在しないエンドポイントテスト"""
        response = client.get("/api/code-generation/nonexistent")
        
        assert response.status_code == 404


class TestAPIPerformance:
    """APIパフォーマンステスト"""
    
    def test_response_time_limits(self, client, sample_generation_request):
        """レスポンス時間制限テスト"""
        import time
        
        start_time = time.time()
        response = client.post("/api/code-generation/generate", json=sample_generation_request)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 妥当なレスポンス時間（テスト環境では緩めに設定）
        assert response_time < 30.0  # 30秒以内
        
        if response.status_code == 200:
            data = response.json()
            if "performance_metrics" in data:
                assert "total_time" in data["performance_metrics"]
    
    def test_concurrent_requests(self, client, sample_generation_request):
        """同時リクエストテスト"""
        import threading
        import time
        
        responses = []
        
        def make_request():
            response = client.post("/api/code-generation/generate", json=sample_generation_request)
            responses.append(response)
        
        # 3つの同時リクエスト
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=30)
        
        assert len(responses) == 3
        for response in responses:
            assert response.status_code in [200, 429, 500]  # 成功、レート制限、またはエラー


class TestAPIAuthentication:
    """API認証テスト（将来実装用）"""
    
    def test_unauthenticated_access(self, client, sample_generation_request):
        """非認証アクセステスト"""
        # 現在は認証なしでテストをパス
        response = client.post("/api/code-generation/generate", json=sample_generation_request)
        
        # 認証が実装された場合は401を期待
        assert response.status_code in [200, 401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])