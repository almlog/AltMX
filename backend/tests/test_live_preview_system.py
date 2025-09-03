"""
ライブプレビューシステムのテスト
TDD: RED → 失敗するテストを最初に作成
"""
import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient


class TestLivePreviewSystem:
    """ライブプレビューシステムテスト"""
    
    @pytest.mark.asyncio
    async def test_preview_server_initialization(self):
        """プレビューサーバー初期化テスト"""
        from live_preview_system import PreviewServer
        
        server = PreviewServer(port=3001)
        assert server is not None
        assert server.port == 3001
        assert server.is_running == False
        assert hasattr(server, 'start')
        assert hasattr(server, 'stop')
        assert hasattr(server, 'update_preview')
    
    @pytest.mark.asyncio
    async def test_code_compilation_and_bundling(self):
        """コード コンパイル・バンドルテスト"""
        from live_preview_system import CodeCompiler
        
        compiler = CodeCompiler()
        
        # TypeScript/React コード
        tsx_code = '''
        import React from 'react';
        
        const PreviewComponent: React.FC = () => {
          return (
            <div>
              <h1>Live Preview Test</h1>
              <p>This is a test component</p>
            </div>
          );
        };
        
        export default PreviewComponent;
        '''
        
        # コンパイル実行
        result = await compiler.compile(tsx_code)
        assert result["success"] == True
        assert result["compiled_code"] is not None
        assert "PreviewComponent" in result["compiled_code"]
        assert result["compile_time"] < 500  # 500ms以内
        assert len(result["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_hot_reload_functionality(self):
        """Hot Reload機能テスト"""
        from live_preview_system import HotReloadManager
        
        hot_reload = HotReloadManager()
        
        # WebSocketクライアント接続モック
        mock_client = MagicMock()
        hot_reload.register_client(mock_client)
        
        # コード更新通知
        update_data = {
            "type": "code_update",
            "timestamp": "2025-09-03T10:00:00",
            "code": "const updated = true;"
        }
        
        await hot_reload.notify_update(update_data)
        
        # クライアントに更新が送信されたか確認
        mock_client.send_json.assert_called_once()
        sent_data = mock_client.send_json.call_args[0][0]
        assert sent_data["type"] == "code_update"
        assert "timestamp" in sent_data
    
    @pytest.mark.asyncio 
    async def test_error_handling_and_display(self):
        """エラーハンドリング・表示テスト"""
        from live_preview_system import ErrorHandler
        
        error_handler = ErrorHandler()
        
        # コンパイルエラーのテスト
        compile_error = {
            "type": "SyntaxError",
            "message": "Unexpected token",
            "line": 10,
            "column": 15,
            "file": "PreviewComponent.tsx"
        }
        
        formatted_error = error_handler.format_error(compile_error)
        assert formatted_error["severity"] == "error"
        assert "SyntaxError" in formatted_error["display_message"]
        assert formatted_error["location"]["line"] == 10
        assert formatted_error["location"]["column"] == 15
        
        # ランタイムエラーのテスト
        runtime_error = {
            "type": "ReferenceError",
            "message": "useState is not defined",
            "stack": "at PreviewComponent..."
        }
        
        formatted_runtime = error_handler.format_error(runtime_error)
        assert formatted_runtime["severity"] == "error"
        assert "useState" in formatted_runtime["display_message"]
    
    @pytest.mark.asyncio
    async def test_preview_update_performance(self):
        """プレビュー更新パフォーマンステスト"""
        from live_preview_system import PreviewSystem
        
        system = PreviewSystem()
        
        # パフォーマンス測定
        code = "const TestComponent = () => <div>Performance Test</div>;"
        
        import time
        start_time = time.time()
        
        result = await system.update_preview(code)
        
        update_time = (time.time() - start_time) * 1000  # ms変換
        
        assert result["success"] == True
        assert update_time < 500  # 500ms以内
        assert result["performance"]["update_time"] < 500
    
    @pytest.mark.asyncio
    async def test_multiple_component_preview(self):
        """複数コンポーネント同時プレビューテスト"""
        from live_preview_system import MultiPreviewManager
        
        manager = MultiPreviewManager()
        
        # 複数コンポーネント登録
        components = [
            {
                "id": "comp1",
                "code": "const Comp1 = () => <div>Component 1</div>;"
            },
            {
                "id": "comp2", 
                "code": "const Comp2 = () => <div>Component 2</div>;"
            }
        ]
        
        for comp in components:
            result = await manager.add_component(comp["id"], comp["code"])
            assert result["success"] == True
        
        # 全コンポーネントのプレビュー取得
        previews = await manager.get_all_previews()
        assert len(previews) == 2
        assert "comp1" in previews
        assert "comp2" in previews
    
    @pytest.mark.asyncio
    async def test_preview_state_persistence(self):
        """プレビュー状態永続化テスト"""
        from live_preview_system import PreviewStateManager
        
        state_manager = PreviewStateManager()
        
        # 状態保存
        state = {
            "component": "TestComponent",
            "props": {"title": "Test", "count": 0},
            "viewport": {"width": 1920, "height": 1080}
        }
        
        await state_manager.save_state("preview1", state)
        
        # 状態復元
        restored = await state_manager.restore_state("preview1")
        assert restored["component"] == "TestComponent"
        assert restored["props"]["title"] == "Test"
        assert restored["viewport"]["width"] == 1920
    
    @pytest.mark.asyncio
    async def test_css_and_styling_support(self):
        """CSS・スタイリングサポートテスト"""
        from live_preview_system import StyleProcessor
        
        processor = StyleProcessor()
        
        # CSS-in-JSコード
        component_with_styles = '''
        import styled from 'styled-components';
        
        const StyledDiv = styled.div`
          background: blue;
          padding: 20px;
        `;
        
        const Component = () => <StyledDiv>Styled Component</StyledDiv>;
        '''
        
        result = await processor.process_styles(component_with_styles)
        assert result["success"] == True
        assert result["styles_extracted"] == True
        assert "blue" in result["css"]
        assert "padding: 20px" in result["css"]


class TestPreviewAPI:
    """プレビューAPI統合テスト"""
    
    @pytest.mark.asyncio
    async def test_preview_websocket_endpoint(self):
        """WebSocketエンドポイントテスト"""
        from main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as client:
            with client.websocket_connect("/ws/preview") as websocket:
                # 初期接続確認
                data = websocket.receive_json()
                assert data["type"] == "connection_established"
                
                # コード送信
                websocket.send_json({
                    "action": "update_code",
                    "code": "const Test = () => <div>Test</div>;"
                })
                
                # レスポンス確認
                response = websocket.receive_json()
                assert response["type"] == "preview_updated"
                assert response["success"] == True
    
    @pytest.mark.asyncio
    async def test_preview_rest_api(self):
        """REST APIエンドポイントテスト"""
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # プレビュー生成API
        response = client.post("/api/preview/generate", json={
            "code": "const Component = () => <h1>Preview</h1>;",
            "options": {
                "hot_reload": True,
                "error_display": True
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["preview_url"] is not None
        assert data["session_id"] is not None
        assert data["hot_reload_enabled"] == True