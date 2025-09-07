# 4. 休憩画面・エンディング画面

## 4-1. 休憩画面

### 概要
セッション中の休憩時間用画面。5分のカウントダウンタイマーと次セッションの予告。

### 主要機能
- カウントダウンタイマー（5:00 → 0:00）
- 音楽ビジュアライザー風アニメーション
- 次セッション予告表示
- 参加者へのメッセージ

### ビジュアル要素
- 大型デジタルタイマー
- ウェーブアニメーションバー
- フローティングパーティクル

## 4-2. エンディング画面（神聖バージョン）

### 概要
セッション完了時の締めくくり画面。達成感と神聖な雰囲気を演出。

### 演出コンセプト
「神様と天使が舞い降りた」ような輝かしい集大成

### 主要コンテンツ
- 統計表示（作成ツール数、生成行数など）
- 作成ツール一覧
- AltMXからの最終メッセージ
- ネクストアクション（相談/資料DL/コミュニティ）
- QRコード

### 特殊エフェクト
- 天から降り注ぐ光線
- 聖なる粒子の上昇
- ゴールドの紙吹雪
- オーラリング拡散
- 神聖なグロー効果

## 実装要件

### React Component構成

#### 休憩画面
- `BreakScreen.tsx` - メインコンポーネント
- `CountdownTimer.tsx` - カウントダウンタイマー
- `VisualWaveBar.tsx` - ビジュアライザー風バー
- `NextSessionPreview.tsx` - 次セッション予告
- `BreakMessage.tsx` - 参加者向けメッセージ

#### エンディング画面
- `EndingScreen.tsx` - メインコンテナ
- `SessionStatistics.tsx` - セッション統計表示
- `CreatedToolsList.tsx` - 作成ツール一覧
- `FinalMessage.tsx` - AltMXからの最終メッセージ
- `NextActionPanel.tsx` - ネクストアクション
- `QRCodeDisplay.tsx` - QRコード表示
- `HeavenlyEffects.tsx` - 神聖エフェクト

### 状態管理

#### 休憩画面
```typescript
interface BreakScreenState {
  timeRemaining: number; // 秒単位（0-300）
  isCountingDown: boolean;
  nextSessionInfo: {
    title: string;
    description: string;
    estimatedDuration: number;
  };
  waveAnimation: {
    bars: number[];
    frequency: number;
  };
}
```

#### エンディング画面
```typescript
interface EndingScreenState {
  sessionStats: {
    toolsCreated: number;
    linesGenerated: number;
    sessionDuration: number;
    successRate: number;
  };
  createdTools: Array<{
    name: string;
    type: string;
    complexity: 'simple' | 'medium' | 'complex';
  }>;
  finalMessage: string;
  nextActions: Array<{
    type: 'consultation' | 'download' | 'community';
    title: string;
    url: string;
    qrCode?: string;
  }>;
  heavenlyEffects: {
    lightRays: boolean;
    particles: boolean;
    confetti: boolean;
    auraRings: boolean;
  };
}
```

### アニメーション仕様

#### 休憩画面
1. **タイマー表示**: 120px `Orbitron` フォント、グラデーション
2. **ビジュアルバー**: 音楽ビジュアライザー風の上下動作
3. **背景**: 15秒サイクルでグラデーション変化
4. **パルス効果**: タイトルに2秒サイクル適用

#### エンディング画面
1. **光線効果**: 天から斜めに降り注ぐ光（CSS linear-gradient）
2. **粒子上昇**: 下から上へゆっくり浮上する光の粒
3. **紙吹雪**: ゴールド色の紙吹雪が舞い散る
4. **オーラリング**: 中央から外側へ拡散する光のリング
5. **神聖グロー**: 全体に柔らかい金色の光

### CSS/Animation設定

#### 休憩画面
```css
.timer-display {
  font-family: 'Orbitron', monospace;
  font-size: 120px;
  font-weight: 900;
  background: linear-gradient(45deg, #00ffff, #ff71ce);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: timer-pulse 1s ease-in-out infinite;
}

.wave-bar {
  animation: wave-bounce 0.5s ease-in-out infinite alternate;
}
```

#### エンディング画面
```css
.heavenly-light {
  background: linear-gradient(45deg, 
    transparent 0%, 
    rgba(255, 215, 0, 0.3) 50%, 
    transparent 100%);
  animation: light-sweep 3s ease-in-out infinite;
}

.sacred-particle {
  animation: float-to-heaven 4s ease-out infinite;
  opacity: 0.8;
  background: radial-gradient(circle, #ffd700, transparent);
}
```

### タイマー機能
- 5分（300秒）からのカウントダウン
- MM:SS形式での表示
- 残り1分で色が警告色に変化
- 0秒到達で自動的にメイン画面へ復帰

### エンディング統計
- セッション開始からの総時間
- 生成されたコード行数
- 作成されたツール/アプリケーション数
- 成功率（エラー発生率の逆算）
- AltMXとのやり取り回数

### 実装優先度

#### 休憩画面
1. **Critical**: カウントダウンタイマー、基本レイアウト
2. **High**: ビジュアルアニメーション、メッセージ表示
3. **Medium**: 波形バーアニメーション、背景エフェクト
4. **Low**: 高度なパーティクル効果

#### エンディング画面
1. **Critical**: 統計表示、最終メッセージ、QRコード
2. **High**: 基本的な光エフェクト、ツール一覧
3. **Medium**: 粒子エフェクト、紙吹雪アニメーション
4. **Low**: オーラリング、複雑な天からの光線

### テスト項目
- [ ] カウントダウンタイマーの正確性
- [ ] エンディング統計の正確な集計
- [ ] アニメーション効果の滑らかさ
- [ ] QRコード生成・表示
- [ ] レスポンシブ対応確認
- [ ] パフォーマンステスト（重いエフェクト時）