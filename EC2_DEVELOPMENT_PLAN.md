# EC2 Development Continuation Plan

## Overview
AltMXプロジェクトをEC2インスタンス上で開発継続するための計画書。ローカルWindows環境からEC2環境にプロジェクトファイルをコピー済み。これ以降はEC2インスタンス上で開発を行う。

## Current Infrastructure Status

### EC2 Instance Details
- **Instance ID**: i-0cf4529f22952a53d
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
- **IP Address**: 43.207.173.148
- **OS**: Ubuntu 22.04 LTS
- **SSH Access**: `ssh -i "altmx-dev-key.pem" AltMX-admin@43.207.173.148`

### Security Configuration
- **Custom Admin User**: AltMX-admin (ubuntu user deleted)
- **SSH Key**: altmx-dev-key.pem (dedicated key pair)
- **Security Groups**: HTTP/HTTPS/SSH access configured
- **Sudo Access**: AltMX-admin has full sudo privileges

### Development Environment Setup Status
✅ **Completed:**
- Python 3.10 + pip
- Node.js 18.x + npm
- Git configuration
- AltMX project repository cloned
- FastAPI backend running on port 8000
- Anthropic SDK installed
- Serena MCP basic structure created
- VS Code Remote-SSH connection verified

### Application Status
- **Backend API**: http://43.207.173.148:8000 (Running)
- **Frontend**: Needs cyber-pop design implementation
- **Database**: In-memory (FastAPI)
- **API Integration**: Claude API ready (needs key configuration)

## 完了したこと ✅

### EC2環境構築
- **EC2インスタンス**: t3.medium作成・設定完了
- **セキュリティ設定**: AltMX-adminユーザー作成、ubuntu削除、専用SSH鍵設定
- **基本ツール**: Python 3.10, Node.js 18.x, Git, npm, pip インストール完了
- **プロジェクトコピー**: ローカルからEC2にAltMXプロジェクト全体をコピー完了

