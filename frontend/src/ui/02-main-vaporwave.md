# 2. メイン画面（ヴェイパーウェイブUI）

## 概要
ライブパフォーマンスの中核となる画面。AltMXとの対話、コード生成、デプロイまでの全工程を表示。

## レイアウト構成
- **左パネル**: AltMXステータス、トークログ
- **メインエリア**: コード表示（4つの表示モード切替可能）
- **下部**: アクションボタン（GENERATE/DEBUG/DEPLOY/SAVE）

## 表示モード
1. **コードビュー**: リアルタイムコード生成
2. **ファイルツリー**: プロジェクト構造
3. **ファイル表示**: 個別ファイル詳細
4. **プレビュー**: 実行結果のライブプレビュー

## インタラクティブ要素
- タブ切り替え
- プログレスバーアニメーション
- トークログ自動スクロール
- ホバーエフェクト

## デザインコンセプト
- **メインテーマ**: 80-90年代レトロコンピューター × ヴェイパーウェイブ
- **カラーパレット**:
  - Primary: `#00ffff` (シアン)、`#ff71ce` (ピンク)
  - Secondary: `#ffb000` (オレンジ)、`#00ff41` (グリーン)
  - Background: `#000000` (黒)、透明度設定

## 実装要件

### React Component構成
- `VaporwaveMainScreen.tsx` - メインコンポーネント
- `SidePanel.tsx` - 左サイドパネル
- `AltMXStatusPanel.tsx` - AltMXステータス表示
- `TalkLogPanel.tsx` - トークログ表示
- `CodeDisplayArea.tsx` - コード表示エリア
- `ViewTabs.tsx` - 表示モード切り替えタブ
- `ActionButtons.tsx` - アクションボタン群
- `ProgressBar.tsx` - プログレスバー
- `TurboModeButton.tsx` - ターボモードボタン

### 状態管理
```typescript
interface VaporwaveMainScreenState {
  currentView: 'code' | 'tree' | 'file' | 'preview';
  altmxStatus: {
    recognition: 'online' | 'offline';
    generation: 'turbo' | 'normal' | 'eco';
    quality: 'maximum' | 'high' | 'medium';
    speed: number; // tokens/second
  };
  talkLog: Array<{
    type: 'user' | 'ai';
    message: string;
    timestamp: Date;
  }>;
  codeContent: {
    currentCode: string;
    fileTree: FileNode[];
    selectedFile: string;
    previewUrl: string;
  };
  progress: {
    current: number;
    message: string;
    isActive: boolean;
  };
  isTurboMode: boolean;
}
```

### CSS/Animation設定
- ネオンパネルグロー効果（3秒サイクル）
- AltMXアバターフロートアニメーション（3秒）
- ロゴパルス効果（2秒サイクル）
- プログレスバーパルス（2秒サイクル）
- ホバー時のスキャンライン効果
- ボタンリップルエフェクト

### 特別エフェクト
1. **ネオングロー**: 全パネルに適用、透明度・ぼかし効果
2. **スキャンライン**: 背景に縦線アニメーション
3. **グリッチエフェクト**: エラー時やターボモード時
4. **パーティクル**: 重要アクション時の演出
5. **トランジション**: 滑らかなビュー切り替え

### インタラクション仕様
- **タブ切り替え**: スムーズなフェードイン/アウト
- **ボタンホバー**: スケール変換 + グロー強化
- **ボタンクリック**: リップル効果 + 一時的なスケール縮小
- **スクロール**: カスタムスクロールバー（ネオン効果付き）
- **プログレス更新**: 1秒間隔でランダム進行

### API連携
- リアルタイムコード生成状況
- トークログ同期
- ファイル構造更新
- デプロイ状況監視

## 実装優先度
1. **Critical**: 基本レイアウト、タブ切り替え、ネオンパネル
2. **High**: トークログ機能、プログレスバー、AltMXステータス
3. **Medium**: アニメーション効果、ホバーエフェクト
4. **Low**: 高度なパーティクル効果、グリッチエフェクト

## パフォーマンス考慮事項
- アニメーションのGPU使用最適化（transform/opacity使用）
- トークログの仮想スクロール（大量履歴対応）
- コード表示の遅延読み込み
- エフェクト用CSS3プロパティの適切な使用

## テスト項目
- [ ] 全タブ切り替え動作確認
- [ ] トークログの自動スクロール
- [ ] プログレスバーアニメーション
- [ ] レスポンシブ対応確認
- [ ] パフォーマンステスト（60fps維持）