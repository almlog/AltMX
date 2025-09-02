"""
Code Generation WebSocket - Green段階（テストを通すための実装）
WebSocket リアルタイム進捗通知
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
import time
from typing import Dict, List, Any

from code_generation.engine import CodeGenerationEngine, GenerationRequest

logger = logging.getLogger(__name__)

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "connected_at": time.time(),
            "session_id": f"session_{len(self.active_connections)}"
        }
        logger.info(f"WebSocket connection established: {self.connection_data[websocket]['session_id']}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            session_id = self.connection_data[websocket]["session_id"]
            del self.connection_data[websocket]
            logger.info(f"WebSocket connection closed: {session_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


# Initialize components
manager = ConnectionManager()
engine = CodeGenerationEngine()
router = APIRouter()


class ProgressTracker:
    """進捗追跡用ヘルパークラス"""
    
    def __init__(self, websocket: WebSocket, manager: ConnectionManager):
        self.websocket = websocket
        self.manager = manager
        self.current_stage = ""
        self.progress = 0
    
    async def update_progress(self, stage: str, progress: int, message: str = ""):
        """進捗更新"""
        self.current_stage = stage
        self.progress = progress
        
        await self.manager.send_personal_message({
            "type": "progress_update",
            "stage": stage,
            "progress": progress,
            "message": message,
            "timestamp": time.time()
        }, self.websocket)
    
    async def send_error(self, error_message: str):
        """エラー送信"""
        await self.manager.send_personal_message({
            "type": "error",
            "message": error_message,
            "timestamp": time.time()
        }, self.websocket)
    
    async def send_completion(self, result: dict):
        """完了通知"""
        await self.manager.send_personal_message({
            "type": "generation_complete",
            "result": result,
            "timestamp": time.time()
        }, self.websocket)


@router.websocket("/code-generation")
async def websocket_code_generation(websocket: WebSocket):
    """
    コード生成WebSocketエンドポイント
    リアルタイム進捗通知付きコード生成
    """
    await manager.connect(websocket)
    tracker = ProgressTracker(websocket, manager)
    
    try:
        # 接続確立メッセージ
        await manager.send_personal_message({
            "type": "connection_established",
            "session_id": manager.connection_data[websocket]["session_id"],
            "message": "WebSocket connection established for code generation"
        }, websocket)
        
        while True:
            # クライアントからのメッセージ受信
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "generate_code":
                await handle_generation_request(message.get("data", {}), tracker)
            elif message.get("action") == "cancel_generation":
                await tracker.update_progress("cancelled", 100, "Generation cancelled by user")
            else:
                await tracker.send_error(f"Unknown action: {message.get('action')}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await tracker.send_error(f"WebSocket error: {str(e)}")
        except:
            pass
        finally:
            manager.disconnect(websocket)


async def handle_generation_request(request_data: dict, tracker: ProgressTracker):
    """
    コード生成リクエスト処理
    
    各ステップで進捗を更新
    """
    try:
        # リクエスト検証
        await tracker.update_progress("validation", 10, "Validating request")
        
        if not request_data.get("user_prompt"):
            await tracker.send_error("user_prompt is required")
            return
        
        # GenerationRequest作成
        await tracker.update_progress("preparation", 20, "Preparing generation request")
        
        generation_request = GenerationRequest(
            user_prompt=request_data["user_prompt"],
            complexity=request_data.get("complexity", "medium"),
            include_security=request_data.get("include_security", True),
            include_accessibility=request_data.get("include_accessibility", False),
            target_framework=request_data.get("target_framework", "react"),
            max_files=request_data.get("max_files", 10),
            timeout=request_data.get("timeout", 60)
        )
        
        # プロンプト最適化段階
        await tracker.update_progress("prompt_optimization", 30, "Optimizing prompt")
        
        # AI生成段階（時間がかかる）
        await tracker.update_progress("ai_generation", 40, "Generating code with AI")
        
        # 実際のコード生成実行
        result = await engine.generate_code(generation_request)
        
        # 解析段階
        await tracker.update_progress("parsing", 70, "Parsing AI response")
        
        # 検証段階
        await tracker.update_progress("validation", 80, "Validating generated code")
        
        # ファイル構成段階
        await tracker.update_progress("organization", 90, "Organizing files")
        
        # 完了
        await tracker.update_progress("completed", 100, "Code generation completed")
        
        # 結果送信
        result_data = {
            "success": result.success,
            "generated_files": result.generated_files,
            "errors": result.errors,
            "warnings": result.warnings,
            "performance_metrics": result.performance_metrics
        }
        
        await tracker.send_completion(result_data)
        
    except asyncio.TimeoutError:
        await tracker.send_error("Code generation timed out")
    except Exception as e:
        logger.error(f"Error in WebSocket generation: {e}")
        await tracker.send_error(f"Generation error: {str(e)}")


# Additional utility endpoints
@router.get("/active-connections")
async def get_active_connections():
    """アクティブな接続数取得"""
    return {
        "active_connections": len(manager.active_connections),
        "connection_info": [
            {
                "session_id": data["session_id"],
                "connected_at": data["connected_at"],
                "duration_seconds": time.time() - data["connected_at"]
            }
            for data in manager.connection_data.values()
        ]
    }