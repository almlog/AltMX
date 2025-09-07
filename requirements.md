# AltMX - AI協働開発ライブデモンストレーションシステム 要件分析書

## Project Overview
**Project Name**: AltMX (Alternative Model X)  
**Version**: 1.0  
**Date**: 2025-09-01  
**Author**: AI Engineer "ANO" & SHUNPEI  

## Executive Summary
社内AI活用を促進するためのライブデモンストレーションシステム。AI エージェント「AltMX」との対話を通じて、45-60分のセッション中に実用的な業務ツールをリアルタイムで開発・デプロイする様子を実演する。参加者が「AIは難しい」から「AIと一緒なら簡単」へ意識変革することを目的とする。

## Stakeholders
### Primary Stakeholders
- **End Users**: 全社員（技術職・非技術職問わず）
- **Business Stakeholders**: 経営層、IT部門、各部署管理職
- **Development Team**: プレゼンター、技術サポート、システム開発者

### Secondary Stakeholders
- **External Services**: Claude API、Microsoft Graph API、LINEWORKS API providers
- **Infrastructure**: Vercel、Supabase等のクラウドプロバイダー

## Functional Requirements

### Core Features

#### Feature 1: AI Agent Voice & Chat Interface
- **Description**: 札幌なまりで親しみやすいAIエージェント「AltMX」との音声・テキスト対話
- **User Story**: As a presenter, I want to interact with AltMX naturally with voice so that participants can see AI as a friendly talking partner
- **Acceptance Criteria**:
  - [ ] 札幌なまり（「なんまら」「っしょ」等）を適切に使用
  - [ ] **音声合成（TTS）**: AltMXが実際に喋る（札幌なまり対応）
  - [ ] **音声認識（STT）**: プレゼンターの音声入力対応
  - [ ] 技術用語を噛み砕いて説明できる
  - [ ] エラー時も親しみやすく対応（「ちょっと調子悪いわ」等）
  - [ ] テキスト入力・出力も並行対応
  - [ ] レスポンス速度 < 2秒（音声生成含む）
- **Priority**: High

#### Feature 2: Real-time Code Generation
- **Description**: 要求に基づいてReact/TypeScriptコードを自動生成
- **User Story**: As a presenter, I want to generate working code in real-time so that participants can see immediate results
- **Acceptance Criteria**:
  - [ ] React + TypeScript コンポーネントの生成
  - [ ] TailwindCSSでのスタイリング自動適用
  - [ ] APIエンドポイント（FastAPI）の生成
  - [ ] 生成速度 < 5秒
  - [ ] 生成コードのシンタックスエラー率 < 5%
- **Priority**: High

#### Feature 3: Live Preview & Instant Deploy
- **Description**: 生成されたコードのリアルタイムプレビューと即座のデプロイ
- **User Story**: As a participant, I want to see the created tool working immediately so that I can understand its practical value
- **Acceptance Criteria**:
  - [ ] Hot reloadでのライブプレビュー
  - [ ] Vercelへの自動デプロイ（< 30秒）
  - [ ] 共有可能なURL生成
  - [ ] モバイル対応の自動最適化
  - [ ] SSL対応（https://）
- **Priority**: High

#### Feature 4: Participant Interaction System
- **Description**: SLACK/LINEWORKS等コミュニケーションツールでの参加者リクエスト受付システム
- **User Story**: As a participant, I want to submit feature requests via familiar chat tools so that I can easily participate without additional setup
- **Acceptance Criteria**:
  - [ ] SLACK API連携でのリアルタイムメッセージ受信
  - [ ] LINEWORKS API連携でのリアルタイムメッセージ受信
  - [ ] Discord/Teams対応（将来拡張）
  - [ ] 要求の優先度付け・投票機能（リアクション活用）
  - [ ] モデレーション機能（不適切投稿フィルター）
  - [ ] 要求の自動分類（UI改善、新機能、連携等）
- **Priority**: High

#### Feature 5: Session Management
- **Description**: デモセッションの進行管理とモニタリング
- **User Story**: As a presenter, I want to manage session flow smoothly so that I can deliver effective demonstrations
- **Acceptance Criteria**:
  - [ ] セッション開始・終了制御
  - [ ] 進捗状況の可視化（プログレスバー）
  - [ ] 参加者数・アクティビティの監視
  - [ ] デモシナリオのテンプレート管理
  - [ ] セッション録画・ログ保存
- **Priority**: Medium

### Supporting Features
- Windows 95風UIテーマ（オプション）
- 多言語対応（日本語、英語）
- アクセシビリティ対応
- パフォーマンス監視・分析
- セキュリティログ・監査

## Non-Functional Requirements

### Performance Requirements
- **Response Time**: 
  - AI チャット応答: < 2秒
  - コード生成: < 5秒  
  - ライブプレビュー更新: < 1秒
- **Throughput**: 同時参加者 50名まで対応（画面共有+チャット参加前提）
- **Scalability**: セッション数に応じた自動スケーリング

