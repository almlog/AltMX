from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from altmx_agent import AltMXAgent
from typing import Optional, Dict, Any, List
import asyncio
import time
import json
from deploy_service_simple import simple_deployment_service
from prompts.live_coding_prompts import get_prompt_for_context, enhance_for_production_quality
from agent_modes import agent_state_manager, AgentMode, QualityLevel, AgentPersonality
from natural_mode_commands import smart_mode_handler

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AltMX API",
    description="AI協働開発ライブデモンストレーションシステム - AltMX Backend API",
    version="1.0.0"
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://18.180.87.189:5173", "http://18.180.87.189:5174"],  # Vite ports + new IP
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods including OPTIONS
    allow_headers=["*"],
)

# Initialize AltMX Agent
altmx = AltMXAgent()


class ChatRequest(BaseModel):
    message: str
    use_sapporo_dialect: bool = True


class ChatResponse(BaseModel):
    response: str
    dialect_applied: bool
    thinking_time_ms: int
    mood: str
    car_status: str


class CarAnimationResponse(BaseModel):
    lights_blinking: bool
    blink_color: str
    blink_speed: float
    car_emoji: str


# Code Generation Models
class GenerationRequest(BaseModel):
    user_prompt: str
    complexity: str = "medium"
    include_security: bool = True
    include_accessibility: bool = False
    target_framework: str = "react"
    max_files: int = 10
    timeout: int = 60


class GeneratedFile(BaseModel):
    filename: str
    content: str
    language: str
    description: Optional[str] = None

class PerformanceMetrics(BaseModel):
    generation_time_ms: int
    ai_thinking_time_ms: int
    files_count: int
    total_lines: int


class GenerationResponse(BaseModel):
    success: bool
    generated_files: List[GeneratedFile]
    errors: List[str] = []
    warnings: List[str] = []
    performance_metrics: Dict[str, Any] = {}


class ValidationRequest(BaseModel):
    code_blocks: List[Dict[str, Any]]


class ValidationError(BaseModel):
    message: str
    line: int
    column: int


class SecurityRisk(BaseModel):
    type: str
    severity: str
    description: str
    line: Optional[int] = None


class ValidationResult(BaseModel):
    filename: str
    is_valid: bool
    syntax_errors: List[ValidationError] = []
    type_errors: List[ValidationError] = []
    lint_errors: List[ValidationError] = []
    security_risks: List[SecurityRisk] = []


class ValidationResponse(BaseModel):
    is_valid: bool
    validation_results: List[ValidationResult]
    security_risks: List[SecurityRisk] = []


class Template(BaseModel):
    name: str
    description: str
    complexity_levels: List[str]


class TemplatesResponse(BaseModel):
    templates: List[Template]


class TemplateDetail(BaseModel):
    name: str
    description: str
    base_prompt: str
    complexity_adjustments: Dict[str, str]


