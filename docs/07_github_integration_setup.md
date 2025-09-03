# GitHub統合機能 設定ガイド (Task 4.5)

## 概要
AltMXのGitHub統合機能により、AIが生成したコードを自動的にGitHubリポジトリにプッシュし、共有可能なURLを提供します。

## 主要機能
- 🚀 **自動リポジトリ作成**: 生成プロジェクト用の新規リポジトリを自動作成
- 📝 **コードプッシュ**: 生成されたファイルを自動コミット・プッシュ
- 🔗 **URL共有**: GitHub上のプロジェクトURLを即座に提供
- 🧹 **自動クリーンアップ**: 30日後に一時リポジトリを自動削除
- 🔐 **セキュリティ**: APIキーなど機密情報の自動除去

## セットアップ手順

### 1. GitHub Personal Access Token の取得

1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token" をクリック
4. 以下の権限を選択：
   - ✅ `repo` - Full control of private repositories
   - ✅ `delete_repo` - Delete repositories (オプション：自動削除用)
5. トークンをコピー（`ghp_` で始まる文字列）

### 2. 環境変数の設定

#### backend/.env ファイルを作成または編集：

```bash
# GitHub Integration Settings
GITHUB_TOKEN=ghp_あなたの実際のトークン
GITHUB_ORGANIZATION=あなたのGitHubユーザー名
GITHUB_BASE_TEMPLATE=altmx-template  # オプション
GITHUB_CLEANUP_DAYS=30  # オプション：デフォルト30日
```

#### 設定例：

| 項目 | 例 | 説明 |
|------|-----|------|
| GITHUB_TOKEN | `ghp_abc123def456...` | Personal Access Token |
| GITHUB_ORGANIZATION | `syunpei` | あなたのGitHubユーザー名 |
| 結果のURL | `https://github.com/syunpei/altmx-xxx` | 生成されるリポジトリ |

### 3. 動作確認テスト

#### モックテスト（設定不要）
```bash
cd backend
python -m pytest test_github_integration_clean.py -v
```

#### 実環境E2Eテスト（要GitHub認証）
```bash
cd backend
python test_github_integration_e2e.py
```

## API使用方法

### Python での使用例

```python
from github_service import GitHubService
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# サービス初期化
config = {
    "token": os.getenv("GITHUB_TOKEN"),
    "organization": os.getenv("GITHUB_ORGANIZATION"),
    "cleanup_days": 30
}

service = GitHubService(config)

# コード生成データ
code_data = {
    "project_name": "my-ai-dashboard",
    "description": "AI生成ダッシュボード",
    "files": [
        {
            "path": "src/App.tsx",
            "content": "// React コンポーネント"
        },
        {
            "path": "package.json",
            "content": '{"name": "my-app"}'
        }
    ],
    "metadata": {
        "session_id": "session_123",
        "ai_model": "claude-3"
    }
}

# デプロイ実行
result = await service.deploy_generated_code(code_data)
print(f"デプロイ完了: {result.repository_url}")
```

## セキュリティ機能

### 危険パターンの自動除去
以下のパターンは自動的に `[REDACTED-SENSITIVE-DATA]` に置換されます：

- OpenAI APIキー (`sk-...`)
- GitHub トークン (`ghp_...`)
- GitLab トークン (`glpat-...`)
- Slack トークン (`xox...`)

### リポジトリ名のサニタイゼーション
- 特殊文字を自動的にハイフンに変換
- GitHub規約に準拠した名前に自動調整
- 重複時は自動的にユニークな名前を生成

## トラブルシューティング

### よくあるエラーと対処法

| エラー | 原因 | 対処法 |
|--------|------|---------|
| `401 Unauthorized` | トークンが無効 | トークンを再生成し、.envを更新 |
| `403 Forbidden` | 権限不足 | トークンに`repo`権限があるか確認 |
| `404 Not Found` | 組織名が間違い | GITHUB_ORGANIZATIONを確認 |
| `422 Validation Failed` | リポジトリ名重複 | 自動的に別名で再試行されます |

### デバッグ方法

1. **認証テスト**：
```python
is_valid = await service.validate_authentication()
print(f"認証状態: {is_valid}")
```

2. **ログ確認**：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## ファイル構成

```
backend/
├── github_service.py              # メイン実装
├── test_github_integration_clean.py  # モックテスト
├── test_github_integration_e2e.py    # 実環境テスト
└── .env.example                   # 設定テンプレート
```

## 制限事項

- **レート制限**: GitHub APIは1時間あたり5000リクエストまで
- **リポジトリサイズ**: 1GBまで推奨
- **ファイル数**: 1プッシュあたり100ファイルまで推奨
- **ファイルサイズ**: 単一ファイル100MBまで

## 次期開発予定

- [ ] GitHub Actions ワークフロー自動生成
- [ ] Pull Request 自動作成機能
- [ ] ブランチ戦略サポート
- [ ] Organization のチーム権限管理
- [ ] GitHub Pages 自動デプロイ
- [ ] Dependabot 設定自動化

## 関連ドキュメント

- [Task 4.6: AWS CloudFormation Template Generation](./08_aws_cloudformation_setup.md)
- [Task 4.7: AWS Real-time Deployment](./09_aws_deployment_setup.md)
- [全体タスクリスト](../tasks.md)

## サポート

問題が発生した場合は、以下を確認してください：

1. `.env` ファイルの設定が正しいか
2. GitHub トークンが有効期限内か
3. 必要な権限が付与されているか
4. ネットワーク接続が正常か

---

*Last Updated: 2025-09-03*
*Status: Implementation Complete, E2E Testing Pending*