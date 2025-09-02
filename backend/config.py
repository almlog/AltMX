"""
AltMX Configuration Management
APIキーと設定の安全な管理
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class AIProvider(Enum):
    """利用可能なAIプロバイダー"""
    GEMINI = "gemini"
    CLAUDE = "claude"


class Config:
    """アプリケーション設定"""
    
    # API Keys (環境変数から取得)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    
    # Development Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info").upper()
    
    # AI Provider Settings
    PRIMARY_AI_PROVIDER: str = os.getenv("PRIMARY_AI_PROVIDER", "gemini")
    ENABLE_FALLBACK: bool = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    TIMEOUT_SECONDS: int = int(os.getenv("TIMEOUT_SECONDS", "10"))
    
    # Sapporo Dialect Settings
    SAPPORO_DIALECT_LEVEL: int = int(os.getenv("SAPPORO_DIALECT_LEVEL", "2"))
    
    @classmethod
    def validate(cls) -> bool:
        """設定の検証"""
        errors = []
        
        # Primary APIキーの確認
        if cls.PRIMARY_AI_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set")
        elif cls.PRIMARY_AI_PROVIDER == "claude" and not cls.CLAUDE_API_KEY:
            errors.append("CLAUDE_API_KEY is not set")
            
        # Fallback設定の確認
        if cls.ENABLE_FALLBACK:
            if not cls.GEMINI_API_KEY and not cls.CLAUDE_API_KEY:
                errors.append("At least one API key must be set for fallback")
                
        if errors:
            for error in errors:
                print(f"❌ Configuration Error: {error}")
            return False
            
        return True
    
    @classmethod
    def get_active_provider(cls) -> AIProvider:
        """現在のプロバイダーを取得"""
        if cls.PRIMARY_AI_PROVIDER == "claude":
            return AIProvider.CLAUDE
        return AIProvider.GEMINI
    
    @classmethod
    def has_api_key(cls, provider: AIProvider) -> bool:
        """指定プロバイダーのAPIキーが設定されているか"""
        if provider == AIProvider.GEMINI:
            return bool(cls.GEMINI_API_KEY)
        elif provider == AIProvider.CLAUDE:
            return bool(cls.CLAUDE_API_KEY)
        return False


# 設定のエクスポート
config = Config()