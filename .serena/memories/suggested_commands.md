# AltMX 開発用推奨コマンド

## Windows System Commands
```cmd
dir                    # ディレクトリ一覧表示 (ls equivalent)
cd [path]             # ディレクトリ移動
type [file]           # ファイル内容表示 (cat equivalent)
findstr [pattern]     # 文字列検索 (grep equivalent)
```

## Git Commands
```bash
git status            # 現在の状態確認
git add .             # 全変更をステージング
git commit -m "msg"   # コミット
git push              # リモートにプッシュ
```

## Project Setup Commands
```bash
# 全依存関係インストール
npm run install:all

# 開発サーバー起動 (frontend + backend 並行)
npm run dev

# フロントエンドのみ起動
npm run dev:frontend

# バックエンドのみ起動  
npm run dev:backend
```

## Testing Commands
```bash
# 全テスト実行
npm run test

# フロントエンドテスト
npm run test:frontend

# バックエンドテスト
npm run test:backend

# TDD用監視モード (推奨)
npm run test:watch
```

## Build Commands
```bash
# プロダクションビルド
npm run build
```

## Development Workflow
1. 要件確認: `requirements.md` 参照
2. 設計確認: `design.md` 参照  
3. タスク確認: `tasks.md` 参照
4. テスト作成: TDD でテストファースト
5. 実装: Red-Green-Refactor
6. 確認: `npm run test` でテスト実行