# タスク完了時のチェックリスト

## 各タスク完了時に必ず実行すること

### 1. テスト実行
```bash
npm run test          # 全テストが通ることを確認
```

### 2. 型チェック (TypeScript)
```bash
# フロントエンド
cd frontend && npx tsc --noEmit

# バックエンド (型ヒント確認)
cd backend && python -m mypy .
```

### 3. リンター & フォーマッター
```bash
# フロントエンド
cd frontend && npm run lint
cd frontend && npm run format

# バックエンド  
cd backend && black .
cd backend && flake8 .
```

### 4. ビルド確認
```bash
npm run build        # プロダクションビルドが通ることを確認
```

### 5. 動作確認
- `npm run dev` で開発サーバーが正常起動すること
- 実装した機能が期待通り動作すること
- エラーがコンソールに出ていないこと

### 6. ドキュメント更新
- コード変更に伴うREADME更新
- API変更時は設計書 (`design.md`) 更新
- 新機能追加時はタスクリスト (`tasks.md`) 更新

### 7. Git操作
```bash
git add .
git commit -m "[task-id] 簡潔なコミットメッセージ"
git push
```

## タスク完了の定義
- [ ] 全テストが通る
- [ ] TypeScript型エラーなし
- [ ] Lintエラーなし  
- [ ] ビルドエラーなし
- [ ] 手動動作確認完了
- [ ] 関連ドキュメント更新済み
- [ ] Git commit & push 完了