# 04. APIキー設定ガイド

## 概要
AltMXのAI機能を有効化するためのAPIキー取得・設定手順

## 🔑 Gemini API キー（無料枠）

### 1. APIキー取得手順
1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. プロジェクトを選択または新規作成
5. APIキーが生成される（安全にコピー）

### 2. 無料枠の制限
- **1分あたり**: 60リクエスト
- **1日あたり**: 1,500リクエスト
- **入力トークン**: 無制限
- **出力トークン**: 制限あり（モデルによる）

### 3. 推奨モデル
```python
# gemini-1.5-flash: 高速・低コスト
# gemini-1.5-pro: 高品質・やや遅い
model = "gemini-1.5-flash"  # MVPではこれを使用
```

## 🔐 Claude API キー（従量課金・バックアップ用）

### 1. APIキー取得手順
1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウント作成またはログイン
3. API Keys セクションへ
4. 「Create Key」をクリック
5. キー名を入力（例: "AltMX-Demo"）
6. APIキーを安全にコピー

### 2. 料金目安
- **Claude 3 Haiku**: $0.25 / 1M入力トークン
- **Claude 3 Sonnet**: $3 / 1M入力トークン  
- **Claude 3 Opus**: $15 / 1M入力トークン
- **デモ1回の目安**: 100-300円程度

## ⚙️ 環境変数の設定

### 1. .envファイルの作成
```bash
# backend/.env を作成
cd backend
cp .env.example .env
```

### 2. APIキーの設定
```env
# backend/.env
GEMINI_API_KEY=あなたの実際のGeminiキー
CLAUDE_API_KEY=あなたの実際のClaudeキー（オプション）

# プロバイダー設定
PRIMARY_AI_PROVIDER=gemini  # 優先使用
ENABLE_FALLBACK=true         # 障害時の自動切り替え
```

## 🛡️ セキュリティ注意事項

### ❌ やってはいけないこと
- APIキーをコードに直接記述
- GitHubにAPIキーをコミット
- 公開の場でAPIキーを共有
- クライアントサイドでAPIキー使用

### ✅ ベストプラクティス
- 環境変数で管理
- .gitignoreで.envを除外（設定済み）
- 本番環境では環境変数サービス使用
- 定期的なキーローテーション

## 🧪 設定確認

### テストスクリプト
```python
# test_api_config.py
from config import config

# 設定の検証
if config.validate():
    print("✅ API設定が正常です")
    print(f"Primary Provider: {config.PRIMARY_AI_PROVIDER}")
    print(f"Fallback Enabled: {config.ENABLE_FALLBACK}")
else:
    print("❌ API設定にエラーがあります")
```

### 動作確認
```bash
cd backend
python test_api_config.py
```

## 📊 使用量モニタリング

### Gemini使用量確認
- [Google Cloud Console](https://console.cloud.google.com/) でAPI使用量を確認

### Claude使用量確認  
- [Anthropic Console](https://console.anthropic.com/settings/usage) で料金を確認

## トラブルシューティング

### よくある問題
1. **"API key not valid"エラー**
   - APIキーが正しくコピーされているか確認
   - 前後の空白を削除
   
2. **"Rate limit exceeded"エラー**
   - 無料枠の制限に達した
   - Claudeへの自動フォールバックが動作

3. **環境変数が読み込まれない**
   - .envファイルの場所を確認（backend/）
   - python-dotenvがインストール済みか確認