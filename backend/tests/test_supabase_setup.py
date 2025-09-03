"""
Supabase Setup Tests (TDD)
テストファースト！まずは失敗するテストを書く
"""

import pytest
import os
from unittest.mock import Mock, patch
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()


class TestSupabaseProjectSetup:
    """Supabaseプロジェクト設定のテスト"""
    
    def test_supabase_environment_variables_are_set(self):
        """Supabase環境変数が設定されていること"""
        # RED: まだ.envにSupabase設定がないので失敗する
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        assert supabase_url is not None, "SUPABASE_URL must be set"
        assert supabase_key is not None, "SUPABASE_ANON_KEY must be set"
        assert supabase_url.startswith("https://"), "SUPABASE_URL must be valid URL"
        assert len(supabase_key) > 50, "SUPABASE_ANON_KEY must be valid key"
    
    def test_supabase_client_creation(self):
        """Supabaseクライアントが作成できること"""
        # RED: まだクライアント作成機能がないので失敗する
        from database_client import get_supabase_client, MockSupabaseClient  # まだ存在しない
        
        client = get_supabase_client()
        # 実際のClientまたはMockSupabaseClientのいずれかであることを確認
        assert isinstance(client, Client) or isinstance(client, MockSupabaseClient)
    
    @pytest.mark.asyncio
    async def test_supabase_connection(self):
        """Supabase接続テスト"""
        # RED: まだ接続テスト機能がないので失敗する
        from database_client import test_supabase_connection  # まだ存在しない
        
        result = await test_supabase_connection()
        assert result == True


class TestDatabaseSchema:
    """データベーススキーマのテスト"""
    
    def test_demo_sessions_table_exists(self):
        """demo_sessionsテーブルが存在すること"""
        # RED: まだテーブルがないので失敗する
        from database_client import get_supabase_client
        
        client = get_supabase_client()
        # テーブル存在確認
        result = client.table('demo_sessions').select('*').limit(1).execute()
        assert result.data is not None  # テーブルが存在すればエラーにならない
    
    def test_participants_table_exists(self):
        """participantsテーブルが存在すること"""
        # RED: まだテーブルがないので失敗する
        from database_client import get_supabase_client
        
        client = get_supabase_client()
        result = client.table('participants').select('*').limit(1).execute()
        assert result.data is not None
    
    def test_messages_table_exists(self):
        """messagesテーブルが存在すること"""
        # RED: まだテーブルがないので失敗する
        from database_client import get_supabase_client
        
        client = get_supabase_client()
        result = client.table('messages').select('*').limit(1).execute()
        assert result.data is not None
    
    def test_generated_code_table_exists(self):
        """generated_codeテーブルが存在すること"""
        # RED: まだテーブルがないので失敗する
        from database_client import get_supabase_client
        
        client = get_supabase_client()
        result = client.table('generated_code').select('*').limit(1).execute()
        assert result.data is not None


class TestRowLevelSecurity:
    """Row Level Security (RLS) のテスト"""
    
    @pytest.mark.asyncio
    async def test_rls_is_enabled_on_tables(self):
        """RLSが全テーブルで有効になっていること"""
        # RED: まだRLS設定がないので失敗する
        from database_client import check_rls_status
        
        tables = ['demo_sessions', 'participants', 'messages', 'generated_code']
        
        for table in tables:
            rls_status = await check_rls_status(table)
            assert rls_status == True, f"RLS must be enabled on {table}"
    
    @pytest.mark.asyncio 
    async def test_demo_session_access_policy(self):
        """デモセッションアクセスポリシーのテスト"""
        # RED: まだポリシーがないので失敗する
        from database_client import test_access_policy
        
        # セッション作成者のみアクセス可能
        result = await test_access_policy('demo_sessions', 'session_owner_policy')
        assert result == True


class TestRealtimeFeatures:
    """リアルタイム機能のテスト"""
    
    @pytest.mark.asyncio
    async def test_realtime_subscription_setup(self):
        """リアルタイム購読設定のテスト"""
        # RED: まだリアルタイム設定がないので失敗する
        from database_client import setup_realtime_subscription
        
        subscription = await setup_realtime_subscription('messages')
        assert subscription is not None
        assert subscription.is_active() == True


if __name__ == "__main__":
    # TDD Red段階確認のためテスト実行
    print("=== Supabase Setup Test Suite (RED Stage) ===")
    print("These tests should FAIL initially - that's the point of TDD!")
    print("")
    
    # pytest実行
    pytest.main([__file__, "-v", "--tb=short"])