"""
自然言語でのモード変更システム
ユーザーが「コーディングモードにして」などの自然な指示でモード変更
"""

import re
from typing import Optional, Dict, Any, List, Tuple
from agent_modes import AgentMode, QualityLevel, AgentPersonality, agent_state_manager

class NaturalModeParser:
    """自然言語のモード変更指示を解析"""
    
    def __init__(self):
        # モード変更を示すパターン
        self.mode_patterns = {
            AgentMode.CODING: [
                r'コーディング.*モード',
                r'開発.*モード', 
                r'プログラミング.*モード',
                r'coding.*mode',
                r'development.*mode'
            ],
            AgentMode.LIVE_CODING: [
                r'ライブ.*コーディング',
                r'配信.*モード',
                r'実況.*コーディング',
                r'live.*coding',
                r'streaming.*mode'
            ],
            AgentMode.PRODUCTION: [
                r'プロダクション.*モード',
                r'本番.*モード',
                r'企業.*レベル',
                r'production.*mode',
                r'enterprise.*mode'
            ],
            AgentMode.TEACHING: [
                r'教育.*モード',
                r'指導.*モード',
                r'レッスン.*モード',
                r'teaching.*mode',
                r'mentor.*mode'
            ],
            AgentMode.CODE_REVIEW: [
                r'レビュー.*モード',
                r'コード.*チェック',
                r'品質.*チェック',
                r'code.*review',
                r'review.*mode'
            ],
            AgentMode.DEBUG: [
                r'デバッグ.*モード',
                r'エラー.*解決',
                r'問題.*解決',
                r'debug.*mode',
                r'troubleshoot.*mode'
            ],
            AgentMode.ARCHITECTURE: [
                r'アーキテクチャ.*モード',
                r'設計.*モード',
                r'システム.*設計',
                r'architecture.*mode',
                r'design.*mode'
            ],
            AgentMode.CHAT: [
                r'チャット.*モード',
                r'会話.*モード',
                r'通常.*モード',
                r'chat.*mode',
                r'normal.*mode'
            ]
        }
        
        # 品質レベルのパターン
        self.quality_patterns = {
            QualityLevel.PROTOTYPE: [
                r'プロトタイプ', r'試作', r'prototype', r'draft'
            ],
            QualityLevel.DEVELOPMENT: [
                r'開発.*品質', r'通常.*品質', r'development', r'standard'
            ],
            QualityLevel.STAGING: [
                r'ステージング', r'テスト.*品質', r'staging', r'testing'
            ],
            QualityLevel.PRODUCTION: [
                r'プロダクション.*品質', r'本番.*品質', r'企業.*品質', 
                r'production.*quality', r'enterprise.*quality'
            ]
        }
        
        # パーソナリティのパターン
        self.personality_patterns = {
            AgentPersonality.MENTOR: [
                r'メンター', r'指導者', r'教師', r'mentor', r'teacher'
            ],
            AgentPersonality.EXPERT: [
                r'エキスパート', r'専門家', r'expert', r'specialist'
            ],
            AgentPersonality.FRIENDLY: [
                r'フレンドリー', r'親しみやすく', r'friendly', r'casual'
            ],
            AgentPersonality.CREATIVE: [
                r'クリエイティブ', r'創造的', r'creative', r'innovative'
            ],
            AgentPersonality.PROFESSIONAL: [
                r'プロフェッショナル', r'専門的', r'professional', r'formal'
            ]
        }
        
        # 簡単なコマンドマッピング（長いパターンを先に配置）
        self.simple_commands = {
            # 日本語（長いパターンを先に）
            'ライブコーディングモードにして': (AgentMode.LIVE_CODING, QualityLevel.PRODUCTION, AgentPersonality.MENTOR),
            'コーディングモードにして': (AgentMode.CODING, QualityLevel.DEVELOPMENT, AgentPersonality.PROFESSIONAL),
            'プロダクションモードにして': (AgentMode.PRODUCTION, QualityLevel.PRODUCTION, AgentPersonality.EXPERT),
            '教育モードにして': (AgentMode.TEACHING, QualityLevel.DEVELOPMENT, AgentPersonality.MENTOR),
            'レビューモードにして': (AgentMode.CODE_REVIEW, QualityLevel.STAGING, AgentPersonality.EXPERT),
            'デバッグモードにして': (AgentMode.DEBUG, QualityLevel.DEVELOPMENT, AgentPersonality.EXPERT),
            'チャットモードにして': (AgentMode.CHAT, QualityLevel.DEVELOPMENT, AgentPersonality.FRIENDLY),
            
            # 英語
            'set to coding mode': (AgentMode.CODING, QualityLevel.DEVELOPMENT, AgentPersonality.PROFESSIONAL),
            'switch to live coding': (AgentMode.LIVE_CODING, QualityLevel.PRODUCTION, AgentPersonality.MENTOR),
            'enable production mode': (AgentMode.PRODUCTION, QualityLevel.PRODUCTION, AgentPersonality.EXPERT),
            'start teaching mode': (AgentMode.TEACHING, QualityLevel.DEVELOPMENT, AgentPersonality.MENTOR),
            
            # 省略形
            'coding': (AgentMode.CODING, QualityLevel.DEVELOPMENT, AgentPersonality.PROFESSIONAL),
            'live': (AgentMode.LIVE_CODING, QualityLevel.PRODUCTION, AgentPersonality.MENTOR),
            'prod': (AgentMode.PRODUCTION, QualityLevel.PRODUCTION, AgentPersonality.EXPERT),
            'review': (AgentMode.CODE_REVIEW, QualityLevel.STAGING, AgentPersonality.EXPERT),
            'debug': (AgentMode.DEBUG, QualityLevel.DEVELOPMENT, AgentPersonality.EXPERT),
            'chat': (AgentMode.CHAT, QualityLevel.DEVELOPMENT, AgentPersonality.FRIENDLY),
        }
    
    def parse_mode_command(self, text: str) -> Optional[Dict[str, Any]]:
        """
        自然言語のテキストからモード変更指示を解析
        
        Args:
            text: ユーザーの入力テキスト
            
        Returns:
            モード設定辞書 or None
        """
        text_lower = text.lower().strip()
        
        # 1. 簡単なコマンドチェック
        for command, (mode, quality, personality) in self.simple_commands.items():
            if command.lower() in text_lower:
                return {
                    'mode': mode,
                    'quality_level': quality,
                    'personality': personality,
                    'match_type': 'simple_command',
                    'matched_text': command
                }
        
        # 2. パターンマッチング
        detected_mode = self._detect_mode(text_lower)
        detected_quality = self._detect_quality(text_lower)
        detected_personality = self._detect_personality(text_lower)
        
        if detected_mode:
            # デフォルト値を設定
            quality = detected_quality or self._get_default_quality(detected_mode)
            personality = detected_personality or self._get_default_personality(detected_mode)
            
            return {
                'mode': detected_mode,
                'quality_level': quality,
                'personality': personality,
                'match_type': 'pattern_match',
                'matched_text': text[:50] + '...' if len(text) > 50 else text
            }
        
        return None
    
    def _detect_mode(self, text: str) -> Optional[AgentMode]:
        """テキストからモードを検出"""
        for mode, patterns in self.mode_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return mode
        return None
    
    def _detect_quality(self, text: str) -> Optional[QualityLevel]:
        """テキストから品質レベルを検出"""
        for quality, patterns in self.quality_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return quality
        return None
    
    def _detect_personality(self, text: str) -> Optional[AgentPersonality]:
        """テキストからパーソナリティを検出"""
        for personality, patterns in self.personality_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return personality
        return None
    
    def _get_default_quality(self, mode: AgentMode) -> QualityLevel:
        """モードに応じたデフォルト品質レベル"""
        defaults = {
            AgentMode.PROTOTYPE: QualityLevel.PROTOTYPE,
            AgentMode.LIVE_CODING: QualityLevel.PRODUCTION,
            AgentMode.PRODUCTION: QualityLevel.PRODUCTION,
            AgentMode.CODE_REVIEW: QualityLevel.STAGING,
        }
        return defaults.get(mode, QualityLevel.DEVELOPMENT)
    
    def _get_default_personality(self, mode: AgentMode) -> AgentPersonality:
        """モードに応じたデフォルトパーソナリティ"""
        defaults = {
            AgentMode.LIVE_CODING: AgentPersonality.MENTOR,
            AgentMode.TEACHING: AgentPersonality.MENTOR,
            AgentMode.PRODUCTION: AgentPersonality.EXPERT,
            AgentMode.CODE_REVIEW: AgentPersonality.EXPERT,
            AgentMode.ARCHITECTURE: AgentPersonality.EXPERT,
            AgentMode.DEBUG: AgentPersonality.EXPERT,
            AgentMode.CHAT: AgentPersonality.FRIENDLY,
        }
        return defaults.get(mode, AgentPersonality.PROFESSIONAL)
    
    def get_suggested_commands(self) -> List[str]:
        """利用可能な簡単コマンド一覧"""
        japanese_commands = [cmd for cmd in self.simple_commands.keys() if 'して' in cmd]
        english_commands = [cmd for cmd in self.simple_commands.keys() if cmd not in japanese_commands and len(cmd) > 10]
        short_commands = [cmd for cmd in self.simple_commands.keys() if len(cmd) <= 10]
        
        return {
            'japanese': japanese_commands,
            'english': english_commands, 
            'short': short_commands
        }

