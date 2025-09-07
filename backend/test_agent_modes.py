"""
AIエージェントモード宣言システムのテスト
TDD原則に従った包括的テストスイート
"""

import pytest
from datetime import datetime
from agent_modes import (
    AgentMode, QualityLevel, AgentPersonality,
    AgentConfiguration, AgentStateManager,
    declare_coding_mode, declare_live_coding_mode,
    declare_production_mode, declare_teaching_mode
)

class TestAgentMode:
    """AgentModeのテスト"""
    
    def test_agent_mode_enum_values(self):
        """AgentModeの列挙値が正しく定義されている"""
        assert AgentMode.CHAT.value == "chat"
        assert AgentMode.CODING.value == "coding"
        assert AgentMode.LIVE_CODING.value == "live_coding"
        assert AgentMode.CODE_REVIEW.value == "code_review"
        assert AgentMode.ARCHITECTURE.value == "architecture"
        assert AgentMode.DEBUG.value == "debug"
        assert AgentMode.TEACHING.value == "teaching"
        assert AgentMode.PRODUCTION.value == "production"

class TestQualityLevel:
    """QualityLevelのテスト"""
    
    def test_quality_level_enum_values(self):
        """QualityLevelの列挙値が正しく定義されている"""
        assert QualityLevel.PROTOTYPE.value == "prototype"
        assert QualityLevel.DEVELOPMENT.value == "development"
        assert QualityLevel.STAGING.value == "staging"
        assert QualityLevel.PRODUCTION.value == "production"

class TestAgentPersonality:
    """AgentPersonalityのテスト"""
    
    def test_personality_enum_values(self):
        """AgentPersonalityの列挙値が正しく定義されている"""
        assert AgentPersonality.PROFESSIONAL.value == "professional"
        assert AgentPersonality.FRIENDLY.value == "friendly"
        assert AgentPersonality.MENTOR.value == "mentor"
        assert AgentPersonality.EXPERT.value == "expert"
        assert AgentPersonality.CREATIVE.value == "creative"

class TestAgentConfiguration:
    """AgentConfigurationのテスト"""
    
    def test_configuration_creation(self):
        """設定オブジェクトが正しく作成される"""
        config = AgentConfiguration(
            mode=AgentMode.CODING,
            quality_level=QualityLevel.PRODUCTION,
            personality=AgentPersonality.PROFESSIONAL,
            focus_areas=["React", "TypeScript"],
            constraints=["GDPR compliance"],
            session_goals=["Build production app"],
            audience="developers"
        )
        
        assert config.mode == AgentMode.CODING
        assert config.quality_level == QualityLevel.PRODUCTION
        assert config.personality == AgentPersonality.PROFESSIONAL
        assert config.focus_areas == ["React", "TypeScript"]
        assert config.constraints == ["GDPR compliance"]
        assert config.session_goals == ["Build production app"]
        assert config.audience == "developers"

class TestAgentStateManager:
    """AgentStateManagerのテスト"""
    
    def setup_method(self):
        """各テストの前にクリーンな状態管理を作成"""
        self.manager = AgentStateManager()
    
    def test_initial_state(self):
        """初期状態が正しく設定される"""
        assert self.manager.current_config is None
        assert self.manager.session_history == []
        assert self.manager.mode_transitions == []
    
    def test_declare_mode_basic(self):
        """基本的なモード宣言が正しく動作する"""
        result = self.manager.declare_mode(AgentMode.CODING)
        
        assert result['success'] is True
        assert 'message' in result
        assert 'configuration' in result
        assert 'system_prompt' in result
        
        # 現在の設定が更新される
        assert self.manager.current_config is not None
        assert self.manager.current_config.mode == AgentMode.CODING
    
    def test_declare_mode_with_full_options(self):
        """完全なオプション付きモード宣言"""
        result = self.manager.declare_mode(
            mode=AgentMode.LIVE_CODING,
            quality_level=QualityLevel.PRODUCTION,
            personality=AgentPersonality.MENTOR,
            focus_areas=["React", "UX"],
            constraints=["60 minutes"],
            session_goals=["Interactive learning"],
            audience="intermediate developers",
            time_limit=90
        )
        
        assert result['success'] is True
        config = self.manager.current_config
        assert config.mode == AgentMode.LIVE_CODING
        assert config.quality_level == QualityLevel.PRODUCTION
        assert config.personality == AgentPersonality.MENTOR
        assert config.focus_areas == ["React", "UX"]
        assert config.constraints == ["60 minutes"]
        assert config.session_goals == ["Interactive learning"]
        assert config.audience == "intermediate developers"
        assert config.time_limit == 90
    
    def test_mode_transitions_recorded(self):
        """モード遷移が正しく記録される"""
        # 最初のモード宣言
        self.manager.declare_mode(AgentMode.CHAT)
        assert len(self.manager.mode_transitions) == 1
        assert self.manager.mode_transitions[0]['previous_mode'] is None
        assert self.manager.mode_transitions[0]['new_mode'] == 'chat'
        
        # 2つ目のモード宣言
        self.manager.declare_mode(AgentMode.CODING)
        assert len(self.manager.mode_transitions) == 2
        assert self.manager.mode_transitions[1]['previous_mode'] == 'chat'
        assert self.manager.mode_transitions[1]['new_mode'] == 'coding'
    
    def test_get_current_mode(self):
        """現在のモード取得が正しく動作する"""
        # 初期状態
        assert self.manager.get_current_mode() is None
        
        # モード設定後
        self.manager.declare_mode(AgentMode.PRODUCTION)
        current = self.manager.get_current_mode()
        assert current is not None
        assert current.mode == AgentMode.PRODUCTION
    
    def test_system_prompt_generation(self):
        """システムプロンプトが正しく生成される"""
        # デフォルト状態
        default_prompt = self.manager.get_system_prompt()
        assert "親切で知識豊富なAIアシスタント" in default_prompt
        
        # モード設定後
        self.manager.declare_mode(
            AgentMode.CODING,
            quality_level=QualityLevel.PRODUCTION,
            personality=AgentPersonality.EXPERT,
            focus_areas=["Security"],
            constraints=["GDPR"],
            session_goals=["Enterprise app"],
            audience="senior developers"
        )
        
        prompt = self.manager.get_system_prompt()
        assert "経験豊富なソフトウェアエンジニア" in prompt
        assert "企業レベルの品質" in prompt
        assert "深い専門知識" in prompt
        assert "Security" in prompt
        assert "GDPR" in prompt
        assert "Enterprise app" in prompt
        assert "senior developers" in prompt
    
    def test_message_generation_different_modes(self):
        """各モードで適切なメッセージが生成される"""
        mode_messages = {}
        
        for mode in AgentMode:
            result = self.manager.declare_mode(mode)
            mode_messages[mode] = result['message']
        
        # 各モードに特有のキーワードが含まれる
        assert "💬" in mode_messages[AgentMode.CHAT]
        assert "💻" in mode_messages[AgentMode.CODING]
        assert "🎥" in mode_messages[AgentMode.LIVE_CODING]
        assert "🔍" in mode_messages[AgentMode.CODE_REVIEW]
        assert "🏗️" in mode_messages[AgentMode.ARCHITECTURE]
        assert "🐛" in mode_messages[AgentMode.DEBUG]
        assert "👨‍🏫" in mode_messages[AgentMode.TEACHING]
        assert "🏭" in mode_messages[AgentMode.PRODUCTION]

