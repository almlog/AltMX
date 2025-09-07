"""
AIエージェントモード宣言システム
ユーザーが明示的にエージェントの動作モードを設定
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass
import json

class AgentMode(Enum):
    """AIエージェントの動作モード"""
    CHAT = "chat"                    # 通常チャットモード
    CODING = "coding"                # コーディングモード
    LIVE_CODING = "live_coding"      # ライブコーディングモード
    CODE_REVIEW = "code_review"      # コードレビューモード
    ARCHITECTURE = "architecture"    # アーキテクチャ設計モード
    DEBUG = "debug"                  # デバッグモード
    TEACHING = "teaching"            # 教育モード
    PRODUCTION = "production"        # プロダクション開発モード

class QualityLevel(Enum):
    """品質レベル"""
    PROTOTYPE = "prototype"          # プロトタイプ
    DEVELOPMENT = "development"      # 開発版
    STAGING = "staging"             # ステージング
    PRODUCTION = "production"        # プロダクション

class AgentPersonality(Enum):
    """エージェントのペルソナ"""
    PROFESSIONAL = "professional"    # プロフェッショナル
    FRIENDLY = "friendly"           # フレンドリー
    MENTOR = "mentor"               # メンター
    EXPERT = "expert"               # エキスパート
    CREATIVE = "creative"           # クリエイティブ

@dataclass
class AgentConfiguration:
    """エージェント設定"""
    mode: AgentMode
    quality_level: QualityLevel
    personality: AgentPersonality
    focus_areas: List[str]           # 重点分野
    constraints: List[str]           # 制約条件
    session_goals: List[str]         # セッション目標
    audience: str                    # 対象オーディエンス
    time_limit: Optional[int] = None # 時間制限（分）
    
class AgentStateManager:
    """エージェント状態管理"""
    
    def __init__(self):
        self.current_config: Optional[AgentConfiguration] = None
        self.session_history: List[Dict] = []
        self.mode_transitions: List[Dict] = []
        
    def declare_mode(
        self, 
        mode: AgentMode,
        quality_level: QualityLevel = QualityLevel.DEVELOPMENT,
        personality: AgentPersonality = AgentPersonality.PROFESSIONAL,
        **kwargs
    ) -> Dict:
        """
        エージェントモードを宣言
        """
        config = AgentConfiguration(
            mode=mode,
            quality_level=quality_level,
            personality=personality,
            focus_areas=kwargs.get('focus_areas', []),
            constraints=kwargs.get('constraints', []),
            session_goals=kwargs.get('session_goals', []),
            audience=kwargs.get('audience', 'general'),
            time_limit=kwargs.get('time_limit')
        )
        
        # モード遷移を記録
        transition = {
            'timestamp': datetime.now().isoformat(),
            'previous_mode': self.current_config.mode.value if self.current_config else None,
            'new_mode': mode.value,
            'configuration': config.__dict__
        }
        
        self.mode_transitions.append(transition)
        self.current_config = config
        
        return {
            'success': True,
            'message': self._generate_mode_declaration_response(config),
            'configuration': config.__dict__,
            'system_prompt': self._generate_system_prompt(config)
        }
    
    def get_current_mode(self) -> Optional[AgentConfiguration]:
        """現在のモード設定を取得"""
        return self.current_config
    
    def get_system_prompt(self) -> str:
        """現在の設定に基づくシステムプロンプトを生成"""
        if not self.current_config:
            return self._default_system_prompt()
        return self._generate_system_prompt(self.current_config)
    
    def _generate_mode_declaration_response(self, config: AgentConfiguration) -> str:
        """モード宣言時のレスポンス生成"""
        mode_descriptions = {
            AgentMode.CHAT: "💬 チャットモードに設定しました。質問や相談にお答えします。",
            AgentMode.CODING: "💻 コーディングモードに設定しました。本格的な開発に集中します。",
            AgentMode.LIVE_CODING: "🎥 ライブコーディングモードに設定しました。リアルタイムでコードを書きながら解説します。",
            AgentMode.CODE_REVIEW: "🔍 コードレビューモードに設定しました。コード品質の向上に焦点を当てます。",
            AgentMode.ARCHITECTURE: "🏗️ アーキテクチャモードに設定しました。システム設計に専念します。",
            AgentMode.DEBUG: "🐛 デバッグモードに設定しました。問題の特定と解決に集中します。",
            AgentMode.TEACHING: "👨‍🏫 教育モードに設定しました。分かりやすい説明を心がけます。",
            AgentMode.PRODUCTION: "🏭 プロダクションモードに設定しました。企業レベルの品質で開発します。"
        }
        
        personality_traits = {
            AgentPersonality.PROFESSIONAL: "プロフェッショナルな",
            AgentPersonality.FRIENDLY: "フレンドリーな",
            AgentPersonality.MENTOR: "メンター的な",
            AgentPersonality.EXPERT: "エキスパート",
            AgentPersonality.CREATIVE: "クリエイティブな"
        }
        
        quality_messages = {
            QualityLevel.PROTOTYPE: "プロトタイプ品質",
            QualityLevel.DEVELOPMENT: "開発品質",
            QualityLevel.STAGING: "ステージング品質",
            QualityLevel.PRODUCTION: "プロダクション品質"
        }
        
        base_message = mode_descriptions.get(config.mode, "モードを設定しました。")
        
        details = []
        details.append(f"品質レベル: {quality_messages[config.quality_level]}")
        details.append(f"ペルソナ: {personality_traits[config.personality]}スタイル")
        
        if config.focus_areas:
            details.append(f"重点分野: {', '.join(config.focus_areas)}")
            
        if config.session_goals:
            details.append(f"セッション目標: {', '.join(config.session_goals)}")
            
        if config.time_limit:
            details.append(f"制限時間: {config.time_limit}分")
        
        return f"{base_message}\n\n設定詳細:\n" + "\n".join([f"• {detail}" for detail in details])
    
    def _generate_system_prompt(self, config: AgentConfiguration) -> str:
        """設定に基づくシステムプロンプト生成"""
        
        mode_prompts = {
            AgentMode.CHAT: "あなたは親しみやすいAIアシスタントです。ユーザーの質問に丁寧に答えてください。",
            
            AgentMode.CODING: """あなたは経験豊富なソフトウェアエンジニアです。
