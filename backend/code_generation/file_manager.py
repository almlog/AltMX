"""
File Manager - Green段階（テストを通すための実装）
一時ファイル管理システム
"""

import os
import time
import uuid
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import threading

logger = logging.getLogger(__name__)


@dataclass
class FileEntry:
    """ファイルエントリ"""
    filename: str
    content: str
    language: str
    size: int = 0
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.size == 0:
            self.size = len(self.content.encode('utf-8'))


@dataclass
class PreviewSession:
    """プレビューセッション"""
    session_id: str
    files: List[FileEntry] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    ttl: int = 3600  # デフォルト1時間
    
    def is_expired(self) -> bool:
        """有効期限切れチェック"""
        return time.time() > (self.created_at + self.ttl)
    
    def get_total_size(self) -> int:
        """総ファイルサイズ"""
        return sum(file_entry.size for file_entry in self.files)


class FileManager:
    """
    一時ファイル管理システム
    セキュアな一時ディレクトリ管理とTTL付きクリーンアップ
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = self._init_config(config)
        self.temp_root = self.config["temp_root"]
        
        # セッション管理
        self._sessions: Dict[str, PreviewSession] = {}
        self._lock = threading.RLock()
        
        # 一時ディレクトリ初期化
        self._init_temp_directory()
        
        # クリーンアップスケジューラー
        self._cleanup_timer = None
        self._start_cleanup_scheduler()
        
        logger.info(f"FileManager initialized with temp_root: {self.temp_root}")
    
    def _init_config(self, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """設定初期化"""
        default_config = {
            "temp_root": os.path.join(os.getcwd(), "temp", "code_gen"),
            "default_ttl": 3600,  # 1時間
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "max_session_size": 100 * 1024 * 1024,  # 100MB
            "max_files_per_session": 100,
            "cleanup_interval": 300,  # 5分
            "allowed_extensions": [".tsx", ".ts", ".jsx", ".js", ".css", ".json", ".html", ".md", ".txt"]
        }
        
        if custom_config:
            default_config.update(custom_config)
        
        return default_config
    
    def _init_temp_directory(self):
        """一時ディレクトリ初期化"""
        try:
            Path(self.temp_root).mkdir(parents=True, exist_ok=True)
            logger.info(f"Temporary directory created: {self.temp_root}")
        except Exception as e:
            logger.error(f"Failed to create temp directory: {e}")
            raise
    
    def _start_cleanup_scheduler(self):
        """クリーンアップスケジューラー開始"""
        def cleanup_task():
            try:
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
            finally:
                # 次回実行をスケジュール
                self._cleanup_timer = threading.Timer(
                    self.config["cleanup_interval"],
                    cleanup_task
                )
                self._cleanup_timer.daemon = True
                self._cleanup_timer.start()
        
        self._cleanup_timer = threading.Timer(
            self.config["cleanup_interval"],
            cleanup_task
        )
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def create_session(self, ttl: Optional[int] = None) -> str:
        """
        新しいプレビューセッション作成
        
        Args:
            ttl: 有効期限（秒）
            
        Returns:
            セッションID
        """
        session_id = str(uuid.uuid4())
        if ttl is None:
            ttl = self.config["default_ttl"]
        
        session = PreviewSession(
            session_id=session_id,
            ttl=ttl
        )
        
        with self._lock:
            self._sessions[session_id] = session
        
        # セッション用ディレクトリ作成
        session_dir = Path(self.temp_root) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Session created: {session_id} (TTL: {ttl}s)")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[PreviewSession]:
        """
        セッション取得
        
        Args:
            session_id: セッションID
            
        Returns:
            セッション（期限切れ・存在しない場合はNone）
        """
        with self._lock:
            session = self._sessions.get(session_id)
            
            if session is None:
                return None
            
            # 有効期限チェック
            if session.is_expired():
                self._cleanup_session(session_id)
                return None
            
            return session
    
    def save_files(self, session_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ファイル保存
        
        Args:
            session_id: セッションID
            files: ファイルリスト
            
        Returns:
            保存結果
        """
        session = self.get_session(session_id)
        if session is None:
            return {"success": False, "error": "Session not found or expired"}
        
        try:
            # 制限チェック
            if len(files) > self.config["max_files_per_session"]:
                return {
                    "success": False,
                    "error": f"Too many files (max: {self.config['max_files_per_session']})"
                }
            
            total_size = 0
            file_entries = []
            
            for file_data in files:
                # ファイル名検証
                filename = self._sanitize_filename(file_data["filename"])
                if not filename:
                    return {
                        "success": False,
                        "error": f"Invalid filename: {file_data['filename']}"
                    }
                
                content = file_data["content"]
                language = file_data.get("language", "text")
                
                # サイズチェック
                file_size = len(content.encode('utf-8'))
                if file_size > self.config["max_file_size"]:
                    return {
                        "success": False,
                        "error": f"File too large: {filename} ({file_size} bytes)"
                    }
                
                total_size += file_size
                
                # ファイルエントリ作成
                file_entry = FileEntry(
                    filename=filename,
                    content=content,
                    language=language,
                    size=file_size
                )
                file_entries.append(file_entry)
            
            # セッション総サイズチェック
            current_size = session.get_total_size()
            if current_size + total_size > self.config["max_session_size"]:
                return {
                    "success": False,
                    "error": f"Session size limit exceeded ({current_size + total_size} bytes)"
                }
            
            # ファイル保存
            session_dir = Path(self.temp_root) / session_id
            
            with self._lock:
                for file_entry in file_entries:
                    # ディスクに保存
                    file_path = session_dir / file_entry.filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_entry.content)
                    
                    # セッションに追加
                    session.files.append(file_entry)
            
            logger.info(f"Saved {len(file_entries)} files to session {session_id}")
            
            return {
                "success": True,
                "files_saved": len(file_entries),
                "total_size": total_size,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error saving files to session {session_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        ファイル名サニタイズ
        
        Args:
            filename: 元のファイル名
            
        Returns:
            サニタイズされたファイル名（無効な場合は空文字）
        """
        if not filename:
            return ""
        
        # パストラバーサル対策
        filename = os.path.basename(filename)  # ディレクトリ部分削除
        filename = filename.replace("..", "")  # パストラバーサル文字削除
        
        # 危険な文字削除
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in dangerous_chars:
            filename = filename.replace(char, '')
        
        # 長さ制限
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        # 拡張子チェック
        _, ext = os.path.splitext(filename)
        if ext.lower() not in self.config["allowed_extensions"]:
            logger.warning(f"File extension not allowed: {ext}")
            return ""  # 許可されていない拡張子
        
        return filename
    
    def delete_session(self, session_id: str) -> bool:
        """
        セッション削除
        
        Args:
            session_id: セッションID
            
        Returns:
            削除成功フラグ
        """
        return self._cleanup_session(session_id)
    
    def _cleanup_session(self, session_id: str) -> bool:
        """
        セッションクリーンアップ（内部用）
        
        Args:
            session_id: セッションID
            
        Returns:
            クリーンアップ成功フラグ
        """
        try:
            with self._lock:
                # セッション削除
                if session_id in self._sessions:
                    del self._sessions[session_id]
            
            # ディスクからファイル削除
            session_dir = Path(self.temp_root) / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir)
            
            logger.info(f"Session cleaned up: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        期限切れセッションクリーンアップ
        
        Returns:
            クリーンアップしたセッション数
        """
        cleanup_count = 0
        expired_sessions = []
        
        # 期限切れセッション特定
        with self._lock:
            for session_id, session in self._sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)
        
        # クリーンアップ実行
        for session_id in expired_sessions:
            if self._cleanup_session(session_id):
                cleanup_count += 1
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} expired sessions")
        
        return cleanup_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        統計情報取得
        
        Returns:
            統計情報
        """
        with self._lock:
            active_sessions = len(self._sessions)
            total_files = sum(len(session.files) for session in self._sessions.values())
            total_size = sum(session.get_total_size() for session in self._sessions.values())
            
            # ディスク使用量
            disk_usage = 0
            try:
                for session_id in self._sessions:
                    session_dir = Path(self.temp_root) / session_id
                    if session_dir.exists():
                        disk_usage += sum(f.stat().st_size for f in session_dir.rglob('*') if f.is_file())
            except Exception as e:
                logger.error(f"Error calculating disk usage: {e}")
        
        return {
            "active_sessions": active_sessions,
            "total_files": total_files,
            "total_size_bytes": total_size,
            "disk_usage_bytes": disk_usage,
            "temp_root": self.temp_root,
            "config": self.config
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        ヘルスチェック
        
        Returns:
            ヘルス情報
        """
        try:
            # 一時ディレクトリアクセス確認
            temp_path = Path(self.temp_root)
            if not temp_path.exists():
                return {
                    "status": "unhealthy",
                    "error": "Temporary directory not accessible"
                }
            
            # 書き込み権限確認
            test_file = temp_path / "health_check.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            stats = self.get_stats()
            
            return {
                "status": "healthy",
                "stats": stats,
                "cleanup_timer_active": self._cleanup_timer.is_alive() if self._cleanup_timer else False
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def __del__(self):
        """デストラクタ"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()