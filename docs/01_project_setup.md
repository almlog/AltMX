# 01. プロジェクト初期セットアップ

## 概要
AltMXプロジェクトの基盤構築と開発環境準備

## 実施内容

### 1. 開発環境準備
- **KIRo風開発手法の採用**: 仕様駆動開発（Specification-Driven Development）
- **TDD原則の確立**: テストファーストの開発サイクル
- **Serena MCP Server**: コード解析・編集ツールの導入

### 2. プロジェクト構造の決定
```
AltMX/
├── frontend/          # React + TypeScript
├── backend/           # FastAPI + Python  
├── docs/              # 開発ドキュメント
├── CLAUDE.md          # AI開発設定
├── PERSONA.md         # 開発者ペルソナ
└── package.json       # Monorepo設定
```

### 3. 技術スタック選定
- **フロントエンド**: React 18 + TypeScript 5.0 + TailwindCSS
- **バックエンド**: FastAPI (Python 3.10+)
- **AI統合**: Claude API + Gemini API (Azure/GPT-4は除外)
- **クラウド**: Google Cloud + AWS (Azureは除外)
- **統合**: SLACK API優先、LINEWORKS API

### 4. 重要な設計決定
- **MVPアプローチ**: カスタムAIエージェントから開始
- **コスト最適化**: プロンプトエンジニアリングでファインチューニング回避
- **札幌なまり**: 「なんまら」「っしょ」「だべ」等の語彙体系
- **スポーツカーUI**: シンプルなライト点滅アニメーション

## 学んだこと
- **仕様駆動の重要性**: requirements.md → design.md → tasks.md の流れ
- **ユーザーフィードバック**: 技術選定での制約条件の重要性
- **MVP思考**: 全機能実装より基本機能の確実な動作優先

## 次のステップ
React + FastAPI の実際の実装とTailwindCSS設定