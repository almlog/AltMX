"""
Code Generation Engine - Green段階（テストを通すための実装）
メインエンジン統合システム
"""

import time
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .prompt_templates import PromptTemplateManager
from .prompt_optimizer import PromptOptimizer
from .response_parser import ResponseParser, ParsedCode, CodeBlock
from .validators import CodeValidator, ValidationResult
from .security_validator import SecurityValidator
from .code_corrector import CodeCorrector
from .file_organizer import FileOrganizer, FileStructure
from .cache import CodeGenerationCache
from ai_integration.llm_client import LLMClient, AIProvider

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """コード生成リクエスト"""
    user_prompt: str
    complexity: str = "medium"
    include_security: bool = True
    include_accessibility: bool = False
    target_framework: str = "react"
    max_files: int = 10
    timeout: int = 60


@dataclass
class GenerationResult:
    """コード生成結果"""
    success: bool
    generated_files: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: str):
        """エラー追加"""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        """警告追加"""
        self.warnings.append(warning)


class CodeGenerationEngine:
    """
    コード生成メインエンジン
    全コンポーネントを統合してコード生成を実行
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, cache: Optional[CodeGenerationCache] = None):
        self.config = self._init_config(config)
        
        # コンポーネント初期化
        self.prompt_template = PromptTemplateManager()
        self.prompt_optimizer = PromptOptimizer()
        self.llm_client = LLMClient()
        self.response_parser = ResponseParser()
        self.validator = CodeValidator()
        self.security_validator = SecurityValidator()
        self.corrector = CodeCorrector()
        self.file_organizer = FileOrganizer()
        
        # キャッシュ初期化
        if cache is not None:
            self.cache = cache
        else:
            cache_config = self.config.get('cache', {})
            self.cache = CodeGenerationCache(
                config=cache_config,
                use_redis=cache_config.get('use_redis', False)
            )
        
        logger.info("CodeGenerationEngine initialized")
    
    def _init_config(self, custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """設定初期化"""
        default_config = {
            'max_file_count': 10,
            'enable_auto_correction': True,
            'timeout_seconds': 60,
            'enable_security_scan': True,
            'enable_performance_metrics': True,
            'max_retry_attempts': 2
        }
        
        if custom_config:
            default_config.update(custom_config)
        
        return default_config
    
    async def generate_code(
        self, 
        request: GenerationRequest, 
        timeout: Optional[int] = None
    ) -> GenerationResult:
        """
        メインコード生成エントリーポイント
        
        Args:
            request: 生成リクエスト
            timeout: タイムアウト（秒）
            
        Returns:
            生成結果
        """
        start_time = time.time()
        result = GenerationResult(success=True)
        
        # タイムアウト設定
        actual_timeout = timeout or request.timeout or self.config['timeout_seconds']
        
        try:
            # リクエスト検証
            if not self._validate_request(request, result):
                return result
            
            logger.info(f"Starting code generation for prompt: {request.user_prompt[:50]}...")
            
            # タイムアウト付きで実行
            result = await asyncio.wait_for(
                self._execute_generation_pipeline(request, result, start_time),
                timeout=actual_timeout
            )
            
        except asyncio.TimeoutError:
            result.add_error(f"Code generation timed out after {actual_timeout} seconds")
            logger.error("Code generation timeout")
        except Exception as e:
            result.add_error(f"Unexpected error during code generation: {str(e)}")
            logger.error(f"Code generation error: {e}", exc_info=True)
        
        # パフォーマンス測定
        if self.config['enable_performance_metrics']:
            result.performance_metrics['total_time'] = time.time() - start_time
        
        logger.info(f"Code generation completed. Success: {result.success}")
        return result
    
    async def generate_code_with_cache(
        self, 
        request: GenerationRequest, 
        timeout: Optional[int] = None
    ) -> GenerationResult:
        """
        キャッシュ付きコード生成
        
        Args:
            request: 生成リクエスト
            timeout: タイムアウト（秒）
            
        Returns:
            生成結果（キャッシュまたは新規生成）
        """
        # キャッシュキー生成
        cache_key = self.cache.generate_prompt_hash(
            user_prompt=request.user_prompt,
            complexity=request.complexity,
            include_security=request.include_security,
            include_accessibility=request.include_accessibility,
            target_framework=request.target_framework
        )
        
        # キャッシュチェック
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for key: {cache_key[:8]}...")
            
            # キャッシュデータをGenerationResultに変換
            result = GenerationResult(
                success=cached_result["success"],
                generated_files=cached_result["generated_files"],
                errors=cached_result["errors"],
                warnings=cached_result["warnings"],
                performance_metrics=cached_result.get("performance_metrics", {})
            )
            result.performance_metrics["cache_hit"] = True
            return result
        
        # キャッシュミス - 新規生成
        logger.info(f"Cache miss for key: {cache_key[:8]}...")
        result = await self.generate_code(request, timeout)
        
        # 成功時のみキャッシュ保存
        if result.success:
            cache_data = {
                "success": result.success,
                "generated_files": result.generated_files,
                "errors": result.errors,
                "warnings": result.warnings,
                "performance_metrics": result.performance_metrics
            }
            
            # TTL計算（複雑度に基づく）
            ttl = self._calculate_cache_ttl(request.complexity)
            
            # キャッシュ保存
            cache_success = self.cache.set(cache_key, cache_data, ttl=ttl)
            if cache_success:
                logger.info(f"Result cached with key: {cache_key[:8]}... (TTL: {ttl}s)")
            else:
                logger.warning(f"Failed to cache result for key: {cache_key[:8]}...")
        
        result.performance_metrics["cache_hit"] = False
        return result
    
    def _calculate_cache_ttl(self, complexity: str) -> int:
        """
        複雑度に基づくキャッシュTTL計算
        
        Args:
            complexity: 複雑度
            
        Returns:
            TTL（秒）
        """
        ttl_map = {
            "simple": 7200,    # 2時間
            "medium": 3600,    # 1時間
            "high": 1800,      # 30分
            "complex": 900     # 15分
        }
        return ttl_map.get(complexity, 3600)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        キャッシュ統計取得
        
        Returns:
            キャッシュ統計情報
        """
        return self.cache.get_stats()
    
    def clear_cache(self) -> bool:
        """
        キャッシュクリア
        
        Returns:
            成功フラグ
        """
        return self.cache.clear()
    
    def _validate_request(self, request: GenerationRequest, result: GenerationResult) -> bool:
        """リクエスト検証"""
        if not request.user_prompt or not request.user_prompt.strip():
            result.add_error("User prompt cannot be empty")
            return False
        
        if len(request.user_prompt) > 10000:
            result.add_error("User prompt too long (max 10000 characters)")
            return False
        
        return True
    
    async def _execute_generation_pipeline(
        self, 
        request: GenerationRequest, 
        result: GenerationResult,
        start_time: float
    ) -> GenerationResult:
        """生成パイプライン実行"""
        
        # 1. プロンプト最適化
        ai_start_time = time.time()
        optimized_prompt = self._optimize_prompt(request)
        logger.debug("Prompt optimization completed")
        
        # 2. AI生成
        ai_response = await self._generate_with_ai(optimized_prompt, request, result)
        if not result.success:
            return result
        
        ai_end_time = time.time()
        result.performance_metrics['ai_generation_time'] = ai_end_time - ai_start_time
        
        # 3. レスポンス解析
        parse_start_time = time.time()
        parsed_code = self._parse_ai_response(ai_response, result)
        if not result.success:
            return result
        
        parse_end_time = time.time()
        result.performance_metrics['parsing_time'] = parse_end_time - parse_start_time
        
        # 4. コード検証・修正
        validation_start_time = time.time()
        validated_blocks = await self._validate_and_correct_code(parsed_code.code_blocks, request, result)
        
        validation_end_time = time.time()
        result.performance_metrics['validation_time'] = validation_end_time - validation_start_time
        
        # 5. ファイル構成
        file_structure = self._organize_files(validated_blocks, result)
        
        # 6. 結果生成
        self._generate_final_result(file_structure, result)
        
        return result
    
    def _select_template_type(self, request: GenerationRequest) -> str:
        """リクエストに基づいてテンプレートタイプを選択"""
        prompt_lower = request.user_prompt.lower()
        
        if any(word in prompt_lower for word in ["form", "login", "register", "input", "validation"]):
            return "form"
        elif any(word in prompt_lower for word in ["dashboard", "chart", "analytics", "admin"]):
            return "dashboard"
        elif any(word in prompt_lower for word in ["list", "table", "data", "items"]):
            return "list"
        else:
            # デフォルトはformテンプレート
            return "form"
    
    def _optimize_prompt(self, request: GenerationRequest) -> str:
        """プロンプト最適化"""
        # リクエストに基づいてテンプレートタイプを選択
        template_type = self._select_template_type(request)
        
        return self.prompt_optimizer.optimize(
            user_prompt=request.user_prompt,
            complexity=request.complexity,
            template_type=template_type,
            include_security=request.include_security
        )
    
    async def _generate_with_ai(
        self, 
        prompt: str, 
        request: GenerationRequest, 
        result: GenerationResult
    ) -> Optional[str]:
        """AI生成実行"""
        try:
            # プロバイダー選択
            provider = self._select_ai_provider(request)
            
            # AI生成実行
            llm_response = await self.llm_client.generate_code(
                prompt=prompt,
                provider=provider,
                enable_fallback=True
            )
            
            if not llm_response.success:
                result.add_error(f"AI generation failed: {llm_response.error_message}")
                return None
            
            return llm_response.content
            
        except Exception as e:
            result.add_error(f"AI service unavailable: {str(e)}")
            return None
    
    def _select_ai_provider(self, request: GenerationRequest) -> AIProvider:
        """AIプロバイダー選択"""
        # 複雑さに応じてプロバイダー選択
        if request.complexity == "high":
            return AIProvider.GEMINI  # 高性能
        else:
            return AIProvider.GEMINI  # デフォルト
    
    def _parse_ai_response(self, ai_response: str, result: GenerationResult) -> Optional[ParsedCode]:
        """AIレスポンス解析"""
        try:
            parsed_code = self.response_parser.parse_response(ai_response)
            
            if not parsed_code.code_blocks:
                result.add_error("No code blocks found in AI response")
                return None
            
            logger.debug(f"Parsed {len(parsed_code.code_blocks)} code blocks")
            return parsed_code
            
        except Exception as e:
            result.add_error(f"Failed to parse AI response: {str(e)}")
            return None
    
    async def _validate_and_correct_code(
        self, 
        code_blocks: List[CodeBlock], 
        request: GenerationRequest, 
        result: GenerationResult
    ) -> List[CodeBlock]:
        """コード検証・修正"""
        validated_blocks = []
        
        for block in code_blocks:
            try:
                # 構文・型検証
                validation_result = self.validator.validate_comprehensive(block)
                
                # セキュリティ検証
                if request.include_security and self.config['enable_security_scan']:
                    security_risks = self.security_validator.scan_security_risks(block)
                    if security_risks:
                        high_risks = [r for r in security_risks if r.severity in ["critical", "high"]]
                        if high_risks:
                            result.add_warning(f"Security risks found in {block.filename}")
                
                # 自動修正
                if self.config['enable_auto_correction'] and not validation_result.is_valid:
                    corrected_block = self.corrector.fix_common_issues(block)
                    if corrected_block:
                        validated_blocks.append(corrected_block)
                        result.add_warning(f"Auto-corrected issues in {block.filename}")
                    else:
                        validated_blocks.append(block)
                        result.add_warning(f"Validation issues in {block.filename}")
                else:
                    validated_blocks.append(block)
                    
            except Exception as e:
                logger.error(f"Error validating {block.filename}: {e}")
                validated_blocks.append(block)  # エラーでも含める
                result.add_warning(f"Validation error in {block.filename}")
        
        return validated_blocks
    
    def _organize_files(self, code_blocks: List[CodeBlock], result: GenerationResult) -> FileStructure:
        """ファイル構成"""
        try:
            file_structure = self.file_organizer.organize_files(code_blocks)
            
            # ファイル数制限チェック
            if len(file_structure.files) > self.config['max_file_count']:
                result.add_warning(f"Generated {len(file_structure.files)} files (limit: {self.config['max_file_count']})")
                # 制限内に収める
                file_structure.files = file_structure.files[:self.config['max_file_count']]
            
            return file_structure
            
        except Exception as e:
            logger.error(f"Error organizing files: {e}")
            # フォールバック：シンプルな構成
            return FileStructure(
                files=code_blocks,
                structure_type="flat",
                dependencies=[]
            )
    
    def _generate_final_result(self, file_structure: FileStructure, result: GenerationResult):
        """最終結果生成"""
        for block in file_structure.files:
            file_info = {
                'filename': block.filename,
                'content': block.content,
                'language': block.detect_language(),
                'description': block.description
            }
            result.generated_files.append(file_info)
        
        logger.info(f"Generated {len(result.generated_files)} files")