class SmartModeHandler:
    """スマートなモード変更ハンドラー"""
    
    def __init__(self):
        self.parser = NaturalModeParser()
    
    def handle_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザー入力を処理してモード変更を実行
        
        Args:
            user_input: ユーザーの自然言語入力
            
        Returns:
            処理結果辞書
        """
        # モード変更指示を検出
        mode_config = self.parser.parse_mode_command(user_input)
        
        if mode_config:
            # モード変更を実行
            try:
                result = agent_state_manager.declare_mode(
                    mode=mode_config['mode'],
                    quality_level=mode_config['quality_level'],
                    personality=mode_config['personality']
                )
                
                return {
                    'mode_changed': True,
                    'success': result['success'],
                    'message': result['message'],
                    'detected_intent': mode_config,
                    'system_prompt': result['system_prompt']
                }
                
            except Exception as e:
                return {
                    'mode_changed': False,
                    'success': False,
                    'error': str(e),
                    'detected_intent': mode_config
                }
        else:
            # 通常のチャット処理
            return {
                'mode_changed': False,
                'success': True,
                'message': 'モード変更指示が検出されませんでした。通常のチャットとして処理します。',
                'suggestions': self._get_mode_suggestions()
            }
    
    def _get_mode_suggestions(self) -> List[str]:
        """モード変更のヒントを提供"""
        return [
            "💻 「コーディングモードにして」- 本格的な開発支援",
            "🎥 「ライブコーディングモードにして」- 配信向け解説付き開発", 
            "🏭 「プロダクションモードにして」- 企業レベル品質",
            "👨‍🏫 「教育モードにして」- 初心者向け丁寧な指導",
            "🔍 「レビューモードにして」- コード品質チェック",
            "🐛 「デバッグモードにして」- 問題解決に特化"
        ]
    
    def is_mode_change_request(self, text: str) -> bool:
        """テキストがモード変更リクエストかを判定"""
        mode_indicators = [
            'モードにして', 'モードに変更', 'モード切り替え',
            'set to', 'switch to', 'change to', 'enable',
            'モード'  # 単体でも判定
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in mode_indicators)

# グローバルインスタンス
smart_mode_handler = SmartModeHandler()

# 使用例とテスト
if __name__ == "__main__":
    handler = SmartModeHandler()
    
    test_inputs = [
        "コーディングモードにして",
        "ライブコーディングモードでメンターとして教えて",
        "プロダクション品質でエキスパートモードに",
        "coding",
        "set to live coding mode",
        "デバッグモードにして問題解決して",
        "普通にチャットしたい"
    ]
    
    for input_text in test_inputs:
        print(f"\n入力: '{input_text}'")
        result = handler.handle_user_input(input_text)
        print(f"結果: {result.get('message', result)}")