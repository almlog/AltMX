"""
GitHub API統合サービス - Task 4.5実装
生成コードの自動リポジトリ作成・プッシュ・管理機能
"""
import asyncio
import aiohttp
import json
import re
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import hashlib
import os

# Configure logging
logger = logging.getLogger(__name__)

class GitHubAPIError(Exception):
    """GitHub API関連エラー"""
    pass

class GitHubAuthenticationError(GitHubAPIError):
    """GitHub認証エラー"""
    pass

class GitHubRateLimitError(GitHubAPIError):
    """GitHub API レート制限エラー"""
    pass

@dataclass
class GitHubRepository:
    """GitHubリポジトリ情報"""
    id: int
    name: str
    full_name: str
    html_url: str
    clone_url: str
    created_at: datetime
    cleanup_scheduled: Optional[datetime] = None

@dataclass
class DeploymentResult:
    """デプロイメント結果"""
    success: bool
    repository_url: str
    repository_id: int
    files_deployed: int
    deployment_id: str
    commit_sha: str
    cleanup_scheduled: bool
    error_message: Optional[str] = None

class GitHubAPI:
    """GitHub API Client - Low level API wrapper"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """GitHub API リクエスト実行"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 401:
                        raise GitHubAuthenticationError(f"Authentication failed: {response_data}")
                    elif response.status == 403:
                        raise GitHubRateLimitError(f"Rate limit exceeded: {response_data}")
                    elif response.status >= 400:
                        raise GitHubAPIError(f"GitHub API error ({response.status}): {response_data}")
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                raise GitHubAPIError(f"Network error: {str(e)}")
    
    async def get_user(self) -> Dict:
        """認証済みユーザー情報取得"""
        return await self._make_request("GET", "/user")
    
    async def create_repository(self, org: str, repo_data: Dict) -> Dict:
        """組織内にリポジトリ作成"""
        endpoint = f"/orgs/{org}/repos"
        return await self._make_request("POST", endpoint, repo_data)
    
    async def create_or_update_file(self, org: str, repo: str, path: str, 
                                   content: str, message: str, sha: Optional[str] = None) -> Dict:
        """ファイル作成または更新"""
        endpoint = f"/repos/{org}/{repo}/contents/{path}"
        
        # Base64エンコード
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message,
            "content": content_b64
        }
        
        if sha:
            data["sha"] = sha
            
        return await self._make_request("PUT", endpoint, data)
    
    async def delete_repository(self, org: str, repo: str) -> Dict:
        """リポジトリ削除"""
        endpoint = f"/repos/{org}/{repo}"
        return await self._make_request("DELETE", endpoint)
    
    async def create_from_template(self, template_owner: str, template_repo: str, 
                                  org: str, new_repo: Dict) -> Dict:
        """テンプレートからリポジトリ作成"""
        endpoint = f"/repos/{template_owner}/{template_repo}/generate"
        repo_data = {
            "owner": org,
            **new_repo
        }
        return await self._make_request("POST", endpoint, repo_data)