### Security Requirements
- **Authentication**: 
  - 社内SSO（Microsoft AD）連携
  - セッション参加者認証
- **Authorization**: 
  - プレゼンター / 参加者 / 管理者の役割分離
  - API アクセス制御
- **Data Protection**: 
  - 生成コードの機密性確保
  - チャットデータの暗号化保存
  - GDPR準拠の個人情報保護

### Compatibility Requirements
- **Browser Compatibility**: 
  - Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Device Compatibility**: 
  - Desktop (Windows, macOS, Linux)
  - Tablet (iPad, Android)
  - Mobile (iOS, Android) - 閲覧のみ
- **Integration Compatibility**:
  - LINEWORKS API v2.0
  - Microsoft Graph API v1.0
  - Claude API / OpenAI GPT-4 API

### Scalability Requirements
- **User Growth**: 最大50名同時参加対応（画面共有ベースの参加想定）
- **Session Scaling**: 複数セッションの同時実行（最大5セッション並行）
- **Data Growth**: セッションログ・生成コード履歴の長期保存
- **Geographic Scaling**: 日本国内リージョン展開

## Technical Constraints
- **Technology Stack**: 
  - Frontend: React 18 + TypeScript 5.0 + TailwindCSS
  - Backend: FastAPI (Python 3.10+)
  - Database: Supabase (PostgreSQL)
  - Deployment: Vercel + Railway/Render
- **AI Integration**: Claude API または OpenAI GPT-4 API必須
- **Real-time Communication**: WebSocket (Socket.io)
- **Voice Technology**:
  - Text-to-Speech: Google Cloud Text-to-Speech API または Web Speech API
  - Speech-to-Text: Google Cloud Speech-to-Text API, OpenAI Whisper API, または Web Speech API
- **External APIs**: 
  - SLACK API（チャット連携・優先）
  - LINEWORKS API（社内チャット連携）
  - Microsoft Graph API（Office365連携）

## Business Rules
- セッション時間は45-60分に制限
- 生成されるコードは社内利用に限定
- 参加者の発言は記録・分析される旨の同意が必要
- デモ用に生成されたツールは30日後に自動削除
- API利用量制限: Claude API 100k tokens/session, 10 sessions/day

## Assumptions and Dependencies
### Assumptions
- 社内ネットワークは安定している
- 参加者はブラウザ操作の基本知識がある
- プレゼンターはAIとの対話に慣れている
- LINEWORKS/Microsoft Graph APIが利用可能

### Dependencies
- **External APIs**: Claude API, SLACK API, LINEWORKS API, Microsoft Graph API
- **Voice Services**: Google Cloud Speech APIs (TTS/STT) または OpenAI Whisper API
- **Infrastructure**: Vercel, Supabase, Google Cloud Services, AWS (if needed)
- **Internal**: 社内SSO認証システム、社内ネットワーク、画面共有システム（Zoom/Teams/Google Meet等）

## Success Criteria
- **Session Success Rate**: 95%以上のセッション完了率
- **Participant Engagement**: 平均70%以上の参加者がリクエスト投稿
- **Code Generation Success**: 90%以上の生成コードが実行可能
- **User Satisfaction**: セッション後アンケートで80%以上が満足
- **Business Impact**: 1ヶ月以内に5部署以上でAIツール導入

## Timeline and Milestones
- **Phase 1** (Week 1-2): プロトタイプ開発・基本機能実装
- **Phase 2** (Week 3-4): AI統合・リアルタイム機能開発
- **Phase 3** (Week 5-6): 外部API連携・UI完成
- **Phase 4** (Week 7-8): テスト・調整・本番環境構築

## Risk Assessment
### High Risk Items
- **AI API障害**: Claude/GPT-4 APIダウン時の対応策（フォールバック機能）
- **リアルタイム処理遅延**: 高負荷時のレスポンス遅延（キューイング・優先度制御）
- **デモ失敗**: ライブ実演でのエラー（事前テスト・代替シナリオ準備）

### Medium Risk Items
- **外部API制限**: 使用量上限への対策（監視・アラート）
- **セキュリティ**: 生成コードの脆弱性（コード検証・サニタイゼーション）
- **スケーラビリティ**: 予想以上の参加者数（オートスケーリング対応）

## Out of Scope
- 本格的な開発プロジェクト管理機能
- 商用レベルのセキュリティ監査
- 他言語（Python, Java等）でのコード生成
- オフライン動作対応
- 詳細なユーザー権限管理

## Future Considerations
- **Phase 2 Features**: 
  - 他のAI モデル（Gemini, Llama等）サポート
  - より自然な音声合成（感情表現、間の取り方）
  - AR/VR対応
  - 他チャットツール対応（Discord, Microsoft Teams等）
- **Enterprise Features**:
  - Advanced Analytics Dashboard
  - カスタムテンプレート機能
  - 部署別設定・カスタマイゼーション