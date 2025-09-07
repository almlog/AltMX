"""
Preview Server - Green段階（テストを通すための実装）
セキュアなプレビュー環境・ファイル配信システム
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import quote
import logging

from .file_manager import FileManager, PreviewSession

logger = logging.getLogger(__name__)


class PreviewServer:
    """
    プレビューサーバー
    セキュアなファイル配信とプレビュー環境提供
    """
    
    def __init__(self, file_manager: FileManager, config: Optional[Dict[str, Any]] = None):
        self.file_manager = file_manager
        self.config = self._init_config(config)
        
        logger.info("PreviewServer initialized")
    
    def _init_config(self, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """設定初期化"""
        default_config = {
            "base_preview_url": "http://localhost:8000/preview",
            "allowed_hosts": ["localhost", "127.0.0.1"],
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "security_headers": True,
            "content_escaping": True,
            "cache_control": "no-cache, no-store, must-revalidate"
        }
        
        if custom_config:
            default_config.update(custom_config)
        
        return default_config
    
    def generate_preview_url(self, session_id: str) -> str:
        """
        プレビューURL生成
        
        Args:
            session_id: セッションID
            
        Returns:
            プレビューURL
        """
        # セッション存在確認
        session = self.file_manager.get_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        
        # セキュアなURL生成
        base_url = self.config["base_preview_url"]
        encoded_session = quote(session_id, safe='')
        
        preview_url = f"{base_url}/{encoded_session}"
        
        logger.info(f"Generated preview URL for session: {session_id}")
        return preview_url
    
    def serve_file(self, session_id: str, filename: str) -> Dict[str, Any]:
        """
        ファイル配信
        
        Args:
            session_id: セッションID
            filename: ファイル名
            
        Returns:
            配信結果
        """
        try:
            # セッション取得
            session = self.file_manager.get_session(session_id)
            if session is None:
                return {
                    "success": False,
                    "error": "Session not found or expired",
                    "status_code": 404
                }
            
            # ファイル名セキュリティチェック
            if not self._is_safe_filename(filename):
                return {
                    "success": False,
                    "error": "Invalid filename",
                    "status_code": 403
                }
            
            # ファイル検索
            file_entry = None
            for f in session.files:
                if f.filename == filename:
                    file_entry = f
                    break
            
            if file_entry is None:
                return {
                    "success": False,
                    "error": "File not found",
                    "status_code": 404
                }
            
            # MIME型判定
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                mimetype = "text/plain"
            
            # コンテンツ処理
            content = file_entry.content
            escaped = False
            sanitized = False
            
            # セキュリティ処理
            if self.config["content_escaping"]:
                if self._needs_escaping(content, mimetype):
                    content = self._escape_content(content, mimetype)
                    escaped = True
                    sanitized = True
            
            # セキュリティヘッダー
            headers = {}
            if self.config["security_headers"]:
                headers.update({
                    "Cache-Control": self.config["cache_control"],
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "SAMEORIGIN",
                    "Content-Security-Policy": "default-src 'self'; script-src 'none';"
                })
            
            logger.info(f"Served file: {filename} for session: {session_id}")
            
            return {
                "success": True,
                "content": content,
                "mimetype": mimetype,
                "headers": headers,
                "filename": filename,
                "size": len(content.encode('utf-8')),
                "escaped": escaped,
                "sanitized": sanitized,
                "status_code": 200
            }
            
        except Exception as e:
            logger.error(f"Error serving file {filename} for session {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 500
            }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        セッション情報取得
        
        Args:
            session_id: セッションID
            
        Returns:
            セッション情報
        """
        try:
            session = self.file_manager.get_session(session_id)
            if session is None:
                return {
                    "success": False,
                    "error": "Session not found or expired"
                }
            
            # ファイルリスト生成
            files_info = []
            for file_entry in session.files:
                files_info.append({
                    "filename": file_entry.filename,
                    "language": file_entry.language,
                    "size": file_entry.size,
                    "created_at": file_entry.created_at
                })
            
            return {
                "success": True,
                "session_id": session_id,
                "created_at": session.created_at,
                "ttl": session.ttl,
                "files_count": len(session.files),
                "total_size": session.get_total_size(),
                "files": files_info,
                "preview_url": self.generate_preview_url(session_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting session info for {session_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_safe_filename(self, filename: str) -> bool:
        """
        ファイル名セキュリティチェック
        
        Args:
            filename: ファイル名
            
        Returns:
            安全フラグ
        """
        if not filename:
            return False
        
        # パストラバーサル チェック
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        # 危険な文字チェック
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            if char in filename:
                return False
        
        # 長さチェック
        if len(filename) > 255:
            return False
        
        return True
    
    def _needs_escaping(self, content: str, mimetype: str) -> bool:
        """
        エスケープ必要性チェック
        
        Args:
            content: コンテンツ
            mimetype: MIME型
            
        Returns:
            エスケープ必要フラグ
        """
        # HTML/JSファイルは常にエスケープ
        if mimetype in ["text/html", "application/javascript", "text/javascript"]:
            return True
        
        # スクリプトタグ等の危険パターン
        dangerous_patterns = [
            "<script", "</script>",
            "javascript:", "data:",
            "onload=", "onclick=", "onerror=",
            "eval(", "Function(",
            "document.write", "innerHTML"
        ]
        
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    def _escape_content(self, content: str, mimetype: str) -> str:
        """
        コンテンツエスケープ
        
        Args:
            content: 元コンテンツ
            mimetype: MIME型
            
        Returns:
            エスケープ後コンテンツ
        """
        if mimetype == "text/html":
            # HTML エスケープ
            content = content.replace("&", "&amp;")
            content = content.replace("<", "&lt;")
            content = content.replace(">", "&gt;")
            content = content.replace('"', "&quot;")
            content = content.replace("'", "&#x27;")
        
        elif mimetype in ["application/javascript", "text/javascript"]:
            # JavaScriptコメントアウト
            lines = content.split('\n')
            escaped_lines = []
            for line in lines:
                if any(pattern in line.lower() for pattern in ["eval(", "function(", "document.write"]):
                    escaped_lines.append(f"// SECURITY: {line}")
                else:
                    escaped_lines.append(line)
            content = '\n'.join(escaped_lines)
        
        return content
    
    def list_session_files(self, session_id: str) -> Dict[str, Any]:
        """
        セッションファイル一覧取得
        
        Args:
            session_id: セッションID
            
        Returns:
            ファイル一覧
        """
        try:
            session = self.file_manager.get_session(session_id)
            if session is None:
                return {
                    "success": False,
                    "error": "Session not found or expired"
                }
            
            files = []
            for file_entry in session.files:
                # ファイル配信URL生成
                file_url = f"{self.config['base_preview_url']}/{quote(session_id)}/{quote(file_entry.filename)}"
                
                files.append({
                    "filename": file_entry.filename,
                    "language": file_entry.language,
                    "size": file_entry.size,
                    "created_at": file_entry.created_at,
                    "preview_url": file_url,
                    "mimetype": mimetypes.guess_type(file_entry.filename)[0] or "text/plain"
                })
            
            return {
                "success": True,
                "session_id": session_id,
                "files": files,
                "total_files": len(files),
                "total_size": session.get_total_size()
            }
            
        except Exception as e:
            logger.error(f"Error listing files for session {session_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        プレビューサーバーヘルスチェック
        
        Returns:
            ヘルス情報
        """
        try:
            # FileManager ヘルスチェック
            fm_health = self.file_manager.health_check()
            
            if fm_health["status"] != "healthy":
                return {
                    "status": "unhealthy",
                    "error": f"FileManager unhealthy: {fm_health.get('error', 'Unknown')}"
                }
            
            return {
                "status": "healthy",
                "service": "Preview Server",
                "file_manager_status": fm_health["status"],
                "config": {
                    "base_preview_url": self.config["base_preview_url"],
                    "security_headers": self.config["security_headers"],
                    "content_escaping": self.config["content_escaping"]
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }