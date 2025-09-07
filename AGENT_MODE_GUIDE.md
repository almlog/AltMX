# AIエージェントモード宣言システム

## 概要
「**エージェントをコーディングモードにセット**」- ユーザーが明示的にAIエージェントの動作モードを宣言し、専門的な作業に特化させるシステムです。

## 🎯 使用方法

### 基本的な宣言
```bash
# ライブコーディングモード宣言
curl -X POST http://18.180.87.189:8000/api/agent/declare-mode \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "live_coding",
    "quality_level": "production", 
    "personality": "mentor"
  }'
```

### レスポンス例
```json
{
  "success": true,
  "message": "🎥 ライブコーディングモードに設定しました。リアルタイムでコードを書きながら解説します。",
  "current_mode": "live_coding",
  "system_prompt": "あなたはライブコーディングのエキスパートです。\n- リアルタイムでコードを書きながら解説\n- 観客にとって分かりやすい進行...",
  "configuration": { ... }
}
```

## 🎭 利用可能なモード

### 1. 💻 **Coding Mode** - 本格開発
```json
{
  "mode": "coding",
  "quality_level": "development",
  "personality": "professional"
}
```
- 高品質なコード生成
- ベストプラクティス適用
- テスト可能で保守しやすい実装

### 2. 🎥 **Live Coding Mode** - ライブコーディング
```json
{
  "mode": "live_coding", 
  "quality_level": "production",
  "personality": "mentor",
  "focus_areas": ["React", "TypeScript"],
  "session_goals": ["観客との相互作用", "教育的価値"]
}
```
- リアルタイム解説付き開発
- 段階的実装とテスト
- インタラクティブな進行

### 3. 🏭 **Production Mode** - エンタープライズ
```json
{
  "mode": "production",
  "quality_level": "production", 
  "personality": "expert",
  "focus_areas": ["Security", "Performance", "Accessibility"],
  "constraints": ["GDPR compliance", "WCAG 2.1 AA"]
}
```
- Fortune 500対応品質
- セキュリティファースト
- 完全アクセシビリティ対応

### 4. 🔍 **Code Review Mode** - 品質監査
```json
{
  "mode": "code_review",
  "personality": "expert", 
  "focus_areas": ["Security", "Performance"]
}
```
- 詳細な品質分析
- セキュリティ脆弱性チェック
- 具体的改善提案

### 5. 🏗️ **Architecture Mode** - システム設計
```json
{
  "mode": "architecture",
  "quality_level": "production",
  "focus_areas": ["Scalability", "Microservices"]
}
```
- スケーラブル設計
- 技術選定の根拠明示
- 将来の拡張性考慮

## 🎨 パーソナリティ設定

### **Professional** - プロフェッショナル
- 簡潔で技術的な対応
- 効率重視のコミュニケーション

### **Mentor** - メンター
- 教育的で励ましの多い対応
- ステップバイステップの説明

### **Expert** - エキスパート
- 権威ある深い専門知識
- 業界標準への言及

### **Friendly** - フレンドリー
- 親しみやすいサポート
- 心理的安全性を重視

### **Creative** - クリエイティブ
- 革新的アプローチ
- 従来の枠を超えた提案

## 📊 品質レベル

| レベル | 用途 | 特徴 |
|--------|------|------|
| **Prototype** | 概念実証 | 迅速な機能実装 |
| **Development** | 通常開発 | バランスの取れた品質 |
| **Staging** | 本番前 | 包括的テスト含む |
| **Production** | エンタープライズ | Fortune 500対応 |

## 🎯 実用的な使用シナリオ

### シナリオ1: ライブコーディング配信
```bash
# 準備フェーズ
curl -X POST .../api/agent/declare-mode -d '{
  "mode": "live_coding",
  "quality_level": "production", 
  "personality": "mentor",
  "focus_areas": ["React", "UX Design"],
  "session_goals": ["観客参加型開発", "教育的価値提供"],
  "audience": "中級〜上級開発者",
  "time_limit": 90
}'
```

**結果**: メンター型エージェントがリアルタイムで解説しながら、プロダクション品質のReactアプリを構築

### シナリオ2: 企業プロジェクト
```bash
# エンタープライズモード
curl -X POST .../api/agent/declare-mode -d '{
  "mode": "production",
  "quality_level": "production",
  "personality": "expert", 
  "focus_areas": ["Security", "Compliance", "Performance"],
  "constraints": ["GDPR", "WCAG 2.1 AA", "SOC2"],
  "session_goals": ["Enterprise-ready application"],
  "audience": "enterprise clients"
}'
```

**結果**: セキュリティとコンプライアンスに配慮した、企業導入可能なアプリケーション

### シナリオ3: 学習セッション
```bash
# 教育モード
curl -X POST .../api/agent/declare-mode -d '{
  "mode": "teaching",
  "personality": "mentor",
  "focus_areas": ["Fundamentals", "Best Practices"],
  "audience": "初心者",
  "session_goals": ["基礎概念の理解", "実践的スキル習得"]
}'
```

**結果**: 初心者に優しい、段階的で丁寧な指導

## 🔄 モード遷移

### セッション中のモード切り替え
```bash
# デバッグモードに切り替え
curl -X POST .../api/agent/declare-mode -d '{
  "mode": "debug",
  "personality": "expert",
  "focus_areas": ["Error Analysis", "Performance Profiling"]
}'

# 現在のモード確認
curl -X GET .../api/agent/current-mode
```

### モード履歴の活用
- 各モード遷移が記録される
- セッション分析に活用可能
- 効果的なワークフローの特定

## 💡 ベストプラクティス

### 1. **明確な目標設定**
```json
{
  "session_goals": [
    "プロダクション品質のTODOアプリ構築",
    "観客との質疑応答",
    "リアルタイムデバッグデモ"
  ]
}
```

### 2. **制約条件の明示**
```json
{
  "constraints": [
    "60分以内での完成",
    "モバイル対応必須", 
    "アクセシビリティ準拠"
  ]
}
```

### 3. **オーディエンス最適化**
```json
{
  "audience": "React初心者",
  "personality": "mentor",
  "focus_areas": ["基本概念", "実践的パターン"]
}
```

## 🚀 高度な活用法

### 1. **チーム開発での活用**
- 役割別モード設定（アーキテクト、レビュアー、実装者）
- コードレビュー自動化
- 品質ゲートの実装

### 2. **教育コンテンツ作成**
- レベル別カリキュラム対応
- インタラクティブな学習体験
- 進捗追跡と適応的指導

### 3. **プロダクション運用**
- 環境別品質基準
- 自動コード監査
- コンプライアンスチェック

---

**「コーディングモードにセット」** - 一言でAIエージェントを専門家に変身させる、革新的な開発体験を提供します。