class GitHubService:
    """GitHub統合サービス - High level business logic"""
    
    def __init__(self, config: Dict[str, Any]):
        self.token = config["token"]
        self.organization = config["organization"]
        self.base_template = config.get("base_template", "altmx-template")
        self.cleanup_days = config.get("cleanup_days", 30)
        self.api = GitHubAPI(self.token)
        
        # Repository name pattern
        self.repo_name_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        
        # Dangerous content patterns
        self.dangerous_patterns = [
            re.compile(r'sk-[a-zA-Z0-9_-]{10,}'),  # OpenAI API keys (更新：最小10文字)
            re.compile(r'ghp_[a-zA-Z0-9_-]{36}'),   # GitHub tokens
            re.compile(r'glpat-[a-zA-Z0-9_-]{20}'), # GitLab tokens
            re.compile(r'xox[baprs]-[a-zA-Z0-9_-]{10,}'),  # Slack tokens
        ]
    
    async def validate_authentication(self) -> bool:
        """GitHub認証を検証"""
        try:
            user_data = await self.api.get_user()
            logger.info(f"Authenticated as: {user_data.get('login', 'Unknown')}")
            return True
        except (GitHubAuthenticationError, Exception) as e:
            logger.error(f"GitHub authentication failed: {e}")
            return False
    
    def validate_repository_name(self, name: str) -> bool:
        """リポジトリ名の妥当性検証"""
        if not name or len(name) == 0:
            return False
        if len(name) > 100:  # GitHub limit
            return False
        if not self.repo_name_pattern.match(name):
            return False
        return True
    
    def sanitize_file_content(self, content: str, file_path: str) -> str:
        """ファイルコンテンツのサニタイゼーション"""
        sanitized = content
        
        # Remove dangerous patterns
        for pattern in self.dangerous_patterns:
            sanitized = pattern.sub('[REDACTED-SENSITIVE-DATA]', sanitized)
        
        # Add warning comment for certain files
        if file_path.endswith(('.js', '.ts', '.py')):
            header_comment = f"// Generated by AltMX - {datetime.now().isoformat()}\n"
            if file_path.endswith('.py'):
                header_comment = f"# Generated by AltMX - {datetime.now().isoformat()}\n"
            sanitized = header_comment + sanitized
            
        return sanitized
    
    def generate_commit_message(self, code_data: Dict[str, Any]) -> str:
        """コミットメッセージ自動生成"""
        project_name = code_data.get("project_name", "AltMX Generated Project")
        description = code_data.get("description", "AI generated project")
        metadata = code_data.get("metadata", {})
        
        # Main commit message
        title = f"✨ Add {project_name} - Generated by AltMX AI"
        
        # Detailed description
        details = [
            f"Project: {description}",
            f"Session ID: {metadata.get('session_id', 'unknown')}",
            f"Generated by: {metadata.get('ai_model', 'AltMX-AI')}",
            f"Timestamp: {metadata.get('timestamp', datetime.now().isoformat())}",
            f"Files: {len(code_data.get('files', []))} files generated"
        ]
        
        #札幌弁での追加コメント
        if "札幌" in description or "札幌弁" in description:
            details.append("なんまらいい感じのプロジェクトだべ〜！ 🎌")
        
        commit_message = title + "\n\n" + "\n".join(details)
        return commit_message
    
    async def create_temporary_repository(self, project_name: str, description: str) -> GitHubRepository:
        """一時リポジトリ作成"""
        # Repository name validation and formatting
        repo_name = re.sub(r'[^a-zA-Z0-9._-]', '-', project_name.lower())
        if not self.validate_repository_name(repo_name):
            repo_name = f"altmx-generated-{hashlib.md5(project_name.encode()).hexdigest()[:8]}"
        
        repo_data = {
            "name": repo_name,
            "description": f"{description} (Auto-deletion scheduled in {self.cleanup_days} days)",
            "private": False,  # Public for demo purposes
            "has_issues": True,
            "has_projects": False,
            "has_wiki": False,
            "auto_init": True,  # Create with README
            "gitignore_template": "Node",  # Default to Node.js template
            "license_template": "mit"
        }
        
        try:
            response = await self.api.create_repository(self.organization, repo_data)
            
            repo = GitHubRepository(
                id=response["id"],
                name=response["name"],
                full_name=response["full_name"],
                html_url=response["html_url"],
                clone_url=response["clone_url"],
                created_at=datetime.fromisoformat(response["created_at"].replace('Z', '+00:00'))
            )
            
            logger.info(f"Created repository: {repo.html_url}")
            return repo
            
        except GitHubAPIError as e:
            logger.error(f"Failed to create repository: {e}")
            raise
    
    async def push_generated_code(self, repository: GitHubRepository, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成されたコードをリポジトリにプッシュ"""
        try:
            commit_message = self.generate_commit_message(code_data)
            files = code_data.get("files", [])
            
            pushed_files = []
            last_commit_sha = None
            
            for file_info in files:
                file_path = file_info["path"]
                file_content = file_info["content"]
                
                # Sanitize content
                sanitized_content = self.sanitize_file_content(file_content, file_path)
                
                # Push file
                response = await self.api.create_or_update_file(
                    org=self.organization,
                    repo=repository.name,
                    path=file_path,
                    content=sanitized_content,
                    message=f"{commit_message} - Add {file_path}"
                )
                
                pushed_files.append({
                    "path": file_path,
                    "sha": response["commit"]["sha"],
                    "size": len(sanitized_content)
                })
                
                last_commit_sha = response["commit"]["sha"]
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            result = {
                "success": True,
                "commit_sha": last_commit_sha,
                "files_pushed": len(pushed_files),
                "commit_message": commit_message,
                "pushed_files": pushed_files
            }
            
            logger.info(f"Pushed {len(pushed_files)} files to {repository.html_url}")
            return result
            
        except GitHubAPIError as e:
            logger.error(f"Failed to push code: {e}")
            # Attempt rollback - delete the repository if no files were pushed successfully
            if not pushed_files:
                try:
                    await self.api.delete_repository(self.organization, repository.name)
                    logger.info(f"Rolled back repository: {repository.name}")
                except:
                    logger.warning(f"Failed to rollback repository: {repository.name}")
            raise
    
    async def schedule_repository_cleanup(self, repository: GitHubRepository) -> datetime:
        """リポジトリクリーンアップのスケジューリング"""
        cleanup_date = datetime.now() + timedelta(days=self.cleanup_days)
        
        # In a real implementation, this would schedule a background job
        # For now, we'll simulate this with a simple storage mechanism
        cleanup_info = {
            "repository_id": repository.id,
            "repository_name": repository.name,
            "organization": self.organization,
            "cleanup_date": cleanup_date.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        # Store cleanup schedule (mock implementation)
        logger.info(f"Scheduled cleanup for {repository.name} at {cleanup_date}")
        
        # TODO: Integrate with Redis/Database for persistent scheduling
        return cleanup_date
    
    def schedule_cleanup(self, repo_data: Dict[str, Any]) -> None:
        """クリーンアップジョブのスケジューリング (mock)"""
        # Mock implementation - in real system would use Celery/Redis
        logger.info(f"Cleanup scheduled for repo {repo_data['id']}")
    
    async def create_from_template(self, template_repo: str, new_repo_name: str) -> Dict[str, Any]:
        """テンプレートリポジトリからの作成"""
        repo_data = {
            "name": new_repo_name,
            "description": f"Generated from {template_repo} template by AltMX",
            "private": False
        }
        
        try:
            response = await self.api.create_from_template(
                template_owner=self.organization,
                template_repo=template_repo,
                org=self.organization,
                new_repo=repo_data
            )
            
            logger.info(f"Created repository from template: {response['html_url']}")
            return response
            
        except GitHubAPIError as e:
            logger.error(f"Failed to create from template: {e}")
            raise
    
    async def deploy_generated_code(self, code_data: Dict[str, Any]) -> DeploymentResult:
        """完全なコードデプロイメントフロー"""
        deployment_id = hashlib.md5(f"{code_data.get('project_name', '')}{datetime.now()}".encode()).hexdigest()[:12]
        
        try:
            # Step 1: Create repository
            repository = await self.create_temporary_repository(
                project_name=code_data["project_name"],
                description=code_data["description"]
            )
            
            # Step 2: Push code
            push_result = await self.push_generated_code(repository, code_data)
            
            # Step 3: Schedule cleanup
            cleanup_date = await self.schedule_repository_cleanup(repository)
            
            # Success result
            result = DeploymentResult(
                success=True,
                repository_url=repository.html_url,
                repository_id=repository.id,
                files_deployed=push_result["files_pushed"],
                deployment_id=deployment_id,
                commit_sha=push_result["commit_sha"],
                cleanup_scheduled=True
            )
            
            logger.info(f"Successfully deployed code to {repository.html_url}")
            return result
            
        except Exception as e:
            # Error result
            result = DeploymentResult(
                success=False,
                repository_url="",
                repository_id=0,
                files_deployed=0,
                deployment_id=deployment_id,
                commit_sha="",
                cleanup_scheduled=False,
                error_message=str(e)
            )
            
            logger.error(f"Deployment failed: {e}")
            return result

# Mock function for scheduling (used in tests)
def schedule_cleanup_job(repo_id: int, cleanup_date: datetime, **kwargs):
    """Mock cleanup job scheduler"""
    logger.info(f"Mock: Scheduled cleanup job for repo {repo_id} at {cleanup_date}")