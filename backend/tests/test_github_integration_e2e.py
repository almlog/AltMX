"""
GitHub統合のEnd-to-End実環境テスト
実際のGitHub APIを使用した統合テスト（要: 環境変数設定）
"""
import pytest
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Skip tests if GitHub credentials are not configured
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_ORG = os.getenv("GITHUB_ORGANIZATION", "")
SKIP_E2E = not (GITHUB_TOKEN and GITHUB_ORG) or GITHUB_TOKEN == "ghp_your_personal_access_token_here"

@pytest.mark.skipif(SKIP_E2E, reason="GitHub credentials not configured in .env")
class TestGitHubIntegrationE2E:
    """実環境でのGitHub統合テスト"""
    
    @pytest.fixture
    def real_github_config(self):
        """実際のGitHub設定を使用"""
        return {
            "token": GITHUB_TOKEN,
            "organization": GITHUB_ORG,
            "base_template": os.getenv("GITHUB_BASE_TEMPLATE", "altmx-template"),
            "cleanup_days": int(os.getenv("GITHUB_CLEANUP_DAYS", "30"))
        }
    
    @pytest.fixture
    def test_code_data(self):
        """テスト用のコード生成データ"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return {
            "project_name": f"altmx-test-{timestamp}",
            "description": "E2E Test - 札幌弁AIアシスタントのテストプロジェクト",
            "files": [
                {
                    "path": "README.md",
                    "content": f"# AltMX E2E Test Project\\n\\nCreated at {timestamp}\\n\\n札幌弁でなんまらいいプロジェクトだべ〜！"
                },
                {
                    "path": "src/test.js",
                    "content": "console.log('AltMX E2E Test - なんまら動くっしょ！');"
                },
                {
                    "path": "package.json",
                    "content": '{\n  "name": "altmx-e2e-test",\n  "version": "0.0.1",\n  "description": "E2E Test Package"\n}'
                }
            ],
            "metadata": {
                "generated_by": "AltMX-E2E-Test",
                "session_id": f"e2e-test-{timestamp}",
                "timestamp": datetime.now().isoformat(),
                "ai_model": "test-mode"
            }
        }
    
    @pytest.mark.asyncio
    async def test_real_github_authentication(self, real_github_config):
        """実際のGitHub認証テスト"""
        from github_service import GitHubService
        
        service = GitHubService(real_github_config)
        is_valid = await service.validate_authentication()
        
        assert is_valid == True, "GitHub authentication failed - check your token"
        logger.info(f"✅ Successfully authenticated with GitHub as {GITHUB_ORG}")
    
    @pytest.mark.asyncio
    async def test_real_repository_creation_and_deletion(self, real_github_config):
        """実際のリポジトリ作成と削除テスト"""
        from github_service import GitHubService
        
        service = GitHubService(real_github_config)
        test_repo_name = f"altmx-e2e-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            # Create repository
            repo = await service.create_temporary_repository(
                project_name=test_repo_name,
                description="E2E Test - This will be deleted immediately"
            )
            
            assert repo.name.startswith("altmx-e2e-test")
            assert repo.html_url.startswith(f"https://github.com/{GITHUB_ORG}/")
            logger.info(f"✅ Created test repository: {repo.html_url}")
            
            # Clean up immediately (don't wait 30 days!)
            await service.api.delete_repository(GITHUB_ORG, repo.name)
            logger.info(f"✅ Deleted test repository: {repo.name}")
            
        except Exception as e:
            logger.error(f"❌ E2E test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_complete_deployment_flow_real(self, real_github_config, test_code_data):
        """完全なデプロイメントフローの実環境テスト"""
        from github_service import GitHubService
        
        service = GitHubService(real_github_config)
        
        try:
            # Deploy code to real GitHub
            result = await service.deploy_generated_code(test_code_data)
            
            assert result.success == True
            assert result.repository_url.startswith(f"https://github.com/{GITHUB_ORG}/")
            assert result.files_deployed == 3
            
            logger.info(f"✅ Successfully deployed to: {result.repository_url}")
            logger.info(f"   Files deployed: {result.files_deployed}")
            logger.info(f"   Commit SHA: {result.commit_sha}")
            
            # Extract repo name from URL for cleanup
            repo_name = result.repository_url.split("/")[-1]
            
            # IMPORTANT: Clean up test repository immediately
            logger.info(f"🧹 Cleaning up test repository: {repo_name}")
            await service.api.delete_repository(GITHUB_ORG, repo_name)
            logger.info(f"✅ Test repository deleted successfully")
            
        except Exception as e:
            logger.error(f"❌ Deployment test failed: {e}")
            # Try to clean up even if test failed
            if 'repo_name' in locals():
                try:
                    await service.api.delete_repository(GITHUB_ORG, repo_name)
                    logger.info(f"🧹 Cleaned up failed test repository")
                except:
                    logger.warning(f"⚠️ Could not clean up test repository: {repo_name}")
            raise

def main():
    """E2Eテストの手動実行"""
    if SKIP_E2E:
        print("\n" + "="*60)
        print("[WARNING] GitHub E2E テストをスキップします")
        print("="*60)
        print("\n実環境テストを実行するには、以下の設定が必要です：\n")
        print("1. GitHubでPersonal Access Tokenを生成")
        print("   https://github.com/settings/tokens")
        print("   必要な権限: repo (Full control of private repositories)")
        print("\n2. backend/.env ファイルに以下を設定:")
        print("   GITHUB_TOKEN=ghp_your_actual_token_here")
        print("   GITHUB_ORGANIZATION=your-github-username")
        print("\n3. テスト実行:")
        print("   cd backend && python test_github_integration_e2e.py")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("[START] GitHub E2E 実環境テストを開始します")
        print(f"   Organization/User: {GITHUB_ORG}")
        print("="*60 + "\n")
        
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", __file__, "-v", "-s"],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n[SUCCESS] 全ての実環境テストが成功しました！")
        else:
            print("\n[FAILED] 一部のテストが失敗しました")

if __name__ == "__main__":
    main()