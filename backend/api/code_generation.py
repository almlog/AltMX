"""
Code Generation API Router - Green段階（テストを通すための実装）
FastAPI コード生成エンドポイント
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time
import logging
import asyncio

from code_generation.engine import CodeGenerationEngine, GenerationRequest, GenerationResult
from code_generation.prompt_templates import PromptTemplateManager
from code_generation.validators import CodeValidator
from code_generation.response_parser import CodeBlock

logger = logging.getLogger(__name__)

# Initialize components
engine = CodeGenerationEngine()
template_manager = PromptTemplateManager()
validator = CodeValidator()

# Create router
router = APIRouter()


# Request/Response models
class GenerationRequestModel(BaseModel):
    user_prompt: str = Field(..., min_length=1, max_length=10000, description="User's code generation prompt")
    complexity: str = Field(default="medium", description="Complexity level: simple, medium, high")
    include_security: bool = Field(default=True, description="Include security validation")
    include_accessibility: bool = Field(default=False, description="Include accessibility features")
    target_framework: str = Field(default="react", description="Target framework")
    max_files: int = Field(default=10, ge=1, le=20, description="Maximum number of files to generate")
    timeout: int = Field(default=60, ge=5, le=300, description="Timeout in seconds")


class ValidationRequestModel(BaseModel):
    code_blocks: List[Dict[str, Any]] = Field(..., description="Code blocks to validate")


class GeneratedFileModel(BaseModel):
    filename: str
    content: str
    language: str
    description: Optional[str] = None


class GenerationResponseModel(BaseModel):
    success: bool
    generated_files: List[GeneratedFileModel] = []
    errors: List[str] = []
    warnings: List[str] = []
    performance_metrics: Dict[str, Any] = {}


class ValidationResultModel(BaseModel):
    filename: str
    is_valid: bool
    syntax_errors: List[Dict[str, Any]] = []
    type_errors: List[Dict[str, Any]] = []
    lint_errors: List[Dict[str, Any]] = []
    security_risks: List[Dict[str, Any]] = []


class ValidationResponseModel(BaseModel):
    is_valid: bool
    validation_results: List[ValidationResultModel] = []
    security_risks: List[Dict[str, Any]] = []


class TemplateModel(BaseModel):
    name: str
    description: str
    complexity_levels: List[str] = []


class TemplatesResponseModel(BaseModel):
    templates: List[TemplateModel] = []


class TemplateDetailModel(BaseModel):
    name: str
    description: str
    base_prompt: str
    complexity_adjustments: Dict[str, str] = {}


@router.post("/generate", response_model=GenerationResponseModel)
async def generate_code(request: GenerationRequestModel) -> GenerationResponseModel:
    """
    コード生成エンドポイント
    
    自然言語プロンプトからReact/TypeScriptコードを生成
    """
    try:
        logger.info(f"Code generation request: {request.user_prompt[:50]}...")
        
        # リクエスト変換
        generation_request = GenerationRequest(
            user_prompt=request.user_prompt,
            complexity=request.complexity,
            include_security=request.include_security,
            include_accessibility=request.include_accessibility,
            target_framework=request.target_framework,
            max_files=request.max_files,
            timeout=request.timeout
        )
        
        # キャッシュ付きコード生成実行
        result = await engine.generate_code_with_cache(generation_request)
        
        # レスポンス変換
        generated_files = []
        for file_info in result.generated_files:
            generated_files.append(GeneratedFileModel(
                filename=file_info["filename"],
                content=file_info["content"],
                language=file_info["language"],
                description=file_info.get("description", "")
            ))
        
        return GenerationResponseModel(
            success=result.success,
            generated_files=generated_files,
            errors=result.errors,
            warnings=result.warnings,
            performance_metrics=result.performance_metrics
        )
        
    except ValueError as e:
        logger.error(f"Validation error in code generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except asyncio.TimeoutError:
        logger.error("Code generation timeout")
        raise HTTPException(status_code=408, detail="Code generation request timed out")
    
    except Exception as e:
        logger.error(f"Internal error in code generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during code generation")


@router.post("/validate", response_model=ValidationResponseModel)
async def validate_code(request: ValidationRequestModel) -> ValidationResponseModel:
    """
    コード検証エンドポイント
    
    提供されたコードブロックの構文・型・セキュリティ検証
    """
    try:
        logger.info(f"Code validation request for {len(request.code_blocks)} files")
        
        validation_results = []
        all_security_risks = []
        overall_valid = True
        
        for block_data in request.code_blocks:
            # CodeBlockオブジェクト作成
            code_block = CodeBlock(
                content=block_data["content"],
                filename=block_data["filename"],
                language=block_data.get("language", "typescript"),
                description=block_data.get("description", "")
            )
            
            # 検証実行
            validation_result = validator.validate_comprehensive(code_block)
            
            # セキュリティ検証
            from code_generation.security_validator import SecurityValidator
            security_validator = SecurityValidator()
            security_risks = security_validator.scan_security_risks(code_block)
            
            # 結果変換
            result_model = ValidationResultModel(
                filename=code_block.filename,
                is_valid=validation_result.is_valid,
                syntax_errors=[{"message": err.message, "line": err.line, "column": err.column} 
                              for err in validation_result.syntax_errors],
                type_errors=[{"message": err.message, "line": err.line, "column": err.column} 
                            for err in validation_result.type_errors],
                lint_errors=[{"message": err.message, "line": err.line, "column": err.column} 
                            for err in validation_result.lint_errors],
                security_risks=[{"type": risk.risk_type, "severity": risk.severity, 
                               "description": risk.description, "line": risk.line} 
                              for risk in security_risks]
            )
            
            validation_results.append(result_model)
            all_security_risks.extend(security_risks)
            
            if not validation_result.is_valid:
                overall_valid = False
        
        return ValidationResponseModel(
            is_valid=overall_valid,
            validation_results=validation_results,
            security_risks=[{"type": risk.risk_type, "severity": risk.severity, 
                           "description": risk.description} for risk in all_security_risks]
        )
        
    except Exception as e:
        logger.error(f"Error in code validation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during code validation")


@router.get("/templates", response_model=TemplatesResponseModel)
async def get_templates() -> TemplatesResponseModel:
    """
    利用可能なテンプレート一覧取得
    """
    try:
        templates = template_manager.list_templates()
        
        template_models = []
        for template_name in templates:
            template = template_manager.get_template(template_name)
            template_models.append(TemplateModel(
                name=template.name,
                description=template.description,
                complexity_levels=list(template.complexity_adjustments.keys())
            ))
        
        return TemplatesResponseModel(templates=template_models)
        
    except Exception as e:
        logger.error(f"Error retrieving templates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving templates")


@router.get("/templates/{template_name}", response_model=TemplateDetailModel)
async def get_template_detail(template_name: str) -> TemplateDetailModel:
    """
    特定テンプレートの詳細取得
    """
    try:
        template = template_manager.get_template(template_name)
        
        return TemplateDetailModel(
            name=template.name,
            description=template.description,
            base_prompt=template.base_prompt[:500] + "..." if len(template.base_prompt) > 500 else template.base_prompt,
            complexity_adjustments=template.complexity_adjustments
        )
        
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
    
    except Exception as e:
        logger.error(f"Error retrieving template {template_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving template")


# Health check for code generation service
@router.get("/health")
async def code_generation_health():
    """コード生成サービスヘルスチェック"""
    try:
        # 簡単な動作確認
        test_request = GenerationRequest(
            user_prompt="test",
            complexity="simple",
            timeout=5
        )
        
        # テンプレートが正常に動作するかチェック
        templates = template_manager.list_templates()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "Code Generation API",
            "available_templates": len(templates),
            "engine_ready": True,
            "cache_stats": engine.get_cache_stats()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "timestamp": time.time(),
            "service": "Code Generation API",
            "error": str(e)
        }


@router.get("/cache/stats")
async def get_cache_stats():
    """キャッシュ統計取得"""
    try:
        return engine.get_cache_stats()
    except Exception as e:
        logger.error(f"Error retrieving cache stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving cache stats")


@router.delete("/cache")
async def clear_cache():
    """キャッシュクリア"""
    try:
        success = engine.clear_cache()
        if success:
            return {"message": "Cache cleared successfully", "timestamp": time.time()}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Internal server error clearing cache")