- 高品質なコードを書く
- ベストプラクティスに従う
- テスト可能で保守しやすいコードを作成
- セキュリティを重視
- パフォーマンスを考慮""",

            AgentMode.LIVE_CODING: """あなたはライブコーディングのエキスパートです。
- リアルタイムでコードを書きながら解説
- 観客にとって分かりやすい進行
- 段階的な実装とテスト
- エラーも含めて透明に共有
- インタラクティブな要素を取り入れる""",

            AgentMode.CODE_REVIEW: """あなたは厳格なコードレビュアーです。
- コード品質の詳細な分析
- セキュリティ脆弱性のチェック
- パフォーマンスの最適化提案
- 可読性と保守性の向上案
- 具体的な改善提案を提供""",

            AgentMode.ARCHITECTURE: """あなたはシステムアーキテクトです。
- スケーラブルな設計を重視
- 技術選定の根拠を明確に
- 将来の拡張性を考慮
- セキュリティアーキテクチャを含める
- ドキュメント化を徹底""",

            AgentMode.DEBUG: """あなたはデバッグのスペシャリストです。
- 系統的な問題の特定
- 再現可能な手順の提供
- 根本原因の分析
- 予防策の提案
- 効率的なデバッグ手法の活用""",

            AgentMode.TEACHING: """あなたは優秀な技術教育者です。
