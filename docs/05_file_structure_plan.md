# 05. UI/UX仕様書ファイル分割計画

## 🎯 分割の目的
- 管理性向上：35,649トークン → 適切サイズに分割
- 責任分離：設計 vs 実装 vs 運用の明確化  
- 再利用性：個別画面の独立開発・テスト

## 📁 提案する分割構造

### 1. 設計ドキュメント（docs/ui/）
```
docs/ui/
├── design_concept.md        # デザインコンセプト・原則
├── screen_specifications.md # 全画面の仕様概要
├── animation_guide.md       # アニメーション仕様
├── performance_guide.md     # 技術仕様・最適化
└── operation_manual.md      # 運用ガイド・カスタマイズ
```

### 2. 実装ファイル（frontend/screens/）
```
frontend/screens/
├── opening/
│   ├── opening.html         # オープニング画面
│   ├── opening.css          # 専用スタイル
│   └── opening.js           # 専用ロジック
├── main/
│   ├── main.html           # メイン画面
│   ├── main.css            # ヴェイパーウェイブUI
│   └── main.js             # インタラクティブ機能
├── error/
│   ├── error.html          # HTTPエラー画面
│   ├── error.css           # エラー演出
│   └── error.js            # エラー処理
├── break/
│   ├── break.html          # 休憩画面
│   ├── break.css           # 休憩演出
│   └── break.js            # タイマー機能
├── ending/
│   ├── ending.html         # エンディング画面
│   ├── ending.css          # 神聖演出
│   └── ending.js           # 成果表示
└── shared/
    ├── common.css          # 共通スタイル
    ├── animations.css      # 共通アニメーション
    └── utils.js            # 共通ユーティリティ
```

### 3. 統合管理（frontend/）
```
frontend/
├── index.html              # 統合エントリーポイント
├── app.js                  # 画面遷移制御
└── config.js               # 設定管理
```

## 🔄 分割手順

### Phase 1: 設計ドキュメント抽出
1. `design_concept.md` - デザインコンセプト部分
2. `screen_specifications.md` - 各画面仕様部分
3. `animation_guide.md` - アニメーション仕様部分
4. `performance_guide.md` - 技術仕様部分
5. `operation_manual.md` - 運用ガイド部分

### Phase 2: 実装コード分離
1. 各画面のHTML/CSS/JS抽出
2. 共通部分の特定・shared/作成
3. 動作テスト・調整

### Phase 3: 統合・テスト
1. 画面遷移システム構築
2. 全体動作確認
3. パフォーマンステスト

## 🎨 メリット

### 開発効率
- **並行開発**: 複数画面を同時開発可能
- **独立テスト**: 各画面の個別テスト
- **部分修正**: 特定画面のみ修正可能

### 保守性
- **責任明確**: 設計 vs 実装の分離
- **バージョン管理**: 変更履歴の追跡
- **再利用**: 他プロジェクトでの活用

### チーム協業
- **役割分担**: デザイナー・エンジニアの専門性
- **レビュー**: 部分的なコードレビュー
- **ドキュメント**: 仕様書の可読性向上

## 📋 次のアクション

1. **しゅんぺいに確認**: この分割方針でOK？
2. **実際の分割作業**: ファイル作成・移動
3. **動作テスト**: 分割後の動作確認
4. **GitHubコミット**: 整理された構造で保存

## 🎯 予想される課題と対策

### 課題1: 共通部分の重複
**対策**: shared/フォルダで共通化

### 課題2: 画面遷移の複雑化  
**対策**: app.jsで一元管理

### 課題3: 設定の散逸
**対策**: config.jsで設定統合