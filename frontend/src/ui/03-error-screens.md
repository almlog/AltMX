# 3. HTTPエラー画面（4パターン）

## 概要
トラブル発生時の対応画面。慌てずに録画デモへ切り替えるための演出。

## エラーパターン
1. **400 Bad Request** - オレンジ系カラー (`#ffb000`)
2. **404 Not Found** - シアン系カラー (`#00ffff`)
3. **500 Internal Server Error** - ピンク系カラー (`#ff006e`)
4. **503 Service Unavailable** - 紫系カラー (`#f093fb`)

## 共通機能
- エラーコードの大型表示
- AltMXからの親しみやすいメッセージ
- 録画デモへの切り替えボタン
- ステータス表示

## デザイン特徴
- グリッチアニメーション
- ネオングロー効果
- パーティクルエフェクト

## 実装要件

### React Component構成
- `ErrorScreenContainer.tsx` - メインコンテナ
- `ErrorScreen.tsx` - 個別エラー画面
- `ErrorCodeDisplay.tsx` - エラーコード大型表示
- `AltMXErrorMessage.tsx` - AIメッセージ
- `ErrorActionPanel.tsx` - アクションボタン群
- `ErrorStatusInfo.tsx` - ステータス情報表示
- `ErrorParticleEffect.tsx` - パーティクル効果

### 状態管理
```typescript
interface ErrorScreenState {
  currentError: 400 | 404 | 500 | 503 | null;
  isGlitching: boolean;
  particleCount: number;
  statusInfo: {
    aiStatus: 'online' | 'standby' | 'error';
    recordingReady: boolean;
    retryAvailable: boolean;
    waitTime?: number;
  };
  altmxMessages: {
    400: string;
    404: string;
    500: string;
    503: string;
  };
}
```

### エラー別設定

#### 400 Bad Request
- **カラー**: `#ffb000` (オレンジ)
- **メッセージ**: "あれ？なんか変なデータ来たっしょ...ちょっと録画デモに切り替えるわ！"
- **アクション**: [録画デモを再生, もう一度試す]
- **ステータス**: [AI: スタンバイ中, 録画: 準備完了]

#### 404 Not Found
- **カラー**: `#00ffff` (シアン)
- **メッセージ**: "探してるファイル、どっか行っちゃったわ...したっけ、録画のやつ見せるね！"
- **アクション**: [録画デモを再生, 最初から]
- **ステータス**: [検索中..., 代替案: あり]
- **特別要素**: ASCII Art装飾

#### 500 Internal Server Error
- **カラー**: `#ff006e` (ピンク)
- **メッセージ**: "なんまらヤバいことになったっしょ！でも大丈夫、録画があるから見せるわ〜"
- **アクション**: [録画デモに切替, 緊急モード]
- **ステータス**: [サーバー: エラー, バックアップ: OK]

#### 503 Service Unavailable
- **カラー**: `#f093fb` (紫)
- **メッセージ**: "ちょっと混雑してるみたいっしょ...録画デモなら、すぐ見せられるよ！"
- **アクション**: [録画を再生, 30秒待つ]
- **ステータス**: [API: 過負荷, 待機時間: 30秒]

### アニメーション詳細

#### グリッチ効果 (`glitch-in`)
```css
@keyframes glitch-in {
  0% { transform: scale(0.9) skew(1deg); opacity: 0; }
  20% { transform: scale(1.1) skew(-1deg); opacity: 0.5; }
  40% { transform: scale(0.95) skew(0.5deg); opacity: 0.8; }
  60% { transform: scale(1.05) skew(-0.5deg); }
  100% { transform: scale(1) skew(0); opacity: 1; }
}
```

#### 数字グリッチ (`number-glitch`)
```css
@keyframes number-glitch {
  0%, 100% { 
    text-shadow: 2px 0 #ff00ff, -2px 0 #00ffff, 0 0 30px currentColor; 
  }
  50% { 
    text-shadow: -2px 0 #ff00ff, 2px 0 #00ffff, 0 0 50px currentColor; 
  }
}
```

#### パーティクル (`float-away`)
- 0.5秒間隔で生成
- ランダムな色とサイズ
- 5秒後に自動削除
- ランダムな軌道で上昇・消失

### エフェクト仕様
1. **ネオンボーダー**: 3秒サイクルでパルス効果
2. **スキャンライン**: 背景に固定表示
3. **グリッドアニメーション**: 20秒サイクルで移動
4. **ボタンリップル**: クリック時の波紋効果
5. **ステータスドット**: 2秒サイクルで点滅

### 実装優先度
1. **Critical**: 基本エラー表示、メッセージ表示、録画切り替えボタン
2. **High**: グリッチアニメーション、カラー設定、ステータス表示
3. **Medium**: パーティクル効果、ASCII Art、高度なアニメーション
4. **Low**: カスタムスクロールバー、詳細なエフェクト

### アクション関数
- `switchToRecording()` - 録画デモへ切り替え
- `retry()` - リトライ処理
- `goHome()` - ホーム画面へ戻る
- `emergencyMode()` - 緊急モード起動
- `waitAndRetry()` - 待機後自動リトライ

### テスト項目
- [ ] 各エラー画面の表示確認
- [ ] グリッチアニメーション動作
- [ ] ボタンアクション確認
- [ ] パーティクル効果動作
- [ ] レスポンシブ対応確認