### 開発環境セットアップ
- **FastAPI Backend**: 起動確認済み (http://43.207.173.148:8000)
- **Python仮想環境**: venv作成・アクティベート確認済み
- **Anthropic SDK**: インストール完了
- **VS Code Remote-SSH**: 接続確認済み

### 基本的なMCP構成
- **Serena MCP構造**: ~/.serena/ フォルダ・設定ファイル作成済み
- **Claude設定**: ~/.claude/claude_desktop_config.json 設定済み
- **カスタムSerena実装**: ~/serena-mcp/main.py 基本版作成済み

## できていないこと・必要なこと 🔄

### 即座に必要
1. **ANTHROPIC_API_KEY設定** - Claude APIテスト用
2. **GitHub最新版PULL** - この計画書を含む最新コードの取得
3. **サイバーポップUI実装** - 現在のMVP版を完全に置換

### 開発継続で必要
1. **フルスペックSerena MCP** - 現在は基本実装のみ
2. **本格的なUI/UX** - 現在のは仮のMVP、サイバーポップデザインに全面刷新
3. **リアルタイム通信** - WebSocket等でライブ更新
4. **本番環境設定** - SSL/TLS、ドメイン等

## 迷ったら見るところ 📚

### 重要ファイルの場所
```
/home/AltMX-admin/AltMX/
├── PERSONA.md              # 「あの」のペルソナ - 開発スタイル・好み
├── PROJECT_PLAN.md         # プロジェクト全体計画 (存在する場合)
├── tasks.md               # 現在のタスク状況
├── CLAUDE.md              # このプロジェクト用のClaude指示書
└── EC2_DEVELOPMENT_PLAN.md # この計画書
```

### 開発指針 - KIRo風
- **仕様駆動開発**: 実装前に必ず仕様書作成
- **TDD必須**: Red-Green-Refactor厳守
- **完成の定義**: コードが動く ≠ 完成。実際のユーザー体験まで確認必須
- **禁止事項**: テストなし完成宣言、エラー無視、表面的確認

### 技術スタック
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **AI Integration**: Claude API (Anthropic SDK)
- **Development**: VS Code + Claude-code + Serena MCP

### サイバーポップデザイン仕様
- **Color Scheme**: ネオンブルー (#00d4ff), ダーク背景 (#0a0a0a, #1a1a1a)
- **Typography**: JetBrains Mono (コード要素)
- **Visual Style**: サイバーパンク美学、ネオンハイライト
- **Interactive**: グロー効果、スムーズアニメーション
- **Layout**: 洗練されたダッシュボード (基本チャットインターフェースではない)

## 次のステップ（EC2上で実行）

### 1. 環境最終確認・設定
```bash
# SSH接続
ssh -i "altmx-dev-key.pem" AltMX-admin@43.207.173.148

# 最新コードPULL
cd ~/AltMX
git pull origin master

# API Key設定（実際のキーに置換）
export ANTHROPIC_API_KEY=your_actual_key_here
echo 'export ANTHROPIC_API_KEY=your_actual_key_here' >> ~/.bashrc

# Claude APIテスト
python3 claude_test.py
```

### 2. VS Code Remote開発環境起動
```bash
# VS Code Remote-SSH接続
code --remote ssh-remote+43.207.173.148 /home/AltMX-admin/AltMX
```

### 3. サイバーポップUI実装開始
```bash
# フロントエンド開発サーバー起動
cd ~/AltMX/frontend
npm run dev
```

## トラブルシューティング 🔧

### よくある問題と解決法
1. **SSH接続が切れる**
   ```bash
   # ~/.ssh/config に設定追加
   Host altmx-ec2
       HostName 43.207.173.148
       User AltMX-admin
       IdentityFile /path/to/altmx-dev-key.pem
       ServerAliveInterval 60
       ServerAliveCountMax 3
   ```

2. **Serena MCPが動かない**
   ```bash
   # 基本設定確認
   ls -la ~/.serena/
   cat ~/.claude/claude_desktop_config.json
   python3 ~/serena-mcp/main.py  # 直接テスト
   ```

3. **Node.js/npm問題**
   ```bash
   # Node.jsバージョン確認・切り替え
   node --version
   npm --version
   # 必要に応じてnvm使用
   ```

4. **ポート問題**
   ```bash
   # ポート使用状況確認
   sudo netstat -tlnp | grep :8000
   sudo netstat -tlnp | grep :5173  # Vite dev server
   ```

### 緊急時コマンド
```bash
# サーバープロセス強制停止
pkill -f "python main.py"
pkill -f "npm run dev"

# Git状態リセット
git stash
git checkout master
git pull origin master

# 環境再構築
source ~/AltMX/venv/bin/activate
cd ~/AltMX/frontend && npm install
```

## 重要な注意事項 ⚠️

### 開発継続時の必須確認
1. **BackendとFrontend両方起動** - 別ターミナルで並行実行
2. **ANTHROPIC_API_KEY設定済み** - Claude API機能に必須
3. **Git最新版確認** - 作業前に必ずpull
4. **Tailwind設定確認** - サイバーポップカラーが定義済みか

### ファイル更新時の注意
- **tasks.md**: 進捗更新時は必ずcommit
- **frontend/src/App.tsx**: サイバーポップUI実装時は完全置換
- **backend/main.py**: API変更時はテスト実行必須

### セキュリティ注意
- **API Key露出禁止** - 環境変数のみ使用
- **SSH Key管理** - .pemファイルは権限400維持
- **Git Commit前確認** - 機密情報含まれていないかチェック

---

**EC2インスタンス上で開発継続準備完了。次はGitHub PUSHしてEC2でPULLして最新化後、サイバーポップUI実装開始。**

## Cost Optimization Notes
- **Current Cost**: ~$0.0464/hour for t3.medium
- **Daily Cost**: ~$1.11/day
- **Monthly Estimate**: ~$33.60/month
- **Stop instance when not actively developing**
- **Consider t3.small for basic development (if sufficient)**

## Security Considerations
- SSH key rotation (monthly recommended)
- Regular security updates: `sudo apt update && sudo apt upgrade`
- Monitor access logs: `sudo tail -f /var/log/auth.log`
- Firewall rules review (Security Groups)

## Backup Strategy
- **Code**: GitHub repository (primary backup)
- **Configuration**: Document all custom configurations
- **Data**: No persistent data storage currently (FastAPI in-memory)
- **Instance Snapshots**: Consider weekly EBS snapshots for development environment

---

**Ready to continue development on EC2 with cyber-pop frontend implementation.**