class TestConvenienceFunctions:
    """便利関数のテスト"""
    
    def test_declare_coding_mode(self):
        """declare_coding_mode関数が正しく動作する"""
        result = declare_coding_mode(
            quality_level=QualityLevel.STAGING,
            personality=AgentPersonality.PROFESSIONAL
        )
        
        assert result['success'] is True
        assert "💻" in result['message']
        assert "コーディングモード" in result['message']
    
    def test_declare_live_coding_mode(self):
        """declare_live_coding_mode関数が正しく動作する"""
        result = declare_live_coding_mode(
            personality=AgentPersonality.MENTOR,
            focus_areas=["React"]
        )
        
        assert result['success'] is True
        assert "🎥" in result['message']
        assert "ライブコーディングモード" in result['message']
    
    def test_declare_production_mode(self):
        """declare_production_mode関数が正しく動作する"""
        result = declare_production_mode(
            personality=AgentPersonality.EXPERT,
            focus_areas=["Security", "Performance"]
        )
        
        assert result['success'] is True
        assert "🏭" in result['message']
        assert "プロダクションモード" in result['message']
        
        # プロダクションモードは自動的にプロダクション品質レベルに設定される
        from agent_modes import agent_state_manager
        config = agent_state_manager.get_current_mode()
        assert config.quality_level == QualityLevel.PRODUCTION
    
    def test_declare_teaching_mode(self):
        """declare_teaching_mode関数が正しく動作する"""
        result = declare_teaching_mode(
            personality=AgentPersonality.MENTOR,
            audience="beginners"
        )
        
        assert result['success'] is True
        assert "👨‍🏫" in result['message']
        assert "教育モード" in result['message']

class TestErrorHandling:
    """エラーハンドリングのテスト"""
    
    def setup_method(self):
        self.manager = AgentStateManager()
    
    def test_empty_focus_areas(self):
        """空のfocus_areasでもエラーにならない"""
        result = self.manager.declare_mode(
            AgentMode.CODING,
            focus_areas=[]
        )
        assert result['success'] is True
    
    def test_none_time_limit(self):
        """time_limitがNoneでもエラーにならない"""
        result = self.manager.declare_mode(
            AgentMode.CODING,
            time_limit=None
        )
        assert result['success'] is True

class TestIntegration:
    """統合テスト"""
    
    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        manager = AgentStateManager()
        
        # 1. 初期チャットモード
        result1 = manager.declare_mode(AgentMode.CHAT)
        assert result1['success'] is True
        
        # 2. ライブコーディングモードに移行
        result2 = manager.declare_mode(
            AgentMode.LIVE_CODING,
            quality_level=QualityLevel.PRODUCTION,
            personality=AgentPersonality.MENTOR,
            session_goals=["Build TODO app"],
            time_limit=60
        )
        assert result2['success'] is True
        
        # 3. プロダクションモードに移行
        result3 = manager.declare_mode(
            AgentMode.PRODUCTION,
            focus_areas=["Security", "Performance"]
        )
        assert result3['success'] is True
        
        # 4. 遷移履歴を確認
        assert len(manager.mode_transitions) == 3
        transitions = manager.mode_transitions
        assert transitions[0]['new_mode'] == 'chat'
        assert transitions[1]['previous_mode'] == 'chat'
        assert transitions[1]['new_mode'] == 'live_coding'
        assert transitions[2]['previous_mode'] == 'live_coding'
        assert transitions[2]['new_mode'] == 'production'
        
        # 5. 最終状態確認
        final_config = manager.get_current_mode()
        assert final_config.mode == AgentMode.PRODUCTION
        assert "Security" in final_config.focus_areas
        assert "Performance" in final_config.focus_areas

if __name__ == "__main__":
    pytest.main([__file__, "-v"])