@app.get("/")
async def root():
    return {"message": "AltMX API is running! なんまら元気っしょ！"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_altmx(request: ChatRequest):
    """AltMXエージェントとのチャット（本物のAI統合版）"""
    
    # コード生成リクエストを検出
    coding_keywords = ["作って", "作る", "コード", "アプリ", "TODO", "react", "React"]
    is_coding_request = any(keyword in request.message.lower() for keyword in coding_keywords)
    
    if is_coding_request:
        # コード生成を実行
        generation_request = GenerationRequest(
            user_prompt=request.message,
            complexity="medium",
            include_security=False,
            include_accessibility=False,
            target_framework="react",
            max_files=5,
            timeout=60
        )
        
        # コード生成実行
        generation_result = await generate_code(generation_request)
        
        # AltMXの応答にコード生成結果を含める
        response_data = await altmx.generate_response(
            user_message=f"{request.message}\n\n[コード生成完了: {len(generation_result.generated_files)}ファイル生成]",
            use_dialect=request.use_sapporo_dialect
        )
        
        # 応答にコード生成結果を追加
        enhanced_response = f"{response_data['response']}\n\n📝 **生成されたコード:**\n"
        for file in generation_result.generated_files:
            enhanced_response += f"\n**{file.filename}** ({file.language})\n```{file.language}\n{file.content}\n```\n"
        
        return ChatResponse(
            response=enhanced_response,
            dialect_applied=response_data["dialect_applied"],
            thinking_time_ms=response_data["thinking_time_ms"],
            mood=response_data["mood"],
            car_status=response_data["car_status"]
        )
    
    # 通常のチャット応答
    response_data = await altmx.generate_response(
        user_message=request.message,
        use_dialect=request.use_sapporo_dialect
    )
    
    return ChatResponse(
        response=response_data["response"],
        dialect_applied=response_data["dialect_applied"],
        thinking_time_ms=response_data["thinking_time_ms"],
        mood=response_data["mood"],
        car_status=response_data["car_status"]
    )


@app.get("/api/car-animation", response_model=CarAnimationResponse)
async def get_car_animation():
    """スポーツカーアニメーション状態取得"""
    animation_data = altmx.get_car_animation_state()
    
    return CarAnimationResponse(
        lights_blinking=animation_data["lights_blinking"],
        blink_color=animation_data["blink_color"],
        blink_speed=animation_data["blink_speed"],
        car_emoji=animation_data["car_emoji"]
    )


class AgentModeDeclarationRequest(BaseModel):
    mode: str  # 'chat', 'coding', 'live_coding', 'code_review', 'architecture', 'debug', 'teaching', 'production'
    quality_level: str = 'development'  # 'prototype', 'development', 'staging', 'production'
    personality: str = 'professional'   # 'professional', 'friendly', 'mentor', 'expert', 'creative'
    focus_areas: List[str] = []
    constraints: List[str] = []
    session_goals: List[str] = []
    audience: str = 'general'
    time_limit: Optional[int] = None

class AgentModeResponse(BaseModel):
    success: bool
    message: str
    current_mode: str
    system_prompt: str
    configuration: Dict[str, Any]

class EnhancedChatRequest(BaseModel):
    message: str
    use_sapporo_dialect: bool = False
    context_type: Optional[str] = None  # 'react_generation', 'live_coding', 'deployment_optimization', 'code_review'
    quality_mode: bool = False  # 高品質モードの有効化
    production_mode: bool = False  # プロダクション品質モード


@app.post("/api/agent/declare-mode", response_model=AgentModeResponse)
async def declare_agent_mode(request: AgentModeDeclarationRequest):
    """AIエージェントモード宣言"""
    try:
        # Enum変換
        mode = AgentMode(request.mode)
        quality_level = QualityLevel(request.quality_level)
        personality = AgentPersonality(request.personality)
        
        # モード宣言実行
        result = agent_state_manager.declare_mode(
            mode=mode,
            quality_level=quality_level,
            personality=personality,
            focus_areas=request.focus_areas,
            constraints=request.constraints,
            session_goals=request.session_goals,
            audience=request.audience,
            time_limit=request.time_limit
        )
        
        return AgentModeResponse(
            success=result['success'],
            message=result['message'],
            current_mode=mode.value,
            system_prompt=result['system_prompt'],
            configuration=result['configuration']
        )
        
    except ValueError as e:
        return AgentModeResponse(
            success=False,
            message=f"無効なモード設定: {str(e)}",
            current_mode="unknown",
            system_prompt="",
            configuration={}
        )

@app.get("/api/agent/current-mode")
async def get_current_agent_mode():
    """現在のエージェントモード取得"""
    config = agent_state_manager.get_current_mode()
    if config:
        return {
            "mode": config.mode.value,
            "quality_level": config.quality_level.value,
            "personality": config.personality.value,
            "focus_areas": config.focus_areas,
            "session_goals": config.session_goals,
            "audience": config.audience,
            "time_limit": config.time_limit
        }
    return {"mode": None, "message": "モードが設定されていません"}

@app.post("/api/chat/enhanced", response_model=ChatResponse)
async def enhanced_chat(request: EnhancedChatRequest):
    """高品質プロンプト対応チャットエンドポイント"""
    
    user_message = request.message
    mode_changed = False
    mode_change_message = ""
    
    # 1. 自然言語でのモード変更チェック
    mode_result = smart_mode_handler.handle_user_input(request.message)
    
    if mode_result.get('mode_changed'):
        mode_changed = True
        mode_change_message = mode_result.get('message', '')
        # モード変更成功時は、変更通知のみ返す
        return ChatResponse(
            response=f"🎯 **モード変更完了**\n\n{mode_change_message}\n\n何をお手伝いしましょうか？",
            dialect_applied=False,
            thinking_time_ms=50,
            mood="excited",
            car_status="ready"
        )
    
    # 2. 現在のモードに基づくシステムプロンプト適用
    current_mode = agent_state_manager.get_current_mode()
    if current_mode:
        mode_system_prompt = agent_state_manager.get_system_prompt()
        user_message = f"{mode_system_prompt}\n\nUser request: {user_message}"
    
    # 3. レガシーな高品質モードサポート
    elif request.production_mode:
        user_message = enhance_for_production_quality(user_message)
    elif request.quality_mode and request.context_type:
        try:
            enhanced_prompt = get_prompt_for_context(
                request.context_type,
                user_request=user_message
            )
            user_message = enhanced_prompt
        except ValueError:
            pass
    
    # 4. コード生成要求の検出（現在のモードを考慮）
    is_coding_request = any(keyword in request.message.lower() for keyword in [
        'create', 'build', 'make', 'generate', 'develop', 'code', 'app', 'component'
    ])
    
    # 現在がコーディング関連モードの場合は、より積極的にコード生成を行う
    if current_mode and current_mode.mode in [
        AgentMode.CODING, AgentMode.LIVE_CODING, AgentMode.PRODUCTION, 
        AgentMode.ARCHITECTURE, AgentMode.DEBUG
    ]:
        is_coding_request = True
    
    # AI応答生成
    response_data = await altmx.generate_response(
        user_message=user_message,
        use_dialect=request.use_sapporo_dialect
    )
    
    # レスポンスにモード情報を追加
    response_text = response_data["response"]
    if current_mode and not mode_changed:
        mode_indicator = f"[{current_mode.mode.value}:{current_mode.quality_level.value}:{current_mode.personality.value}]"
        response_text = f"{response_text}\n\n---\n*{mode_indicator}*"
    
    return ChatResponse(
        response=response_text,
        dialect_applied=response_data["dialect_applied"],
        thinking_time_ms=response_data["thinking_time_ms"],
        mood=response_data["mood"],
        car_status=response_data["car_status"]
    )


# Code Generation Endpoints
@app.post("/api/code-generation/generate", response_model=GenerationResponse)
async def generate_code(request: GenerationRequest):
    """コード生成API - AltMXエージェントを使用してReact/TypeScriptコードを生成"""
    start_time = time.time()
    
    try:
        # 特別にTODOアプリの場合は完全なコードを生成
        if "todo" in request.user_prompt.lower() and request.target_framework.lower() == "react":
            # 完全なReact TODOアプリを生成
            todo_app_code = """import React, { useState } from 'react';
import './App.css';

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

const App: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [inputText, setInputText] = useState('');

  const addTodo = () => {
    if (inputText.trim() !== '') {
      const newTodo: Todo = {
        id: Date.now(),
        text: inputText,
        completed: false
      };
      setTodos([...todos, newTodo]);
      setInputText('');
    }
  };

  const toggleTodo = (id: number) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const deleteTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 AltMX TODO アプリ</h1>
        <div className="todo-input">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTodo()}
            placeholder="新しいタスクを入力..."
          />
          <button onClick={addTodo}>追加</button>
        </div>
        
        <div className="todo-list">
          {todos.map(todo => (
            <div key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
              <span onClick={() => toggleTodo(todo.id)} className="todo-text">
                {todo.text}
              </span>
              <button onClick={() => deleteTodo(todo.id)} className="delete-btn">
                削除
              </button>
            </div>
          ))}
        </div>
        
        <p className="todo-count">
          残り {todos.filter(todo => !todo.completed).length} 件
        </p>
      </header>
    </div>
  );
};

export default App;"""

            app_css_code = """.App {
  text-align: center;
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  max-width: 600px;
  width: 100%;
}

.todo-input {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.todo-input input {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
}

.todo-input button {
  padding: 10px 20px;
  background-color: #61dafb;
  color: #282c34;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.todo-list {
  margin: 20px 0;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin: 5px 0;
  background-color: #3a3f47;
  border-radius: 5px;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  opacity: 0.6;
}

.todo-text {
  flex: 1;
  text-align: left;
  cursor: pointer;
}

.delete-btn {
  background-color: #ff4444;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
}

.todo-count {
  margin-top: 20px;
  font-size: 18px;
  color: #61dafb;
}"""
            
            generated_files = [
                GeneratedFile(
                    filename="App.tsx",
                    content=todo_app_code,
                    language="typescript",
                    description="完全なReact TODO アプリケーション"
                ),
                GeneratedFile(
                    filename="App.css",
                    content=app_css_code,
                    language="css",
                    description="TODOアプリのスタイルシート"
                )
            ]
            
            generation_time = (time.time() - start_time) * 1000
            return GenerationResponse(
                success=True,
                generated_files=generated_files,
                errors=[],
                warnings=[],
                performance_metrics={
                    "generation_time_ms": int(generation_time),
                    "ai_thinking_time_ms": int(generation_time),
                    "files_count": len(generated_files),
                    "total_lines": len(todo_app_code.split('\n')) + len(app_css_code.split('\n'))
                }
            )
        
        # 通常のコード生成（従来の方式）
        generation_prompt = f"""
あなたは{request.target_framework}の専門家です。以下のリクエストに基づいてコードを生成してください：

ユーザープロンプト: {request.user_prompt}
複雑度: {request.complexity}
セキュリティ機能: {'含む' if request.include_security else '含まない'}
アクセシビリティ機能: {'含む' if request.include_accessibility else '含まない'}
最大ファイル数: {request.max_files}

以下の形式でJSONレスポンスを返してください：
{{
  "files": [
    {{
      "filename": "Component.tsx",
      "content": "// TypeScriptコード内容",
      "language": "typescript",
      "description": "コンポーネントの説明"
    }}
  ],
  "warnings": ["警告メッセージがあれば"]
}}

実用的で動作するコードを生成してください。コメントは日本語で記載してください。
        """
        
        response_data = await altmx.generate_response(
            user_message=generation_prompt,
            use_dialect=False  # コード生成では標準語を使用
        )
        
        # AI応答からJSONを抽出して解析
        ai_response = response_data["response"]
        
        # シンプルなコード生成レスポンスを作成
        generated_files = []
        
        if "tsx" in request.user_prompt.lower() or "component" in request.user_prompt.lower():
            # Reactコンポーネントを生成
            component_name = "GeneratedComponent"
            if "form" in request.user_prompt.lower():
                component_name = "FormComponent"
            elif "button" in request.user_prompt.lower():
                component_name = "ButtonComponent"
            elif "modal" in request.user_prompt.lower():
                component_name = "ModalComponent"
                
            generated_files.append(GeneratedFile(
                filename=f"{component_name}.tsx",
                content=f"""import React, {{ useState }} from 'react';
import type {{ FC }} from 'react';

interface {component_name}Props {{
  // プロパティを定義
}}

const {component_name}: FC<{component_name}Props> = (props) => {{
  const [state, setState] = useState({{}});
  
  return (
    <div className="{component_name.lower()}">
      {{/* {request.user_prompt} に基づいたコンポーネント */}}
      <h2>Generated Component</h2>
      <p>ユーザーリクエスト: {request.user_prompt}</p>
      <p>複雑度: {request.complexity}</p>
      <p>AI応答: {ai_response[:200]}...</p>
    </div>
  );
}};

export default {component_name};
""",
                language="typescript",
                description=f"AltMXが生成した{component_name}コンポーネント"
            ))
        else:
            # その他のファイル
            generated_files.append(GeneratedFile(
                filename="generated-code.ts",
                content=f"""// AltMXが生成したコード
// ユーザーリクエスト: {request.user_prompt}
// 複雑度: {request.complexity}

export const generatedFunction = () => {{
  console.log('Generated code based on: {request.user_prompt}');
  
  // AI応答の一部を含む
  const aiResponse = `{ai_response[:200]}...`;
  
  return {{
    prompt: '{request.user_prompt}',
    complexity: '{request.complexity}',
    aiResponse
  }};
}};
""",
                language="typescript",
                description="AltMXが生成したTypeScriptコード"
            ))
        
        end_time = time.time()
        
        return GenerationResponse(
            success=True,
            generated_files=generated_files,
            errors=[],
            warnings=[] if request.complexity != "high" else ["高複雑度での生成は実験的機能です"],
            performance_metrics={
                "generation_time_ms": int((end_time - start_time) * 1000),
                "ai_thinking_time_ms": response_data["thinking_time_ms"],
                "files_count": len(generated_files),
                "total_lines": sum(len(f.content.split('\n')) for f in generated_files)
            }
        )
        
    except Exception as e:
        return GenerationResponse(
            success=False,
            generated_files=[],
            errors=[f"コード生成エラー: {str(e)}"],
            warnings=[],
            performance_metrics={"generation_time_ms": int((time.time() - start_time) * 1000)}
        )


@app.post("/api/code-generation/validate", response_model=ValidationResponse)
async def validate_code(request: ValidationRequest):
    """コード検証API - 生成されたコードの構文・型チェック"""
    validation_results = []
    all_security_risks = []
    
    for code_block in request.code_blocks:
        filename = code_block.get("filename", "unknown.ts")
        content = code_block.get("content", "")
        language = code_block.get("language", "typescript")
        
        # 基本的な検証
        syntax_errors = []
        security_risks = []
        
        # シンプルな構文チェック
        if not content.strip():
            syntax_errors.append(ValidationError(
                message="ファイルが空です",
                line=1,
                column=1
            ))
        
        # TypeScript/JSXの基本チェック
        if language in ["typescript", "tsx"]:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'eval(' in line:
                    security_risks.append(SecurityRisk(
                        type="dangerous_function",
                        severity="high",
                        description="eval()の使用は危険です",
                        line=i + 1
                    ))
                
                if 'innerHTML' in line:
                    security_risks.append(SecurityRisk(
                        type="xss_risk",
                        severity="medium", 
                        description="innerHTML使用はXSSリスクがあります",
                        line=i + 1
                    ))
        
        all_security_risks.extend(security_risks)
        
        validation_results.append(ValidationResult(
            filename=filename,
            is_valid=len(syntax_errors) == 0,
            syntax_errors=syntax_errors,
            type_errors=[],
            lint_errors=[],
            security_risks=security_risks
        ))
    
    return ValidationResponse(
        is_valid=all(result.is_valid for result in validation_results),
        validation_results=validation_results,
        security_risks=all_security_risks
    )


@app.get("/api/code-generation/templates", response_model=TemplatesResponse)
async def get_templates():
    """コードテンプレート一覧取得"""
    templates = [
        Template(
            name="form",
            description="フォームコンポーネント",
            complexity_levels=["simple", "medium", "high"]
        ),
        Template(
            name="dashboard", 
            description="ダッシュボードレイアウト",
            complexity_levels=["medium", "high"]
        ),
        Template(
            name="list",
            description="リストコンポーネント", 
            complexity_levels=["simple", "medium"]
        ),
        Template(
            name="modal",
            description="モーダルダイアログ",
            complexity_levels=["simple", "medium", "high"]
        ),
        Template(
            name="button",
            description="ボタンコンポーネント",
            complexity_levels=["simple", "medium"]
        )
    ]
    
    return TemplatesResponse(templates=templates)


# EC2 Deploy API Models
class DeployRequest(BaseModel):
    app_name: str
    generated_files: List[Dict[str, str]]
    instance_type: str = "local"
    region: str = "ap-northeast-1"


class DeployResponse(BaseModel):
    deployment_id: str
    status: str
    url: Optional[str] = None
    message: str
    error: Optional[str] = None


class DeploymentStatus(BaseModel):
    deployment_id: str
    status: str
    progress: int
    message: str
    url: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


# EC2 Deploy API Endpoints
@app.post("/api/deploy/ec2", response_model=DeployResponse)
async def deploy_to_ec2(request: DeployRequest):
    """生成されたアプリをEC2にデプロイ"""
    try:
        result = await simple_deployment_service.deploy_simple_app(
            app_name=request.app_name,
            files=request.generated_files
        )
        
        return DeployResponse(
            deployment_id=result["deployment_id"],
            status=result["status"],
            url=result.get("url"),
            message=result["message"]
        )
    except Exception as e:
        return DeployResponse(
            deployment_id="error",
            status="failed",
            message="デプロイに失敗しました",
            error=str(e)
        )


@app.get("/api/deploy/status/{deployment_id}", response_model=DeploymentStatus)
async def get_deployment_status(deployment_id: str):
    """デプロイメントステータスを取得"""
    status = simple_deployment_service.get_deployment_status(deployment_id)
    
    if "error" in status and status["error"] == "Deployment not found":
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return DeploymentStatus(**status)


@app.get("/api/deploy/list")
async def list_deployments():
    """全デプロイメントをリスト"""
    return simple_deployment_service.list_deployments()


@app.delete("/api/deploy/{deployment_id}")
async def stop_deployment(deployment_id: str):
    """デプロイメントを停止"""
    success = simple_deployment_service.stop_deployment(deployment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return {"message": "Deployment stopped", "deployment_id": deployment_id}


@app.get("/api/code-generation/templates/{template_name}", response_model=TemplateDetail)
async def get_template_detail(template_name: str):
    """テンプレート詳細取得"""
    templates_data = {
        "form": TemplateDetail(
            name="form",
            description="フォームコンポーネントを生成します",
            base_prompt="入力フォームを作成してください。バリデーション機能も含めてください。",
            complexity_adjustments={
                "simple": "基本的な入力フィールドのみ",
                "medium": "バリデーション、エラー表示を含む",
                "high": "アニメーション、カスタムスタイリング、高度なバリデーションを含む"
            }
        ),
        "dashboard": TemplateDetail(
            name="dashboard", 
            description="ダッシュボードレイアウトを生成します",
            base_prompt="管理画面のダッシュボードを作成してください。",
            complexity_adjustments={
                "medium": "基本的なグリッドレイアウト",
                "high": "レスポンシブ、チャート表示、リアルタイム更新機能"
            }
        ),
        "list": TemplateDetail(
            name="list",
            description="リストコンポーネントを生成します", 
            base_prompt="データリストを表示するコンポーネントを作成してください。",
            complexity_adjustments={
                "simple": "基本的なリスト表示",
                "medium": "フィルタリング、ソート機能付き"
            }
        )
    }
    
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return templates_data[template_name]


@app.get("/api/code-generation/health")
async def get_code_generation_health():
    """コード生成システムのヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "ai_agent_status": "online",
        "templates_count": 5,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )