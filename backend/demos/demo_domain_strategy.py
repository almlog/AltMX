"""
ライブデモ用のドメイン戦略 - DNS伝搬問題の解決案
"""
from typing import Dict, List, Optional
import hashlib
import time

class LiveDemoDomainStrategy:
    """ライブデモ用のドメイン戦略クラス"""
    
    def __init__(self, base_domain: str = "demo.altmx.com"):
        self.base_domain = base_domain
        self.pre_warmed_subdomains = []
        
    def get_demo_urls(self, app_config: Dict) -> Dict[str, str]:
        """ライブデモ用のURL戦略を返す（シンプル版）"""
        
        # ALB URL のみ（ライブデモ用）
        alb_url = f"https://altmx-{app_config['app_name']}-alb-{self._generate_alb_suffix()}.ap-northeast-1.elb.amazonaws.com"
        
        return {
            "immediate": alb_url,  # 5-8分でCloudFormation完了後に利用可能
        }
    
    def _generate_alb_suffix(self) -> str:
        """ALB名のサフィックス生成"""
        return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
        
    def _generate_demo_id(self) -> str:
        """デモ用ID生成"""
        timestamp = int(time.time())
        return f"demo{timestamp % 10000}"  # demo1234 形式

class PreWarmingStrategy:
    """DNS事前準備戦略"""
    
    def __init__(self):
        self.prepared_domains = [
            "demo1.altmx.com",
            "demo2.altmx.com", 
            "demo3.altmx.com",
            "live1.altmx.com",
            "live2.altmx.com",
            "session1.altmx.com",
            "session2.altmx.com"
        ]
    
    def get_next_available_domain(self) -> str:
        """次に利用可能な事前準備済みドメインを取得"""
        # 実装: データベースやRedisで使用中ドメインをチェック
        for domain in self.prepared_domains:
            if not self._is_domain_in_use(domain):
                return domain
        
        # フォールバック: タイムスタンプベース
        return f"demo{int(time.time()) % 1000}.altmx.com"
    
    def _is_domain_in_use(self, domain: str) -> bool:
        """ドメインが使用中かチェック（モック実装）"""
        # 実際の実装では Redis/Database でチェック
        return False

# ライブデモでの使用例
def demo_scenario():
    """実際のライブデモシナリオ"""
    strategy = LiveDemoDomainStrategy()
    prewarming = PreWarmingStrategy()
    
    app_config = {
        "app_name": "ai-dashboard",
        "session_id": "12345"
    }
    
    urls = strategy.get_demo_urls(app_config)
    
    print("=== ライブデモURL戦略（シンプル版）===")
    print(f"🚀 ALB URL (即座に利用): {urls['immediate']}")
    
    print("\n=== デモフロー（60分会議想定）===")
    print("1. CloudFormation開始 → '生成中...' 表示")
    print("2. ALB作成完了(5-8分) → ALB URLでデプロイ完了")
    print("3. 参加者と一緒にアプリ動作確認")
    print("※ DNS設定は不要（ライブデモには複雑すぎる）")

if __name__ == "__main__":
    demo_scenario()