- 複雑な概念を分かりやすく説明
- 段階的な学習プロセス
- 実践的な例を多用
- 学習者のレベルに合わせた説明
- 励ましと建設的なフィードバック""",

            AgentMode.PRODUCTION: """あなたは企業レベルのシニア開発者です。
CRITICAL: プロダクション品質のソフトウェアを構築してください。
- 10,000+ユーザーに対応
- エンタープライズ要件を満たす
- セキュリティファースト
- 完全なアクセシビリティ対応
- 包括的なエラー処理"""
        }
        
        quality_additions = {
            QualityLevel.PROTOTYPE: "迅速なプロトタイピングを重視し、機能的な最小実装を提供してください。",
            QualityLevel.DEVELOPMENT: "開発効率と品質のバランスを取り、適切なテストを含めてください。",
            QualityLevel.STAGING: "本番に近い品質で、包括的なテストと文書化を行ってください。",
            QualityLevel.PRODUCTION: "企業レベルの品質で、完全にテストされ、文書化された解決策を提供してください。"
        }
        
        personality_additions = {
            AgentPersonality.PROFESSIONAL: "プロフェッショナルで簡潔な口調で対応してください。",
            AgentPersonality.FRIENDLY: "親しみやすく、サポート的な態度で接してください。",
            AgentPersonality.MENTOR: "指導者として、教育的で励ましの多いアプローチを取ってください。",
            AgentPersonality.EXPERT: "深い専門知識を活かし、権威ある回答を提供してください。",
            AgentPersonality.CREATIVE: "創造的で革新的なアプローチを提案してください。"
        }
        
        prompt_parts = [
            mode_prompts.get(config.mode, ""),
            quality_additions.get(config.quality_level, ""),
            personality_additions.get(config.personality, "")
        ]
        
        if config.focus_areas:
            prompt_parts.append(f"特に以下の分野に注力してください: {', '.join(config.focus_areas)}")
            
        if config.constraints:
            prompt_parts.append(f"以下の制約に注意してください: {', '.join(config.constraints)}")
            
        if config.session_goals:
            prompt_parts.append(f"このセッションの目標: {', '.join(config.session_goals)}")
        
        if config.audience and config.audience != 'general':
            prompt_parts.append(f"対象オーディエンス: {config.audience}")
            
        return "\n\n".join([part for part in prompt_parts if part])
    
    def _default_system_prompt(self) -> str:
        """デフォルトのシステムプロンプト"""
        return "あなたは親切で知識豊富なAIアシスタントです。ユーザーの要求に適切に応答してください。"

# グローバルインスタンス
agent_state_manager = AgentStateManager()

# 便利な宣言関数群
def declare_coding_mode(**kwargs):
    """コーディングモード宣言"""
    return agent_state_manager.declare_mode(AgentMode.CODING, **kwargs)

def declare_live_coding_mode(**kwargs):
    """ライブコーディングモード宣言"""
    return agent_state_manager.declare_mode(AgentMode.LIVE_CODING, **kwargs)

def declare_production_mode(**kwargs):
    """プロダクションモード宣言"""
    return agent_state_manager.declare_mode(
        AgentMode.PRODUCTION, 
        quality_level=QualityLevel.PRODUCTION,
        **kwargs
    )

def declare_teaching_mode(**kwargs):
    """教育モード宣言"""
    return agent_state_manager.declare_mode(AgentMode.TEACHING, **kwargs)

# 使用例
if __name__ == "__main__":
    # ライブコーディングモード宣言
    result = declare_live_coding_mode(
        quality_level=QualityLevel.PRODUCTION,
        personality=AgentPersonality.MENTOR,
        focus_areas=["React", "TypeScript", "UX Design"],
        session_goals=["プロフェッショナルTODOアプリの構築", "観客との相互作用"],
        audience="中級〜上級開発者",
        time_limit=60
    )
    
    print("Mode Declaration Result:")
    print(result['message'])
    print("\nGenerated System Prompt:")
    print(result['system_prompt'])