# Serena MCP Server 導入ガイド

## 概要

SerenaはModel Context Protocol (MCP)を使用した強力なコーディングエージェントツールキットです。セマンティックなコード検索・編集機能を提供し、Claude Codeと連携して開発効率を向上させます。

## 前提条件

- Python 3.8以上
- uvパッケージマネージャー
- Claude Code CLI

## インストール手順

### 1. uvパッケージマネージャーの確認・インストール

既にuvがインストールされているか確認：
```bash
python -m uv --version
```

インストールされていない場合：
```bash
python -m pip install uv
```

### 2. Serena MCPサーバーの設定

プロジェクトディレクトリで以下のコマンドを実行：

```bash
claude mcp add serena -- python -m uv tool run --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

Windows PowerShellの場合：
```powershell
claude mcp add serena -- python -m uv tool run --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $PWD
```

### 3. プロジェクト設定ファイルの作成

プロジェクトルートに`.serena`ディレクトリを作成：
```bash
mkdir -p .serena
```

`.serena/project.yml`ファイルを作成：
```yaml
project_name: [プロジェクト名]
language: [メイン言語]  # python, typescript, java, csharp, rust, go, ruby, cpp, php, swift, elixir, terraform, bash, markdown
description: [プロジェクトの説明]
```

例：
```yaml
project_name: MyProject
language: python
description: Python web application project
```

### 4. 対応言語

Serenaは以下の言語をサポート：
- Python
- TypeScript/JavaScript
- Java
- C#
- Rust
- Go
- Ruby
- C++
- PHP
- Swift
- Elixir
- Terraform
- Bash
- Markdown

### 5. 動作確認

Claude Codeを再起動後、以下のコマンドで確認：
```bash
claude mcp list
```

Serenaが正常に動作している場合、ツール一覧が表示されます。

## 主な機能

### セマンティック検索・編集ツール（19個）
- `list_dir` - ディレクトリ一覧
- `find_file` - ファイル検索
- `search_for_pattern` - パターン検索
- `get_symbols_overview` - シンボル概要取得
- `find_symbol` - シンボル検索
- `find_referencing_symbols` - 参照シンボル検索
- `replace_symbol_body` - シンボル本体置換
- `insert_after_symbol` - シンボル後挿入
- `insert_before_symbol` - シンボル前挿入
- `write_memory` - メモリ書き込み
- `read_memory` - メモリ読み込み
- `list_memories` - メモリ一覧
- `delete_memory` - メモリ削除
- `activate_project` - プロジェクト有効化
- `check_onboarding_performed` - オンボーディング確認
- `onboarding` - オンボーディング実行
- `think_about_collected_information` - 情報整理
- `think_about_task_adherence` - タスク遵守確認
- `think_about_whether_you_are_done` - 完了判定

### Webダッシュボード
- ログ表示とMCPサーバー管理
- デフォルト: http://127.0.0.1:24283/dashboard/index.html

## トラブルシューティング

### よくある問題と解決方法

#### 1. "No source files found" エラー
**原因**: プロジェクトに対応言語のソースファイルがない

**解決方法**:
- `.serena/project.yml`ファイルを手動作成
- 適切な`language`を設定

#### 2. "uvx: command not found" エラー
**原因**: uvが正しくインストールされていない

**解決方法**:
```bash
python -m pip install uv
```

#### 3. MCPサーバー接続失敗
**原因**: プロジェクト設定が不完全

**解決方法**:
1. `.serena`ディレクトリの存在確認
2. `project.yml`の内容確認
3. Claude Code再起動

#### 4. 文字エンコーディングエラー
**原因**: パスに日本語文字が含まれている

**解決方法**:
- 英数字のみのディレクトリに移動
- またはパスを適切にエスケープ

## 設定ファイル例

### Python プロジェクト
```yaml
project_name: PythonApp
language: python
description: Python web application with Django
```

### TypeScript プロジェクト
```yaml
project_name: ReactApp
language: typescript
description: React TypeScript frontend application
```

### Go プロジェクト
```yaml
project_name: GoAPI
language: go
description: REST API server written in Go
```

## 高度な設定

### カスタムコンテキスト
```bash
claude mcp add serena -- python -m uv tool run --from git+https://github.com/oraios/serena serena start-mcp-server --context custom-context --project $(pwd)
```

### SSEモード（Server-Sent Events）
```bash
python -m uv tool run --from git+https://github.com/oraios/serena serena start-mcp-server --transport sse --port 9121
```

## プロジェクト毎の設定を避ける方法

現在、Serenaはプロジェクト毎の設定が必要ですが、以下の方法で効率化できます：

### 1. セットアップスクリプト作成
```bash
#!/bin/bash
# setup-serena.sh
mkdir -p .serena
cat > .serena/project.yml << EOF
project_name: $(basename $PWD)
language: python  # または適切な言語を設定
description: Auto-generated project configuration
EOF

claude mcp add serena -- python -m uv tool run --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
```

### 2. テンプレート使用
プロジェクトテンプレートに`.serena`ディレクトリを含める

### 3. グローバル設定（将来的な機能）
現在は未対応ですが、将来のバージョンでグローバル設定が追加される可能性があります。

## 参考リンク

- [Serena GitHub Repository](https://github.com/oraios/serena)
- [MCP Protocol Documentation](https://mcp.so/)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)

## 更新履歴

- 2025-09-01: 初版作成（実際の導入手順を基に作成）