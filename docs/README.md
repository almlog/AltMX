# AltMX 開発ドキュメント

## ドキュメント一覧

### 開発プロセス順
1. **[01_project_setup.md](./01_project_setup.md)** - プロジェクト初期セットアップ
   - KIRo風開発手法の採用
   - 技術スタック選定  
   - プロジェクト構造設計

2. **[02_mvp_implementation.md](./02_mvp_implementation.md)** - MVP実装とフロントエンド構築
   - React + FastAPI の実装
   - カスタムAltMXエージェント作成
   - 基本UI構築

3. **[03_troubleshooting_and_testing.md](./03_troubleshooting_and_testing.md)** - トラブルシューティングとTDD実践
   - CORS問題の解決
   - TDD原則の学習と適用
   - 実ユーザーテストの重要性

## プロジェクト概要
**AltMX** - AI協働開発ライブデモンストレーションシステム  
札幌なまりで話すAIエージェント「AltMX」との対話で、リアルタイムツール開発を実演

## 現在の進捗
- ✅ **基盤設計**: 完了
- ✅ **MVP基本機能**: 完了
- ✅ **フロントエンド⇔バックエンド通信**: 完了
- 🔄 **次期**: Claude API統合
- ⏳ **将来**: 音声機能、コード生成、AWS展開

## 技術スタック
- **Frontend**: React 18 + TypeScript + TailwindCSS
- **Backend**: FastAPI + Python
- **AI**: Claude API + Gemini API (予定)
- **Cloud**: Google Cloud + AWS

## 重要な学び
1. **TDDの重要性**: テストファーストがバグを防ぐ
2. **実ユーザー確認**: APIテスト ≠ ユーザビリティ
3. **札幌なまり実装**: 語彙辞書ベースの自然な変換
4. **MVP思考**: 完璧より動作する最小機能

## Qiita記事用素材
これらのドキュメントは最終的に統合して、以下のテーマでQiita記事化予定：
- 「札幌なまりAIエージェントをReact + FastAPIで作った話」
- 「TDD で学んだ『動く』と『使える』の違い」
- 「MVPアプローチでAIデモシステムを1日で構築」