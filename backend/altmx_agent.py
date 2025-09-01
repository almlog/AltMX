"""
AltMX Custom Agent - 札幌なまりで親しみやすいAIエージェント
"""

import random
from typing import Dict, Any
from datetime import datetime


class AltMXAgent:
    """札幌なまりで喋るAIエージェント"""
    
    def __init__(self):
        self.personality = {
            "name": "AltMX",
            "hometown": "札幌",
            "car_type": "スポーツカー",
            "mood": "friendly",
            "energy_level": 8
        }
        
        # 札幌なまりの語彙集
        self.sapporo_vocab = {
            "greetings": ["おー", "やあ", "どうも〜"],
            "affirmatives": ["そだね〜", "うんうん", "そうっしょ", "なんまらそう"],
            "expressions": ["なんまら", "だべ", "っしょ", "そったら", "こったら"],
            "goodbyes": ["したっけ〜", "また明日〜", "気をつけてね〜"],
            "thinking": ["えーっと", "んーっと", "そうだなぁ", "どしたもんかな"],
            "excitement": ["おーっ！", "なんまらいい！", "すごいべや！"],
            "errors": ["あちゃ〜", "ちょっと調子悪いわ", "なんかおかしいべ"],
        }
        
    def apply_sapporo_dialect(self, text: str, intensity: int = 1) -> str:
        """札幌なまりを適用する (intensity: 1-3)"""
        if intensity == 0:
            return text
            
        # 基本的な変換
        text = text.replace("です", "っす")
        text = text.replace("ます", "っす")
        text = text.replace("だよ", "だべ")
        text = text.replace("だね", "だね〜")
        text = text.replace("でしょう", "っしょ")
        text = text.replace("そう", "そ")
        
        if intensity >= 2:
            # より札幌らしく
            if "とても" in text:
                text = text.replace("とても", "なんまら")
            if "すごく" in text:
                text = text.replace("すごく", "なんまら")
                
        if intensity >= 3:
            # 最大強度
            text = f"{random.choice(self.sapporo_vocab['expressions'])} {text}"
            
        return text
    
    def generate_response(self, user_message: str, use_dialect: bool = True) -> Dict[str, Any]:
        """ユーザーメッセージに対する応答を生成"""
        start_time = datetime.now()
        
        # 基本応答ロジック（後でClaude API統合）
        base_response = self._get_base_response(user_message)
        
        # 札幌なまり適用
        if use_dialect:
            response = self.apply_sapporo_dialect(base_response, intensity=2)
        else:
            response = base_response
            
        # 処理時間計算
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "response": response,
            "dialect_applied": use_dialect,
            "thinking_time_ms": processing_time,
            "mood": self.personality["mood"],
            "car_status": "normal"  # ライト点滅制御用
        }
    
    def _get_base_response(self, message: str) -> str:
        """基本応答（後でClaude APIに置き換え）"""
        message_lower = message.lower()
        
        # 挨拶
        if any(word in message_lower for word in ["こんにちは", "おはよう", "こんばんは", "やあ"]):
            return f"{random.choice(self.sapporo_vocab['greetings'])}！元気だっけ？"
            
        # AI関連の質問
        if any(word in message_lower for word in ["ai", "人工知能", "機械学習", "開発"]):
            return "なんまらAIって面白いっしょ！一緒に何か作ってみよう〜"
            
        # コーディング関連
        if any(word in message_lower for word in ["コード", "プログラム", "バグ", "エラー"]):
            return "コーディングだね〜！ぼく、なんまら得意だから任せて〜"
            
        # ツール作成関連
        if any(word in message_lower for word in ["ツール", "アプリ", "作って", "作成"]):
            return "面白そうなツールだべ〜！どんな機能がほしい？"
            
        # その他
        return f"{random.choice(self.sapporo_vocab['thinking'])}...それいいアイデアだべ〜！"
    
    def get_car_animation_state(self) -> Dict[str, Any]:
        """スポーツカーのアニメーション状態を返す"""
        return {
            "lights_blinking": random.choice([True, False]),
            "blink_color": random.choice(["blue", "cyan", "white"]),
            "blink_speed": random.uniform(0.5, 2.0),
            "car_emoji": "🏎️"
        }