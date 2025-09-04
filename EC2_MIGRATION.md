# EC2開発環境移行ガイド

## 移行の目的
- Windows/Linux環境差異によるパス問題解決
- 開発環境と本番環境の統一
- EC2上でのClaude + Serena MCP活用

## 移行手順

### 1. Windows環境での準備
```bash
# 最新コードをコミット・プッシュ
git add .
git commit -m "Prepare for EC2 development environment migration

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin master
```

### 2. EC2インスタンス情報
- **インスタンスID**: i-0cf4529f22952a53d
- **インスタンスタイプ**: t3.medium (2 vCPU, 4GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **ユーザー**: AltMX-admin
- **SSH接続**: `ssh -i "altmx-dev-key.pem" AltMX-admin@[PUBLIC_IP]`

### 3. EC2上での開発環境セットアップ

#### 3.1 基本ツールインストール
```bash
# システムアップデート
sudo apt update && sudo apt upgrade -y

# 開発ツール
sudo apt install -y git nodejs npm python3 python3-pip curl wget

# Docker（必要に応じて）
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker AltMX-admin
```

#### 3.2 GitHubリポジトリクローン
```bash
# ホームディレクトリに移動
cd ~

# AltMXリポジトリクローン
git clone https://github.com/[YOUR_GITHUB_USERNAME]/AltMX.git
cd AltMX

# 開発ブランチ作成（必要に応じて）
git checkout -b ec2-development
```

#### 3.3 Node.js環境セットアップ
```bash
# Node.jsバージョン確認・アップデート
node --version
npm --version

# パッケージインストール
npm install

# フロントエンド依存関係（存在する場合）
cd frontend && npm install && cd ..
```

#### 3.4 Python環境セットアップ
```bash
# Python仮想環境作成
python3 -m venv venv
source venv/bin/activate

# Python依存関係インストール
pip install -r requirements.txt

# 追加で必要なパッケージ
pip install anthropic fastapi uvicorn
```

### 4. 認証情報・設定ファイル手動設定

#### 4.1 環境変数ファイル作成
```bash
# バックエンド環境変数
cat > backend/.env << 'EOF'
# Claude API
ANTHROPIC_API_KEY=your_claude_api_key_here

# AWS設定（必要に応じて）
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=ap-northeast-1

# データベース（使用する場合）
DATABASE_URL=your_database_url_here

# アプリケーション設定
DEBUG=true
HOST=0.0.0.0
PORT=8000
EOF
```

#### 4.2 フロントエンド設定（存在する場合）
```bash
# フロントエンド環境変数
cat > frontend/.env.local << 'EOF'
# API エンドポイント
NEXT_PUBLIC_API_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000

# その他の設定
NODE_ENV=development
EOF
```

#### 4.3 Claude設定
```bash
# Claude設定ファイル
mkdir -p ~/.claude
cat > ~/.claude/config.json << 'EOF'
{
  "api_key": "your_claude_api_key_here",
  "default_model": "claude-3-5-sonnet-20241022"
}
EOF
```

### 5. アプリケーション起動テスト

#### 5.1 バックエンド起動
```bash
cd ~/AltMX/backend
source ../venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 5.2 フロントエンド起動（別ターミナル）
```bash
cd ~/AltMX/frontend
npm run dev
```

#### 5.3 動作確認
- バックエンドAPI: `curl http://localhost:8000/`
- フロントエンド: ブラウザで確認（ポートフォワーディング設定）

### 6. VS Code Remote-SSH設定

#### 6.1 VS Code拡張機能
- Remote - SSH
- Remote - SSH: Editing Configuration Files

#### 6.2 SSH設定追加
```
# ~/.ssh/config または C:\Users\[USERNAME]\.ssh\config
Host altmx-ec2
    HostName [EC2_PUBLIC_IP]
    User AltMX-admin
    IdentityFile path/to/altmx-dev-key.pem
    ServerAliveInterval 60
```

### 7. 引き継ぎが必要な設定ファイル・認証情報

#### 7.1 手入力が必要なファイル
1. `backend/.env` - Claude API Key, AWS認証情報
2. `frontend/.env.local` - フロントエンド環境変数
3. `~/.claude/config.json` - Claude設定
4. `~/.aws/credentials` - AWS認証情報（CLI使用時）

#### 7.2 認証情報リスト
- **Claude API Key**: Anthropicダッシュボードから取得
- **AWS Access Key/Secret**: AWS IAMから取得
- **GitHub Token**: リポジトリアクセス用（プライベートリポジトリの場合）

### 8. 開発ワークフロー（移行後）

1. **コード編集**: VS Code Remote-SSH
2. **AI支援**: EC2上で`claude`コマンド実行
3. **テスト**: EC2上で直接実行
4. **デプロイ**: EC2 = 本番環境（または別インスタンスへデプロイ）

### 9. トラブルシューティング

#### 9.1 SSH接続問題
```bash
# 権限修正
chmod 400 altmx-dev-key.pem

# 詳細ログ確認
ssh -v -i "altmx-dev-key.pem" AltMX-admin@[PUBLIC_IP]
```

#### 9.2 ポート開放確認
```bash
# セキュリティグループ確認
aws ec2 describe-security-groups --region ap-northeast-1 --group-names altmx-prod-sg
```

#### 9.3 サービス状態確認
```bash
# プロセス確認
ps aux | grep python
ps aux | grep node

# ポート使用状況
sudo netstat -tlnp
```

## 移行完了チェックリスト

- [ ] EC2インスタンス起動・SSH接続確認
- [ ] GitHubリポジトリクローン完了
- [ ] Node.js/Python環境セットアップ完了
- [ ] 認証情報・環境変数設定完了
- [ ] バックエンドAPI起動確認
- [ ] フロントエンド起動確認（該当する場合）
- [ ] Claude + Serena MCP動作確認
- [ ] VS Code Remote-SSH接続確認
- [ ] 本番表示テスト完了

## 注意事項

1. **セキュリティ**: 認証情報は絶対にGitにコミットしない
2. **バックアップ**: Windows環境のコードは移行完了まで保持
3. **コスト**: EC2インスタンス稼働時間に注意
4. **ネットワーク**: インターネット接続が開発環境に必須

---

**移行担当**: Claude Code + あの（AIエンジニア）
**移行日**: 2025-09-04
**移行理由**: Windows/Linux環境差異解決、開発効率向上